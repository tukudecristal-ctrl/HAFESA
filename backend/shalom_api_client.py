#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shalom API Latam - Cliente Python
==================================

Cliente completo para consumir la API de Shalom Courier Service Latam.
Base URL: https://shalom-api.lat
Documentación: https://shalom-api.lat/dashboard/docs

Características:
- Listado de agencias
- Búsqueda de agencias (general y por nombre)
- Tracking de pedidos
- Generación de imágenes y PDFs
- Cotización de envíos
- Registro de envíos (Plan Pro)

Uso:
    from shalom_api_client import ShalomAPIClient

    client = ShalomAPIClient(api_key="tu-api-key")
    agencies = client.list_agencies()
"""

import requests
import logging
import time
from typing import Optional, Dict, List, Any
from urllib.parse import urljoin
from dataclasses import dataclass


# ════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ════════════════════════════════════════════════════════════

BASE_URL = "https://shalom-api.lat"
TIMEOUT = 30

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════
# DATACLASSES
# ════════════════════════════════════════════════════════════

@dataclass
class Agency:
    """Representa una agencia de Shalom"""
    ter_id: str
    lugar_over: str
    direccion: str
    zona: str
    provincia: str
    departamento: str
    telefono: str
    hora_atencion: str
    latitud: str
    longitud: str
    hora_domingo: Optional[str] = None


# ════════════════════════════════════════════════════════════
# EXCEPCIONES
# ════════════════════════════════════════════════════════════

class ShalomAPIError(Exception):
    """Error base para la API de Shalom"""
    pass


class ShalomAuthError(ShalomAPIError):
    """Error de autenticación"""
    pass


class ShalomNotFoundError(ShalomAPIError):
    """Recurso no encontrado"""
    pass


class ShalomValidationError(ShalomAPIError):
    """Error de validación"""
    pass


# ════════════════════════════════════════════════════════════
# CLIENTE SHALOM API
# ════════════════════════════════════════════════════════════

class ShalomAPIClient:
    """
    Cliente para la API de Shalom Latam.

    Maneja:
    - Autenticación por API Key
    - Listado y búsqueda de agencias
    - Tracking de pedidos
    - Generación de imágenes y documentos
    - Cotizaciones
    - Registro de envíos (Plan Pro)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = BASE_URL,
        timeout: int = TIMEOUT,
        verbose: bool = True
    ):
        """
        Inicializa el cliente de Shalom API.

        Args:
            api_key: Clave API de Shalom
            base_url: URL base de la API
            timeout: Timeout para requests en segundos
            verbose: Mostrar logs detallados
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout

        if verbose:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.WARNING)

        # Session HTTP
        self._session = requests.Session()
        self._session.headers.update({
            'x-api-key': api_key,
            'User-Agent': 'ShalomAPIClient/1.0 Python'
        })

        logger.info(f"ShalomAPIClient inicializado - URL: {self.base_url}")

    # ─── HTTP Methods ───────────────────────────────────

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Realiza una request HTTP.

        Args:
            method: GET, POST, etc.
            endpoint: Ruta relativa (ej: /api/listar)
            params: Query parameters
            json: Body JSON

        Returns:
            Response JSON parseada

        Raises:
            ShalomAPIError: En caso de error
        """
        url = urljoin(self.base_url, endpoint)
        logger.debug(f"{method} {url} params={params}")

        try:
            response = self._session.request(
                method=method,
                url=url,
                params=params,
                json=json,
                timeout=self.timeout,
                **kwargs
            )

            logger.debug(f"Status: {response.status_code}")

            # Manejo de errores
            if response.status_code == 401:
                raise ShalomAuthError(
                    f"No autorizado. Verifica tu API Key. "
                    f"Respuesta: {response.text}"
                )

            if response.status_code == 404:
                raise ShalomNotFoundError(
                    f"Recurso no encontrado: {endpoint}"
                )

            if response.status_code >= 400:
                raise ShalomAPIError(
                    f"Error {response.status_code}: {response.text}"
                )

            # Success
            if response.text:
                return response.json()
            else:
                return {}

        except requests.RequestException as e:
            raise ShalomAPIError(f"Error de conexión: {e}")

    # ─── Agencias ───────────────────────────────────────

    def list_agencies(self) -> List[Dict[str, Any]]:
        """
        Lista todas las agencias.

        Returns:
            Lista completa de agencias
        """
        logger.info("Listando todas las agencias")
        response = self._make_request('GET', '/api/listar')

        # Manejar diferentes formatos de respuesta
        if isinstance(response, list):
            return response
        elif isinstance(response, dict):
            # Formato: {"success": true, "data": [...]}
            if 'data' in response:
                return response.get('data', [])
            # Formato: {"resultados": [...]}
            elif 'resultados' in response:
                return response.get('resultados', [])

        return []

    def search_agencies(self, query: str) -> List[Dict[str, Any]]:
        """
        Busca agencias por cualquier campo.

        Args:
            query: Término de búsqueda (nombre, dirección, teléfono, etc.)

        Returns:
            Lista de agencias que coinciden
        """
        logger.info(f"Buscando agencias: {query}")
        response = self._make_request(
            'GET',
            '/api/buscar',
            params={'q': query}
        )

        if isinstance(response, list):
            return response
        elif isinstance(response, dict):
            return response.get('data', response.get('resultados', []))

        return []

    def search_agency_by_name(self, query: str) -> List[Dict[str, Any]]:
        """
        Busca agencias únicamente por nombre.

        Args:
            query: Término de búsqueda por nombre

        Returns:
            Lista de agencias que coinciden
        """
        logger.info(f"Buscando agencia por nombre: {query}")
        response = self._make_request(
            'GET',
            '/api/agencia',
            params={'q': query}
        )

        if isinstance(response, list):
            return response
        elif isinstance(response, dict):
            return response.get('data', response.get('resultados', []))

        return []

    def get_agencies_minimal(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtiene información resumida de agencias.

        Args:
            query: Término de búsqueda (opcional, si no se proporciona devuelve todas)

        Returns:
            Lista de agencias con información minimal
        """
        logger.info(f"Obteniendo agencias (minimal): {query}")
        params = {'q': query} if query else {}
        response = self._make_request(
            'GET',
            '/api/agencia-minimal',
            params=params
        )

        if isinstance(response, list):
            return response
        elif isinstance(response, dict):
            return response.get('data', response.get('resultados', []))

        return []

    def get_agencies_image(self, query: str) -> bytes:
        """
        Genera una imagen PNG con agencias encontradas.

        Args:
            query: Término de búsqueda

        Returns:
            Imagen PNG como bytes
        """
        logger.info(f"Generando imagen de agencias: {query}")
        response = self._session.get(
            f"{self.base_url}/api/image",
            params={'q': query},
            headers={'x-api-key': self.api_key},
            timeout=self.timeout
        )

        if response.status_code != 200:
            raise ShalomAPIError(f"Error {response.status_code}: {response.text}")

        return response.content

    # ─── Tracking ───────────────────────────────────────

    def track_shipment(
        self,
        order_number: str,
        order_code: str
    ) -> Dict[str, Any]:
        """
        Rastrea un pedido.

        Args:
            order_number: Número de orden
            order_code: Código de orden

        Returns:
            Información de seguimiento del pedido
        """
        logger.info(f"Rastreando pedido: {order_number}/{order_code}")
        return self._make_request(
            'POST',
            '/api/track',
            json={'orderNumber': order_number, 'orderCode': order_code}
        )

    # ─── Imágenes y PDFs ─────────────────────────────────

    def get_ticket_image(
        self,
        order_number: str,
        order_code: str
    ) -> bytes:
        """
        Genera una imagen tipo ticket del envío.

        Args:
            order_number: Número de orden
            order_code: Código de orden

        Returns:
            Imagen PNG como bytes
        """
        logger.info(f"Generando imagen de ticket: {order_number}/{order_code}")
        response = self._session.post(
            f"{self.base_url}/api/ticket-image",
            json={'orderNumber': order_number, 'orderCode': order_code},
            headers={'x-api-key': self.api_key},
            timeout=self.timeout
        )

        if response.status_code != 200:
            raise ShalomAPIError(f"Error {response.status_code}: {response.text}")

        return response.content

    def get_label_pdf(
        self,
        order_number: str,
        order_code: str
    ) -> bytes:
        """
        Descarga el PDF de la etiqueta de envío.

        Args:
            order_number: Número de orden
            order_code: Código de orden

        Returns:
            PDF como bytes
        """
        logger.info(f"Descargando PDF de etiqueta: {order_number}/{order_code}")
        response = self._session.post(
            f"{self.base_url}/api/label",
            json={'orderNumber': order_number, 'orderCode': order_code},
            headers={'x-api-key': self.api_key},
            timeout=self.timeout
        )

        if response.status_code != 200:
            raise ShalomAPIError(f"Error {response.status_code}: {response.text}")

        return response.content

    # ─── Cotizaciones ───────────────────────────────────

    def get_quote(self, origin: int, destination: int) -> Dict[str, Any]:
        """
        Obtiene una cotización de envío.

        Args:
            origin: Código de origen
            destination: Código de destino

        Returns:
            Información de cotización
        """
        logger.info(f"Cotizando envío: {origin} → {destination}")
        return self._make_request(
            'POST',
            '/api/quote',
            json={'origin': origin, 'destination': destination}
        )

    # ─── Registro de Envíos (Plan Pro) ──────────────────

    def register_shipments(
        self,
        instance_id: str,
        shipments: List[Dict[str, Any]],
        security_code: str
    ) -> Dict[str, Any]:
        """
        Registra múltiples envíos (requiere Plan Pro).

        Args:
            instance_id: ID de la instancia Pro
            shipments: Lista de envíos a registrar
            security_code: Código de seguridad

        Returns:
            Respuesta del registro
        """
        logger.info(f"Registrando {len(shipments)} envío(s)")
        return self._make_request(
            'POST',
            '/api/register',
            json={
                'instanceId': instance_id,
                'shipments': shipments,
                'securityCode': security_code
            }
        )

    def register_individual_shipment(
        self,
        instance_id: str,
        origen: int,
        destino: str,
        content: str,
        cantidad: int,
        documento: str,
        name: str,
        firstname: str,
        lastname: str,
        phone: int,
        clave: str,
        declaracion_jurada: str
    ) -> Dict[str, Any]:
        """
        Registra un envío individual (requiere Plan Pro).

        Args:
            instance_id: ID de la instancia Pro
            origen: Código de origen
            destino: Código de destino
            content: Contenido del paquete
            cantidad: Cantidad
            documento: Documento del remitente
            name: Nombre
            firstname: Primer nombre
            lastname: Apellido
            phone: Teléfono
            clave: Clave de seguridad
            declaracion_jurada: Declaración jurada

        Returns:
            Respuesta del registro
        """
        logger.info(f"Registrando envío individual: {origen} → {destino}")
        return self._make_request(
            'POST',
            '/api/register-individual',
            json={
                'instanceId': instance_id,
                'origen': origen,
                'destino': destino,
                'content': content,
                'cantidad': cantidad,
                'documento': documento,
                'name': name,
                'firstname': firstname,
                'lastname': lastname,
                'phone': phone,
                'clave': clave,
                'declaracion_jurada': declaracion_jurada
            }
        )

    def get_pending_shipments(self, instance_id: str) -> List[Dict[str, Any]]:
        """
        Obtiene envíos pendientes (requiere Plan Pro).

        Args:
            instance_id: ID de la instancia Pro

        Returns:
            Lista de envíos pendientes
        """
        logger.info(f"Obteniendo envíos pendientes")
        response = self._make_request(
            'POST',
            '/api/pending-shipments',
            json={'instanceId': instance_id}
        )

        if isinstance(response, list):
            return response
        elif isinstance(response, dict):
            return response.get('data', response.get('shipments', []))

        return []

    def get_user_info(self, instance_id: str) -> Dict[str, Any]:
        """
        Obtiene información del usuario (requiere Plan Pro).

        Args:
            instance_id: ID de la instancia Pro

        Returns:
            Información del usuario
        """
        logger.info(f"Obteniendo información del usuario")
        return self._make_request(
            'POST',
            '/api/get-user',
            json={'instanceId': instance_id}
        )

    # ─── Health Check ───────────────────────────────────

    def health_check(self) -> bool:
        """
        Verifica si la API está disponible.

        Returns:
            True si está disponible
        """
        try:
            agencies = self.list_agencies()
            logger.info("Health check: OK")
            return isinstance(agencies, list) and len(agencies) > 0
        except Exception as e:
            logger.error(f"Health check falló: {e}")
            return False


# ════════════════════════════════════════════════════════════
# EJEMPLOS DE USO
# ════════════════════════════════════════════════════════════

if __name__ == '__main__':
    # Inicializar cliente
    api_key = "tu-api-key-aqui"
    client = ShalomAPIClient(api_key=api_key, verbose=True)

    print("═" * 70)
    print("SHALOM API CLIENT - EJEMPLOS DE USO")
    print("═" * 70)

    # Health check
    print("\n1. Verificando disponibilidad...")
    if client.health_check():
        print("✅ API disponible")
    else:
        print("❌ API no disponible")
        exit(1)

    # Listar agencias
    print("\n2. Listando agencias...")
    try:
        agencies = client.list_agencies()
        print(f"✅ Total agencias: {len(agencies)}")
        if agencies:
            for agency in agencies[:3]:
                print(f"   - {agency.get('lugar_over')} ({agency.get('departamento')})")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Buscar agencias
    print("\n3. Buscando agencias (Lima)...")
    try:
        results = client.search_agencies("lima")
        print(f"✅ Encontradas {len(results)} agencias")
        if results:
            for r in results[:2]:
                print(f"   - {r.get('lugar_over')}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Tracking
    print("\n4. Rastreando pedido...")
    try:
        # Reemplaza con valores reales
        # tracking = client.track_shipment("66479331", "3KTH")
        # print(f"✅ Tracking: {tracking}")
        print("   (Descomenta para usar con datos reales)")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "═" * 70)
    print("Para más ejemplos, ver shalom_examples.py")
    print("═" * 70)
