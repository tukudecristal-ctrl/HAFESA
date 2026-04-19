#!/bin/bash

set -e

echo "=== Deploy Local — VERDE ==="

# 1. Verificar PostgreSQL
echo "Verificando PostgreSQL..."
if ! pg_isready -q; then
    echo "PostgreSQL no está activo. Iniciando..."
    sudo systemctl start postgresql
    sleep 2
    if ! pg_isready -q; then
        echo "ERROR: No se pudo iniciar PostgreSQL."
        exit 1
    fi
fi
echo "PostgreSQL OK"

# 2. Activar environment
echo "Activando environment..."
source /home/darh/trabajo/env_pytuku/bin/activate
echo "Environment OK: $(which python3)"

# 3. Levantar Uvicorn
echo "Levantando servidor en http://0.0.0.0:8000 ..."
cd "$(dirname "$0")/backend"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
