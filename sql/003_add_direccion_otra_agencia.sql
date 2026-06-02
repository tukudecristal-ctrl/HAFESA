-- ============================================================
-- MIGRACIÓN: Agregar soporte para destinos no-Shalom
-- Proyecto: VERDE (HAFESA)
-- Fecha: 2026-06-02
-- ============================================================

-- Agregar columnas a tabla pedidos para soportar dos tipos de destino:
-- 1. tipo_destino: 'shalom' (usa agencia_id) o 'otro' (usa direccion_otra_agencia)
-- 2. direccion_otra_agencia: dirección manual cuando tipo_destino='otro'

ALTER TABLE pedidos
ADD COLUMN tipo_destino VARCHAR(20) DEFAULT 'shalom';

ALTER TABLE pedidos
ADD COLUMN direccion_otra_agencia VARCHAR(500);

-- Crear índice en tipo_destino para queries rápidas
CREATE INDEX idx_pedidos_tipo_destino ON pedidos(tipo_destino);

-- ============================================================
-- Fin de migración
-- ============================================================
