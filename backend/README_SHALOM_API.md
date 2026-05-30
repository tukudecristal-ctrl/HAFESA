# Shalom API Client - Documentación de Integración

Cliente Python completo para consumir todas las APIs de **Shalom Courier Service Perú**.

## 📋 Tabla de Contenidos

1. [Características](#características)
2. [Instalación](#instalación)
3. [Configuración](#configuración)
4. [Uso Básico](#uso-básico)
5. [API Reference](#api-reference)
6. [Integración con FastAPI](#integración-con-fastapi)
7. [Manejo de Errores](#manejo-de-errores)
8. [Ejemplos Completos](#ejemplos-completos)

---

## ✨ Características

- ✅ **Cobertura completa de APIs**: Tracking, Agencias, Ubicaciones, Órdenes
- ✅ **Autenticación robusta**: API Key + Session Tokens para Shalom Pro
- ✅ **Rate limiting automático**: 60 requests/minuto con esperas transparentes
- ✅ **Reintentos inteligentes**: Exponential backoff para errores transitorios
- ✅ **Type hints completos**: Soporte para IDE autocompletar y type checking
- ✅ **Logging detallado**: Configuración verbose para debugging
- ✅ **Manejo de errores**: Excepciones específicas para cada tipo de error
- ✅ **Descargas binarias**: Soporta PDFs (vouchers, etiquetas, GRTs)

---

## 📦 Instalación

### Requisitos

```bash
Python >= 3.8
requests >= 2.28.0
```

### Pasos

```bash
# El cliente solo requiere requests (ya incluido en requirements.txt de VERDE)
pip install requests

# O si usas el proyecto VERDE:
pip install -r requirements.txt
```

---

## ⚙️ Configuración

### 1. Obtener API Key

1. Ve a https://shalom-api-peru.com
2. Inicia sesión o crea una cuenta
3. Genera una API Key en tu dashboard
4. Guarda la clave de forma segura

### 2. Configurar Variables de Entorno

```bash
# .env
SHALOM_API_KEY=tu-api-key-aqui
SHALOM_EMAIL=tu-email@shalom.com      # Para operaciones que crean órdenes
SHALOM_PASSWORD=tu-contraseña-aqui    # Para operaciones que crean órdenes
```

### 3. Cargar en tu Aplicación

```python
import os
from shalom_api_client import ShalomAPIClient

api_key = os.getenv('SHALOM_API_KEY')
client = ShalomAPIClient(api_key=api_key)
```

---

## 🚀 Uso Básico

### Cliente Mínimo

```python
from shalom_api_client import ShalomAPIClient

# Inicializar
client = ShalomAPIClient(api_key="tu-api-key")

# Rastrear envío
order = client.tracking.search(numero="123456")
print(order)

# Listar agencias
agencies = client.agencies.list(per_page=10)
print(agencies)

# Obtener departamentos
departments = client.locations.get_departments()
print(departments)

# Obtener productos
products = client.orders.get_products()
print(products)
```

### Con Autenticación (Shalom Pro)

Para crear órdenes, necesitas autenticarte:

```python
from shalom_api_client import ShalomAPIClient, DocumentType

client = ShalomAPIClient(api_key="tu-api-key")

# Obtener session token
session = client.authenticate(
    email="tu-email@shalom.com",
    password="tu-contraseña"
)

# Ahora puedes crear órdenes
new_order = client.orders.create(
    origin_terminal_id="LIMACENTRAL",
    destiny_terminal_id="AREQPUERTO",
    product_id="CAJA_PEQUENA",
    sender={
        'nombre': 'Juan Pérez',
        'documento': '12345678',
        'documento_tipo': 'DNI',
        'email': 'juan@example.com',
        'telefono': '987654321'
    },
    receiver={
        'nombre': 'María García',
        'documento': '87654321',
        'documento_tipo': 'DNI',
        'email': 'maria@example.com',
        'telefono': '912345678'
    },
    pickup_code="PICKUP123"
)

# Revocar sesión cuando termines
client.revoke_session()
```

---

## 📚 API Reference

### Tracking

```python
# Buscar envío (al menos uno requerido)
order = client.tracking.search(
    numero="123456",      # Número de guía
    codigo="ABC123",      # Código del envío
    ose_id="NGN01-123"    # ID del sistema
)

# Obtener eventos/milestones
events = client.tracking.get_events(ose_id="NGN01-123")

# Descargar voucher (PDF)
pdf_bytes = client.tracking.get_voucher(ose_id="NGN01-123")
with open('voucher.pdf', 'wb') as f:
    f.write(pdf_bytes)

# Obtener guía de transporte (GRT)
grt_url = client.tracking.get_grt(ose_id="NGN01-123", cap_id="CAP123")
```

### Agencias

```python
# Listar todas las agencias (paginado)
agencies = client.agencies.list(page=1, per_page=100)

# Buscar agencias con filtros
lima_agencies = client.agencies.search(
    departamento="Lima",
    provincia="Lima",
    aereo=False
)

# Obtener detalles de una agencia
agency = client.agencies.get(agency_id=123)
```

### Ubicaciones

```python
# Departamentos del Perú
departments = client.locations.get_departments()

# Provincias de un departamento
provinces = client.locations.get_provinces(dep_id="15")

# Distritos de una provincia
districts = client.locations.get_districts(dep_id="15", prov_id="1501")
```

### Órdenes

```python
# Obtener productos disponibles
products = client.orders.get_products()

# Buscar persona (resolver datos)
person = client.orders.search_person(
    document="12345678",
    doc_type=DocumentType.DNI
)

# Calcular tarifa
tariff = client.orders.calculate_tariff(
    origin_terminal_id="LIMACENTRAL",
    destiny_terminal_id="AREQPUERTO",
    product_id="CAJA_PEQUENA"  # opcional
)

# Crear nueva guía (requiere autenticación)
order = client.orders.create(
    origin_terminal_id="...",
    destiny_terminal_id="...",
    product_id="...",
    sender={...},
    receiver={...},
    pickup_code="..."
)

# Listar todas las órdenes (requiere autenticación)
my_orders = client.orders.list()

# Eliminar orden (requiere autenticación)
deleted = client.orders.delete(order_id="ORD123")

# Descargar etiqueta (PDF)
label = client.orders.get_label(ose_id="NGN01-123")

# Descargar voucher de orden (PDF)
voucher = client.orders.get_voucher(ose_id="NGN01-123")
```

### Health Checks

```python
# ¿Está la API disponible?
is_alive = client.health_check()

# ¿Está lista para tráfico?
is_ready = client.ready_check()
```

---

## 🔗 Integración con FastAPI

### 1. Crear Servicio

```python
# backend/services/shalom_service.py

from fastapi import HTTPException
from shalom_api_client import ShalomAPIClient, ShalomAPIError
import os

class ShalomService:
    def __init__(self):
        self.client = ShalomAPIClient(
            api_key=os.getenv('SHALOM_API_KEY'),
            verbose=False
        )
    
    async def track_order(self, numero: str):
        """Rastrear un envío"""
        try:
            return self.client.tracking.search(numero=numero)
        except ShalomAPIError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def search_agencies(self, departamento: str):
        """Buscar agencias"""
        try:
            return self.client.agencies.search(departamento=departamento)
        except ShalomAPIError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def get_shipping_tariff(self, origin: str, destiny: str):
        """Calcular tarifa"""
        try:
            return self.client.orders.calculate_tariff(
                origin_terminal_id=origin,
                destiny_terminal_id=destiny
            )
        except ShalomAPIError as e:
            raise HTTPException(status_code=400, detail=str(e))

# Instancia global
shalom_service = ShalomService()
```

### 2. Crear Rutas

```python
# backend/routes/shalom_routes.py

from fastapi import APIRouter, Query
from services.shalom_service import shalom_service
from pydantic import BaseModel

router = APIRouter(prefix="/api/shalom", tags=["shalom"])

class TrackingRequest(BaseModel):
    numero: str

class AgencySearchRequest(BaseModel):
    departamento: str
    provincia: str = None

class TariffRequest(BaseModel):
    origin_terminal_id: str
    destiny_terminal_id: str
    product_id: str = None

@router.post("/tracking")
async def track_order(request: TrackingRequest):
    """Rastrear un envío"""
    return await shalom_service.track_order(request.numero)

@router.post("/agencies/search")
async def search_agencies(request: AgencySearchRequest):
    """Buscar agencias"""
    return await shalom_service.search_agencies(
        departamento=request.departamento,
        provincia=request.provincia
    )

@router.post("/tariff")
async def calculate_tariff(request: TariffRequest):
    """Calcular tarifa de envío"""
    return await shalom_service.get_shipping_tariff(
        origin=request.origin_terminal_id,
        destiny=request.destiny_terminal_id
    )

@router.get("/products")
async def get_products():
    """Obtener productos disponibles"""
    return shalom_service.client.orders.get_products()

@router.get("/departments")
async def get_departments():
    """Obtener departamentos"""
    return shalom_service.client.locations.get_departments()
```

### 3. Incluir en FastAPI

```python
# backend/main.py

from fastapi import FastAPI
from routes.shalom_routes import router as shalom_router

app = FastAPI()

# Incluir rutas de Shalom
app.include_router(shalom_router)
```

---

## ⚠️ Manejo de Errores

El cliente usa excepciones específicas:

```python
from shalom_api_client import (
    ShalomAPIError,           # Base para todos los errores
    ShalomAuthError,          # Autenticación fallida
    ShalomRateLimitError,     # Límite de requests excedido
    ShalomNotFoundError,      # Recurso no encontrado
    ShalomValidationError     # Parámetros inválidos
)

try:
    order = client.tracking.search(numero="123456")
except ShalomAuthError:
    print("API Key inválida")
except ShalomNotFoundError:
    print("Envío no encontrado")
except ShalomRateLimitError:
    print("Límite de requests alcanzado - esperar")
except ShalomValidationError:
    print("Parámetros inválidos")
except ShalomAPIError as e:
    print(f"Error de API: {e}")
```

---

## 📖 Ejemplos Completos

Ver archivo `shalom_examples.py` en el mismo directorio.

### Ejecutar Ejemplos

```bash
# Primero, configura tu API_KEY en shalom_examples.py (línea 13)
python3 shalom_examples.py
```

### Ejemplos Incluidos

1. **Tracking** - Rastrear envíos existentes
2. **Agencias** - Listar y buscar agencias
3. **Ubicaciones** - Departamentos, provincias, distritos
4. **Productos y Personas** - Catálogo y búsqueda de datos
5. **Tarifas** - Cálculo de costos de envío
6. **Crear Órdenes** - Crear guías de envío
7. **Gestionar Órdenes** - Listar, descargar, eliminar
8. **Manejo de Errores** - Patrones recomendados

---

## 🔐 Seguridad

### Best Practices

```python
# ❌ NUNCA hardcodees credenciales
api_key = "abc123xyz"  # ¡MAL!

# ✅ USA variables de entorno
import os
api_key = os.getenv('SHALOM_API_KEY')

# ✅ USA .env con python-dotenv
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('SHALOM_API_KEY')
```

### .env Seguro

```bash
# .env (nunca commitear a git)
SHALOM_API_KEY=tu-clave-aqui
SHALOM_EMAIL=email@example.com
SHALOM_PASSWORD=contraseña-aqui
```

```bash
# .gitignore
.env
.env.local
*.key
secrets/
```

---

## 📊 Rate Limiting

El cliente maneja automáticamente:

```python
# Límite: 60 requests por minuto
# Si se excede:
# 1. Calcula tiempo de espera
# 2. Espera transparentemente (con log)
# 3. Reinicia el contador
# 4. Continúa con la request

client = ShalomAPIClient(api_key="...")
for i in range(200):
    # Las primeras 60 se ejecutan inmediatamente
    # Las siguientes esperan ~60 segundos
    # Las siguientes otras 60 esperan otros ~60 segundos
    result = client.agencies.list(per_page=1)
```

---

## 🐛 Debugging

```python
# Habilitar logs detallados
client = ShalomAPIClient(api_key="...", verbose=True)

# Ahora verás:
# DEBUG: GET https://api.shalom-api-peru.com/v1/agencies
# DEBUG: Response status: 200
# INFO: Listando agencias - página 1, 100 por página
```

---

## 📞 Soporte

- **Documentación Shalom**: https://shalom-api-peru.com/docs
- **Base URL**: https://api.shalom-api-peru.com
- **Rate Limit**: 60 requests/minuto

---

## 📝 Changelog

### v1.0 (2026-05-25)
- ✅ Implementación completa de todos los endpoints
- ✅ Autenticación y session tokens
- ✅ Rate limiting automático
- ✅ Reintentos con backoff exponencial
- ✅ Type hints completos
- ✅ Logging detallado
- ✅ Ejemplos y documentación

---

## 📄 Licencia

Parte del proyecto VERDE - Sistema de Ventas HAFESA

---

**Última actualización**: 2026-05-25
