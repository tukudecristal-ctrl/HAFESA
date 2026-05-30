# Plan de Integración: Agencias Shalom en VERDE

**Fecha**: 2026-05-29  
**Proyecto**: VERDE (HAFESA)  
**Autor**: Claude Code  
**Estado**: Planificación

---

## 📋 Objetivo General

Integrar completamente el catálogo de agencias de Shalom Courier en el sistema VERDE:
1. Expandir tabla `agencias_destino` con datos completos del CSV
2. Integrar selector en frontend "Nuevo Pedido" → "Agencia Shalom destino"
3. Crear proceso de sincronización automática con API de Shalom (manual por ahora)

---

## 🏗️ Fase 1: Expansión de Tabla de Agencias (Backend)

### Tarea 1.1: Expandir modelo SQLAlchemy
**Archivo**: `backend/models.py`

Reemplazar tabla `AgenciaDestino` simple por modelo completo:

```python
class AgenciaShalom(Base):
    __tablename__ = "agencias_shalom"
    
    # Identificadores
    id = Column(Integer, primary_key=True)
    ter_id = Column(String(20), unique=True, nullable=False)  # ID único de Shalom
    
    # Ubicación
    lugar = Column(String(200), nullable=False)           # ej: "CHACHAPOYAS CO DOS DE MAYO"
    lugar_over = Column(String(200))                       # nombre alternativo
    direccion = Column(String(500), nullable=False)        # dirección completa
    provincia = Column(String(100), nullable=False)
    departamento = Column(String(100), nullable=False)
    zona = Column(String(50))
    ter_zona = Column(String(100))
    
    # Geolocalización
    latitud = Column(Float)
    longitud = Column(Float)
    
    # Contacto
    telefono = Column(String(20))
    
    # Horarios
    hora_atencion = Column(String(100))
    hora_domingo = Column(String(100))
    hora_entrega = Column(String(100))
    hora_entrega_domingo = Column(String(100))
    
    # Estado
    estadoAgencia = Column(String(50))                     # "ATENDIENDO EN ESTE MOMENTO"
    ter_estado_agente = Column(Integer, default=1)
    ter_habilitado_OS = Column(Integer, default=1)
    ter_reparto_habilitado = Column(Integer, default=1)
    ter_principal = Column(Integer, default=1)
    
    # Servicios
    origen = Column(Integer, default=1)
    destino = Column(Integer, default=1)
    ter_aereo = Column(Integer, default=0)
    ter_internacional = Column(Integer, default=0)
    
    # Administración
    activo = Column(Boolean, default=True)
    sincronizado_at = Column(DateTime)                    # última sincronización
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relación con Pedidos
    pedidos = relationship("Pedido", back_populates="agencia")
```

**Cambios en `Pedido`**:
```python
# Cambiar
agencia_id = Column(Integer, ForeignKey("agencias_destino.id"))
agencia = relationship("AgenciaDestino")

# Por
agencia_id = Column(Integer, ForeignKey("agencias_shalom.id"))
agencia = relationship("AgenciaShalom", back_populates="pedidos")
```

---

### Tarea 1.2: Crear migración SQL
**Archivo**: `sql/001_expand_agencias.sql`

```sql
-- Renombrar tabla antigua
ALTER TABLE agencias_destino RENAME TO agencias_destino_legacy;

-- Crear nueva tabla
CREATE TABLE agencias_shalom (
    id SERIAL PRIMARY KEY,
    ter_id VARCHAR(20) UNIQUE NOT NULL,
    lugar VARCHAR(200) NOT NULL,
    lugar_over VARCHAR(200),
    direccion VARCHAR(500) NOT NULL,
    provincia VARCHAR(100) NOT NULL,
    departamento VARCHAR(100) NOT NULL,
    zona VARCHAR(50),
    ter_zona VARCHAR(100),
    latitud FLOAT,
    longitud FLOAT,
    telefono VARCHAR(20),
    hora_atencion VARCHAR(100),
    hora_domingo VARCHAR(100),
    hora_entrega VARCHAR(100),
    hora_entrega_domingo VARCHAR(100),
    estadoAgencia VARCHAR(50),
    ter_estado_agente INTEGER DEFAULT 1,
    ter_habilitado_OS INTEGER DEFAULT 1,
    ter_reparto_habilitado INTEGER DEFAULT 1,
    ter_principal INTEGER DEFAULT 1,
    origen INTEGER DEFAULT 1,
    destino INTEGER DEFAULT 1,
    ter_aereo INTEGER DEFAULT 0,
    ter_internacional INTEGER DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE,
    sincronizado_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Crear índices para búsquedas comunes
CREATE INDEX idx_agencias_provincia ON agencias_shalom(provincia);
CREATE INDEX idx_agencias_departamento ON agencias_shalom(departamento);
CREATE INDEX idx_agencias_ter_id ON agencias_shalom(ter_id);
CREATE INDEX idx_agencias_activo ON agencias_shalom(activo);

-- Actualizar FK en pedidos
ALTER TABLE pedidos 
DROP CONSTRAINT pedidos_agencia_id_fkey,
ADD CONSTRAINT pedidos_agencia_id_fkey 
    FOREIGN KEY (agencia_id) REFERENCES agencias_shalom(id);
```

---

### Tarea 1.3: Crear Schema Pydantic
**Archivo**: `backend/schemas.py` (agregar)

```python
class AgenciaShalomlista(BaseModel):
    ter_id: str
    lugar: str
    lugar_over: Optional[str]
    direccion: str
    provincia: str
    departamento: str
    telefono: Optional[str]
    hora_atencion: Optional[str]
    latitud: Optional[float]
    longitud: Optional[float]
    activo: bool

    class Config:
        from_attributes = True

class AgenciaShalomDetalle(AgenciaShalomlista):
    id: int
    zona: Optional[str]
    ter_zona: Optional[str]
    hora_domingo: Optional[str]
    estadoAgencia: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    sincronizado_at: Optional[datetime]
```

---

## 🎨 Fase 2: Integración Frontend (Selector en Nuevo Pedido)

### Tarea 2.1: Crear endpoint API para agencias
**Archivo**: `backend/routes/agencias_routes.py` (nuevo)

```python
from fastapi import APIRouter, Depends, Query
from database import get_db
from models import AgenciaShalom
from schemas import AgenciaShalomlista

router = APIRouter(prefix="/api/agencias", tags=["agencias"])

@router.get("/list", response_model=List[AgenciaShalomlista])
async def listar_agencias(
    provincia: Optional[str] = Query(None),
    departamento: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Listar agencias filtrables por provincia/departamento"""
    query = db.query(AgenciaShalom).filter(AgenciaShalom.activo == True)
    
    if provincia:
        query = query.filter(AgenciaShalom.provincia.ilike(f"%{provincia}%"))
    if departamento:
        query = query.filter(AgenciaShalom.departamento.ilike(f"%{departamento}%"))
    
    return query.all()

@router.get("/provincia/{provincia}", response_model=List[AgenciaShalomlista])
async def agencias_por_provincia(provincia: str, db: Session = Depends(get_db)):
    """Obtener todas las agencias de una provincia"""
    return db.query(AgenciaShalom).filter(
        AgenciaShalom.provincia.ilike(f"%{provincia}%"),
        AgenciaShalom.activo == True
    ).all()

@router.get("/{agencia_id}", response_model=AgenciaShalomDetalle)
async def obtener_agencia(agencia_id: int, db: Session = Depends(get_db)):
    """Obtener detalles completos de una agencia"""
    agencia = db.query(AgenciaShalom).filter(AgenciaShalom.id == agencia_id).first()
    if not agencia:
        raise HTTPException(status_code=404, detail="Agencia no encontrada")
    return agencia
```

Incluir en `backend/main.py`:
```python
from routes.agencias_routes import router as agencias_router
app.include_router(agencias_router)
```

---

### Tarea 2.2: Actualizar componente Vue en formulario_pedido.html
**Archivo**: `frontend/formulario_pedido.html`

Modificar sección de selector de agencia:

```html
<!-- Sección ENVÍO -->
<div class="section-title">Envío y Destino</div>

<div class="form-group">
  <label for="agencia">Agencia Shalom Destino <span class="req">*</span></label>
  
  <!-- Selector de Provincia (opcional para filtrar) -->
  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-bottom: 0.5rem;">
    <select v-model="filtro_provincia" @change="cargarAgencias">
      <option value="">--- Todas las provincias ---</option>
      <option v-for="prov in provincias" :key="prov" :value="prov">
        {{ prov }}
      </option>
    </select>
  </div>
  
  <!-- Selector Principal de Agencia -->
  <select v-model="pedido.agencia_id" @change="actualizarAgenciaSeleccionada" required>
    <option value="">--- Seleccionar Agencia ---</option>
    <option v-for="agencia in agencias_filtradas" :key="agencia.id" :value="agencia.id">
      {{ agencia.direccion }} ({{ agencia.provincia }}, {{ agencia.departamento }})
    </option>
  </select>
  
  <!-- Mostrar detalles de agencia seleccionada -->
  <div v-if="agencia_seleccionada" style="margin-top: 0.8rem; padding: 0.8rem; background: #f7fafc; border-radius: 6px; font-size: 0.85rem;">
    <div><strong>Lugar:</strong> {{ agencia_seleccionada.lugar }}</div>
    <div><strong>Dirección:</strong> {{ agencia_seleccionada.direccion }}</div>
    <div><strong>Provincia:</strong> {{ agencia_seleccionada.provincia }}</div>
    <div><strong>Departamento:</strong> {{ agencia_seleccionada.departamento }}</div>
    <div v-if="agencia_seleccionada.telefono"><strong>Teléfono:</strong> {{ agencia_seleccionada.telefono }}</div>
    <div v-if="agencia_seleccionada.hora_atencion"><strong>Horario:</strong> {{ agencia_seleccionada.hora_atencion }}</div>
  </div>
</div>
```

Agregar en script Vue:

```javascript
data() {
  return {
    // ... datos existentes
    agencias: [],
    provincias: [],
    filtro_provincia: "",
    agencia_seleccionada: null,
    pedido: {
      // ... campos existentes
      agencia_id: null,  // GUARDAR EL ID DE LA AGENCIA
    }
  }
},
computed: {
  agencias_filtradas() {
    if (!this.filtro_provincia) return this.agencias;
    return this.agencias.filter(a => a.provincia === this.filtro_provincia);
  }
},
methods: {
  async cargarAgencias() {
    try {
      const url = this.filtro_provincia
        ? `/api/agencias/provincia/${encodeURIComponent(this.filtro_provincia)}`
        : '/api/agencias/list';
      const res = await fetch(url);
      this.agencias = await res.json();
    } catch (e) {
      console.error("Error cargando agencias:", e);
      alert("Error al cargar agencias");
    }
  },
  async cargarProvincias() {
    // Extraer provincias únicas de agencias cargadas
    const url = '/api/agencias/list';
    const res = await fetch(url);
    const todas = await res.json();
    this.provincias = [...new Set(todas.map(a => a.provincia))].sort();
  },
  async actualizarAgenciaSeleccionada() {
    if (!this.pedido.agencia_id) {
      this.agencia_seleccionada = null;
      return;
    }
    const agencia = this.agencias.find(a => a.id === parseInt(this.pedido.agencia_id));
    this.agencia_seleccionada = agencia || null;
  },
  // En mounted()
  async mounted() {
    // ... código existente
    await this.cargarAgencias();
    await this.cargarProvincias();
  }
}
```

---

## 🔄 Fase 3: Sincronización con API Shalom

### Tarea 3.1: Crear servicio de sincronización
**Archivo**: `backend/shalom_sync_service.py` (nuevo)

```python
#!/usr/bin/env python3
"""
Servicio de Sincronización de Agencias Shalom
==============================================

Obtiene lista de agencias desde API de Shalom y sincroniza con BD local.
Maneja inserciones, actualizaciones y eliminaciones de agencias.

Uso:
    python shalom_sync_service.py [--verbose]
"""

import logging
from datetime import datetime
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from shalom_api_client import ShalomAPIClient
from models import AgenciaShalom
from database import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgenciasSyncService:
    """Servicio de sincronización bidireccional de agencias"""
    
    def __init__(self, api_key: str, verbose: bool = False):
        self.client = ShalomAPIClient(api_key=api_key)
        self.verbose = verbose
        self.stats = {
            'insertadas': 0,
            'actualizadas': 0,
            'eliminadas': 0,
            'errores': 0
        }
    
    def obtener_agencias_shalom(self) -> List[Dict[str, Any]]:
        """Obtiene lista completa de agencias desde API Shalom"""
        try:
            logger.info("Obteniendo agencias desde API Shalom...")
            agencias = self.client.agencies.list(per_page=1000)
            logger.info(f"✓ Obtenidas {len(agencias)} agencias")
            return agencias
        except Exception as e:
            logger.error(f"✗ Error obteniendo agencias: {e}")
            raise
    
    def sincronizar(self, db: Session):
        """Sincroniza agencias: inserta, actualiza, elimina"""
        try:
            agencias_api = self.obtener_agencias_shalom()
            
            # Obtener agencias actuales de BD
            agencias_bd = db.query(AgenciaShalom).all()
            ter_ids_bd = {a.ter_id for a in agencias_bd}
            ter_ids_api = {a.get('ter_id') for a in agencias_api}
            
            # 1. INSERCIONES (nuevas en API)
            self._insertar_nuevas(db, agencias_api, ter_ids_bd)
            
            # 2. ACTUALIZACIONES (existen en ambas)
            self._actualizar_existentes(db, agencias_api, agencias_bd)
            
            # 3. ELIMINACIONES (solo en BD, marcadas como inactivas)
            self._marcar_eliminadas(db, ter_ids_bd, ter_ids_api)
            
            # Guardar cambios
            db.commit()
            
            self._imprimir_reporte()
            return self.stats
        
        except Exception as e:
            db.rollback()
            logger.error(f"✗ Error en sincronización: {e}")
            raise
    
    def _insertar_nuevas(self, db: Session, agencias_api: List[Dict], ter_ids_bd: set):
        """Inserta agencias nuevas desde API"""
        for agencia in agencias_api:
            ter_id = agencia.get('ter_id')
            
            if ter_id not in ter_ids_bd:
                try:
                    nueva = AgenciaShalom(
                        ter_id=ter_id,
                        lugar=agencia.get('lugar_over', agencia.get('lugar', 'N/A')),
                        lugar_over=agencia.get('lugar_over'),
                        direccion=agencia.get('direccion', ''),
                        provincia=agencia.get('provincia', ''),
                        departamento=agencia.get('departamento', ''),
                        zona=agencia.get('zona'),
                        ter_zona=agencia.get('ter_zona'),
                        latitud=float(agencia.get('latitud', 0)) if agencia.get('latitud') else None,
                        longitud=float(agencia.get('longitud', 0)) if agencia.get('longitud') else None,
                        telefono=agencia.get('telefono'),
                        hora_atencion=agencia.get('hora_atencion'),
                        hora_domingo=agencia.get('hora_domingo'),
                        hora_entrega=agencia.get('hora_entrega'),
                        hora_entrega_domingo=agencia.get('hora_entrega_domingo'),
                        estadoAgencia=agencia.get('estadoAgencia'),
                        ter_estado_agente=int(agencia.get('ter_estado_agente', 1)),
                        ter_habilitado_OS=int(agencia.get('ter_habilitado_OS', 1)),
                        ter_reparto_habilitado=int(agencia.get('ter_reparto_habilitado', 1)),
                        ter_principal=int(agencia.get('ter_principal', 1)),
                        origen=int(agencia.get('origen', 1)),
                        destino=int(agencia.get('destino', 1)),
                        ter_aereo=int(agencia.get('ter_aereo', 0)),
                        ter_internacional=int(agencia.get('ter_internacional', 0)),
                        activo=True,
                        sincronizado_at=datetime.now()
                    )
                    db.add(nueva)
                    self.stats['insertadas'] += 1
                    
                    if self.verbose:
                        logger.info(f"  + Insertada: {ter_id} - {agencia.get('lugar')}")
                
                except Exception as e:
                    logger.error(f"  ✗ Error insertando {ter_id}: {e}")
                    self.stats['errores'] += 1
    
    def _actualizar_existentes(self, db: Session, agencias_api: List[Dict], agencias_bd: List[AgenciaShalom]):
        """Actualiza agencias que existen en ambas fuentes"""
        for agencia_bd in agencias_bd:
            agencia_api = next(
                (a for a in agencias_api if a.get('ter_id') == agencia_bd.ter_id),
                None
            )
            
            if not agencia_api:
                continue
            
            try:
                # Campos que se actualizan
                campos_actualizables = [
                    'lugar', 'direccion', 'provincia', 'departamento',
                    'telefono', 'hora_atencion', 'hora_domingo',
                    'estadoAgencia', 'ter_estado_agente', 'ter_habilitado_OS'
                ]
                
                cambio = False
                for campo in campos_actualizables:
                    nuevo_valor = agencia_api.get(campo)
                    valor_actual = getattr(agencia_bd, campo, None)
                    
                    if nuevo_valor and valor_actual != nuevo_valor:
                        setattr(agencia_bd, campo, nuevo_valor)
                        cambio = True
                
                if cambio:
                    agencia_bd.sincronizado_at = datetime.now()
                    agencia_bd.activo = True
                    self.stats['actualizadas'] += 1
                    
                    if self.verbose:
                        logger.info(f"  ↻ Actualizada: {agencia_bd.ter_id}")
            
            except Exception as e:
                logger.error(f"  ✗ Error actualizando {agencia_bd.ter_id}: {e}")
                self.stats['errores'] += 1
    
    def _marcar_eliminadas(self, db: Session, ter_ids_bd: set, ter_ids_api: set):
        """Marca como inactivas agencias que ya no están en API"""
        ids_eliminadas = ter_ids_bd - ter_ids_api
        
        if ids_eliminadas:
            eliminadas = db.query(AgenciaShalom).filter(
                AgenciaShalom.ter_id.in_(ids_eliminadas)
            ).update({'activo': False})
            
            self.stats['eliminadas'] = eliminadas
            logger.info(f"✓ Marcadas {eliminadas} agencias como inactivas")
    
    def _imprimir_reporte(self):
        """Imprime reporte final de sincronización"""
        print("\n" + "="*60)
        print("REPORTE DE SINCRONIZACIÓN DE AGENCIAS SHALOM")
        print("="*60)
        print(f"✓ Insertadas:   {self.stats['insertadas']}")
        print(f"↻ Actualizadas: {self.stats['actualizadas']}")
        print(f"✗ Eliminadas:   {self.stats['eliminadas']}")
        print(f"⚠  Errores:     {self.stats['errores']}")
        print("="*60 + "\n")


def main():
    """Función principal para ejecutar manualmente"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    api_key = os.getenv('SHALOM_API_KEY')
    if not api_key:
        raise ValueError("SHALOM_API_KEY no configurada en variables de entorno")
    
    db = SessionLocal()
    
    try:
        servicio = AgenciasSyncService(api_key=api_key, verbose=True)
        servicio.sincronizar(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
```

---

### Tarea 3.2: Script ejecutable para sincronización
**Archivo**: `backend/sync_agencias.py` (nuevo, alias ejecutable)

```bash
#!/usr/bin/env python3
"""
Script de sincronización manual de agencias Shalom
Uso: python sync_agencias.py [--verbose]
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from shalom_sync_service import main

if __name__ == "__main__":
    main()
```

Hacer ejecutable:
```bash
chmod +x backend/sync_agencias.py
```

---

### Tarea 3.3: Endpoint FastAPI para sincronización manual
**Archivo**: `backend/routes/agencias_routes.py` (agregar)

```python
from shalom_sync_service import AgenciasSyncService
from fastapi import BackgroundTasks

@router.post("/sync", tags=["admin"])
async def sincronizar_agencias(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)  # Solo admins
):
    """
    Inicia sincronización de agencias desde API Shalom (background)
    Respuesta inmediata, procesa en background
    """
    def sync_task():
        api_key = os.getenv('SHALOM_API_KEY')
        servicio = AgenciasSyncService(api_key=api_key, verbose=True)
        servicio.sincronizar(db)
    
    background_tasks.add_task(sync_task)
    
    return {
        "mensaje": "Sincronización iniciada en background",
        "status": "PROCESANDO"
    }

@router.get("/sync/status", tags=["admin"])
async def estado_sincronizacion(db: Session = Depends(get_db)):
    """Obtiene info de última sincronización"""
    ultima = db.query(AgenciaShalom).order_by(
        AgenciaShalom.sincronizado_at.desc()
    ).first()
    
    return {
        "ultima_sincronizacion": ultima.sincronizado_at if ultima else None,
        "total_agencias": db.query(AgenciaShalom).count(),
        "agencias_activas": db.query(AgenciaShalom).filter(
            AgenciaShalom.activo == True
        ).count()
    }
```

---

## 📦 Fase 4: Carga Inicial de Datos CSV

### Tarea 4.1: Script de importación desde CSV
**Archivo**: `backend/import_csv_agencias.py` (nuevo)

```python
#!/usr/bin/env python3
"""
Script para importar agencias desde CSV local (agencias_shalom.csv)
Uso: python import_csv_agencias.py [archivo.csv]
"""

import csv
from datetime import datetime
from sqlalchemy.orm import Session
from models import AgenciaShalom
from database import SessionLocal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def importar_csv(archivo_csv: str):
    """Importa agencias desde archivo CSV"""
    db = SessionLocal()
    contador = 0
    errores = 0
    
    try:
        with open(archivo_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for fila in reader:
                try:
                    ter_id = fila.get('ter_id', '').strip()
                    
                    if not ter_id:
                        logger.warning(f"Fila sin ter_id, saltando")
                        continue
                    
                    # Verificar si ya existe
                    existe = db.query(AgenciaShalom).filter(
                        AgenciaShalom.ter_id == ter_id
                    ).first()
                    
                    if existe:
                        logger.info(f"  ⊘ {ter_id} ya existe, actualizando...")
                        # Actualizar campos relevantes
                        existe.direccion = fila.get('direccion', existe.direccion)
                        existe.provincia = fila.get('provincia', existe.provincia)
                        existe.departamento = fila.get('departamento', existe.departamento)
                        existe.telefono = fila.get('telefono')
                        existe.hora_atencion = fila.get('hora_atencion')
                        existe.sincronizado_at = datetime.now()
                        contador += 1
                    else:
                        # Insertar nueva
                        nueva_agencia = AgenciaShalom(
                            ter_id=ter_id,
                            lugar=fila.get('lugar_over', fila.get('lugar', 'N/A')),
                            lugar_over=fila.get('lugar_over'),
                            direccion=fila.get('direccion', ''),
                            provincia=fila.get('provincia', ''),
                            departamento=fila.get('departamento', ''),
                            zona=fila.get('zona'),
                            ter_zona=fila.get('ter_zona'),
                            latitud=_to_float(fila.get('latitud')),
                            longitud=_to_float(fila.get('longitud')),
                            telefono=fila.get('telefono'),
                            hora_atencion=fila.get('hora_atencion'),
                            hora_domingo=fila.get('hora_domingo'),
                            estadoAgencia=fila.get('estadoAgencia'),
                            ter_estado_agente=_to_int(fila.get('ter_estado_agente', 1)),
                            ter_habilitado_OS=_to_int(fila.get('ter_habilitado_OS', 1)),
                            ter_principal=_to_int(fila.get('ter_principal', 1)),
                            activo=True,
                            sincronizado_at=datetime.now()
                        )
                        db.add(nueva_agencia)
                        contador += 1
                        
                        if contador % 10 == 0:
                            logger.info(f"  + Procesadas {contador} agencias...")
                
                except Exception as e:
                    logger.error(f"  ✗ Error procesando fila: {e}")
                    errores += 1
        
        # Guardar cambios
        db.commit()
        
        print(f"\n{'='*60}")
        print(f"IMPORTACIÓN COMPLETADA")
        print(f"{'='*60}")
        print(f"✓ Procesadas: {contador}")
        print(f"✗ Errores:    {errores}")
        print(f"{'='*60}\n")
    
    except FileNotFoundError:
        logger.error(f"Archivo no encontrado: {archivo_csv}")
    finally:
        db.close()


def _to_float(valor):
    try:
        return float(valor) if valor else None
    except:
        return None

def _to_int(valor):
    try:
        return int(valor) if valor else 0
    except:
        return 0


if __name__ == "__main__":
    import sys
    
    archivo = sys.argv[1] if len(sys.argv) > 1 else "agencias_shalom.csv"
    importar_csv(archivo)
```

Ejecutar: `python backend/import_csv_agencias.py ../agencias_shalom.csv`

---

## 📋 Resumen de Archivos a Crear/Modificar

| Archivo | Tipo | Descripción |
|---------|------|-------------|
| `backend/models.py` | MOD | Expandir `AgenciaShalom` + relación con Pedidos |
| `backend/schemas.py` | MOD | Agregar schemas Pydantic para agencias |
| `backend/routes/agencias_routes.py` | NEW | Endpoints API de agencias |
| `backend/shalom_sync_service.py` | NEW | Servicio de sincronización |
| `backend/sync_agencias.py` | NEW | Script ejecutable de sincronización |
| `backend/import_csv_agencias.py` | NEW | Importador de CSV |
| `frontend/formulario_pedido.html` | MOD | Selector Vue.js de agencias |
| `sql/001_expand_agencias.sql` | NEW | Migración de BD |

---

## 🚀 Orden de Ejecución Recomendado

1. **Modelo Backend** (Tarea 1.1)
2. **Migración SQL** (Tarea 1.2) 
3. **Schemas Pydantic** (Tarea 1.3)
4. **Importar CSV** (Tarea 4.1) → `python backend/import_csv_agencias.py ../agencias_shalom.csv`
5. **Endpoints API** (Tarea 2.1)
6. **Frontend Vue.js** (Tarea 2.2)
7. **Servicio Sincronización** (Tarea 3.1, 3.2, 3.3)
8. **Testing manual** → /nuevo-pedido → Seleccionar agencia

---

## 🧪 Testing

### Test 1: Cargar datos iniciales
```bash
python backend/import_csv_agencias.py ../agencias_shalom.csv
# Verificar: SELECT COUNT(*) FROM agencias_shalom;
```

### Test 2: API endpoints
```bash
curl http://localhost:8000/api/agencias/list
curl "http://localhost:8000/api/agencias/list?provincia=LIMA"
curl http://localhost:8000/api/agencias/1
```

### Test 3: Frontend
1. Abrir http://localhost:3000/formulario_pedido.html
2. Seleccionar provincia (debe filtrar agencias)
3. Seleccionar agencia (debe mostrar detalles)
4. Crear pedido (debe guardar agencia_id en BD)

### Test 4: Sincronización
```bash
# Manual
python backend/sync_agencias.py --verbose

# Vía API
curl -X POST http://localhost:8000/api/agencias/sync -H "Authorization: Bearer TOKEN_ADMIN"
```

---

## 📝 Notas Importantes

1. **Preservar compatibilidad**: Tabla antigua se renombra a `agencias_destino_legacy` para referencia histórica
2. **API Key Shalom**: Debe estar en `.env.shalom` con clave `SHALOM_API_KEY`
3. **Índices de BD**: Se crean en migración para optimizar búsquedas por provincia/departamento
4. **Sincronización incremental**: Identifica cambios por `ter_id` (ID único de Shalom)
5. **Permisos**: El endpoint `/api/agencias/sync` requiere rol ADMIN

---

**Fin del Plan**  
Última actualización: 2026-05-29

