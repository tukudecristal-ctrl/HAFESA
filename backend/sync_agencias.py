#!/usr/bin/env python3
"""
Script de sincronización manual de agencias Shalom

Uso:
    python sync_agencias.py                    # Sincronización silenciosa
    python sync_agencias.py --verbose          # Con detalles
    python sync_agencias.py --help             # Ayuda

Descripción:
    Obtiene la lista de agencias desde la API de Shalom y sincroniza
    la BD local, detectando: inserciones, actualizaciones y eliminaciones.
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(__file__))

from shalom_sync_service import AgenciasSyncService, main

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sincronizar agencias Shalom con BD local"
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Mostrar detalles de cada operación'
    )

    args = parser.parse_args()

    # Si se especifica --verbose, usar ese flag
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)

    # Ejecutar sincronización
    main()
