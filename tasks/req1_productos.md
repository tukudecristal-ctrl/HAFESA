# REQ 1 — Nuevos campos en tabla Productos

**Estado:** ✅ Completado  
**Fecha:** 2026-04-17

---

## Requerimiento original

> Agregar 3 precios de venta a la tabla de productos para usarlos según la cantidad solicitada por el cliente en un mismo pedido. Agregar campo para porcentaje de comisión (default 3%). Agregar campo `stock_comprometido` que se incrementa al registrar el pedido y disminuye cuando el pedido pasa a DEPOSITADO (junto con el stock real).

---

## Decisiones tomadas

- El campo existente `precio_venta` actúa como `precio_venta_0` (qty 1–2). No se renombró para mantener compatibilidad con registros históricos.
- `stock_comprometido` **nunca es negativo** — es una reserva activa, no un saldo contable.
- `porcentaje_comision` en productos existe como campo de referencia; la comisión efectiva de pago a vendedores usa `empresas.porcentaje_comision`.

## Regla de selección de precio

| Cantidad solicitada | Precio aplicado |
|---|---|
| 1 – 2 | `precio_venta` (P0) |
| 3 – 6 | `precio_venta_1` (P1) |
| 7 – 12 | `precio_venta_2` (P2) |
| ≥ 13 | `precio_venta_3` (P3) |

---

## Implementación

### Base de datos

```sql
ALTER TABLE productos
  ADD COLUMN precio_venta_1      NUMERIC(10,2) DEFAULT 0,
  ADD COLUMN precio_venta_2      NUMERIC(10,2) DEFAULT 0,
  ADD COLUMN precio_venta_3      NUMERIC(10,2) DEFAULT 0,
  ADD COLUMN porcentaje_comision NUMERIC(5,2)  DEFAULT 3.00,
  ADD COLUMN stock_comprometido  INT           DEFAULT 0;
```

### Backend

**`models.py`** — clase `Producto`:
```python
precio_venta_1      = Column(Numeric(10,2), default=0)
precio_venta_2      = Column(Numeric(10,2), default=0)
precio_venta_3      = Column(Numeric(10,2), default=0)
porcentaje_comision = Column(Numeric(5,2),  default=3.00)
stock_comprometido  = Column(Integer,       default=0)
```

**`schemas.py`** — `ProductoOut` expone los 5 campos nuevos.  
**`schemas.py`** — función `seleccionar_precio(producto, cantidad)` implementada.

**`routers/catalogos.py`** — `crear_producto`:
- Si `precio_venta_1/2/3` llegan en 0, se replican desde `precio_venta` automáticamente.

### Frontend — `crud_productos.html`

- Tabla: columna P0/P1/P2/P3 y stock/comprometido.
- Modal: grid 2×2 para los 3 precios de volumen + comisión %.
- Al ingresar `precio_venta` (P0) en modo nuevo, P1/P2/P3 se rellenan automáticamente (`replicarPrecioBase()`).
- Thumbnail de imagen en tabla (ver REQ imagen).
