from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from decimal import Decimal

from database import get_db
import models, schemas

router = APIRouter()


# ── Listar compras ─────────────────────────────────────────────
@router.get("/", response_model=List[schemas.CompraOut])
def listar_compras(
    empresa_id: int | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(models.Compra).options(joinedload(models.Compra.detalles))
    if empresa_id:
        q = q.filter(models.Compra.empresa_id == empresa_id)
    return q.order_by(models.Compra.fecha_compra.desc()).all()


# ── Registrar compra ───────────────────────────────────────────
@router.post("/", response_model=schemas.CompraOut, status_code=201)
def registrar_compra(data: schemas.CompraCreate, db: Session = Depends(get_db)):
    if not data.detalles:
        raise HTTPException(status_code=400, detail="La compra debe tener al menos un item")

    # Verificar que todos los productos existen
    ids_productos = [d.producto_id for d in data.detalles]
    productos = db.query(models.Producto).filter(models.Producto.id.in_(ids_productos)).all()
    if len(productos) != len(ids_productos):
        raise HTTPException(status_code=404, detail="Uno o más productos no encontrados")

    # Calcular total
    subtotal_items = sum(d.cantidad * d.costo_unitario for d in data.detalles)
    total = subtotal_items + data.costo_transporte + data.costo_impuesto + data.otros_costos

    compra = models.Compra(
        empresa_id=data.empresa_id,
        proveedor_id=data.proveedor_id,
        fecha_compra=data.fecha_compra,
        costo_transporte=data.costo_transporte,
        costo_impuesto=data.costo_impuesto,
        otros_costos=data.otros_costos,
        total_calculado=total,
        observaciones=data.observaciones,
    )
    db.add(compra)
    db.flush()  # obtener compra.id sin commitear aún

    # Insertar detalles y actualizar stock
    mapa_productos = {p.id: p for p in productos}
    for item in data.detalles:
        detalle = models.DetalleCompra(
            compra_id=compra.id,
            producto_id=item.producto_id,
            cantidad=item.cantidad,
            costo_unitario=item.costo_unitario,
        )
        db.add(detalle)
        mapa_productos[item.producto_id].stock += item.cantidad

    db.commit()
    db.refresh(compra)
    return compra


# ── Detalle de compra ──────────────────────────────────────────
@router.get("/{compra_id}", response_model=schemas.CompraOut)
def obtener_compra(compra_id: int, db: Session = Depends(get_db)):
    compra = (
        db.query(models.Compra)
        .options(joinedload(models.Compra.detalles))
        .filter(models.Compra.id == compra_id)
        .first()
    )
    if not compra:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    return compra
