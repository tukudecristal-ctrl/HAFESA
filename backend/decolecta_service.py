import json
from urllib import error, parse, request
import os


class DniLookupError(Exception):
    pass


def consultar_dni_decolecta(dni: str) -> dict:
    """Consulta DNI en Decolecta y retorna nombres y apellidos"""
    token = os.getenv("DECOLECTA_API_TOKEN", "").strip()
    if not token:
        raise DniLookupError("No se configuró el token de Decolecta (DECOLECTA_API_TOKEN).")

    base_url = os.getenv("DECOLECTA_API_BASE_URL", "https://api.decolecta.com").rstrip("/")
    query = parse.urlencode({"numero": dni})
    url = f"{base_url}/v1/reniec/dni?{query}"

    api_request = request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="GET",
    )

    try:
        with request.urlopen(api_request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise DniLookupError(
            f"Decolecta respondió con error HTTP {exc.code}: {detail or 'sin detalle'}"
        ) from exc
    except error.URLError as exc:
        raise DniLookupError("No se pudo conectar con Decolecta.") from exc
    except json.JSONDecodeError as exc:
        raise DniLookupError("La respuesta de Decolecta no fue JSON válido.") from exc

    nombres = (payload.get("first_name") or "").strip()
    apellido_paterno = (payload.get("first_last_name") or "").strip()
    apellido_materno = (payload.get("second_last_name") or "").strip()
    document_number = (payload.get("document_number") or dni).strip()

    if not nombres and not apellido_paterno and not apellido_materno:
        raise DniLookupError("Decolecta no devolvió datos para ese DNI.")

    nombre_completo_ordenado = " ".join(
        part for part in [nombres, apellido_paterno, apellido_materno] if part
    )

    return {
        "dni": document_number,
        "nombres": nombres,
        "apellido_paterno": apellido_paterno,
        "apellido_materno": apellido_materno,
        "nombre_completo": nombre_completo_ordenado,
    }
