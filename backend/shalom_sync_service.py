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
from typing import List, Dict, Any, Optional

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
            logger.info("📡 Obteniendo agencias desde API Shalom...")
            # Usar el cliente para obtener agencias con paginación
            agencias = self.client.agencies.list(per_page=1000)
            logger.info(f"✓ Obtenidas {len(agencias)} agencias")
            return agencias if agencias else []
        except Exception as e:
            logger.error(f"✗ Error obteniendo agencias: {e}")
            raise

    def sincronizar(self, db: Session):
        """Sincroniza agencias: inserta, actualiza, elimina"""
        try:
            agencias_api = self.obtener_agencias_shalom()

            if not agencias_api:
                logger.warning("⚠ No se obtuvieron agencias de la API")
                return self.stats

            # Obtener agencias actuales de BD
            agencias_bd = db.query(AgenciaShalom).all()
            ter_ids_bd = {a.ter_id for a in agencias_bd}
            ter_ids_api = {a.get('ter_id') for a in agencias_api if a.get('ter_id')}

            logger.info(f"📊 Estado: {len(agencias_bd)} en BD, {len(agencias_api)} en API")

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
        logger.info("➕ Procesando inserciones...")

        for agencia in agencias_api:
            ter_id = agencia.get('ter_id')

            if not ter_id or ter_id in ter_ids_bd:
                continue

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
                    latitud=self._to_float(agencia.get('latitud')),
                    longitud=self._to_float(agencia.get('longitud')),
                    telefono=agencia.get('telefono'),
                    hora_atencion=agencia.get('hora_atencion'),
                    hora_domingo=agencia.get('hora_domingo'),
                    hora_entrega=agencia.get('hora_entrega'),
                    hora_entrega_domingo=agencia.get('hora_entrega_domingo'),
                    estadoAgencia=agencia.get('estadoAgencia'),
                    ter_estado_agente=self._to_int(agencia.get('ter_estado_agente', 1)),
                    ter_habilitado_OS=self._to_int(agencia.get('ter_habilitado_OS', 1)),
                    ter_reparto_habilitado=self._to_int(agencia.get('ter_reparto_habilitado', 1)),
                    ter_principal=self._to_int(agencia.get('ter_principal', 1)),
                    origen=self._to_int(agencia.get('origen', 1)),
                    destino=self._to_int(agencia.get('destino', 1)),
                    ter_aereo=self._to_int(agencia.get('ter_aereo', 0)),
                    ter_internacional=self._to_int(agencia.get('ter_internacional', 0)),
                    activo=True,
                    sincronizado_at=datetime.now()
                )
                db.add(nueva)
                self.stats['insertadas'] += 1

                if self.verbose:
                    logger.info(f"  ✓ {ter_id}: {agencia.get('lugar')}")

            except Exception as e:
                logger.error(f"  ✗ Error en {ter_id}: {e}")
                self.stats['errores'] += 1

    def _actualizar_existentes(self, db: Session, agencias_api: List[Dict], agencias_bd: List[AgenciaShalom]):
        """Actualiza agencias que existen en ambas fuentes"""
        logger.info("↻ Procesando actualizaciones...")

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
                    'lugar', 'lugar_over', 'direccion', 'provincia', 'departamento',
                    'zona', 'ter_zona', 'telefono', 'hora_atencion', 'hora_domingo',
                    'hora_entrega', 'hora_entrega_domingo', 'estadoAgencia',
                    'ter_estado_agente', 'ter_habilitado_OS', 'ter_principal'
                ]

                cambio = False
                for campo in campos_actualizables:
                    nuevo_valor = agencia_api.get(campo)
                    valor_actual = getattr(agencia_bd, campo, None)

                    if nuevo_valor and valor_actual != nuevo_valor:
                        setattr(agencia_bd, campo, nuevo_valor)
                        cambio = True

                # Actualizar coordenadas si existen
                nueva_lat = self._to_float(agencia_api.get('latitud'))
                nueva_long = self._to_float(agencia_api.get('longitud'))
                if nueva_lat and agencia_bd.latitud != nueva_lat:
                    agencia_bd.latitud = nueva_lat
                    cambio = True
                if nueva_long and agencia_bd.longitud != nueva_long:
                    agencia_bd.longitud = nueva_long
                    cambio = True

                if cambio:
                    agencia_bd.sincronizado_at = datetime.now()
                    agencia_bd.activo = True
                    self.stats['actualizadas'] += 1

                    if self.verbose:
                        logger.info(f"  ↻ {agencia_bd.ter_id}")

            except Exception as e:
                logger.error(f"  ✗ Error actualizando {agencia_bd.ter_id}: {e}")
                self.stats['errores'] += 1

    def _marcar_eliminadas(self, db: Session, ter_ids_bd: set, ter_ids_api: set):
        """Marca como inactivas agencias que ya no están en API"""
        ids_eliminadas = ter_ids_bd - ter_ids_api

        if ids_eliminadas:
            logger.info("🗑  Procesando eliminaciones...")
            eliminadas = db.query(AgenciaShalom).filter(
                AgenciaShalom.ter_id.in_(ids_eliminadas)
            ).update({'activo': False})

            self.stats['eliminadas'] = eliminadas
            logger.info(f"  ✓ Marcadas {eliminadas} agencias como inactivas")

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

    @staticmethod
    def _to_float(valor) -> Optional[float]:
        """Convierte valor a float de forma segura"""
        try:
            return float(valor) if valor and str(valor).strip() else None
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _to_int(valor, default=0) -> int:
        """Convierte valor a int de forma segura"""
        try:
            return int(valor) if valor and str(valor).strip() else default
        except (ValueError, TypeError):
            return default


def main():
    """Función principal para ejecutar manualmente"""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.getenv('SHALOM_API_KEY')
    if not api_key:
        logger.error("✗ SHALOM_API_KEY no configurada en variables de entorno")
        raise ValueError("SHALOM_API_KEY no configurada")

    db = SessionLocal()

    try:
        servicio = AgenciasSyncService(api_key=api_key, verbose=True)
        servicio.sincronizar(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
