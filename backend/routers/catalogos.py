from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models, schemas
import os, shutil, uuid

router = APIRouter()


# ── Empresas ───────────────────────────────────────────────────
@router.get("/empresas", response_model=List[schemas.EmpresaOut])
def listar_empresas(todos: bool = False, db: Session = Depends(get_db)):
    q = db.query(models.Empresa)
    if not todos:
        q = q.filter(models.Empresa.activo == True)
    return q.order_by(models.Empresa.nombre).all()

@router.post("/empresas", response_model=schemas.EmpresaOut, status_code=201)
def crear_empresa(data: schemas.EmpresaCreate, db: Session = Depends(get_db)):
    if db.query(models.Empresa).filter(models.Empresa.codigo == data.codigo).first():
        raise HTTPException(status_code=400, detail="El código ya existe")
    empresa = models.Empresa(**data.model_dump())
    db.add(empresa)
    db.commit()
    db.refresh(empresa)
    return empresa

@router.put("/empresas/{eid}", response_model=schemas.EmpresaOut)
def actualizar_empresa(eid: int, data: schemas.EmpresaUpdate, db: Session = Depends(get_db)):
    empresa = db.query(models.Empresa).filter(models.Empresa.id == eid).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(empresa, field, value)
    db.commit()
    db.refresh(empresa)
    return empresa


# ── Vendedores ─────────────────────────────────────────────────
@router.get("/vendedores", response_model=List[schemas.VendedorOut])
def listar_vendedores(empresa_id: int | None = None, todos: bool = False, db: Session = Depends(get_db)):
    q = db.query(models.Vendedor)
    if not todos:
        q = q.filter(models.Vendedor.activo == True)
    if empresa_id:
        q = q.filter(models.Vendedor.empresa_id == empresa_id)
    return q.order_by(models.Vendedor.nombre_completo).all()

@router.post("/vendedores", response_model=schemas.VendedorOut, status_code=201)
def crear_vendedor(data: schemas.VendedorCreate, db: Session = Depends(get_db)):
    if db.query(models.Vendedor).filter(models.Vendedor.codigo == data.codigo).first():
        raise HTTPException(status_code=400, detail="El código ya existe")
    vendedor = models.Vendedor(**data.model_dump())
    db.add(vendedor)
    db.commit()
    db.refresh(vendedor)
    return vendedor

@router.put("/vendedores/{vid}", response_model=schemas.VendedorOut)
def actualizar_vendedor(vid: int, data: schemas.VendedorUpdate, db: Session = Depends(get_db)):
    vendedor = db.query(models.Vendedor).filter(models.Vendedor.id == vid).first()
    if not vendedor:
        raise HTTPException(status_code=404, detail="Vendedor no encontrado")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(vendedor, field, value)
    db.commit()
    db.refresh(vendedor)
    return vendedor


# ── Productos ──────────────────────────────────────────────────
@router.get("/productos", response_model=List[schemas.ProductoOut])
def listar_productos(empresa_id: int | None = None, todos: bool = False, db: Session = Depends(get_db)):
    q = db.query(models.Producto)
    if not todos:
        q = q.filter(models.Producto.activo == True)
    if empresa_id:
        q = q.filter(models.Producto.empresa_id == empresa_id)
    return q.order_by(models.Producto.nombre).all()

@router.post("/productos", response_model=schemas.ProductoOut, status_code=201)
def crear_producto(data: schemas.ProductoCreate, db: Session = Depends(get_db)):
    if db.query(models.Producto).filter(models.Producto.codigo == data.codigo).first():
        raise HTTPException(status_code=400, detail="El código ya existe")
    dump = data.model_dump()
    # Si precio_venta_1/2/3 no fueron definidos (quedan en 0), replica precio_venta
    for campo in ("precio_venta_1", "precio_venta_2", "precio_venta_3"):
        if not dump.get(campo):
            dump[campo] = dump["precio_venta"]
    producto = models.Producto(**dump)
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return producto

@router.put("/productos/{pid}", response_model=schemas.ProductoOut)
def actualizar_producto(pid: int, data: schemas.ProductoUpdate, db: Session = Depends(get_db)):
    producto = db.query(models.Producto).filter(models.Producto.id == pid).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(producto, field, value)
    db.commit()
    db.refresh(producto)
    return producto

IMAGENES_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "imagenes")
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE_MB = 5

@router.post("/productos/{pid}/imagen", response_model=schemas.ProductoOut)
async def subir_imagen_producto(pid: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    producto = db.query(models.Producto).filter(models.Producto.id == pid).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Solo se permiten imágenes JPEG, PNG o WebP")

    contenido = await file.read()
    if len(contenido) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"La imagen no debe superar {MAX_SIZE_MB} MB")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "jpg"
    nombre_archivo = f"prod_{pid}_{uuid.uuid4().hex[:8]}.{ext}"
    ruta = os.path.join(IMAGENES_DIR, nombre_archivo)
    os.makedirs(IMAGENES_DIR, exist_ok=True)

    # Eliminar imagen anterior si existe
    if producto.imagen_url:
        anterior = os.path.join(IMAGENES_DIR, os.path.basename(producto.imagen_url))
        if os.path.exists(anterior):
            os.remove(anterior)

    with open(ruta, "wb") as f:
        f.write(contenido)

    producto.imagen_url = f"/imagenes/{nombre_archivo}"
    db.commit()
    db.refresh(producto)
    return producto

@router.delete("/productos/{pid}/imagen", response_model=schemas.ProductoOut)
def eliminar_imagen_producto(pid: int, db: Session = Depends(get_db)):
    producto = db.query(models.Producto).filter(models.Producto.id == pid).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if producto.imagen_url:
        ruta = os.path.join(IMAGENES_DIR, os.path.basename(producto.imagen_url))
        if os.path.exists(ruta):
            os.remove(ruta)
        producto.imagen_url = None
        db.commit()
        db.refresh(producto)
    return producto


# ── Proveedores ────────────────────────────────────────────────
@router.get("/proveedores", response_model=List[schemas.ProveedorOut])
def listar_proveedores(todos: bool = False, db: Session = Depends(get_db)):
    q = db.query(models.Proveedor)
    if not todos:
        q = q.filter(models.Proveedor.activo == True)
    return q.order_by(models.Proveedor.nombre).all()

@router.post("/proveedores", response_model=schemas.ProveedorOut, status_code=201)
def crear_proveedor(data: schemas.ProveedorCreate, db: Session = Depends(get_db)):
    if db.query(models.Proveedor).filter(models.Proveedor.codigo == data.codigo).first():
        raise HTTPException(status_code=400, detail="El código ya existe")
    proveedor = models.Proveedor(**data.model_dump())
    db.add(proveedor)
    db.commit()
    db.refresh(proveedor)
    return proveedor

@router.put("/proveedores/{pid}", response_model=schemas.ProveedorOut)
def actualizar_proveedor(pid: int, data: schemas.ProveedorUpdate, db: Session = Depends(get_db)):
    proveedor = db.query(models.Proveedor).filter(models.Proveedor.id == pid).first()
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(proveedor, field, value)
    db.commit()
    db.refresh(proveedor)
    return proveedor


# ── Agencias ───────────────────────────────────────────────────
@router.get("/agencias", response_model=List[schemas.AgenciaOut])
def listar_agencias(db: Session = Depends(get_db)):
    return db.query(models.AgenciaDestino).filter(models.AgenciaDestino.activo == True).order_by(models.AgenciaDestino.ciudad).all()
