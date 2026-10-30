-- ============================================================
-- MIGRACIÓN: Crear tablas de Publicidad (gasto + prorateo)
-- Proyecto: VERDE (HAFESA)
-- Fecha: 2026-10-29
-- ============================================================

CREATE TABLE publicidad (
    id SERIAL PRIMARY KEY,
    medio VARCHAR(20) NOT NULL CHECK (medio IN ('facebook', 'instagram', 'youtube', 'whatsapp')),
    fecha_inicio DATE NOT NULL,
    fecha_final DATE NOT NULL CHECK (fecha_final >= fecha_inicio),
    moneda VARCHAR(3) NOT NULL CHECK (moneda IN ('PEN', 'USD')),
    monto NUMERIC(10, 2) NOT NULL CHECK (monto > 0),
    tipo_cambio NUMERIC(6, 3) NOT NULL DEFAULT 1.000,
    monto_soles NUMERIC(10, 2) NOT NULL,
    observaciones TEXT,
    usuario_id INTEGER REFERENCES usuarios(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE publicidad_detalle (
    id SERIAL PRIMARY KEY,
    publicidad_id INTEGER NOT NULL REFERENCES publicidad(id) ON DELETE CASCADE,
    vendedor_id INTEGER NOT NULL REFERENCES vendedores(id),
    empresa_id INTEGER REFERENCES empresas(id),
    fecha DATE NOT NULL,
    monto_prorateado NUMERIC(10, 2) NOT NULL
);

CREATE INDEX idx_publicidad_fecha ON publicidad(fecha_inicio, fecha_final);
CREATE INDEX idx_publicidad_medio ON publicidad(medio);
CREATE INDEX idx_publicidad_detalle_publicidad ON publicidad_detalle(publicidad_id);
CREATE INDEX idx_publicidad_detalle_vendedor ON publicidad_detalle(vendedor_id);
CREATE INDEX idx_publicidad_detalle_fecha ON publicidad_detalle(fecha);

-- ============================================================
-- Fin de migración
-- ============================================================
