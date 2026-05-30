-- Crear tabla CLIENTES
CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    dni VARCHAR(8) UNIQUE NOT NULL,
    nombres VARCHAR(100) NOT NULL,
    apellido_paterno VARCHAR(100) NOT NULL,
    apellido_materno VARCHAR(100),
    nombre_completo VARCHAR(250) NOT NULL,
    fuente VARCHAR(20) DEFAULT 'manual',  -- manual | decolecta
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Crear índices
CREATE INDEX idx_clientes_dni ON clientes(dni);
CREATE INDEX idx_clientes_activo ON clientes(activo);
CREATE INDEX idx_clientes_fuente ON clientes(fuente);
