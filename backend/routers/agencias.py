from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
import models, schemas
import os
from datetime import datetime

router = APIRouter(tags=["agencias"])


# ==================== RUTAS ESPECÍFICAS (primero) ====================

# ── Listar agencias (con filtros opcionales) ──────────────────────
@router.get("/list", response_model=List[schemas.AgenciaShalomLista])
def listar_agencias(
    provincia: Optional[str] = Query(None),
    departamento: Optional[str] = Query(None),
    activas: bool = True,
    db: Session = Depends(get_db)
):
    """
    Listar todas las agencias Shalom con filtros opcionales

    Parámetros:
    - provincia: filtrar por provincia (case-insensitive)
    - departamento: filtrar por departamento (case-insensitive)
    - activas: solo agencias activas (default: True)
    """
    query = db.query(models.AgenciaShalom)

    if activas:
        query = query.filter(models.AgenciaShalom.activo == True)

    if provincia:
        query = query.filter(
            models.AgenciaShalom.provincia.ilike(f"%{provincia}%")
        )

    if departamento:
        query = query.filter(
            models.AgenciaShalom.departamento.ilike(f"%{departamento}%")
        )

    return query.order_by(models.AgenciaShalom.lugar).all()


# ── Sincronización: obtener status ─────────────────────────────────
@router.get("/sync/status", tags=["admin"])
def estado_sincronizacion(db: Session = Depends(get_db)):
    """Obtener info de última sincronización y estado actual"""
    ultima = db.query(models.AgenciaShalom).order_by(
        models.AgenciaShalom.sincronizado_at.desc()
    ).first()

    return {
        "ultima_sincronizacion": ultima.sincronizado_at if ultima else None,
        "total_agencias": db.query(models.AgenciaShalom).count(),
        "agencias_activas": db.query(models.AgenciaShalom).filter(
            models.AgenciaShalom.activo == True
        ).count(),
        "agencias_inactivas": db.query(models.AgenciaShalom).filter(
            models.AgenciaShalom.activo == False
        ).count()
    }


# ── Obtener provincias únicas ─────────────────────────────────────
@router.get("/meta/provincias", response_model=List[str])
def obtener_provincias(db: Session = Depends(get_db)):
    """Obtener lista de provincias únicas donde hay agencias"""
    provincias = db.query(
        models.AgenciaShalom.provincia
    ).distinct().filter(
        models.AgenciaShalom.activo == True
    ).all()

    return sorted([p[0] for p in provincias if p[0]])


# ── Obtener departamentos únicos ──────────────────────────────────
@router.get("/meta/departamentos", response_model=List[str])
def obtener_departamentos(db: Session = Depends(get_db)):
    """Obtener lista de departamentos únicos donde hay agencias"""
    departamentos = db.query(
        models.AgenciaShalom.departamento
    ).distinct().filter(
        models.AgenciaShalom.activo == True
    ).all()

    return sorted([d[0] for d in departamentos if d[0]])


# ── Obtener zonas únicas ──────────────────────────────────────────
@router.get("/meta/zonas", response_model=List[str])
def obtener_zonas(db: Session = Depends(get_db)):
    """Obtener lista de zonas únicas donde hay agencias"""
    zonas = db.query(
        models.AgenciaShalom.zona
    ).distinct().filter(
        models.AgenciaShalom.activo == True
    ).all()

    return sorted([z[0] for z in zonas if z[0]])


# ── Estadísticas de agencias ──────────────────────────────────────
@router.get("/meta/stats", response_model=dict)
def obtener_estadisticas(db: Session = Depends(get_db)):
    """Obtener estadísticas de agencias en la BD"""
    total = db.query(models.AgenciaShalom).count()
    activas = db.query(models.AgenciaShalom).filter(
        models.AgenciaShalom.activo == True
    ).count()
    inactivas = total - activas

    # Última sincronización
    ultima_sync = db.query(
        models.AgenciaShalom.sincronizado_at
    ).order_by(
        models.AgenciaShalom.sincronizado_at.desc()
    ).first()

    return {
        "total": total,
        "activas": activas,
        "inactivas": inactivas,
        "ultima_sincronizacion": ultima_sync[0] if ultima_sync and ultima_sync[0] else None
    }


# ── Listar agencias por provincia ─────────────────────────────────
@router.get("/provincia/{provincia}", response_model=List[schemas.AgenciaShalomLista])
def agencias_por_provincia(
    provincia: str,
    db: Session = Depends(get_db)
):
    """Obtener todas las agencias activas de una provincia específica"""
    agencias = db.query(models.AgenciaShalom).filter(
        models.AgenciaShalom.provincia.ilike(f"%{provincia}%"),
        models.AgenciaShalom.activo == True
    ).order_by(models.AgenciaShalom.lugar).all()

    if not agencias:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron agencias en la provincia: {provincia}"
        )

    return agencias


# ── Listar agencias por departamento ──────────────────────────────
@router.get("/departamento/{departamento}", response_model=List[schemas.AgenciaShalomLista])
def agencias_por_departamento(
    departamento: str,
    db: Session = Depends(get_db)
):
    """Obtener todas las agencias activas de un departamento específico"""
    agencias = db.query(models.AgenciaShalom).filter(
        models.AgenciaShalom.departamento.ilike(f"%{departamento}%"),
        models.AgenciaShalom.activo == True
    ).order_by(models.AgenciaShalom.provincia).all()

    if not agencias:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron agencias en el departamento: {departamento}"
        )

    return agencias


# ── Obtener agencia por ter_id (ID de Shalom) ────────────────────
@router.get("/ter/{ter_id}", response_model=schemas.AgenciaShalomDetalle)
def obtener_agencia_por_ter_id(
    ter_id: str,
    db: Session = Depends(get_db)
):
    """Obtener agencia por su ter_id (ID único de Shalom)"""
    agencia = db.query(models.AgenciaShalom).filter(
        models.AgenciaShalom.ter_id == ter_id
    ).first()

    if not agencia:
        raise HTTPException(
            status_code=404,
            detail=f"Agencia con ter_id {ter_id} no encontrada"
        )

    return agencia


# ==================== RUTAS GENÉRICAS (al final) ====================

# ── Sincronización con Shalom API (background task) ────────────────
@router.post("/sync", tags=["admin"])
async def sincronizar_agencias(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Inicia sincronización de agencias desde API Shalom (background)

    Respuesta inmediata, procesa en background.
    Requiere variable de entorno SHALOM_API_KEY configurada.
    """
    def sync_task():
        from shalom_sync_service import AgenciasSyncService
        api_key = os.getenv('SHALOM_API_KEY')
        if not api_key:
            import logging
            logging.error("SHALOM_API_KEY no configurada")
            return

        servicio = AgenciasSyncService(api_key=api_key, verbose=False)
        servicio.sincronizar(db)

    background_tasks.add_task(sync_task)

    return {
        "mensaje": "Sincronización iniciada en background",
        "status": "PROCESANDO"
    }


# ── Obtener detalles de una agencia (ÚLTIMA) ──────────────────────
@router.get("/{agencia_id}", response_model=schemas.AgenciaShalomDetalle)
def obtener_agencia(
    agencia_id: int,
    db: Session = Depends(get_db)
):
    """Obtener detalles completos de una agencia específica"""
    agencia = db.query(models.AgenciaShalom).filter(
        models.AgenciaShalom.id == agencia_id
    ).first()

    if not agencia:
        raise HTTPException(
            status_code=404,
            detail="Agencia no encontrada"
        )

    return agencia
