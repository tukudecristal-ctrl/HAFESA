# REQ 5 — Acceso y Autenticación

**Estado:** ✅ Completado  
**Fecha:** 2026-04-18

---

## Requerimiento original

> Sistema de autenticación con 3 roles: administrador (acceso total, aterriza en backoffice), vendedor (aterriza en formulario de pedidos con su nombre preseleccionado y bloqueado, puede ver sus ventas y comisiones pendientes), logística (aterriza en backoffice con todas sus funcionalidades). Usuario = DNI de 8 dígitos. Pantalla de inicio con nombre "Hafesa".

---

## Decisiones tomadas

- **Token:** JWT con `PyJWT` (ya instalado). Expiración: 10 horas. Firmado con `SECRET_KEY` del `.env`.
- **Hash de contraseñas:** `bcrypt` directamente (passlib 1.7.4 es incompatible con bcrypt 5.x — da error en Python 3.13).
- **Almacenamiento en frontend:** `localStorage` con claves `hafesa_token` y `hafesa_user`.
- **Guard compartido:** archivo `auth.js` incluido en todas las páginas — evita duplicar lógica.
- **Imágenes de subida:** el endpoint de upload usa `UploadFile` de FastAPI (multipart), el `auth.js` detecta `FormData` y no fuerza `Content-Type: application/json`.

---

## Roles y redirección

| Rol | Aterriza en | Restricciones |
|---|---|---|
| `administrador` | `backoffice.html` | Acceso a todo, incluye CRUD usuarios |
| `logistica` | `backoffice.html` | Acceso a pedidos, compras, productos |
| `vendedor` | `formulario_pedido.html` | Empresa y vendedor preseleccionados y bloqueados |

---

## Tabla de acceso por página

| Página | Roles permitidos |
|---|---|
| `login.html` | Público |
| `backoffice.html` | administrador, logistica |
| `formulario_pedido.html` | todos (autenticados) |
| `mis_ventas.html` | vendedor |
| `comisiones.html` | administrador, logistica |
| `compras.html` | administrador, logistica |
| `crud_productos.html` | administrador, logistica |
| `crud_vendedores.html` | administrador |
| `crud_empresas.html` | administrador |
| `crud_proveedores.html` | administrador |
| `crud_usuarios.html` | administrador |

---

## Implementación

### Base de datos

```sql
CREATE TABLE usuarios (
    id           SERIAL PRIMARY KEY,
    dni          VARCHAR(8) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre       VARCHAR(150) NOT NULL,
    rol          VARCHAR(20) NOT NULL CHECK (rol IN ('administrador','vendedor','logistica')),
    vendedor_id  INT REFERENCES vendedores(id),
    activo       BOOLEAN DEFAULT TRUE,
    created_at   TIMESTAMP DEFAULT NOW()
);
```

### Backend — archivos nuevos/modificados

| Archivo | Cambio |
|---|---|
| `backend/dependencies.py` | `get_current_user` (decode JWT), `require_roles(*roles)` |
| `backend/routers/auth.py` | `POST /login`, `GET /me`, CRUD usuarios (solo admin), `POST /setup` (primer admin) |
| `backend/routers/mis_ventas.py` | `GET /pedidos` y `GET /comisiones` para el vendedor autenticado |
| `backend/models.py` | Clase `Usuario` |
| `backend/schemas.py` | `LoginInput`, `TokenOut`, `UsuarioCreate/Update/Out`, `UsuarioPasswordReset` |
| `backend/main.py` | Routers `auth` y `mis_ventas` incluidos; redirect raíz → `login.html` |

### Frontend — archivos nuevos

| Archivo | Descripción |
|---|---|
| `auth.js` | `Auth.getToken()`, `Auth.getUser()`, `Auth.save()`, `Auth.logout()`, `Auth.require(roles)`, `Auth.fetch()` |
| `login.html` | Pantalla de ingreso con branding Hafesa (gradiente azul marino, logo 🏭) |
| `mis_ventas.html` | Dashboard vendedor: stats (pedidos, ventas netas, comisión pendiente/cobrada), tabla con estado + fecha estado |
| `crud_usuarios.html` | CRUD completo: crear, editar rol/vendedor, toggle activo, reset contraseña |

### Frontend — cambios en páginas existentes

- `<script src="auth.js">` agregado a todas las páginas.
- `Auth.require([roles])` en `onMounted` de cada página.
- Botón **Salir** en header de todas las páginas.
- `formulario_pedido.html`: si `user.rol === 'vendedor'`, empresa y vendedor se preseleccionan automáticamente y el select queda `disabled`.
- `backoffice.html`: enlace "Usuarios" en nav (solo visible a admin en la práctica).

### Usuarios iniciales creados

| DNI | Nombre | Rol | Clave | vendedor_id |
|---|---|---|---|---|
| 10000001 | David | administrador | 10000001 | — |
| 10000002 | Mayra | vendedor | 10000002 | 1 (Carlos Mamani Torres) |
| 10000003 | Christian | logistica | 10000003 | — |

---

## Notas técnicas

- `POST /api/auth/setup` crea el primer administrador solo si la tabla `usuarios` está vacía. Útil en deploy inicial.
- El token JWT contiene: `sub` (dni), `rol`, `nombre`, `usuario_id`, `vendedor_id`, `exp`.
- `Auth.fetch()` maneja automáticamente el header `Authorization: Bearer <token>` y redirige a login en 401.
