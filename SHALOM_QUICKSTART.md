# 🚀 Shalom API - Guía de Inicio Rápido

**5 minutos para empezar a usar Shalom API en tu proyecto VERDE**

## Paso 1️⃣ - Obtener API Key (2 minutos)

1. Ve a https://shalom-api-peru.com
2. Inicia sesión o crea una cuenta
3. En Dashboard → API Settings → Genera una API Key
4. Copia tu clave (algo como: `sk_live_abc123xyz...`)

## Paso 2️⃣ - Configurar Proyecto (1 minuto)

```bash
# 1. Copiar archivo de configuración
cp backend/.env.example.shalom backend/.env.shalom

# 2. Editar y agregar tu API Key
# backend/.env.shalom
SHALOM_API_KEY=tu-clave-aqui
```

## Paso 3️⃣ - Verificar Funcionamiento (1 minuto)

```bash
# Ejecutar verificación rápida
cd /Users/darh/proyectos/VERDE

python3 << 'EOF'
from backend.shalom_api_client import ShalomAPIClient
import os

api_key = "tu-clave-aqui"  # Reemplaza con tu clave
client = ShalomAPIClient(api_key=api_key)

print("🔍 Verificando conexión...")
if client.health_check():
    print("✅ API disponible")
else:
    print("❌ API no disponible")

print("\n📦 Probando endpoint de agencias...")
agencies = client.agencies.list(per_page=3)
if agencies.get('agencies'):
    print(f"✅ {len(agencies['agencies'])} agencias listadas")
    for a in agencies['agencies'][:2]:
        print(f"   - {a.get('nombre')}")
else:
    print("⚠️ No se obtuvieron agencias")
EOF
```

## Paso 4️⃣ - Usar en tu Código (1 minuto)

### Opción A: Uso Directo

```python
from backend.shalom_api_client import ShalomAPIClient

client = ShalomAPIClient(api_key="tu-api-key")

# Rastrear envío
order = client.tracking.search(numero="123456")
print(order)

# Listar agencias
agencies = client.agencies.list(per_page=10)
print(agencies)
```

### Opción B: En FastAPI (Recomendado)

```python
# backend/routes/shalom_routes.py
from fastapi import APIRouter, Depends
from backend.shalom_service import ShalomService, get_service
from backend.shalom_service import TrackingRequest

router = APIRouter(prefix="/api/shalom", tags=["Shalom"])

@router.post("/track")
async def track_order(
    request: TrackingRequest,
    service: ShalomService = Depends(get_service)
):
    return await service.track_order(request)

@router.get("/agencies")
async def list_agencies(service: ShalomService = Depends(get_service)):
    return await service.list_agencies(per_page=10)
```

```python
# backend/main.py
from fastapi import FastAPI
from backend.routes.shalom_routes import router as shalom_router

app = FastAPI()
app.include_router(shalom_router)
```

## 📚 Documentación Completa

| Archivo | Descripción |
|---------|-------------|
| `backend/README_SHALOM_API.md` | Documentación técnica completa |
| `backend/shalom_examples.py` | 8 ejemplos prácticos (descomenta para usar) |
| `backend/SHALOM_IMPLEMENTATION.md` | Detalles de implementación |
| `backend/shalom_api_client.py` | Cliente principal (1000+ líneas) |
| `backend/shalom_service.py` | Capa de servicio FastAPI (400+ líneas) |

## 🔍 Operaciones Disponibles

### Rastreo de Envíos
```python
# Buscar
client.tracking.search(numero="123456")

# Eventos
client.tracking.get_events(ose_id="NGN01-123")

# Descargar PDFs
client.tracking.get_voucher(ose_id="NGN01-123")
client.tracking.get_grt(ose_id="NGN01-123", cap_id="CAP123")
```

### Agencias
```python
# Listar todas
client.agencies.list(page=1, per_page=100)

# Buscar por departamento
client.agencies.search(departamento="Lima")

# Obtener detalles
client.agencies.get(agency_id=123)
```

### Ubicaciones
```python
# Departamentos
client.locations.get_departments()

# Provincias
client.locations.get_provinces(dep_id="15")

# Distritos
client.locations.get_districts(dep_id="15", prov_id="1501")
```

### Órdenes (Requiere Autenticación)
```python
# Autenticar primero
client.authenticate(email="...", password="...")

# Productos
client.orders.get_products()

# Calcular tarifa
client.orders.calculate_tariff(
    origin_terminal_id="LIMACENTRAL",
    destiny_terminal_id="AREQPUERTO"
)

# Crear guía
client.orders.create(
    origin_terminal_id="...",
    destiny_terminal_id="...",
    product_id="...",
    sender={...},
    receiver={...},
    pickup_code="..."
)

# Listar órdenes
client.orders.list()

# Eliminar orden
client.orders.delete(order_id="...")

# Descargar documentos
client.orders.get_label(ose_id="...")
client.orders.get_voucher(ose_id="...")

# Revocar sesión
client.revoke_session()
```

## ⚡ Características Automáticas

- ✅ **Rate Limiting**: Manejo automático de 60 req/min
- ✅ **Reintentos**: Exponential backoff en errores
- ✅ **Logging**: Debugging con `verbose=True`
- ✅ **Validación**: Schemas Pydantic en FastAPI
- ✅ **Errores**: Excepciones específicas por tipo

## 🔐 Ejemplos Seguros

### ❌ NUNCA hagas esto:
```python
# Hardcodear credenciales
client = ShalomAPIClient(api_key="sk_live_abc123")  # ¡MAL!
```

### ✅ SIEMPRE usa:
```python
import os
from dotenv import load_dotenv

load_dotenv('.env.shalom')
api_key = os.getenv('SHALOM_API_KEY')
client = ShalomAPIClient(api_key=api_key)
```

## 🧪 Ejemplos Listos para Usar

Ver archivo `backend/shalom_examples.py`

```bash
# Descomenta los ejemplos que quieras probar
# y ejecuta:
python3 backend/shalom_examples.py
```

## 📞 Problemas Comunes

| Problema | Solución |
|----------|----------|
| `ShalomAuthError` | Verifica que tu API_KEY sea correcta |
| `ShalomNotFoundError` | El envío/recurso no existe |
| `ShalomRateLimitError` | Esperando límite de 60 req/min (automático) |
| `ShalomValidationError` | Parámetros requeridos faltantes |

## 📋 Checklist Final

- [ ] API Key obtenida
- [ ] `.env.shalom` configurado
- [ ] `health_check()` devuelve `True`
- [ ] Ejemplo simple probado
- [ ] Integración FastAPI funcionando
- [ ] Endpoints listados en OpenAPI docs

## 🎯 Próximas Tareas

1. **Integrar en endpoints existentes**
   - Crear rutas en `routes/shalom_routes.py`
   - Usar `ShalomService` con dependency injection

2. **Testing**
   - Crear tests unitarios con pytest
   - Mock de Shalom API para tests

3. **Frontend**
   - Conectar endpoints frontend a las rutas API
   - Mostrar datos de tracking en UI

---

**¡Listo! Ahora puedes empezar a usar Shalom API. Consulta la documentación completa en `backend/README_SHALOM_API.md` para más detalles.**
