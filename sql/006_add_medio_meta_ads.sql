-- ============================================================
-- MIGRACIÓN: Agregar "Meta Ads" como medio válido en publicidad
-- Proyecto: VERDE (HAFESA)
-- Fecha: 2026-10-30
-- ============================================================

ALTER TABLE publicidad DROP CONSTRAINT publicidad_medio_check;

ALTER TABLE publicidad ADD CONSTRAINT publicidad_medio_check
    CHECK (medio IN ('facebook', 'instagram', 'youtube', 'whatsapp', 'meta_ads'));

-- ============================================================
-- Fin de migración
-- ============================================================
