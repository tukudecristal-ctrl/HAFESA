# REQ 2 — Pedidos Multi-producto

**Estado:** ✅ Completado  
**Fecha:** 2026-04-17

---

## Requerimiento original

> Convertir el módulo de pedidos de un solo producto a multi-producto (similar a compras). Mostrar los precios de volumen al seleccionar el producto. Aplicar precio automático según cantidad. Agregar campo de descuento sobre el total del pedido (no por producto). Registrar la cantidad como `stock_comprometido`.

---

## Decisiones tomadas

- La tabla `pedidos` conserva los campos legacy `producto_id` y `cantidad` (nullable) para no romper registros históricos.
- El descuento es **sobre el total del pedido**, no por producto — se ubica en `pedidos.descuento`.
- `resta_pagar = precio_total - separacion - descuento`.
- El precio se selecciona en backend al crear el pedido (no solo en frontend) para garantizar integridad.

---

## Implementación

### Base de datos

```sql
-- Nueva tabla de detalle
CREATE TABLE detalle_pedido (
  id              SERIAL PRIMARY KEY,
  pedido_id       INT NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE,
  producto_id     INT NOT NULL REFERENCES productos(id),
  cantidad        INT NOT NULL CHECK (cantidad > 0),
  precio_unitario NUMERIC(10,2) NOT NULL,
  subtotal        NUMERIC(10,2) GENERATED ALWAYS AS (cantidad * precio_unitario) STORED
);

-- Ajustes en pedidos
ALTER TABLE pedidos
  ADD COLUMN descuento NUMERIC(10,2) DEFAULT 0,
  ALTER COLUMN cantidad DROP NOT NULL;  -- legacy nullable
```

### Backend

**`models.py`** — nueva clase `DetallePedido` con `subtotal` GENERATED.  
**`models.py`** — `Pedido`: agregado `descuento`, `fecha_cancelado`, relación `detalles`.

**`schemas.py`:**
- `DetallePedidoCreate`: `{producto_id, cantidad}`
- `DetallePedidoOut`: `{id, producto_id, cantidad, precio_unitario, subtotal}`
- `PedidoCreate`: reemplaza `producto_id/cantidad` por `detalles: list[DetallePedidoCreate]` + `descuento`
- `PedidoOut`: incluye `detalles: list[DetallePedidoOut]`
- Validación de DNI ampliada a 8–10 dígitos (`\d{8,10}`)

**`routers/pedidos.py`** — `crear_pedido`:
1. Para cada detalle: valida stock disponible, aplica `seleccionar_precio()`, crea `DetallePedido`.
2. Incrementa `producto.stock_comprometido += cantidad`.
3. Calcula `precio_total = Σ subtotales + costo_envio`.
4. Calcula `resta_pagar = precio_total - separacion - descuento`.

### Frontend — `formulario_pedido.html`

- Tabla dinámica de productos: select producto → muestra P0/P1/P2/P3 resaltando el activo → input cantidad → precio auto (read-only) → subtotal (read-only) → botón eliminar fila.
- Descripción del producto visible al seleccionarlo.
- Resumen al pie: subtotal items + costo envío − separación − descuento = **Resta a pagar**.
- Función JS `seleccionarPrecio(producto, cantidad)` espeja la lógica del backend.
- Envía `detalles: [{producto_id, cantidad}]` al API.
