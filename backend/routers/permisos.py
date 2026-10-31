from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user, require_roles
from catalogo_pantallas import PANTALLAS, CLAVES, ROLES, ROL_ADMIN, pantallas_de_rol, pantallas_de_usuario, detalle_pantallas
import models, schemas

router = APIRouter()


@router.get("/mis-pantallas")
def mis_pantallas(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Pantallas del usuario que llama; el frontend la consulta en cada página para reflejar cambios."""
    usuario = db.get(models.Usuario, user.get("usuario_id"))
    if not usuario or not usuario.activo:
        raise HTTPException(status_code=401, detail="Usuario inactivo o inexistente")
    return {"pantallas": detalle_pantallas(pantallas_de_usuario(db, usuario))}


@router.get("/catalogo")
def catalogo(_: dict = Depends(require_roles("administrador"))):
    return PANTALLAS


def _salida(db: Session, rol: str) -> schemas.PermisosRolOut:
    usuarios = (
        db.query(models.Usuario)
        .filter(models.Usuario.rol == rol)
        .order_by(models.Usuario.nombre)
        .all()
    )
    return schemas.PermisosRolOut(
        rol=rol,
        editable=rol != ROL_ADMIN,
        pantallas=pantallas_de_rol(db, rol),
        usuarios=[
            schemas.PermisosRolUsuario(nombre=u.nombre.strip(), dni=u.dni, activo=bool(u.activo))
            for u in usuarios
        ],
    )


@router.get("/roles", response_model=list[schemas.PermisosRolOut])
def listar_roles(
    db: Session = Depends(get_db),
    _: dict = Depends(require_roles("administrador")),
):
    return [_salida(db, rol) for rol in ROLES]


@router.put("/roles/{rol}", response_model=schemas.PermisosRolOut)
def guardar_permisos_rol(
    rol: str,
    data: schemas.PermisosRolInput,
    db: Session = Depends(get_db),
    _: dict = Depends(require_roles("administrador")),
):
    if rol not in ROLES:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    if rol == ROL_ADMIN:
        raise HTTPException(status_code=400, detail="El administrador siempre tiene acceso a todas las pantallas")
    desconocidas = sorted(set(data.pantallas) - set(CLAVES))
    if desconocidas:
        raise HTTPException(status_code=400, detail=f"Pantallas desconocidas: {', '.join(desconocidas)}")

    db.query(models.RolPermiso).filter(models.RolPermiso.rol == rol).delete()
    for clave in sorted(set(data.pantallas)):
        db.add(models.RolPermiso(rol=rol, pantalla=clave))
    db.commit()
    return _salida(db, rol)
