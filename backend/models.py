from sqlalchemy import (
    Column, Integer, String, Boolean, Numeric, Text, Float,
    DateTime, Date, ForeignKey, CheckConstraint, Computed
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Empresa(Base):
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True)
    codigo = Column(String(10), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    rubro = Column(String(50))
    porcentaje_comision = Column(Numeric(5, 2), default=3.00)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    vendedores = relationship("Vendedor", back_populates="empresa")
    productos = relationship("Producto", back_populates="empresa")


class AgenciaDestino(Base):
    __tablename__ = "agencias_destino"

    id = Column(Integer, primary_key=True)
    ciudad = Column(String(100), nullable=False)
    direccion = Column(String(200))
    activo = Column(Boolean, default=True)


class AgenciaShalom(Base):
    __tablename__ = "agencias_shalom"

    # Identificadores
    id = Column(Integer, primary_key=True)
    ter_id = Column(String(20), unique=True, nullable=False)

    # Ubicación
    lugar = Column(String(200), nullable=False)
    lugar_over = Column(String(200))
    direccion = Column(String(500), nullable=False)
    provincia = Column(String(100), nullable=False)
    departamento = Column(String(100), nullable=False)
    zona = Column(String(50))
    ter_zona = Column(String(100))

    # Geolocalización
    latitud = Column(Float)
    longitud = Column(Float)

    # Contacto
    telefono = Column(String(20))

    # Horarios
    hora_atencion = Column(String(100))
    hora_domingo = Column(String(100))
    hora_entrega = Column(String(100))
    hora_entrega_domingo = Column(String(100))

    # Estado
    estado_agencia = Column(String(50))
    ter_estado_agente = Column(Integer, default=1)
    ter_habilitado_os = Column(Integer, default=1)
    ter_reparto_habilitado = Column(Integer, default=1)
    ter_principal = Column(Integer, default=1)

    # Servicios
    origen = Column(Integer, default=1)
    destino = Column(Integer, default=1)
    ter_aereo = Column(Integer, default=0)
    ter_internacional = Column(Integer, default=0)

    # Administración
    activo = Column(Boolean, default=True)
    sincronizado_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relación con Pedidos
    pedidos = relationship("Pedido", back_populates="agencia")


class Vendedor(Base):
    __tablename__ = "vendedores"

    id = Column(Integer, primary_key=True)
    codigo = Column(String(20), unique=True, nullable=False)
    nombre_completo = Column(String(150), nullable=False)
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    telefono = Column(String(9))
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    empresa = relationship("Empresa", back_populates="vendedores")


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True)
    codigo = Column(String(30), unique=True, nullable=False)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text)
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    precio_venta = Column(Numeric(10, 2), nullable=False)   # precio_venta_0: qty 1-2
    precio_venta_1 = Column(Numeric(10, 2), default=0)      # qty 3-6
    precio_venta_2 = Column(Numeric(10, 2), default=0)      # qty 7-12
    precio_venta_3 = Column(Numeric(10, 2), default=0)      # qty >= 13
    porcentaje_comision = Column(Numeric(5, 2), default=3.00)
    stock = Column(Integer, default=0)
    stock_comprometido = Column(Integer, default=0)
    imagen_url = Column(String(255))
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    empresa = relationship("Empresa", back_populates="productos")


class Proveedor(Base):
    __tablename__ = "proveedores"

    id = Column(Integer, primary_key=True)
    codigo = Column(String(20), unique=True, nullable=False)
    nombre = Column(String(150), nullable=False)
    contacto = Column(String(100))
    telefono = Column(String(20))
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True)
    dni = Column(String(8), unique=True, nullable=False)
    nombres = Column(String(100), nullable=False)
    apellido_paterno = Column(String(100), nullable=False)
    apellido_materno = Column(String(100))
    nombre_completo = Column(String(250), nullable=False)
    fuente = Column(String(20), default="manual")  # manual | decolecta
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Compra(Base):
    __tablename__ = "compras"

    id = Column(Integer, primary_key=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"))
    proveedor = Column(String(150))  # campo legado, se mantiene por compatibilidad
    fecha_compra = Column(Date, nullable=False)
    costo_transporte = Column(Numeric(10, 2), default=0)
    costo_impuesto = Column(Numeric(10, 2), default=0)
    otros_costos = Column(Numeric(10, 2), default=0)
    total_calculado = Column(Numeric(10, 2))
    observaciones = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    empresa   = relationship("Empresa")
    proveedor_rel = relationship("Proveedor")
    detalles  = relationship("DetalleCompra", back_populates="compra", cascade="all, delete-orphan")


class DetalleCompra(Base):
    __tablename__ = "detalle_compra"

    id = Column(Integer, primary_key=True)
    compra_id = Column(Integer, ForeignKey("compras.id", ondelete="CASCADE"))
    producto_id = Column(Integer, ForeignKey("productos.id"))
    cantidad = Column(Integer, nullable=False)
    costo_unitario = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), Computed("cantidad * costo_unitario", persisted=True))

    compra = relationship("Compra", back_populates="detalles")
    producto = relationship("Producto")


class DetallePedido(Base):
    __tablename__ = "detalle_pedido"

    id = Column(Integer, primary_key=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id", ondelete="CASCADE"))
    producto_id = Column(Integer, ForeignKey("productos.id"))
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), Computed("cantidad * precio_unitario", persisted=True))

    pedido = relationship("Pedido", back_populates="detalles")
    producto = relationship("Producto")


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    vendedor_id = Column(Integer, ForeignKey("vendedores.id"))
    nombre_cliente = Column(String(200), nullable=False)
    dni = Column(String(10), nullable=False)
    telefono = Column(String(9), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"))  # legacy
    cantidad = Column(Integer)                                  # legacy
    agencia_id = Column(Integer, ForeignKey("agencias_shalom.id"))
    detalle_observacion = Column(Text)
    separacion = Column(Numeric(10, 2), default=0)
    costo_envio = Column(Numeric(10, 2), default=0)
    descuento = Column(Numeric(10, 2), default=0)
    precio_total = Column(Numeric(10, 2))
    resta_pagar = Column(Numeric(10, 2))
    estado = Column(String(30), default="REGISTRADO")
    fecha_registro = Column(DateTime, server_default=func.now())
    fecha_empacado = Column(DateTime)
    fecha_rotulo = Column(DateTime)
    fecha_deposito = Column(DateTime)
    fecha_entrega = Column(DateTime)
    fecha_cancelado = Column(DateTime)
    fecha_pago_comision = Column(DateTime)
    tipo_destino = Column(String(20), default='shalom')
    direccion_otra_agencia = Column(String(500), nullable=True)

    empresa = relationship("Empresa")
    vendedor = relationship("Vendedor")
    producto = relationship("Producto")  # legacy
    agencia = relationship("AgenciaShalom", back_populates="pedidos")
    logs = relationship("FlujoLog", back_populates="pedido")
    detalles = relationship("DetallePedido", back_populates="pedido", cascade="all, delete-orphan")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    dni = Column(String(8), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nombre = Column(String(150), nullable=False)
    rol = Column(String(20), nullable=False)   # administrador | vendedor | logistica
    vendedor_id = Column(Integer, ForeignKey("vendedores.id"), nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    vendedor = relationship("Vendedor")


class FlujoLog(Base):
    __tablename__ = "flujo_log"

    id = Column(Integer, primary_key=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"))
    estado_anterior = Column(String(30))
    estado_nuevo = Column(String(30))
    usuario = Column(String(100))
    observacion = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    pedido = relationship("Pedido", back_populates="logs")
