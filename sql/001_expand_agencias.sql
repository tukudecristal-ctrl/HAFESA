-- ============================================================
-- MIGRACIÓN: Expansión de tabla de agencias Shalom
-- Proyecto: VERDE (HAFESA)
-- Fecha: 2026-05-29
-- ============================================================

-- Renombrar tabla antigua para referencia histórica
ALTER TABLE agencias_destino RENAME TO agencias_destino_legacy;

-- ============================================================
-- Crear nueva tabla agencias_shalom con estructura completa
-- ============================================================
CREATE TABLE agencias_shalom (
    -- Identificadores
    id SERIAL PRIMARY KEY,
    ter_id VARCHAR(20) UNIQUE NOT NULL,

    -- Ubicación
    lugar VARCHAR(200) NOT NULL,
    lugar_over VARCHAR(200),
    direccion VARCHAR(500) NOT NULL,
    provincia VARCHAR(100) NOT NULL,
    departamento VARCHAR(100) NOT NULL,
    zona VARCHAR(50),
    ter_zona VARCHAR(100),

    -- Geolocalización
    latitud FLOAT,
    longitud FLOAT,

    -- Contacto
    telefono VARCHAR(20),

    -- Horarios
    hora_atencion VARCHAR(100),
    hora_domingo VARCHAR(100),
    hora_entrega VARCHAR(100),
    hora_entrega_domingo VARCHAR(100),

    -- Estado
    estadoAgencia VARCHAR(50),
    ter_estado_agente INTEGER DEFAULT 1,
    ter_habilitado_OS INTEGER DEFAULT 1,
    ter_reparto_habilitado INTEGER DEFAULT 1,
    ter_principal INTEGER DEFAULT 1,

    -- Servicios
    origen INTEGER DEFAULT 1,
    destino INTEGER DEFAULT 1,
    ter_aereo INTEGER DEFAULT 0,
    ter_internacional INTEGER DEFAULT 0,

    -- Administración
    activo BOOLEAN DEFAULT TRUE,
    sincronizado_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- Crear índices para optimizar búsquedas
-- ============================================================
CREATE INDEX idx_agencias_provincia ON agencias_shalom(provincia);
CREATE INDEX idx_agencias_departamento ON agencias_shalom(departamento);
CREATE INDEX idx_agencias_ter_id ON agencias_shalom(ter_id);
CREATE INDEX idx_agencias_activo ON agencias_shalom(activo);
CREATE INDEX idx_agencias_sincronizado ON agencias_shalom(sincronizado_at);

-- ============================================================
-- Actualizar FK en tabla pedidos
-- ============================================================
-- Primero, eliminar la restricción antigua
ALTER TABLE pedidos
DROP CONSTRAINT pedidos_agencia_id_fkey;

-- Luego, crear la nueva restricción
ALTER TABLE pedidos
ADD CONSTRAINT pedidos_agencia_id_fkey
FOREIGN KEY (agencia_id) REFERENCES agencias_shalom(id);

-- ============================================================
-- Fin de migración
-- ============================================================
