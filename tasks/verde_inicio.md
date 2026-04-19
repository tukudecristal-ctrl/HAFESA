# Plan de Implementación — Sistema de Ventas Multiempresa
**Stack:** Vue.js (CDN) · FastAPI + SQLAlchemy + Pydantic · PostgreSQL
**Entorno dev:** Linux Mint · **Deploy:** Digital Ocean (Droplet Ubuntu)
**Virtualenv:** `/home/darh/trabajo/env_pytuku`

---

## 1. Software a Instalar

### Linux Mint (Máquina de Desarrollo)

#### Python y FastAPI
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv python3-dev -y

# Usar el entorno virtual existente
source /home/darh/trabajo/env_pytuku/bin/activate

# Paquetes ya instalados en el env:
# fastapi uvicorn sqlalchemy psycopg2-binary pydantic pydantic-settings python-dotenv
```

#### PostgreSQL
```bash
sudo apt install postgresql postgresql-contrib -y
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Crear base de datos y usuario
sudo -u postgres psql
  CREATE DATABASE verde;
  CREATE USER admin_verde WITH PASSWORD 'HaFeSa@2026';
  GRANT ALL PRIVILEGES ON DATABASE verde TO admin_verde;
  \q
```

#### Git
```bash
sudo apt install git -y
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"
```

#### VS Code (recomendado)
```bash
# Descargar .deb desde https://code.visualstudio.com
sudo dpkg -i code_*.deb
# Extensiones recomendadas: Python, Django, Vue Volar, PostgreSQL
```

#### Herramientas adicionales
```bash
sudo apt install curl wget htop -y
# Postman: descargar AppImage desde https://www.postman.com/downloads/
```

---

### Digital Ocean — Droplet (Deploy)

> Recomendado: Ubuntu 22.04 LTS · 2 GB RAM · 1 vCPU · 50 GB SSD (~$12/mes)

```bash
apt update && apt upgrade -y
apt install python3 python3-pip python3-venv python3-dev -y
apt install postgresql postgresql-contrib -y
apt install nginx git -y
pip install fastapi uvicorn[standard] sqlalchemy psycopg2-binary pydantic pydantic-settings python-dotenv
apt install certbot python3-certbot-nginx -y
```

---

## 2. Flujo de Estados del Pedido

```
Pendiente → Empacado → Despachado → En Destino → Pagado → Entregado (Cierre)
```

| Estado | Descripción | Timestamp registrado |
|--------|-------------|----------------------|
| **Pendiente** | Pedido recién creado | `creado_en` |
| **Empacado** | Producto preparado y embalado | `fecha_empacado` |
| **Despachado** | Entregado a agencia Shalom | `fecha_despachado` |
| **En Destino** | Llegó a agencia destino | `fecha_en_destino` |
| **Pagado** | Cliente pagó (incluye cobro de comisión al vendedor) | `fecha_pagado` |
| **Entregado** | Entregado al cliente — **Cierre** | `fecha_entregado` |

> **Pagado** agrupa lo que antes eran "Cobrado" y "Comisión" en un solo paso.

---

## 3. Estructura del Proyecto FastAPI

```
VERDE/
├── backend/
│   ├── main.py             # App FastAPI + registro de routers
│   ├── database.py         # SQLAlchemy engine + sesión
│   ├── models.py           # Modelos ORM
│   ├── schemas.py          # Schemas Pydantic (validación + serialización)
│   ├── requirements.txt
│   ├── .env
│   └── routers/
│       ├── catalogos.py    # Empresas, Vendedores, Productos, Agencias
│       ├── pedidos.py      # Pedidos + flujo de estados
│       └── compras.py      # Compras + actualización de stock
└── frontend/               # HTML + Vue.js CDN
    ├── formulario_pedido.html
    ├── backoffice.html
    ├── seguimiento.html
    ├── rotulo.html
    ├── compras.html
    ├── crud_productos.html
    └── crud_vendedores.html
```

---

## 4. Schema SQL

```sql
-- ─────────────────────────────────────────
-- MAESTROS
-- ─────────────────────────────────────────

CREATE TABLE empresas (
    id         SERIAL PRIMARY KEY,
    codigo     VARCHAR(10) UNIQUE NOT NULL,
    nombre     VARCHAR(100) NOT NULL,
    rubro      VARCHAR(50)
);

CREATE TABLE vendedores (
    id         SERIAL PRIMARY KEY,
    codigo     VARCHAR(10) UNIQUE NOT NULL,
    nombre     VARCHAR(100) NOT NULL,
    telefono   CHAR(9) CHECK (telefono ~ '^9[0-9]{8}$'),
    empresa_id INT REFERENCES empresas(id),
    activo     BOOLEAN DEFAULT TRUE
);

CREATE TABLE proveedores (
    id         SERIAL PRIMARY KEY,
    codigo     VARCHAR(10) UNIQUE NOT NULL,
    nombre     VARCHAR(100) NOT NULL,
    contacto   VARCHAR(100),
    telefono   VARCHAR(20),
    activo     BOOLEAN DEFAULT TRUE
);

CREATE TABLE categorias (
    id         SERIAL PRIMARY KEY,
    nombre     VARCHAR(60) NOT NULL
);

CREATE TABLE productos (
    id                        SERIAL PRIMARY KEY,
    codigo                    VARCHAR(20) UNIQUE NOT NULL,
    codigo_producto_proveedor VARCHAR(30),
    nombre                    VARCHAR(150) NOT NULL,
    descripcion               TEXT,
    empresa_id                INT REFERENCES empresas(id),
    categoria_id              INT REFERENCES categorias(id),
    proveedor_id              INT REFERENCES proveedores(id),
    precio_venta              NUMERIC(10,2) NOT NULL DEFAULT 0,
    stock                     INT NOT NULL DEFAULT 0,
    activo                    BOOLEAN DEFAULT TRUE
);

CREATE TABLE agencias_destino (
    id         SERIAL PRIMARY KEY,
    nombre     VARCHAR(100) NOT NULL,
    ciudad     VARCHAR(60),
    activo     BOOLEAN DEFAULT TRUE
);

-- ─────────────────────────────────────────
-- COMPRAS
-- ─────────────────────────────────────────

CREATE TABLE compras (
    id            SERIAL PRIMARY KEY,
    proveedor_id  INT NOT NULL REFERENCES proveedores(id),
    fecha_compra  DATE NOT NULL DEFAULT CURRENT_DATE,
    observaciones TEXT,
    creado_en     TIMESTAMP DEFAULT NOW()
);

CREATE TABLE compra_items (
    id          SERIAL PRIMARY KEY,
    compra_id   INT NOT NULL REFERENCES compras(id) ON DELETE CASCADE,
    producto_id INT NOT NULL REFERENCES productos(id),
    costo       NUMERIC(10,2) NOT NULL,
    cantidad    INT NOT NULL CHECK (cantidad > 0),
    total       NUMERIC(10,2) GENERATED ALWAYS AS (costo * cantidad) STORED
);

-- Trigger: actualizar stock al registrar compra
CREATE OR REPLACE FUNCTION actualizar_stock_compra()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE productos SET stock = stock + NEW.cantidad
    WHERE id = NEW.producto_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_stock_compra
AFTER INSERT ON compra_items
FOR EACH ROW EXECUTE FUNCTION actualizar_stock_compra();

-- ─────────────────────────────────────────
-- PEDIDOS
-- ─────────────────────────────────────────

CREATE TYPE estado_pedido AS ENUM (
    'pendiente',
    'empacado',
    'despachado',
    'en_destino',
    'pagado',
    'entregado'
);

CREATE TABLE pedidos (
    id                SERIAL PRIMARY KEY,
    empresa_id        INT NOT NULL REFERENCES empresas(id),
    vendedor_id       INT NOT NULL REFERENCES vendedores(id),
    cliente_nombre    VARCHAR(150) NOT NULL,
    cliente_dni       CHAR(10) CHECK (cliente_dni ~ '^[0-9]{10}$'),
    cliente_telefono  CHAR(9)  CHECK (cliente_telefono ~ '^9[0-9]{8}$'),
    producto_id       INT NOT NULL REFERENCES productos(id),
    cantidad          INT NOT NULL CHECK (cantidad > 0),
    agencia_id        INT NOT NULL REFERENCES agencias_destino(id),
    detalle           TEXT,
    separacion        NUMERIC(10,2) NOT NULL DEFAULT 0,
    costo_envio       NUMERIC(10,2) NOT NULL DEFAULT 0,
    precio_total      NUMERIC(10,2),
    resta_pagar       NUMERIC(10,2),   -- precio_total - separacion
    estado            estado_pedido NOT NULL DEFAULT 'pendiente',
    -- Timestamps por etapa
    creado_en         TIMESTAMP DEFAULT NOW(),
    fecha_empacado    TIMESTAMP,
    fecha_despachado  TIMESTAMP,
    fecha_en_destino  TIMESTAMP,
    fecha_pagado      TIMESTAMP,
    fecha_entregado   TIMESTAMP        -- Cierre
);
```

---

## 5. Endpoints API (FastAPI)

### Maestros — CRUD
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET / POST | `/api/vendedores/` | Listar / Crear |
| GET / PUT / DELETE | `/api/vendedores/{id}/` | Ver / Editar / Eliminar |
| GET / POST | `/api/proveedores/` | Listar / Crear |
| GET / PUT / DELETE | `/api/proveedores/{id}/` | Ver / Editar / Eliminar |
| GET / POST | `/api/productos/` | Listar / Crear |
| GET / PUT / DELETE | `/api/productos/{id}/` | Ver / Editar / Eliminar |
| GET | `/api/agencias/` | Listar agencias Shalom |
| GET | `/api/empresas/` | Listar empresas |

### Compras
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/compras/` | Listar compras |
| POST | `/api/compras/` | Registrar compra con items (actualiza stock) |
| GET | `/api/compras/{id}/` | Detalle de compra |

### Pedidos
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/pedidos/` | Listar (filtros: estado, empresa, fecha, vendedor) |
| POST | `/api/pedidos/` | Crear pedido |
| GET | `/api/pedidos/{id}/` | Detalle de pedido |
| PATCH | `/api/pedidos/{id}/avanzar/` | Avanzar al siguiente estado → registra timestamp |
| GET | `/api/pedidos/{id}/rotulo/` | Datos para impresión de rótulo |
| GET | `/api/pedidos/{id}/seguimiento/` | Estado actual + historial de etapas con fechas |

---

## 6. Páginas HTML + Vue.js

### 6.1 `formulario_pedido.html` — Público (vendedores)
- Selector de empresa
- Buscador de vendedor por código → autocompleta nombre
- Validación en tiempo real: DNI (10 dígitos), teléfono (9 dígitos, empieza en 9)
- Selector de producto filtrado por empresa
- Selector de agencia Shalom (desde API)
- Cálculo en tiempo real de **Resta a Pagar**
- Sin autenticación requerida

### 6.2 `backoffice.html` — Panel de gestión
- Tabla de pedidos con filtros: empresa, estado, fecha, vendedor
- Botón **Avanzar estado** por fila
- Botón **Imprimir Rótulo** → `rotulo.html?id=X`
- Botón **Ver Seguimiento** → `seguimiento.html?id=X`
- Indicadores de color por etapa:
  - 🔵 Pendiente · 🟡 Empacado · 🟠 Despachado · 🟣 En Destino · 🟢 Pagado · ✅ Entregado

### 6.3 `seguimiento.html` — Línea de tiempo del pedido *(Sprint 7)*
- Buscar por ID de pedido o DNI del cliente
- Consume `/api/pedidos/{id}/seguimiento/`
- Línea de tiempo visual:
  ```
  ✅ Pendiente     → 01/04/2026 10:30
  ✅ Empacado      → 01/04/2026 14:15
  ✅ Despachado    → 02/04/2026 09:00
  ✅ En Destino    → 03/04/2026 16:45
  🔄 Pagado        → (en curso)
  ⬜ Entregado (Cierre)
  ```
- Datos del pedido: cliente, producto, agencia destino, resta pagar
- Diseño detallado pendiente para Sprint 7

### 6.4 `rotulo.html` — Impresión
- Datos: CLIENTE · DESTINO · PRODUCTO · DNI · TELÉFONO · CANTIDAD · COSTO ENVÍO · RESTA PAGAR
- CSS `@media print` — sin botones al imprimir
- Auto-dispara `window.print()` al cargar

### 6.5 `compras.html` — Registro de compras
- Selector de proveedor por código
- Tabla dinámica de items con opción **"+ Nuevo producto"** inline
- Total por fila calculado automáticamente
- Stock se actualiza via trigger al guardar

### 6.6 CRUDs
- `crud_productos.html` — listar, crear, editar, ver stock
- `crud_proveedores.html` — listar, crear, editar
- `crud_vendedores.html` — listar, crear, editar, asignar empresa

---

## 7. Sprints de Desarrollo

| Sprint | Contenido | Estado |
|--------|-----------|--------|
| **1** | Schema SQL + trigger de stock + datos de prueba | ✅ |
| **2** | Proyecto FastAPI + modelos SQLAlchemy + schemas Pydantic | ✅ |
| **3** | Routers: catálogos ✅ · pedidos · compras | 🔄 En curso |
| **4** | `formulario_pedido.html` con Vue.js CDN | ⬜ |
| **5** | `backoffice.html` + `rotulo.html` | ⬜ |
| **6** | `compras.html` + CRUDs (productos, vendedores) | ⬜ |
| **7** | `seguimiento.html` — línea de tiempo visual | ⬜ |
| **8** | Deploy Digital Ocean: Uvicorn + Nginx + SSL | ⬜ |

---

## 8. Variables de Entorno (`.env`)

```env
DATABASE_URL=postgresql://admin_verde:HaFeSa@2026@localhost:5432/verde
SECRET_KEY=genera-una-clave-larga-y-aleatoria
DEBUG=True                  # False en producción
ALLOWED_HOSTS=localhost,127.0.0.1,tu-dominio.com
CORS_ALLOWED_ORIGINS=http://localhost:8000,https://tu-dominio.com
```

---

## 9. Notas Técnicas para Claude Code

- `NUMERIC(10,2)` para todos los montos — **nunca FLOAT**.
- `formulario_pedido.html` es **público** — sin autenticación.
- `precio_total` y `resta_pagar` se calculan en el **backend** al crear el pedido.
- El endpoint `/pedidos/{id}/avanzar` determina el siguiente estado con `SIGUIENTE_ESTADO` dict en `schemas.py` y registra el timestamp automáticamente.
- El campo `subtotal` en `detalle_compra` es columna generada en PostgreSQL — no enviar en el INSERT.
- Vue.js via CDN (`https://unpkg.com/vue@3`) — no requiere Node.js ni npm.
- La actualización de stock al registrar compra se hace en el **router de compras** (no trigger SQL) para mantener la lógica en Python.
- Virtualenv: `/home/darh/trabajo/env_pytuku` — no crear uno nuevo.
- Correr el servidor: `uvicorn main:app --reload` desde `/home/proyectos/VERDE/backend/`.
