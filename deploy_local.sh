#!/bin/bash

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║          🚀 Deploy Local — VERDE (HAFESA)                 ║"
echo "║              Backend + Frontend                            ║"
echo "╚════════════════════════════════════════════════════════════╝"

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
VENV_DIR="$PROJECT_DIR/.venv"

# Archivo PID para detener servicios
BACKEND_PID_FILE="/tmp/verde_backend.pid"
FRONTEND_PID_FILE="/tmp/verde_frontend.pid"

# ════════════════════════════════════════════════════════════════
# 1. VERIFICAR POSTGRESQL
# ════════════════════════════════════════════════════════════════
echo -e "\n${BLUE}[1/5]${NC} Verificando PostgreSQL..."
if ! pg_isready -q -h localhost; then
    echo -e "${YELLOW}⏳ PostgreSQL no está activo. Iniciando...${NC}"
    if ! sudo systemctl start postgresql 2>/dev/null; then
        echo -e "${RED}✗ No se pudo iniciar PostgreSQL${NC}"
        exit 1
    fi
    sleep 2
    if ! pg_isready -q -h localhost; then
        echo -e "${RED}✗ PostgreSQL sigue sin responder${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}✓ PostgreSQL activo${NC}"

# ════════════════════════════════════════════════════════════════
# 2. ACTIVAR VIRTUAL ENVIRONMENT
# ════════════════════════════════════════════════════════════════
echo -e "\n${BLUE}[2/5]${NC} Activando virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${RED}✗ Virtual environment no encontrado en $VENV_DIR${NC}"
    exit 1
fi
source "$VENV_DIR/bin/activate"
echo -e "${GREEN}✓ Entorno activo: $(which python3)${NC}"

# ════════════════════════════════════════════════════════════════
# 3. LIMPIAR PROCESOS PREVIOS
# ════════════════════════════════════════════════════════════════
echo -e "\n${BLUE}[3/5]${NC} Limpiando procesos previos..."

# Matar por puerto si existen
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⏳ Deteniendo backend anterior (puerto 8000)...${NC}"
    lsof -i :8000 -t | xargs kill -9 2>/dev/null || true
    sleep 1
fi

if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⏳ Deteniendo frontend anterior (puerto 3000)...${NC}"
    lsof -i :3000 -t | xargs kill -9 2>/dev/null || true
    sleep 1
fi

# Limpiar archivos PID antiguos
rm -f "$BACKEND_PID_FILE" "$FRONTEND_PID_FILE"
echo -e "${GREEN}✓ Procesos limpios${NC}"

# ════════════════════════════════════════════════════════════════
# 4. LEVANTAR BACKEND (Uvicorn)
# ════════════════════════════════════════════════════════════════
echo -e "\n${BLUE}[4/5]${NC} Levantando Backend (Uvicorn en puerto 8000)..."
cd "$BACKEND_DIR"
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --reload > /tmp/verde_backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > "$BACKEND_PID_FILE"
sleep 3

# Verificar que está corriendo
if ! curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    echo -e "${RED}✗ Backend no respondió${NC}"
    echo "Logs:"
    tail -20 /tmp/verde_backend.log
    exit 1
fi
echo -e "${GREEN}✓ Backend corriendo (PID: $BACKEND_PID)${NC}"

# ════════════════════════════════════════════════════════════════
# 5. LEVANTAR FRONTEND (HTTP Server)
# ════════════════════════════════════════════════════════════════
echo -e "\n${BLUE}[5/5]${NC} Levantando Frontend (HTTP Server en puerto 3000)..."
cd "$FRONTEND_DIR"
nohup python3 -m http.server 3000 > /tmp/verde_frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > "$FRONTEND_PID_FILE"
sleep 2

# Verificar que está corriendo
if ! curl -s http://localhost:3000/login.html > /dev/null 2>&1; then
    echo -e "${RED}✗ Frontend no respondió${NC}"
    echo "Logs:"
    tail -20 /tmp/verde_frontend.log
    exit 1
fi
echo -e "${GREEN}✓ Frontend corriendo (PID: $FRONTEND_PID)${NC}"

# ════════════════════════════════════════════════════════════════
# 6. RESUMEN Y ACCESO
# ════════════════════════════════════════════════════════════════
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              ✅ SISTEMA LEVANTADO EXITOSAMENTE            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}📍 ACCESO:${NC}"
echo -e "   ${BLUE}Backend (API)${NC}        → ${YELLOW}http://localhost:8000${NC}"
echo -e "   ${BLUE}API Docs (Swagger)${NC}   → ${YELLOW}http://localhost:8000/docs${NC}"
echo -e "   ${BLUE}Frontend (Login)${NC}     → ${YELLOW}http://localhost:3000/login.html${NC}"
echo -e "   ${BLUE}Nuevo Pedido${NC}        → ${YELLOW}http://localhost:3000/formulario_pedido.html${NC}"
echo ""
echo -e "${GREEN}📊 DATOS:${NC}"
echo -e "   • 548 agencias importadas"
echo -e "   • 116 provincias"
echo -e "   • 25 departamentos"
echo ""
echo -e "${GREEN}🛑 DETENER:${NC}"
echo -e "   ${YELLOW}./stop_local.sh${NC}  (detiene ambos servicios)"
echo ""
echo -e "${GREEN}📋 LOGS:${NC}"
echo -e "   Backend:  tail -f /tmp/verde_backend.log"
echo -e "   Frontend: tail -f /tmp/verde_frontend.log"
echo ""

# ════════════════════════════════════════════════════════════════
# MANTENER PROCESOS ACTIVOS
# ════════════════════════════════════════════════════════════════
echo -e "${YELLOW}Presiona Ctrl+C para detener...${NC}"
echo ""

# Trap para capturar Ctrl+C
trap_handler() {
    echo ""
    echo -e "\n${YELLOW}⏹️  Deteniendo servicios...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    rm -f "$BACKEND_PID_FILE" "$FRONTEND_PID_FILE"
    echo -e "${GREEN}✓ Servicios detenidos${NC}"
    exit 0
}

trap trap_handler INT TERM

# Mantener el script en ejecución
wait $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
