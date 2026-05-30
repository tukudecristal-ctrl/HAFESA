from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os

from routers import catalogos, pedidos, compras, comisiones, auth, mis_ventas, agencias, clientes

load_dotenv()

app = FastAPI(
    title="Sistema de Ventas Multiempresa",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,        prefix="/api/auth",        tags=["Auth"])
app.include_router(mis_ventas.router,  prefix="/api/mis-ventas",  tags=["Mis Ventas"])
app.include_router(catalogos.router,   prefix="/api/catalogos",   tags=["Catálogos"])
app.include_router(agencias.router,    prefix="/api/agencias",    tags=["Agencias"])
app.include_router(clientes.router,    prefix="/api/clientes",    tags=["Clientes"])
app.include_router(pedidos.router,     prefix="/api/pedidos",     tags=["Pedidos"])
app.include_router(compras.router,     prefix="/api/compras",     tags=["Compras"])
app.include_router(comisiones.router,  prefix="/api/comisiones",  tags=["Comisiones"])

# Servir imágenes de productos
IMAGENES_DIR = os.path.join(os.path.dirname(__file__), "static", "imagenes")
os.makedirs(IMAGENES_DIR, exist_ok=True)
app.mount("/imagenes", StaticFiles(directory=IMAGENES_DIR), name="imagenes")

# Servir frontend estático
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/app", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


@app.get("/", tags=["Root"])
def root():
    return RedirectResponse(url="/app/login.html")
