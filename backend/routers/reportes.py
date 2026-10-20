from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

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
