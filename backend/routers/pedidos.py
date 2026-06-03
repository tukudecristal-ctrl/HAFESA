from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal

from database import get_db
import models, schemas

router = APIRouter()

TIMESTAMP_POR_ESTADO = {
    "EMPACADO":       "fecha_empacado",
    "ROTULO_IMPRESO": "fecha_rotulo",
    "DEPOSITADO":     "fecha_deposito",
    "ENTREGADO":      "fecha_entrega",
    "CANCELADO":      "fecha_cancelado",
}


# ── Listar pedidos ─────────────────────────────────────────────
@router.get("/", response_model=List[schemas.PedidoOut])
def listar_pedidos(
    empresa_id: Optional[int] = None,
    vendedor_id: Optional[int] = None,
    estado: Optional[str] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    dni: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(models.Pedido).options(
        joinedload(models.Pedido.detalles).joinedload(models.DetallePedido.producto),
        joinedload(models.Pedido.empresa),
        joinedload(models.Pedido.agencia),
    )
    if empresa_id:
        q = q.filter(models.Pedido.empresa_id == empresa_id)
    if vendedor_id:
        q = q.filter(models.Pedido.vendedor_id == vendedor_id)
    if estado:
        q = q.filter(models.Pedido.estado == estado.upper())
    if fecha_desde:
        q = q.filter(models.Pedido.fecha_registro >= datetime.combine(fecha_desde, datetime.min.time()))
    if fecha_hasta:
        q = q.filter(models.Pedido.fecha_registro <= datetime.combine(fecha_hasta, datetime.max.time()))
    if dni:
        q = q.filter(models.Pedido.dni == dni)
    return q.order_by(models.Pedido.fecha_registro.desc()).all()


# ── Crear pedido ───────────────────────────────────────────────
@router.post("/", response_model=schemas.PedidoOut, status_code=201)
def crear_pedido(data: schemas.PedidoCreate, db: Session = Depends(get_db)):
    # Validar consistencia de tipo_destino
    if data.tipo_destino == 'shalom' and not data.agencia_id:
        raise HTTPException(status_code=400, detail="agencia_id requerido cuando tipo_destino='shalom'")
    if data.tipo_destino == 'otro' and not data.direccion_otra_agencia:
        raise HTTPException(status_code=400, detail="direccion_otra_agencia requerido cuando tipo_destino='otro'")

    # Validar productos y calcular precios
    detalles_preparados = []
    for item in data.detalles:
        producto = db.query(models.Producto).filter(models.Producto.id == item.producto_id).first()
        if not producto:
            raise HTTPException(status_code=404, detail=f"Producto {item.producto_id} no encontrado")
        stock_disponible = max(0, (producto.stock or 0) - (producto.stock_comprometido or 0))
        if stock_disponible < item.cantidad:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente para '{producto.nombre}'. Disponible: {stock_disponible}",
            )
        precio_unitario = schemas.seleccionar_precio(producto, item.cantidad)
        detalles_preparados.append((producto, item.cantidad, precio_unitario))

    # Calcular totales
    subtotal_items = sum(cant * precio for _, cant, precio in detalles_preparados)
    precio_total = subtotal_items + data.costo_envio
    resta_pagar = precio_total - data.descuento - data.separacion

    # Crear cabecera del pedido
    pedido = models.Pedido(
        empresa_id=data.empresa_id,
        vendedor_id=data.vendedor_id,
        nombre_cliente=data.nombre_cliente,
        dni=data.dni,
        telefono=data.telefono,
        agencia_id=data.agencia_id,
        tipo_destino=data.tipo_destino,
        direccion_otra_agencia=data.direccion_otra_agencia,
        detalle_observacion=data.detalle_observacion,
        separacion=data.separacion,
        costo_envio=data.costo_envio,
        descuento=data.descuento,
        precio_total=precio_total,
        resta_pagar=resta_pagar,
        estado="REGISTRADO",
    )
    db.add(pedido)
    db.flush()  # obtener pedido.id antes del commit

    # Crear detalles e incrementar stock comprometido
    for producto, cantidad, precio_unitario in detalles_preparados:
        detalle = models.DetallePedido(
            pedido_id=pedido.id,
            producto_id=producto.id,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
        )
        db.add(detalle)
        producto.stock_comprometido = (producto.stock_comprometido or 0) + cantidad

    db.commit()
    db.refresh(pedido)
    return pedido


# ── Detalle de pedido ──────────────────────────────────────────
@router.get("/{pedido_id}", response_model=schemas.PedidoDetalleOut)
def obtener_pedido(pedido_id: int, db: Session = Depends(get_db)):
    pedido = (
        db.query(models.Pedido)
        .options(
            joinedload(models.Pedido.empresa),
            joinedload(models.Pedido.vendedor),
            joinedload(models.Pedido.producto),
            joinedload(models.Pedido.agencia),
            joinedload(models.Pedido.detalles),
        )
        .filter(models.Pedido.id == pedido_id)
        .first()
    )
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return pedido


# ── Avanzar estado ─────────────────────────────────────────────
@router.post("/{pedido_id}/avanzar", response_model=schemas.PedidoOut)
def avanzar_estado(
    pedido_id: int,
    data: schemas.PedidoEstadoUpdate,
    db: Session = Depends(get_db),
):
    pedido = (
        db.query(models.Pedido)
        .options(joinedload(models.Pedido.detalles))
        .filter(models.Pedido.id == pedido_id)
        .first()
    )
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    siguiente = schemas.SIGUIENTE_ESTADO.get(pedido.estado)
    if not siguiente:
        raise HTTPException(status_code=400, detail=f"El pedido ya está en estado final: {pedido.estado}")

    # Al pasar a DEPOSITADO: descontar stock real y stock comprometido
    if siguiente == "DEPOSITADO":
        for detalle in pedido.detalles:
            producto = db.query(models.Producto).filter(models.Producto.id == detalle.producto_id).first()
            if producto:
                producto.stock = max(0, (producto.stock or 0) - detalle.cantidad)
                producto.stock_comprometido = max(0, (producto.stock_comprometido or 0) - detalle.cantidad)

    log = models.FlujoLog(
        pedido_id=pedido.id,
        estado_anterior=pedido.estado,
        estado_nuevo=siguiente,
        usuario=data.usuario,
        observacion=data.observacion,
    )
    db.add(log)

    campo_ts = TIMESTAMP_POR_ESTADO.get(siguiente)
    if campo_ts:
        setattr(pedido, campo_ts, datetime.now())

    pedido.estado = siguiente
    db.commit()
    db.refresh(pedido)
    return pedido


# ── Cancelar pedido ────────────────────────────────────────────
@router.post("/{pedido_id}/cancelar", response_model=schemas.PedidoOut)
def cancelar_pedido(
    pedido_id: int,
    data: schemas.PedidoEstadoUpdate,
    db: Session = Depends(get_db),
):
    pedido = (
        db.query(models.Pedido)
        .options(joinedload(models.Pedido.detalles))
        .filter(models.Pedido.id == pedido_id)
        .first()
    )
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if pedido.estado in ("DEPOSITADO", "ENTREGADO", "CANCELADO"):
        raise HTTPException(status_code=400, detail=f"No se puede cancelar un pedido en estado: {pedido.estado}")

    # Solo descontar stock comprometido
    for detalle in pedido.detalles:
        producto = db.query(models.Producto).filter(models.Producto.id == detalle.producto_id).first()
        if producto:
            producto.stock_comprometido = max(0, (producto.stock_comprometido or 0) - detalle.cantidad)

    log = models.FlujoLog(
        pedido_id=pedido.id,
        estado_anterior=pedido.estado,
        estado_nuevo="CANCELADO",
        usuario=data.usuario,
        observacion=data.observacion,
    )
    db.add(log)

    pedido.estado = "CANCELADO"
    pedido.fecha_cancelado = datetime.now()
    db.commit()
    db.refresh(pedido)
    return pedido


# ── Datos para rótulo ──────────────────────────────────────────
@router.get("/{pedido_id}/rotulo", response_model=schemas.PedidoRotuloOut)
def obtener_rotulo(pedido_id: int, db: Session = Depends(get_db)):
    pedido = (
        db.query(models.Pedido)
        .options(
            joinedload(models.Pedido.detalles).joinedload(models.DetallePedido.producto),
            joinedload(models.Pedido.agencia),
            joinedload(models.Pedido.empresa),
        )
        .filter(models.Pedido.id == pedido_id)
        .first()
    )
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    items = [
        schemas.ItemPedidoOut(
            nombre_producto=d.producto.nombre,
            cantidad=d.cantidad,
            precio_unitario=d.precio_unitario,
            subtotal=d.subtotal,
        )
        for d in pedido.detalles
    ]

    return schemas.PedidoRotuloOut(
        id=pedido.id,
        nombre_cliente=pedido.nombre_cliente,
        dni=pedido.dni,
        telefono=pedido.telefono,
        items=items,
        ciudad_agencia=pedido.agencia.lugar if pedido.agencia else "No especificada",
        direccion_agencia=pedido.agencia.direccion if pedido.agencia else None,
        tipo_destino=pedido.tipo_destino,
        direccion_otra_agencia=pedido.direccion_otra_agencia,
        costo_envio=pedido.costo_envio,
        descuento=pedido.descuento or Decimal("0.00"),
        resta_pagar=pedido.resta_pagar,
        nombre_empresa=pedido.empresa.nombre,
    )


# ── Seguimiento ────────────────────────────────────────────────
@router.get("/{pedido_id}/seguimiento", response_model=schemas.PedidoSeguimientoOut)
def obtener_seguimiento(pedido_id: int, db: Session = Depends(get_db)):
    pedido = (
        db.query(models.Pedido)
        .options(
            joinedload(models.Pedido.detalles).joinedload(models.DetallePedido.producto),
            joinedload(models.Pedido.agencia),
            joinedload(models.Pedido.logs),
        )
        .filter(models.Pedido.id == pedido_id)
        .first()
    )
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    items = [
        schemas.ItemPedidoOut(
            nombre_producto=d.producto.nombre,
            cantidad=d.cantidad,
            precio_unitario=d.precio_unitario,
            subtotal=d.subtotal,
        )
        for d in pedido.detalles
    ]

    etapas = [
        {"estado": "REGISTRADO",     "timestamp": pedido.fecha_registro},
        {"estado": "EMPACADO",       "timestamp": pedido.fecha_empacado},
        {"estado": "ROTULO_IMPRESO", "timestamp": pedido.fecha_rotulo},
        {"estado": "DEPOSITADO",     "timestamp": pedido.fecha_deposito},
        {"estado": "ENTREGADO",      "timestamp": pedido.fecha_entrega},
    ]
    if pedido.estado == "CANCELADO":
        etapas.append({"estado": "CANCELADO", "timestamp": pedido.fecha_cancelado})

    return schemas.PedidoSeguimientoOut(
        id=pedido.id,
        nombre_cliente=pedido.nombre_cliente,
        dni=pedido.dni,
        items=items,
        ciudad_agencia=pedido.agencia.lugar if pedido.agencia else "No especificada",
        resta_pagar=pedido.resta_pagar,
        estado_actual=pedido.estado,
        etapas=etapas,
    )
