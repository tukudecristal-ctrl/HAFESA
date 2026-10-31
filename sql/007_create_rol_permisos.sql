-- ============================================================
-- MIGRACIÓN: Permisos por pantalla para cada rol
-- Proyecto: VERDE (HAFESA)
-- Fecha: 2026-10-31
-- ============================================================
-- Cada rol (usuarios.rol) tiene una lista de pantallas; todos los usuarios del
-- rol la heredan. Las claves son las de backend/catalogo_pantallas.py.
-- Se siembra lo que cada rol ya podía abrir antes de esta migración, así que
-- aplicarla no cambia el acceso de nadie.

CREATE TABLE rol_permisos (
    rol VARCHAR(20) NOT NULL,
    pantalla VARCHAR(40) NOT NULL,
    PRIMARY KEY (rol, pantalla)
);

INSERT INTO rol_permisos (rol, pantalla) VALUES
    -- administrador: todas las pantallas. Cubre a todos los usuarios con ese rol
    -- (en producción: 10313289 David y 73894502 Ricardo Vidal).
    ('administrador', 'pedidos'),
    ('administrador', 'nuevo_pedido'),
    ('administrador', 'mis_ventas'),
    ('administrador', 'compras'),
    ('administrador', 'productos'),
    ('administrador', 'comisiones'),
    ('administrador', 'reporte_ventas'),
    ('administrador', 'estado_financiero'),
    ('administrador', 'publicidad'),
    ('administrador', 'proveedores'),
    ('administrador', 'empresas'),
    ('administrador', 'vendedores'),
    -- logistica
    ('logistica', 'pedidos'),
    ('logistica', 'nuevo_pedido'),
    ('logistica', 'compras'),
    ('logistica', 'productos'),
    ('logistica', 'comisiones'),
    -- vendedor
    ('vendedor', 'nuevo_pedido'),
    ('vendedor', 'mis_ventas')
ON CONFLICT (rol, pantalla) DO NOTHING;

-- Aviso (no detiene la migración) si el usuario 10313289 no es administrador activo
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM usuarios WHERE dni = '10313289' AND rol = 'administrador' AND activo
    ) THEN
        RAISE WARNING 'El usuario 10313289 no existe o no es administrador activo: no tendrá acceso total.';
    END IF;
END $$;

-- ============================================================
-- Fin de migración
-- ============================================================
