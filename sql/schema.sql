-- ============================================================
-- Sistema de Ventas Multiempresa — Schema PostgreSQL
-- ============================================================

-- 1. EMPRESAS
-- ============================================================
CREATE TABLE empresas (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(10) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    rubro VARCHAR(50),           -- 'LUMINARIAS' | 'SONIDO'
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO empresas (codigo, nombre, rubro) VALUES
('EMP001', 'LumiSolar SAC', 'LUMINARIAS'),
('EMP002', 'AudioPro SAC', 'SONIDO');


-- 2. AGENCIAS DE DESTINO (Shalom)
-- ============================================================
CREATE TABLE agencias_destino (
    id SERIAL PRIMARY KEY,
    ciudad VARCHAR(100) NOT NULL,
    direccion VARCHAR(200),
    activo BOOLEAN DEFAULT TRUE
);

INSERT INTO agencias_destino (ciudad, direccion) VALUES
('Lima - Central', 'Av. México 333, La Victoria'),
('Arequipa', 'Av. Goyeneche 123, Arequipa'),
('Cusco', 'Av. El Sol 456, Cusco'),
('Trujillo', 'Jr. Gamarra 200, Trujillo'),
('Chiclayo', 'Av. Balta 789, Chiclayo'),
('Piura', 'Jr. Loreto 111, Piura'),
('Iquitos', 'Av. Quiñones 321, Iquitos'),
('Huancayo', 'Av. Ferrocarril 555, Huancayo'),
('Pucallpa', 'Jr. Ucayali 88, Pucallpa'),
('Tacna', 'Av. Bolognesi 210, Tacna'),
('Juliaca', 'Jr. Moquegua 45, Juliaca'),
('Ayacucho', 'Jr. Lima 77, Ayacucho'),
('Puno', 'Jr. Deustua 90, Puno'),
('Cajamarca', 'Av. Hoyos Rubio 60, Cajamarca'),
('Chimbote', 'Av. José Pardo 400, Chimbote'),
('Sullana', 'Jr. Tarapacá 30, Sullana'),
('Tumbes', 'Av. Tumbes Norte 150, Tumbes'),
('Moyobamba', 'Jr. San Martín 20, Moyobamba'),
('Tarapoto', 'Jr. Ramírez Hurtado 55, Tarapoto'),
('Huaraz', 'Jr. Luzuriaga 180, Huaraz');


-- 3. VENDEDORES
-- ============================================================
CREATE TABLE vendedores (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nombre_completo VARCHAR(150) NOT NULL,
    empresa_id INTEGER REFERENCES empresas(id),
    telefono VARCHAR(9),
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Vendedores de prueba — LumiSolar
INSERT INTO vendedores (codigo, nombre_completo, empresa_id, telefono) VALUES
('LUMI-V001', 'Carlos Mamani Torres', 1, '987654321'),
('LUMI-V002', 'Rosa Quispe Huanca', 1, '976543210'),
('LUMI-V003', 'Juan Apaza Lima', 1, '965432109');

-- Vendedores de prueba — AudioPro
INSERT INTO vendedores (codigo, nombre_completo, empresa_id, telefono) VALUES
('AUDIO-V001', 'Pedro Vargas Soto', 2, '954321098'),
('AUDIO-V002', 'María Condori Ramos', 2, '943210987'),
('AUDIO-V003', 'Luis Huanca Flores', 2, '932109876');


-- 4. PRODUCTOS
-- ============================================================
CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(30) UNIQUE NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    empresa_id INTEGER REFERENCES empresas(id),
    precio_venta  NUMERIC(10,2) NOT NULL,          -- precio_venta_0: qty 1-2
    precio_venta_1 NUMERIC(10,2) DEFAULT 0,        -- qty 3-6
    precio_venta_2 NUMERIC(10,2) DEFAULT 0,        -- qty 7-12
    precio_venta_3 NUMERIC(10,2) DEFAULT 0,        -- qty >= 13
    porcentaje_comision NUMERIC(5,2) DEFAULT 3.00,
    stock INTEGER DEFAULT 0,
    stock_comprometido INTEGER DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Productos de prueba — LumiSolar (Luminarias)
INSERT INTO productos (codigo, nombre, descripcion, empresa_id, precio_venta, stock) VALUES
('LUMI-FAR-30W', 'Farola Solar 30W', 'Farola solar LED 30W, panel monocristalino, batería LiFePO4', 1, 450.00, 50),
('LUMI-FAR-60W', 'Farola Solar 60W', 'Farola solar LED 60W, panel monocristalino, batería LiFePO4', 1, 750.00, 30),
('LUMI-LAMP-10W', 'Lámpara Solar 10W', 'Lámpara solar portátil 10W, carga USB, 8h autonomía', 1, 120.00, 100),
('LUMI-KIT-DOM', 'Kit Solar Doméstico', 'Kit panel 100W + batería 12V 50Ah + controlador', 1, 980.00, 20),
('LUMI-PANEL-200W', 'Panel Solar 200W', 'Panel policristalino 200W, 24V, garantía 25 años', 1, 320.00, 40);

-- Productos de prueba — AudioPro (Sonido)
INSERT INTO productos (codigo, nombre, descripcion, empresa_id, precio_venta, stock) VALUES
('AUDIO-PARL-8P', 'Parlante 8" Portátil', 'Parlante Bluetooth 8 pulgadas, 80W RMS, batería 6h', 2, 280.00, 60),
('AUDIO-PARL-15P', 'Parlante 15" Torre', 'Parlante torre 15 pulgadas, 300W RMS, karaoke, TWS', 2, 650.00, 25),
('AUDIO-VG-2MP', 'Videograbadora 2MP', 'Kit DVR 4 cámaras 2MP, disco 1TB, visión nocturna', 2, 890.00, 15),
('AUDIO-VG-4MP', 'Videograbadora 4MP', 'Kit NVR 8 cámaras 4MP IP, disco 2TB, acceso remoto', 2, 1450.00, 10),
('AUDIO-MIC-UHF', 'Micrófono UHF Inalámbrico', 'Sistema UHF doble micrófono, 80m alcance, anti-interferencia', 2, 180.00, 45);


-- 5. COMPRAS (registro de ingresos de mercadería)
-- ============================================================
CREATE TABLE compras (
    id SERIAL PRIMARY KEY,
    empresa_id INTEGER REFERENCES empresas(id),
    proveedor VARCHAR(150),
    fecha_compra DATE NOT NULL,
    costo_transporte NUMERIC(10,2) DEFAULT 0,
    costo_impuesto NUMERIC(10,2) DEFAULT 0,
    otros_costos NUMERIC(10,2) DEFAULT 0,
    total_calculado NUMERIC(10,2),   -- calculado automáticamente en el backend
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);


-- 6. DETALLE COMPRA
-- ============================================================
CREATE TABLE detalle_compra (
    id SERIAL PRIMARY KEY,
    compra_id INTEGER REFERENCES compras(id) ON DELETE CASCADE,
    producto_id INTEGER REFERENCES productos(id),
    cantidad INTEGER NOT NULL,
    costo_unitario NUMERIC(10,2) NOT NULL,
    subtotal NUMERIC(10,2) GENERATED ALWAYS AS (cantidad * costo_unitario) STORED
);


-- 7. PEDIDOS
-- ============================================================
CREATE TABLE pedidos (
    id SERIAL PRIMARY KEY,
    empresa_id INTEGER REFERENCES empresas(id),
    vendedor_id INTEGER REFERENCES vendedores(id),
    -- Datos del cliente
    nombre_cliente VARCHAR(200) NOT NULL,
    dni VARCHAR(10) NOT NULL CHECK (LENGTH(dni) >= 8 AND dni ~ '^\d{8,10}$'),
    telefono VARCHAR(9) NOT NULL CHECK (telefono ~ '^9\d{8}$'),
    -- Producto y destino (campos legacy — ver detalle_pedido para multi-producto)
    producto_id INTEGER REFERENCES productos(id),
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    agencia_id INTEGER REFERENCES agencias_destino(id),
    detalle_observacion TEXT,
    -- Pagos
    separacion NUMERIC(10,2) DEFAULT 0,
    costo_envio NUMERIC(10,2) DEFAULT 0,
    descuento NUMERIC(10,2) DEFAULT 0, -- descuento en monto sobre el total del pedido
    precio_total NUMERIC(10,2),       -- calculado: sum(detalle_pedido.subtotal) + costo_envio
    resta_pagar NUMERIC(10,2),        -- calculado: precio_total - descuento - separacion
    -- Estado del flujo
    estado VARCHAR(30) DEFAULT 'REGISTRADO',
    -- REGISTRADO | EMPACADO | ROTULO_IMPRESO | DEPOSITADO | ENTREGADO | CANCELADO
    fecha_registro TIMESTAMP DEFAULT NOW(),
    fecha_empacado TIMESTAMP,
    fecha_rotulo TIMESTAMP,
    fecha_deposito TIMESTAMP,
    fecha_entrega TIMESTAMP,
    fecha_cancelado TIMESTAMP
);


-- 8. DETALLE PEDIDO (multi-producto por pedido)
-- ============================================================
CREATE TABLE detalle_pedido (
    id              SERIAL PRIMARY KEY,
    pedido_id       INTEGER NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE,
    producto_id     INTEGER NOT NULL REFERENCES productos(id),
    cantidad        INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario NUMERIC(10,2) NOT NULL,   -- precio aplicado al momento del pedido
    subtotal        NUMERIC(10,2) GENERATED ALWAYS AS (cantidad * precio_unitario) STORED
);


-- 9. FLUJO LOG (auditoría de cambios de estado)
-- ============================================================
CREATE TABLE flujo_log (
    id SERIAL PRIMARY KEY,
    pedido_id INTEGER REFERENCES pedidos(id),
    estado_anterior VARCHAR(30),
    estado_nuevo VARCHAR(30),
    usuario VARCHAR(100),
    observacion TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);


-- ============================================================
-- ÍNDICES para performance
-- ============================================================
CREATE INDEX idx_pedidos_estado ON pedidos(estado);
CREATE INDEX idx_pedidos_empresa ON pedidos(empresa_id);
CREATE INDEX idx_pedidos_vendedor ON pedidos(vendedor_id);
CREATE INDEX idx_pedidos_fecha_registro ON pedidos(fecha_registro);
CREATE INDEX idx_flujo_log_pedido ON flujo_log(pedido_id);
CREATE INDEX idx_detalle_compra_compra ON detalle_compra(compra_id);
CREATE INDEX idx_productos_empresa ON productos(empresa_id);
CREATE INDEX idx_vendedores_empresa ON vendedores(empresa_id);
