from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

from database import get_db
import models, schemas

router = APIRouter()


def _calcular_comision(precio_total, descuento, porcentaje) -> tuple[Decimal, Decimal]:
    """Retorna (monto_neto, comision)."""
    neto = Decimal(str(precio_total or 0)) - Decimal(str(descuento or 0))
    comision = (Decimal(str(porcentaje or 0)) / 100 * neto).quantize(Decimal("0.01"))
    return neto, comision


# ── Resumen por vendedor ───────────────────────────────────────
@router.get("/resumen", response_model=List[schemas.ComisionVendedorOut])
def resumen_comisiones(empresa_id: Optional[int] = None, db: Session = Depends(get_db)):
    q = (
        db.query(models.Pedido)
        .options(joinedload(models.Pedido.vendedor), joinedload(models.Pedido.empresa))
        .filter(
            models.Pedido.estado == "ENTREGADO",
            models.Pedido.fecha_pago_comision == None,
        )
    )
    if empresa_id:
        q = q.filter(models.Pedido.empresa_id == empresa_id)

    pedidos = q.all()

    # Agrupar por vendedor
    agrupado: dict[int, dict] = {}
    for p in pedidos:
        vid = p.vendedor_id
        empresa = p.empresa
        pct = Decimal(str(empresa.porcentaje_comision or 0))
        neto, comision = _calcular_comision(p.precio_total, p.descuento, pct)

        if vid not in agrupado:
            agrupado[vid] = {
                "vendedor_id":       vid,
                "nombre_completo":   p.vendedor.nombre_completo,
                "empresa_id":        p.empresa_id,
                "nombre_empresa":    empresa.nombre,
                "porcentaje_comision": pct,
                "pedidos_pendientes": 0,
                "ventas_netas":      Decimal("0"),
                "comision_pendiente": Decimal("0"),
            }
        agrupado[vid]["pedidos_pendientes"] += 1
        agrupado[vid]["ventas_netas"]       += neto
        agrupado[vid]["comision_pendiente"] += comision

    return list(agrupado.values())


# ── Detalle de pedidos pendientes de un vendedor ───────────────
@router.get("/vendedor/{vendedor_id}", response_model=List[schemas.ComisionPedidoOut])
def detalle_vendedor(vendedor_id: int, db: Session = Depends(get_db)):
    pedidos = (
        db.query(models.Pedido)
        .filter(
            models.Pedido.vendedor_id == vendedor_id,
            models.Pedido.estado == "ENTREGADO",
            models.Pedido.fecha_pago_comision == None,
        )
        .options(joinedload(models.Pedido.empresa))
        .order_by(models.Pedido.fecha_entrega)
        .all()
    )

    resultado = []
    for p in pedidos:
        pct = Decimal(str(p.empresa.porcentaje_comision or 0))
        neto, comision = _calcular_comision(p.precio_total, p.descuento, pct)
        resultado.append(schemas.ComisionPedidoOut(
            pedido_id=p.id,
            nombre_cliente=p.nombre_cliente,
            fecha_registro=p.fecha_registro,
            fecha_entrega=p.fecha_entrega,
            precio_total=Decimal(str(p.precio_total or 0)),
            descuento=Decimal(str(p.descuento or 0)),
            monto_neto=neto,
            comision=comision,
            porcentaje_comision=pct,
        ))
    return resultado


# ── Registrar pago de comisión ─────────────────────────────────
@router.post("/pagar")
def pagar_comisiones(data: schemas.PagarComisionesInput, db: Session = Depends(get_db)):
    if not data.pedido_ids:
        raise HTTPException(status_code=400, detail="Debe seleccionar al menos un pedido")

    pedidos = (
        db.query(models.Pedido)
        .filter(models.Pedido.id.in_(data.pedido_ids))
        .all()
    )

    if len(pedidos) != len(data.pedido_ids):
        raise HTTPException(status_code=404, detail="Uno o más pedidos no encontrados")

    for p in pedidos:
        if p.estado != "ENTREGADO":
            raise HTTPException(
                status_code=400,
                detail=f"Pedido #{p.id} no está en estado ENTREGADO"
            )
        if p.fecha_pago_comision:
            raise HTTPException(
                status_code=400,
                detail=f"Pedido #{p.id} ya tiene comisión pagada"
            )
        p.fecha_pago_comision = datetime.combine(data.fecha_pago, datetime.min.time())

    db.commit()
    return {"pagados": len(pedidos), "fecha_pago": str(data.fecha_pago)}
