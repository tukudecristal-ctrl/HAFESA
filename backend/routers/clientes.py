from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from decolecta_service import consultar_dni_decolecta, DniLookupError

router = APIRouter(tags=["clientes"])


@router.get("/buscar/{dni}", response_model=schemas.ClienteLookup)
def buscar_cliente(dni: str, db: Session = Depends(get_db)):
    """
    Busca un cliente por DNI.
    - Si existe en BD, retorna sus datos
    - Si no existe, consulta Decolecta, inserta el cliente y retorna datos
    """
    # Validar formato DNI (8 dígitos)
    if not dni.isdigit() or len(dni) != 8:
        raise HTTPException(status_code=400, detail="DNI debe tener exactamente 8 dígitos")

    # Buscar en base de datos
    cliente = db.query(models.Cliente).filter(models.Cliente.dni == dni).first()
    if cliente:
        return schemas.ClienteLookup(
            dni=cliente.dni,
            nombres=cliente.nombres,
            apellido_paterno=cliente.apellido_paterno,
            apellido_materno=cliente.apellido_materno,
            nombre_completo=cliente.nombre_completo,
        )

    # No encontrado en BD, consultar Decolecta
    try:
        datos = consultar_dni_decolecta(dni)
    except DniLookupError as e:
        raise HTTPException(status_code=404, detail=f"No se encontró en Decolecta: {str(e)}")

    # Insertar en BD
    nuevo_cliente = models.Cliente(
        dni=datos["dni"],
        nombres=datos["nombres"],
        apellido_paterno=datos["apellido_paterno"],
        apellido_materno=datos["apellido_materno"],
        nombre_completo=datos["nombre_completo"],
        fuente="decolecta",
    )
    db.add(nuevo_cliente)
    db.commit()
    db.refresh(nuevo_cliente)

    return schemas.ClienteLookup(
        dni=nuevo_cliente.dni,
        nombres=nuevo_cliente.nombres,
        apellido_paterno=nuevo_cliente.apellido_paterno,
        apellido_materno=nuevo_cliente.apellido_materno,
        nombre_completo=nuevo_cliente.nombre_completo,
    )
