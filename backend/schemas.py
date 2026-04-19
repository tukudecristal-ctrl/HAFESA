from pydantic import BaseModel, field_validator, model_validator
from typing import Optional, Literal
from datetime import datetime, date
from decimal import Decimal
import re


# ── Auth ──────────────────────────────────────────────────────
class LoginInput(BaseModel):
    dni: str
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: str
    nombre: str
    vendedor_id: Optional[int]

class UsuarioCreate(BaseModel):
    dni: str
    password: str
    nombre: str
    rol: Literal["administrador", "vendedor", "logistica"]
    vendedor_id: Optional[int] = None

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    rol: Optional[Literal["administrador", "vendedor", "logistica"]] = None
    vendedor_id: Optional[int] = None
    activo: Optional[bool] = None

class UsuarioPasswordReset(BaseModel):
    password: str

class UsuarioOut(BaseModel):
    id: int
    dni: str
    nombre: str
    rol: str
    vendedor_id: Optional[int]
    activo: bool
    created_at: Optional[datetime]

    model_config = {"from_attributes": True}


# ── Empresa ───────────────────────────────────────────────────
class EmpresaCreate(BaseModel):
    codigo: str
    nombre: str
    rubro: Optional[str] = None
    porcentaje_comision: Decimal = Decimal("3.00")

class EmpresaUpdate(BaseModel):
    nombre: Optional[str] = None
    rubro: Optional[str] = None
    porcentaje_comision: Optional[Decimal] = None
    activo: Optional[bool] = None

class EmpresaOut(BaseModel):
    id: int
    codigo: str
    nombre: str
    rubro: Optional[str]
    porcentaje_comision: Decimal
    activo: bool

    model_config = {"from_attributes": True}


# ── Agencia ───────────────────────────────────────────────────
class AgenciaOut(BaseModel):
    id: int
    ciudad: str
    direccion: Optional[str]
    activo: bool

    model_config = {"from_attributes": True}


# ── Proveedor ─────────────────────────────────────────────────
class ProveedorCreate(BaseModel):
    codigo: str
    nombre: str
    contacto: Optional[str] = None
    telefono: Optional[str] = None

class ProveedorUpdate(BaseModel):
    nombre:   Optional[str]  = None
    contacto: Optional[str]  = None
    telefono: Optional[str]  = None
    activo:   Optional[bool] = None

class ProveedorOut(BaseModel):
    id:       int
    codigo:   str
    nombre:   str
    contacto: Optional[str]
    telefono: Optional[str]
    activo:   bool

    model_config = {"from_attributes": True}


# ── Vendedor ──────────────────────────────────────────────────
class VendedorCreate(BaseModel):
    codigo: str
    nombre_completo: str
    empresa_id: int
    telefono: Optional[str] = None

class VendedorUpdate(BaseModel):
    nombre_completo: Optional[str] = None
    empresa_id: Optional[int] = None
    telefono: Optional[str] = None
    activo: Optional[bool] = None

class VendedorOut(BaseModel):
    id: int
    codigo: str
    nombre_completo: str
    empresa_id: int
    telefono: Optional[str]
    activo: bool

    model_config = {"from_attributes": True}


# ── Producto ──────────────────────────────────────────────────
class ProductoCreate(BaseModel):
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    empresa_id: int
    precio_venta: Decimal
    precio_venta_1: Decimal = Decimal("0.00")
    precio_venta_2: Decimal = Decimal("0.00")
    precio_venta_3: Decimal = Decimal("0.00")
    porcentaje_comision: Decimal = Decimal("3.00")
    stock: int = 0

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio_venta: Optional[Decimal] = None
    precio_venta_1: Optional[Decimal] = None
    precio_venta_2: Optional[Decimal] = None
    precio_venta_3: Optional[Decimal] = None
    porcentaje_comision: Optional[Decimal] = None
    activo: Optional[bool] = None
    imagen_url: Optional[str] = None

class ProductoOut(BaseModel):
    id: int
    codigo: str
    nombre: str
    descripcion: Optional[str]
    empresa_id: int
    precio_venta: Decimal
    precio_venta_1: Decimal
    precio_venta_2: Decimal
    precio_venta_3: Decimal
    porcentaje_comision: Decimal
    stock: int
    stock_comprometido: int
    imagen_url: Optional[str]
    activo: bool

    model_config = {"from_attributes": True}


def seleccionar_precio(producto, cantidad: int) -> Decimal:
    """Determina el precio unitario según la cantidad solicitada."""
    if cantidad <= 2:
        return Decimal(str(producto.precio_venta))
    elif cantidad <= 6:
        return Decimal(str(producto.precio_venta_1))
    elif cantidad <= 12:
        return Decimal(str(producto.precio_venta_2))
    else:
        return Decimal(str(producto.precio_venta_3))


# ── Pedido ────────────────────────────────────────────────────
ESTADOS_VALIDOS = ["REGISTRADO", "EMPACADO", "ROTULO_IMPRESO", "DEPOSITADO", "ENTREGADO", "CANCELADO"]

SIGUIENTE_ESTADO = {
    "REGISTRADO": "EMPACADO",
    "EMPACADO": "ROTULO_IMPRESO",
    "ROTULO_IMPRESO": "DEPOSITADO",
    "DEPOSITADO": "ENTREGADO",
}


class DetallePedidoCreate(BaseModel):
    producto_id: int
    cantidad: int

    @field_validator("cantidad")
    @classmethod
    def validar_cantidad(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        return v


class DetallePedidoOut(BaseModel):
    id: int
    producto_id: int
    cantidad: int
    precio_unitario: Decimal
    subtotal: Optional[Decimal]

    model_config = {"from_attributes": True}


class PedidoCreate(BaseModel):
    empresa_id: int
    vendedor_id: int
    nombre_cliente: str
    dni: str
    telefono: str
    detalles: list[DetallePedidoCreate]
    agencia_id: int
    detalle_observacion: Optional[str] = None
    separacion: Decimal = Decimal("0.00")
    costo_envio: Decimal = Decimal("0.00")
    descuento: Decimal = Decimal("0.00")

    @field_validator("dni")
    @classmethod
    def validar_dni(cls, v: str) -> str:
        if not re.fullmatch(r"\d{8,10}", v):
            raise ValueError("El DNI debe tener entre 8 y 10 dígitos numéricos")
        return v

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, v: str) -> str:
        if not re.fullmatch(r"9\d{8}", v):
            raise ValueError("El teléfono debe tener 9 dígitos y empezar con 9")
        return v

    @field_validator("detalles")
    @classmethod
    def validar_detalles(cls, v: list) -> list:
        if not v:
            raise ValueError("Debe incluir al menos un producto")
        return v

    @field_validator("separacion", "costo_envio", "descuento")
    @classmethod
    def validar_montos(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("El monto no puede ser negativo")
        return v.quantize(Decimal("0.01"))


class PedidoEstadoUpdate(BaseModel):
    usuario: Optional[str] = "sistema"
    observacion: Optional[str] = None


class PedidoOut(BaseModel):
    id: int
    empresa_id: int
    vendedor_id: int
    nombre_cliente: str
    dni: str
    telefono: str
    producto_id: Optional[int]      # legacy
    cantidad: Optional[int]         # legacy
    agencia_id: int
    detalle_observacion: Optional[str]
    separacion: Decimal
    costo_envio: Decimal
    descuento: Decimal
    precio_total: Optional[Decimal]
    resta_pagar: Optional[Decimal]
    estado: str
    fecha_registro: Optional[datetime]
    fecha_empacado: Optional[datetime]
    fecha_rotulo: Optional[datetime]
    fecha_deposito: Optional[datetime]
    fecha_entrega: Optional[datetime]
    fecha_cancelado: Optional[datetime]
    fecha_pago_comision: Optional[datetime]
    detalles: list[DetallePedidoOut] = []

    model_config = {"from_attributes": True}


class PedidoDetalleOut(PedidoOut):
    empresa: EmpresaOut
    vendedor: VendedorOut
    producto: Optional[ProductoOut]  # legacy
    agencia: AgenciaOut

    model_config = {"from_attributes": True}


class ItemPedidoOut(BaseModel):
    nombre_producto: str
    cantidad: int
    precio_unitario: Decimal
    subtotal: Optional[Decimal]


class PedidoRotuloOut(BaseModel):
    id: int
    nombre_cliente: str
    dni: str
    telefono: str
    items: list[ItemPedidoOut]
    ciudad_agencia: str
    costo_envio: Decimal
    descuento: Decimal
    resta_pagar: Decimal
    nombre_empresa: str

    model_config = {"from_attributes": True}


# ── Seguimiento ───────────────────────────────────────────────
class EtapaSeguimiento(BaseModel):
    estado: str
    timestamp: Optional[datetime]


class PedidoSeguimientoOut(BaseModel):
    id: int
    nombre_cliente: str
    dni: str
    items: list[ItemPedidoOut]
    ciudad_agencia: str
    resta_pagar: Optional[Decimal]
    estado_actual: str
    etapas: list[EtapaSeguimiento]


# ── Comisiones ───────────────────────────────────────────────
class ComisionVendedorOut(BaseModel):
    vendedor_id: int
    nombre_completo: str
    empresa_id: int
    nombre_empresa: str
    porcentaje_comision: Decimal
    pedidos_pendientes: int
    ventas_netas: Decimal
    comision_pendiente: Decimal


class ComisionPedidoOut(BaseModel):
    pedido_id: int
    nombre_cliente: str
    fecha_registro: Optional[datetime]
    fecha_entrega: Optional[datetime]
    precio_total: Decimal
    descuento: Decimal
    monto_neto: Decimal
    comision: Decimal
    porcentaje_comision: Decimal


class PagarComisionesInput(BaseModel):
    pedido_ids: list[int]
    fecha_pago: date


# ── Compra ────────────────────────────────────────────────────
class DetalleCompraCreate(BaseModel):
    producto_id: int
    cantidad: int
    costo_unitario: Decimal

    @field_validator("cantidad")
    @classmethod
    def validar_cantidad(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        return v

    @field_validator("costo_unitario")
    @classmethod
    def validar_costo(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("El costo unitario debe ser mayor a 0")
        return v.quantize(Decimal("0.01"))


class DetalleCompraOut(BaseModel):
    id: int
    producto_id: int
    cantidad: int
    costo_unitario: Decimal
    subtotal: Optional[Decimal]

    model_config = {"from_attributes": True}


class CompraCreate(BaseModel):
    empresa_id:   int
    proveedor_id: Optional[int] = None
    fecha_compra: date
    detalles: list[DetalleCompraCreate]
    costo_transporte: Decimal = Decimal("0.00")
    costo_impuesto: Decimal = Decimal("0.00")
    otros_costos: Decimal = Decimal("0.00")
    observaciones: Optional[str] = None


class CompraOut(BaseModel):
    id:           int
    empresa_id:   int
    proveedor_id: Optional[int]
    fecha_compra: date
    costo_transporte: Decimal
    costo_impuesto: Decimal
    otros_costos: Decimal
    total_calculado: Optional[Decimal]
    observaciones: Optional[str]
    created_at: Optional[datetime]
    detalles: list[DetalleCompraOut]

    model_config = {"from_attributes": True}
