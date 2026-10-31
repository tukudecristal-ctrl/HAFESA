-- ============================================================
-- MIGRACIÓN: Eliminar el estado ROTULO_IMPRESO del flujo de pedidos
-- Proyecto: VERDE (HAFESA)
-- Fecha: 2026-10-31
-- ============================================================
-- Flujo nuevo: REGISTRADO -> EMPACADO -> DEPOSITADO -> ENTREGADO (y CANCELADO).
-- Los pedidos que estaban en ROTULO_IMPRESO pasan a EMPACADO (quedan listos para
-- depositarse). Se deja registro en flujo_log. No se borra nada del historial:
-- pedidos.fecha_rotulo y los movimientos antiguos de flujo_log se conservan.
-- Se puede volver a ejecutar sin efecto si ya no quedan pedidos en ese estado.

INSERT INTO flujo_log (pedido_id, estado_anterior, estado_nuevo, usuario, observacion)
SELECT id, 'ROTULO_IMPRESO', 'EMPACADO', 'sistema',
       'Migración 008: el estado Rótulo impreso se eliminó del flujo'
FROM pedidos
WHERE estado = 'ROTULO_IMPRESO';

UPDATE pedidos
SET estado = 'EMPACADO'
WHERE estado = 'ROTULO_IMPRESO';

-- ============================================================
-- Fin de migración
-- ============================================================
