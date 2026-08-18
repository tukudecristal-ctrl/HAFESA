from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt, os, bcrypt

from database import get_db
from dependencies import get_current_user, require_roles
import models, schemas

router = APIRouter()
SECRET_KEY = os.getenv("SECRET_KEY", "cambia-esta-clave-en-produccion")
ALGORITHM = "HS256"
TOKEN_HOURS = 10


def _hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def _verify(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

def _create_token(payload: dict) -> str:
    data = payload.copy()
    data["exp"] = datetime.utcnow() + timedelta(hours=TOKEN_HOURS)
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


# ── Login ──────────────────────────────────────────────────────
@router.post("/login", response_model=schemas.TokenOut)
def login(data: schemas.LoginInput, db: Session = Depends(get_db)):
    usuario = (
        db.query(models.Usuario)
        .filter(models.Usuario.dni == data.dni, models.Usuario.activo == True)
        .first()
    )
    if not usuario or not _verify(data.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="DNI o contraseña incorrectos")
    token = _create_token({
        "sub":         usuario.dni,
        "usuario_id":  usuario.id,
        "rol":         usuario.rol,
        "nombre":      usuario.nombre,
        "vendedor_id": usuario.vendedor_id,
    })
    return schemas.TokenOut(
        access_token=token,
        rol=usuario.rol,
        nombre=usuario.nombre,
        vendedor_id=usuario.vendedor_id,
    )


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return current_user


# ── CRUD usuarios (solo administrador) ─────────────────────────
@router.get("/usuarios", response_model=list[schemas.UsuarioOut])
def listar_usuarios(
    db: Session = Depends(get_db),
    _: dict = Depends(require_roles("administrador"))
):
    return db.query(models.Usuario).order_by(models.Usuario.nombre).all()


@router.post("/usuarios", response_model=schemas.UsuarioOut, status_code=201)
def crear_usuario(
    data: schemas.UsuarioCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_roles("administrador"))
):
    if db.query(models.Usuario).filter(models.Usuario.dni == data.dni).first():
        raise HTTPException(status_code=400, detail="El DNI ya está registrado")
    if data.rol == "vendedor" and not data.vendedor_id:
        raise HTTPException(status_code=400, detail="Un usuario vendedor requiere vendedor_id")
    usuario = models.Usuario(
        dni=data.dni,
        password_hash=_hash(data.password),
        nombre=data.nombre,
        rol=data.rol,
        vendedor_id=data.vendedor_id,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.put("/usuarios/{uid}", response_model=schemas.UsuarioOut)
def actualizar_usuario(
    uid: int,
    data: schemas.UsuarioUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_roles("administrador"))
):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == uid).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(usuario, field, value)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.post("/usuarios/{uid}/reset-password", response_model=schemas.UsuarioOut)
def reset_password(
    uid: int,
    data: schemas.UsuarioPasswordReset,
    db: Session = Depends(get_db),
    _: dict = Depends(require_roles("administrador"))
):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == uid).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario.password_hash = _hash(data.password)
    db.commit()
    db.refresh(usuario)
    return usuario


# ── Cambio de clave (cualquier usuario autenticado) ────────────
@router.post("/cambiar-clave")
def cambiar_clave(
    data: schemas.CambiarClaveInput,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == current_user["usuario_id"]).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if not _verify(data.clave_actual, usuario.password_hash):
        raise HTTPException(status_code=400, detail="La clave actual es incorrecta")
    usuario.password_hash = _hash(data.nueva_clave)
    db.commit()
    return {"ok": True}


# ── Setup inicial (solo si no hay usuarios) ────────────────────
@router.post("/setup", response_model=schemas.UsuarioOut, status_code=201)
def setup_inicial(data: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    if db.query(models.Usuario).count() > 0:
        raise HTTPException(status_code=403, detail="Ya existen usuarios. Usa el CRUD de usuarios.")
    usuario = models.Usuario(
        dni=data.dni,
        password_hash=_hash(data.password),
        nombre=data.nombre,
        rol="administrador",
        vendedor_id=None,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario
