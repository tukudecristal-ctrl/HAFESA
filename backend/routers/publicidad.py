from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

from database import get_db
from dependencies import require_pantalla
import models, schemas

router = APIRouter()


def _redondear(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@router.post("/", response_model=schemas.PublicidadOut, status_code=201)
def crear_publicidad(
    data: schemas.PublicidadCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_pantalla("publicidad")),
):
    vendedores = (
        db.query(models.Vendedor)
        .filter(models.Vendedor.id.in_(data.vendedor_ids))
        .all()
    )
    if len(vendedores) != len(set(data.vendedor_ids)):
        raise HTTPException(status_code=404, detail="Uno o más asesores no existen")

    tipo_cambio = Decimal("1.000") if data.moneda == "PEN" else data.tipo_cambio
    monto_soles = _redondear(data.monto * tipo_cambio)

    dias = (data.fecha_final - data.fecha_inicio).days + 1
    celdas = dias * len(vendedores)
    monto_por_celda = _redondear(monto_soles / celdas)

    publicidad = models.Publicidad(
        medio=data.medio,
        fecha_inicio=data.fecha_inicio,
        fecha_final=data.fecha_final,
        moneda=data.moneda,
        monto=data.monto,
        tipo_cambio=tipo_cambio,
        monto_soles=monto_soles,
        observaciones=data.observaciones,
        usuario_id=user.get("usuario_id"),
    )
    db.add(publicidad)
    db.flush()  # obtener publicidad.id

    for vendedor in vendedores:
        for i in range(dias):
            fecha = data.fecha_inicio + timedelta(days=i)
            db.add(models.PublicidadDetalle(
                publicidad_id=publicidad.id,
                vendedor_id=vendedor.id,
                empresa_id=vendedor.empresa_id,
                fecha=fecha,
                monto_prorateado=monto_por_celda,
            ))

    db.commit()
    db.refresh(publicidad)

    publicidad_out = db.query(models.Publicidad).options(
        joinedload(models.Publicidad.detalles).joinedload(models.PublicidadDetalle.vendedor)
    ).get(publicidad.id)

    detalles_out = [
        schemas.PublicidadDetalleOut(
            vendedor_id=d.vendedor_id,
            nombre_vendedor=d.vendedor.nombre_completo,
            fecha=d.fecha,
            monto_prorateado=d.monto_prorateado,
        )
        for d in publicidad_out.detalles
    ]
    return schemas.PublicidadOut(
        id=publicidad_out.id,
        medio=publicidad_out.medio,
        fecha_inicio=publicidad_out.fecha_inicio,
        fecha_final=publicidad_out.fecha_final,
        moneda=publicidad_out.moneda,
        monto=publicidad_out.monto,
        tipo_cambio=publicidad_out.tipo_cambio,
        monto_soles=publicidad_out.monto_soles,
        observaciones=publicidad_out.observaciones,
        created_at=publicidad_out.created_at,
        detalles=detalles_out,
    )
