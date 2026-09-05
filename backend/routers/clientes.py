from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from decolecta_service import consultar_dni_decolecta, DniLookupError

router = APIRouter(tags=["clientes"])


@router.get("/buscar/{documento}", response_model=schemas.ClienteLookup)
def buscar_cliente(
    documento: str,
    tipo_documento: str = Query("dni", pattern="^(dni|ce)$"),
    db: Session = Depends(get_db),
):
    """
    Busca un cliente por documento.
    - DNI: exactamente 8 dígitos. Si existe en BD lo retorna; si no, consulta
      Decolecta, lo inserta y lo retorna.
    - C.E.: hasta 10 caracteres, validación mínima. Solo busca en las tablas
      del sistema (clientes y pedidos históricos) para traer nombre y
      teléfono; nunca consulta Decolecta ni inserta un cliente nuevo.
    """
    if tipo_documento == "ce":
        documento = documento.strip()
        if not documento or len(documento) > 10:
            raise HTTPException(status_code=400, detail="El C.E. debe tener hasta 10 caracteres")

        cliente = db.query(models.Cliente).filter(models.Cliente.dni == documento).first()
        ultimo_pedido = (
            db.query(models.Pedido)
            .filter(models.Pedido.dni == documento)
            .order_by(models.Pedido.fecha_registro.desc())
            .first()
        )
        if not cliente and not ultimo_pedido:
            raise HTTPException(status_code=404, detail="No se encontró el C.E. en el sistema")

        return schemas.ClienteLookup(
            dni=documento,
            nombres=cliente.nombres if cliente else "",
            apellido_paterno=cliente.apellido_paterno if cliente else "",
            apellido_materno=cliente.apellido_materno if cliente else None,
            nombre_completo=cliente.nombre_completo if cliente else ultimo_pedido.nombre_cliente,
            telefono=ultimo_pedido.telefono if ultimo_pedido else None,
        )

    # ── Flujo DNI (comportamiento original) ─────────────────────
    if not documento.isdigit() or len(documento) != 8:
        raise HTTPException(status_code=400, detail="DNI debe tener exactamente 8 dígitos")

    cliente = db.query(models.Cliente).filter(models.Cliente.dni == documento).first()
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
        datos = consultar_dni_decolecta(documento)
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
