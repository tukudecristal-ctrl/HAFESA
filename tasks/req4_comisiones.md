# REQ 4 — Comisiones de Vendedores

**Estado:** ✅ Completado  
**Fecha:** 2026-04-17

---

## Requerimiento original

> Calcular la comisión a pagar a cada vendedor por sus ventas. Fuente: pedidos en estado ENTREGADO y pendientes de pagar comisión. Cálculo: `empresas.porcentaje_comision * (pedido.precio_total - pedido.descuento)`. Operativa: listar vendedores con monto pendiente → ver detalle → imprimir → botón PAGAR que registra la fecha de pago.

---

## Decisiones tomadas

- **Tasa de comisión:** se usa `empresas.porcentaje_comision` (por empresa), no `productos.porcentaje_comision`. El campo en productos es referencial.
- **Base de cálculo:** `monto_neto = precio_total - descuento` (descuento ya registrado en el pedido).
- **Estado de pago:** se usa `pedidos.fecha_pago_comision` (datetime). `NULL` = pendiente, fecha registrada = pagado. Es más útil que un booleano porque guarda cuándo se pagó.
- **Selección de pedidos a pagar:** el admin selecciona individualmente qué pedidos incluir en el pago (checkboxes), no se paga todo el histórico de golpe.

---

## Fórmula

```
comision_pedido = (empresa.porcentaje_comision / 100) × (pedido.precio_total - pedido.descuento)
```

---

## Implementación

### Base de datos

```sql
ALTER TABLE pedidos ADD COLUMN fecha_pago_comision TIMESTAMP;
ALTER TABLE empresas ADD COLUMN porcentaje_comision NUMERIC(5,2) DEFAULT 3.00;
```

### Backend — `routers/comisiones.py` (nuevo archivo)

| Endpoint | Descripción |
|---|---|
| `GET /resumen` | Agrupa pedidos ENTREGADO + sin pagar por vendedor. Devuelve lista con monto pendiente por vendedor. |
| `GET /vendedor/{id}` | Detalle de pedidos pendientes de un vendedor. |
| `POST /pagar` | Body: `{pedido_ids: [int], fecha_pago: date}`. Valida que todos sean ENTREGADO y sin pagar. Actualiza `fecha_pago_comision`. |

**`schemas.py`** — nuevos schemas:
- `ComisionVendedorOut`: resumen por vendedor (nombre, empresa, pedidos pendientes, ventas netas, comisión).
- `ComisionPedidoOut`: detalle por pedido (cliente, fechas, total, descuento, neto, comisión).
- `PagarComisionesInput`: `{pedido_ids, fecha_pago}`.

### Frontend — `comisiones.html` (nuevo archivo)

**Vista 1 — Resumen por vendedor:**
- Stats globales: vendedores con pendiente, pedidos, total ventas netas, total comisiones.
- Tabla con columnas: vendedor, empresa, comisión %, pedidos pendientes, ventas netas, comisión pendiente.
- Click en fila → navega a vista detalle.

**Vista 2 — Detalle vendedor:**
- Header: nombre vendedor, empresa, porcentaje de comisión.
- Tabla con checkboxes: pedido, cliente, fecha registro, fecha entrega, total, descuento, neto, comisión.
- Select all / deselect all.
- Consolidado al pie: neto total + comisión total de los seleccionados.
- Botón **PAGAR**: abre modal con input fecha (default hoy, max hoy) → `POST /api/comisiones/pagar`.
- Soporte de impresión (`@media print` oculta controles, muestra solo tabla + consolidado).

### Frontend — navegación

- Enlace "💰 Comisiones" en el header de `backoffice.html`.
