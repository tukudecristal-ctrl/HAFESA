#!/usr/bin/env python3
"""
Script para importar agencias desde CSV local (agencias_shalom.csv)
Uso: python import_csv_agencias.py [archivo.csv]
"""

import sys
import os
import csv
from datetime import datetime

# Asegura que el directorio backend esté en el path
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from models import AgenciaShalom
from database import SessionLocal

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _to_float(valor):
    """Convierte valor a float de forma segura"""
    try:
        return float(valor) if valor and str(valor).strip() else None
    except (ValueError, TypeError):
        return None


def _to_int(valor, default=0):
    """Convierte valor a int de forma segura"""
    try:
        return int(valor) if valor and str(valor).strip() else default
    except (ValueError, TypeError):
        return default


def importar_csv(archivo_csv: str):
    """Importa agencias desde archivo CSV"""
    db = SessionLocal()
    contador = 0
    errores = 0

    try:
        # Verificar que el archivo existe
        if not os.path.exists(archivo_csv):
            logger.error(f"✗ Archivo no encontrado: {archivo_csv}")
            return

        with open(archivo_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            logger.info(f"📂 Leyendo archivo: {archivo_csv}")
            logger.info("Procesando agencias...\n")

            for idx, fila in enumerate(reader, 1):
                try:
                    ter_id = fila.get('ter_id', '').strip()

                    if not ter_id:
                        logger.warning(f"  ⊘ Fila {idx}: sin ter_id, saltando")
                        continue

                    # Verificar si ya existe
                    existe = db.query(AgenciaShalom).filter(
                        AgenciaShalom.ter_id == ter_id
                    ).first()

                    if existe:
                        # Actualizar campos relevantes
                        existe.direccion = fila.get('direccion', existe.direccion)
                        existe.provincia = fila.get('provincia', existe.provincia)
                        existe.departamento = fila.get('departamento', existe.departamento)
                        existe.telefono = fila.get('telefono')
                        existe.hora_atencion = fila.get('hora_atencion')
                        existe.hora_domingo = fila.get('hora_domingo')
                        existe.latitud = _to_float(fila.get('latitud'))
                        existe.longitud = _to_float(fila.get('longitud'))
                        existe.estadoAgencia = fila.get('estadoAgencia')
                        existe.sincronizado_at = datetime.now()
                        contador += 1

                        if idx % 50 == 0:
                            logger.info(f"  ↻ Actualizadas {contador} agencias...")
                    else:
                        # Insertar nueva agencia
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
                            hora_entrega=fila.get('hora_entrega'),
                            hora_entrega_domingo=fila.get('hora_entrega_domingo'),
                            estado_agencia=fila.get('estadoAgencia'),
                            ter_estado_agente=_to_int(fila.get('ter_estado_agente', 1)),
                            ter_habilitado_os=_to_int(fila.get('ter_habilitado_OS', 1)),
                            ter_reparto_habilitado=_to_int(fila.get('ter_reparto_habilitado', 1)),
                            ter_principal=_to_int(fila.get('ter_principal', 1)),
                            origen=_to_int(fila.get('origen', 1)),
                            destino=_to_int(fila.get('destino', 1)),
                            ter_aereo=_to_int(fila.get('ter_aereo', 0)),
                            ter_internacional=_to_int(fila.get('ter_internacional', 0)),
                            activo=True,
                            sincronizado_at=datetime.now()
                        )
                        db.add(nueva_agencia)
                        contador += 1

                        if idx % 50 == 0:
                            logger.info(f"  + Procesadas {contador} agencias...")

                except Exception as e:
                    logger.error(f"  ✗ Error en fila {idx}: {e}")
                    errores += 1

        # Guardar cambios
        db.commit()

        # Imprimir reporte final
        print("\n" + "="*60)
        print("IMPORTACIÓN COMPLETADA")
        print("="*60)
        print(f"✓ Procesadas: {contador}")
        print(f"✗ Errores:    {errores}")
        print("="*60 + "\n")

        # Mostrar información adicional
        total_bd = db.query(AgenciaShalom).count()
        total_activas = db.query(AgenciaShalom).filter(
            AgenciaShalom.activo == True
        ).count()

        print(f"📊 Estado de BD:")
        print(f"   Total agencias: {total_bd}")
        print(f"   Activas:        {total_activas}")
        print()

    except FileNotFoundError:
        logger.error(f"✗ Archivo no encontrado: {archivo_csv}")
    except Exception as e:
        db.rollback()
        logger.error(f"✗ Error general: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    archivo = sys.argv[1] if len(sys.argv) > 1 else "../agencias_shalom.csv"
    importar_csv(archivo)
