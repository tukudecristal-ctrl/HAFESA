# REQ 3 — Estado CANCELADO y gestión de stock en DEPOSITADO

**Estado:** ✅ Completado  
**Fecha:** 2026-04-17

---

## Requerimiento original

> En la pantalla de seguimiento (avance de estados), solo cuando el pedido cambia a DEPOSITADO se debe restar el stock real y el stock comprometido. Agregar estado CANCELADO: solo resta el stock comprometido (no el real). Un pedido solo puede cancelarse antes de llegar a DEPOSITADO.

---

## Decisiones tomadas

### ¿Vale la pena registrar stock comprometido en negativo?

**No.** El `stock_comprometido` representa reservas activas y válidas — no tiene sentido semántico negativo. Un valor negativo indicaría un error de datos (se liberó más de lo que se reservó). Se implementó con protección `max(0, ...)` para evitar inconsistencias.

### Regla de cancelación

Un pedido solo puede cancelarse si su estado es `REGISTRADO`, `EMPACADO` o `ROTULO_IMPRESO`. Una vez en `DEPOSITADO` (ya entregado a la agencia de transporte), no es reversible operativamente.

### Flujo de stock por estado

| Transición | `stock_comprometido` | `stock` (real) |
|---|---|---|
| Nuevo pedido registrado | `+= cantidad` | sin cambio |
| → DEPOSITADO | `-= cantidad` | `-= cantidad` |
| → CANCELADO (antes de DEPOSITADO) | `-= cantidad` | sin cambio |
| Resto de transiciones | sin cambio | sin cambio |

---

## Implementación

### Base de datos

```sql
ALTER TABLE pedidos ADD COLUMN fecha_cancelado TIMESTAMP;
```

### Backend — `routers/pedidos.py`

**`avanzar_estado`** — al transicionar a `DEPOSITADO`:
```python
for detalle in pedido.detalles:
    producto = detalle.producto
    producto.stock -= detalle.cantidad
    producto.stock_comprometido = max(0, producto.stock_comprometido - detalle.cantidad)
```

**Nuevo endpoint `POST /{id}/cancelar`**:
- Bloquea si estado en `{DEPOSITADO, ENTREGADO, CANCELADO}`.
- Solo libera `stock_comprometido`:
```python
for detalle in pedido.detalles:
    producto.stock_comprometido = max(0, producto.stock_comprometido - detalle.cantidad)
pedido.estado = "CANCELADO"
pedido.fecha_cancelado = datetime.utcnow()
```

**`schemas.py`:**
```python
ESTADOS_VALIDOS = ["REGISTRADO", "EMPACADO", "ROTULO_IMPRESO", "DEPOSITADO", "ENTREGADO", "CANCELADO"]
SIGUIENTE_ESTADO = { "REGISTRADO": "EMPACADO", "EMPACADO": "ROTULO_IMPRESO",
                     "ROTULO_IMPRESO": "DEPOSITADO", "DEPOSITADO": "ENTREGADO" }
# CANCELADO no tiene siguiente estado (es salida lateral)
```

### Frontend — `backoffice.html`

- Badge `CANCELADO` en rojo (`#fed7d7 / #742a2a`).
- Botón "✕" (icono) en columna acciones → llama `POST /{id}/cancelar`.
- Deshabilitado si estado en `['DEPOSITADO', 'ENTREGADO', 'CANCELADO']`.
- CANCELADO incluido en filtros de estado y conteo KPI con ícono ❌.
- Icono por estado: `{REGISTRADO:'📋', EMPACADO:'📦', ROTULO_IMPRESO:'🏷️', DEPOSITADO:'🚚', ENTREGADO:'✅', CANCELADO:'❌'}`.

### Frontend — `seguimiento.html`

- Etapa CANCELADO agregada al timeline (ícono ❌, clase CSS `.cancelada`).
- CSS: `.etapa.cancelada .etapa-icono { background:#fed7d7; border-color:#e53e3e }`.
