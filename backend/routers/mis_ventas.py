from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal

from database import get_db
from dependencies import get_current_user
import models, schemas

router = APIRouter()


def _vendedor_id(current_user: dict) -> int:
    vid = current_user.get("vendedor_id")
    if not vid:
        raise HTTPException(status_code=403, detail="No tienes un vendedor asociado")
    return vid


# ── Mis pedidos ─────────────────────────────────────────────────
@router.get("/pedidos")
def mis_pedidos(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    vid = _vendedor_id(current_user)
    pedidos = (
        db.query(models.Pedido)
        .filter(models.Pedido.vendedor_id == vid)
        .order_by(models.Pedido.fecha_registro.desc())
        .all()
    )
    result = []
    for p in pedidos:
        # Fecha del estado actual
        fecha_estado = {
            "REGISTRADO":     p.fecha_registro,
            "EMPACADO":       p.fecha_empacado,
            "ROTULO_IMPRESO": p.fecha_rotulo,
            "DEPOSITADO":     p.fecha_deposito,
            "ENTREGADO":      p.fecha_entrega,
            "CANCELADO":      p.fecha_cancelado,
        }.get(p.estado)

        # Items
        items = [
            {"nombre": d.producto.nombre if d.producto else "—", "cantidad": d.cantidad, "subtotal": float(d.subtotal or 0)}
            for d in p.detalles
        ]

        # Comisión (solo si entregado y sin pagar)
        comision = None
        if p.estado == "ENTREGADO" and not p.fecha_pago_comision:
            empresa = p.empresa
            pct = Decimal(str(empresa.porcentaje_comision)) / 100 if empresa else Decimal("0")
            neto = Decimal(str(p.precio_total or 0)) - Decimal(str(p.descuento or 0))
            comision = float(pct * neto)

        result.append({
            "id":               p.id,
            "nombre_cliente":   p.nombre_cliente,
            "fecha_registro":   p.fecha_registro.isoformat() if p.fecha_registro else None,
            "estado":           p.estado,
            "fecha_estado":     fecha_estado.isoformat() if fecha_estado else None,
            "precio_total":     float(p.precio_total or 0),
            "descuento":        float(p.descuento or 0),
            "resta_pagar":      float(p.resta_pagar or 0),
            "comision_pendiente": comision,
            "comision_pagada":  p.fecha_pago_comision is not None,
            "items":            items,
        })
    return result


# ── Mi resumen de comisiones ────────────────────────────────────
@router.get("/comisiones")
def mis_comisiones(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    vid = _vendedor_id(current_user)
    vendedor = db.query(models.Vendedor).filter(models.Vendedor.id == vid).first()
    empresa = db.query(models.Empresa).filter(models.Empresa.id == vendedor.empresa_id).first() if vendedor else None
    pct = Decimal(str(empresa.porcentaje_comision)) / 100 if empresa else Decimal("0")

    pedidos = db.query(models.Pedido).filter(
        models.Pedido.vendedor_id == vid,
        models.Pedido.estado == "ENTREGADO",
    ).all()

    total_ventas = Decimal("0")
    comision_pendiente = Decimal("0")
    comision_cobrada = Decimal("0")

    for p in pedidos:
        neto = Decimal(str(p.precio_total or 0)) - Decimal(str(p.descuento or 0))
        total_ventas += neto
        comision = pct * neto
        if p.fecha_pago_comision:
            comision_cobrada += comision
        else:
            comision_pendiente += comision

    return {
        "vendedor_nombre":    vendedor.nombre_completo if vendedor else "—",
        "empresa_nombre":     empresa.nombre if empresa else "—",
        "porcentaje_comision": float(empresa.porcentaje_comision) if empresa else 0,
        "total_pedidos_entregados": len(pedidos),
        "total_ventas_netas": float(total_ventas),
        "comision_pendiente": float(comision_pendiente),
        "comision_cobrada":   float(comision_cobrada),
    }
