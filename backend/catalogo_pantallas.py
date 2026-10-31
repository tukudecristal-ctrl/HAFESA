"""Catálogo de pantallas configurables y cálculo del acceso efectivo de cada usuario.

Los permisos se dan por rol (tabla rol_permisos). Las pantallas Usuarios y Permisos no están
aquí: son siempre solo para el rol administrador.
"""
from sqlalchemy.orm import Session
import models

PANTALLAS = [
    {"key": "pedidos",            "nombre": "Gestión de pedidos", "url": "backoffice.html",        "grupo": "Pedidos y ventas"},
    {"key": "nuevo_pedido",       "nombre": "Nuevo pedido",       "url": "formulario_pedido.html", "grupo": "Pedidos y ventas"},
    {"key": "mis_ventas",         "nombre": "Mis ventas",         "url": "mis_ventas.html",        "grupo": "Pedidos y ventas"},
    {"key": "compras",            "nombre": "Compras",            "url": "compras.html",           "grupo": "Compras e inventario"},
    {"key": "productos",          "nombre": "Productos",          "url": "crud_productos.html",    "grupo": "Compras e inventario"},
    {"key": "comisiones",         "nombre": "Comisiones",         "url": "comisiones.html",        "grupo": "Reportes"},
    {"key": "reporte_ventas",     "nombre": "Reporte de ventas",  "url": "reporte_ventas.html",    "grupo": "Reportes"},
    {"key": "estado_financiero",  "nombre": "Estado financiero",  "url": "estado_financiero.html", "grupo": "Reportes"},
    {"key": "publicidad",         "nombre": "Publicidad",         "url": "publicidad.html",        "grupo": "Administración"},
    {"key": "proveedores",        "nombre": "Proveedores",        "url": "crud_proveedores.html",  "grupo": "Administración"},
    {"key": "empresas",           "nombre": "Empresas",           "url": "crud_empresas.html",     "grupo": "Administración"},
    {"key": "vendedores",         "nombre": "Vendedores",         "url": "crud_vendedores.html",   "grupo": "Administración"},
]

CLAVES = [p["key"] for p in PANTALLAS]
ROLES = ["administrador", "logistica", "vendedor"]
ROL_ADMIN = "administrador"


def pantallas_de_rol(db: Session, rol: str) -> list[str]:
    """Claves de pantalla de un rol, en el orden del catálogo.

    El administrador siempre tiene todas, sin importar lo que haya en la tabla, para que
    nadie pueda quedarse sin acceso a la configuración.
    """
    if rol == ROL_ADMIN:
        return list(CLAVES)
    asignadas = {f.pantalla for f in db.query(models.RolPermiso).filter(models.RolPermiso.rol == rol)}
    return [k for k in CLAVES if k in asignadas]


def pantallas_de_usuario(db: Session, usuario: models.Usuario) -> list[str]:
    return pantallas_de_rol(db, usuario.rol)


def detalle_pantallas(claves: list[str]) -> list[dict]:
    """Datos de cada pantalla (clave, nombre, url, grupo) para enviar al frontend."""
    permitidas = set(claves)
    return [
        {k: p[k] for k in ("key", "nombre", "url", "grupo")}
        for p in PANTALLAS if p["key"] in permitidas
    ]
