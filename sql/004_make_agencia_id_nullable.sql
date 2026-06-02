-- ============================================================
-- MIGRACIÓN: Hacer agencia_id nullable en pedidos
-- Proyecto: VERDE (HAFESA)
-- Fecha: 2026-06-02
-- ============================================================

-- Permitir valores NULL en agencia_id para soportar destinos no-Shalom
ALTER TABLE pedidos
ALTER COLUMN agencia_id DROP NOT NULL;

-- ============================================================
-- Fin de migración
-- ============================================================
