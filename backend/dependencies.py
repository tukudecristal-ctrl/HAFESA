from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt
import os

from database import get_db

SECRET_KEY = os.getenv("SECRET_KEY", "cambia-esta-clave-en-produccion")
ALGORITHM = "HS256"

security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Sesión expirada, ingresa nuevamente")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")


def require_roles(*roles):
    def _check(user: dict = Depends(get_current_user)):
        if user.get("rol") not in roles:
            raise HTTPException(status_code=403, detail="Sin permisos para esta acción")
        return user
    return _check


def require_pantalla(clave: str):
    """Exige que el usuario tenga asignada la pantalla `clave` (consulta la BD en cada llamada,
    así un cambio de permisos o una desactivación surten efecto de inmediato)."""
    def _check(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
        import models
        from catalogo_pantallas import pantallas_de_usuario
        usuario = db.get(models.Usuario, user.get("usuario_id"))
        if not usuario or not usuario.activo or clave not in pantallas_de_usuario(db, usuario):
            raise HTTPException(status_code=403, detail="Sin permisos para esta acción")
        return user
    return _check
