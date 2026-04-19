# Plan de Implementación — VERDE Sistema de Ventas Hafesa

**Última actualización:** 2026-04-18  
**Estado general:** ✅ Todos los requerimientos completados

---

## Índice de requerimientos

| # | Requerimiento | Archivo de detalle | Estado |
|---|---|---|---|
| 1 | Nuevos campos en tabla Productos (precios volumen, comisión, stock comprometido) | [req1_productos.md](req1_productos.md) | ✅ |
| 2 | Pedidos multi-producto con precio automático por cantidad y descuento | [req2_pedidos_multiproducto.md](req2_pedidos_multiproducto.md) | ✅ |
| 3 | Estado CANCELADO y gestión de stock en DEPOSITADO | [req3_estados_stock.md](req3_estados_stock.md) | ✅ |
| 4 | Comisiones de vendedores: cálculo, selección y pago | [req4_comisiones.md](req4_comisiones.md) | ✅ |
| 5 | Acceso y autenticación (JWT, roles: admin/vendedor/logística) | [req5_autenticacion.md](req5_autenticacion.md) | ✅ |

---

## Mejoras adicionales implementadas

| Mejora | Descripción |
|---|---|
| CRUD Empresas | Pantalla completa de gestión de empresas con porcentaje de comisión y rubro |
| CRUD Usuarios | Pantalla admin para crear/editar usuarios, asignar rol y vendedor, reset contraseña |
| Imágenes de productos | Upload de imagen por producto (disco + `/imagenes/` estático), thumbnail en tabla, lightbox |
| Formato decimal | Todos los montos en formato `es-PE` (1.234,50) en todas las pantallas |
| Botones icono en backoffice | Cancelar/Rótulo/Seguimiento reducidos a icono con tooltip |
| Filtro últimos 30 días | Backoffice muestra por defecto pedidos de los últimos 30 días |
| Iconos en stats | Cada estado tiene un emoji en los contadores del backoffice |
| Logout global | Botón "Salir" en el header de todas las páginas |
| DNI flexible | Validación de DNI acepta 8–10 dígitos (peruano + extranjero) |

---

## Archivos creados / modificados

### Backend

| Archivo | Tipo |
|---|---|
| `backend/models.py` | Modificado — Producto, DetallePedido, Pedido, Usuario |
| `backend/schemas.py` | Modificado — nuevos schemas + auth + comisiones |
| `backend/main.py` | Modificado — nuevos routers, mount imagenes, redirect login |
| `backend/dependencies.py` | **Nuevo** — get_current_user, require_roles |
| `backend/routers/catalogos.py` | Modificado — CRUD empresas, upload imagen |
| `backend/routers/pedidos.py` | Modificado — multi-producto, stock, cancelar |
| `backend/routers/comisiones.py` | **Nuevo** — resumen, detalle, pagar |
| `backend/routers/auth.py` | **Nuevo** — login, CRUD usuarios |
| `backend/routers/mis_ventas.py` | **Nuevo** — dashboard vendedor |
| `backend/static/imagenes/` | **Nuevo** — directorio de imágenes de productos |

### Frontend

| Archivo | Tipo |
|---|---|
| `frontend/auth.js` | **Nuevo** — guard compartido JWT |
| `frontend/login.html` | **Nuevo** — pantalla de ingreso Hafesa |
| `frontend/mis_ventas.html` | **Nuevo** — dashboard del vendedor |
| `frontend/comisiones.html` | **Nuevo** — gestión de comisiones |
| `frontend/crud_empresas.html` | **Nuevo** — CRUD empresas |
| `frontend/crud_usuarios.html` | **Nuevo** — CRUD usuarios (admin) |
| `frontend/backoffice.html` | Modificado — estados, iconos, filtro 30d, logout, auth |
| `frontend/formulario_pedido.html` | Modificado — multi-producto, preselección vendedor |
| `frontend/crud_productos.html` | Modificado — precios volumen, imagen |
| `frontend/seguimiento.html` | Modificado — estado CANCELADO |
| `frontend/compras.html` | Modificado — auth guard, formato decimal |
| `frontend/crud_vendedores.html` | Modificado — auth guard, logout |
| `frontend/crud_proveedores.html` | Modificado — auth guard, logout |

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | FastAPI + SQLAlchemy ORM + Pydantic v2 |
| Base de datos | PostgreSQL 16 |
| Autenticación | JWT (PyJWT) + bcrypt |
| Frontend | Vue 3 CDN (sin build step) + HTML/CSS vanilla |
| Imágenes | Disco local + FastAPI StaticFiles |
| Servidor | Uvicorn con `--reload` |

---

## Pendiente / Próximos pasos

- [ ] Deploy en nube (Railway o Hetzner) con CI/CD desde GitHub
- [ ] Migrar almacenamiento de imágenes a Cloudflare R2 (requerido en PaaS)
- [ ] Configurar `SECRET_KEY` segura en producción (`.env` real)
- [ ] Cambiar contraseñas iniciales de usuarios de prueba
