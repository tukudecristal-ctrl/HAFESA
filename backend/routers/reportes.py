from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from decimal import Decimal

from database import get_db
from dependencies import require_roles
import schemas

router = APIRouter()

TIPO_A_TRUNC = {"dia": "day", "mes": "month", "anio": "year"}
MAX_DIAS_TIPO_DIA = 60


@router.get("/ventas", response_model=List[schemas.ReporteVentaItem])
def reporte_ventas(
    tipo: str = Query(..., pattern="^(dia|mes|anio)$"),
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(default_factory=date.today),
    empresa_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: dict = Depends(require_roles("administrador")),
):
    if fecha_fin < fecha_inicio:
        raise HTTPException(status_code=400, detail="fecha_fin no puede ser menor que fecha_inicio")

    if tipo == "dia" and (fecha_fin - fecha_inicio).days > MAX_DIAS_TIPO_DIA:
        raise HTTPException(
            status_code=400,
            detail=f"El quiebre por día solo admite rangos de hasta {MAX_DIAS_TIPO_DIA} días",
        )

    sql = text(f"""
        SELECT
            date_trunc(:trunc_unit, p.fecha_registro)::date AS periodo,
            e.nombre AS empresa,
            pr.nombre AS producto,
            pr.stock AS stock,
            pr.precio_venta AS precio_venta,
            SUM(dp.cantidad) AS suma_cantidad,
            SUM(dp.subtotal) AS suma_precio_venta,
            ROUND(SUM(dp.subtotal * pr.porcentaje_comision / 100), 2) AS suma_comision
        FROM pedidos p
        JOIN detalle_pedido dp ON dp.pedido_id = p.id
        JOIN productos pr ON pr.id = dp.producto_id
        JOIN empresas e ON e.id = p.empresa_id
        WHERE p.estado = 'ENTREGADO'
          AND p.fecha_registro >= :fecha_inicio
          AND p.fecha_registro < (:fecha_fin + interval '1 day')
          AND (:empresa_id IS NULL OR p.empresa_id = :empresa_id)
        GROUP BY periodo, e.nombre, pr.id, pr.nombre, pr.stock, pr.precio_venta
        ORDER BY periodo, e.nombre, pr.nombre
    """)

    filas = db.execute(sql, {
        "trunc_unit": TIPO_A_TRUNC[tipo],
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "empresa_id": empresa_id,
    }).mappings().all()

    return list(filas)


# ── Estado financiero ────────────────────────────────────────────
CERO = Decimal("0.00")

# La comisión se calcula igual que en la pantalla de Comisiones (la que se paga):
# % de la empresa × (precio_total − descuento), redondeada por pedido.
_COMISION_PEDIDO = "ROUND(e.porcentaje_comision / 100 * (COALESCE(p.precio_total, 0) - COALESCE(p.descuento, 0)), 2)"


def _por_mes(db: Session, sql: str, params: dict) -> dict:
    """Ejecuta una consulta que devuelve (mes, valores...) y la indexa por mes."""
    return {fila["mes"]: fila for fila in db.execute(text(sql), params).mappings().all()}


@router.get("/estado-financiero", response_model=schemas.EstadoFinancieroOut)
def estado_financiero(
    anio: int = Query(..., ge=2000, le=2100),
    mes: Optional[int] = Query(None, ge=1, le=12),
    empresa_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: dict = Depends(require_roles("administrador")),
):
    inicio = date(anio, mes or 1, 1)
    if mes:
        fin = date(anio + (mes == 12), mes % 12 + 1, 1)
    else:
        fin = date(anio + 1, 1, 1)
    params = {"inicio": inicio, "fin": fin, "empresa_id": empresa_id}

    ventas = _por_mes(db, """
        SELECT EXTRACT(MONTH FROM p.fecha_registro)::int AS mes, SUM(dp.subtotal) AS ventas
        FROM pedidos p
        JOIN detalle_pedido dp ON dp.pedido_id = p.id
        WHERE p.estado = 'ENTREGADO'
          AND p.fecha_registro >= :inicio AND p.fecha_registro < :fin
          AND (:empresa_id IS NULL OR p.empresa_id = :empresa_id)
        GROUP BY mes
    """, params)

    pedidos = _por_mes(db, f"""
        SELECT EXTRACT(MONTH FROM p.fecha_registro)::int AS mes,
               SUM(COALESCE(p.descuento, 0)) AS descuentos,
               SUM({_COMISION_PEDIDO}) AS comisiones,
               SUM(CASE WHEN p.fecha_pago_comision IS NOT NULL THEN {_COMISION_PEDIDO} ELSE 0 END) AS pagadas
        FROM pedidos p
        JOIN empresas e ON e.id = p.empresa_id
        WHERE p.estado = 'ENTREGADO'
          AND p.fecha_registro >= :inicio AND p.fecha_registro < :fin
          AND (:empresa_id IS NULL OR p.empresa_id = :empresa_id)
        GROUP BY mes
    """, params)

    compras = _por_mes(db, """
        SELECT EXTRACT(MONTH FROM c.fecha_compra)::int AS mes, SUM(c.total_calculado) AS compras
        FROM compras c
        WHERE c.fecha_compra >= :inicio AND c.fecha_compra < :fin
          AND (:empresa_id IS NULL OR c.empresa_id = :empresa_id)
        GROUP BY mes
    """, params)

    publicidad = _por_mes(db, """
        SELECT EXTRACT(MONTH FROM d.fecha)::int AS mes, SUM(d.monto_prorateado) AS publicidad
        FROM publicidad_detalle d
        WHERE d.fecha >= :inicio AND d.fecha < :fin
          AND (:empresa_id IS NULL OR d.empresa_id = :empresa_id)
        GROUP BY mes
    """, params)

    def valor(fuentes: dict, m: int, campo: str) -> Decimal:
        fila = fuentes.get(m)
        return Decimal(fila[campo] or 0) if fila else CERO

    def armar(m: Optional[int], v, d, c, pag, comp, pub) -> schemas.EstadoFinancieroPeriodo:
        netas = v - d
        return schemas.EstadoFinancieroPeriodo(
            mes=m,
            ventas_brutas=v,
            descuentos=d,
            ventas_netas=netas,
            compras=comp,
            comisiones=c,
            comisiones_pagadas=pag,
            comisiones_pendientes=c - pag,
            publicidad=pub,
            resultado_neto=netas - comp - c - pub,
        )

    meses_rango = [mes] if mes else list(range(1, 13))
    periodos = [
        armar(
            m,
            valor(ventas, m, "ventas"),
            valor(pedidos, m, "descuentos"),
            valor(pedidos, m, "comisiones"),
            valor(pedidos, m, "pagadas"),
            valor(compras, m, "compras"),
            valor(publicidad, m, "publicidad"),
        )
        for m in meses_rango
    ]

    def suma(campo: str) -> Decimal:
        return sum((getattr(p, campo) for p in periodos), CERO)

    total = armar(
        None,
        suma("ventas_brutas"), suma("descuentos"), suma("comisiones"),
        suma("comisiones_pagadas"), suma("compras"), suma("publicidad"),
    )
    return schemas.EstadoFinancieroOut(
        anio=anio, mes=mes, empresa_id=empresa_id, meses=periodos, total=total,
    )
