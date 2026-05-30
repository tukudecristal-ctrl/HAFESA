#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║          🛑 Deteniendo servicios — VERDE                  ║"
echo "╚════════════════════════════════════════════════════════════╝"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

BACKEND_PID_FILE="/tmp/verde_backend.pid"
FRONTEND_PID_FILE="/tmp/verde_frontend.pid"

# ════════════════════════════════════════════════════════════════
# DETENER POR PID
# ════════════════════════════════════════════════════════════════

echo -e "\n${YELLOW}Deteniendo servicios...${NC}\n"

# Backend
if [ -f "$BACKEND_PID_FILE" ]; then
    BACKEND_PID=$(cat "$BACKEND_PID_FILE")
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${RED}✗${NC} Backend (PID: $BACKEND_PID)"
        kill $BACKEND_PID 2>/dev/null || kill -9 $BACKEND_PID 2>/dev/null
        echo -e "${GREEN}✓${NC} Backend detenido"
    fi
    rm -f "$BACKEND_PID_FILE"
fi

# Frontend
if [ -f "$FRONTEND_PID_FILE" ]; then
    FRONTEND_PID=$(cat "$FRONTEND_PID_FILE")
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${RED}✗${NC} Frontend (PID: $FRONTEND_PID)"
        kill $FRONTEND_PID 2>/dev/null || kill -9 $FRONTEND_PID 2>/dev/null
        echo -e "${GREEN}✓${NC} Frontend detenido"
    fi
    rm -f "$FRONTEND_PID_FILE"
fi

# ════════════════════════════════════════════════════════════════
# DETENER POR PUERTO (si quedan procesos)
# ════════════════════════════════════════════════════════════════

if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⏳ Limpiando puerto 8000...${NC}"
    lsof -i :8000 -t | xargs kill -9 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Puerto 8000 limpio"
fi

if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⏳ Limpiando puerto 3000...${NC}"
    lsof -i :3000 -t | xargs kill -9 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Puerto 3000 limpio"
fi

echo ""
echo -e "${GREEN}✅ Todos los servicios detenidos${NC}"
echo ""
