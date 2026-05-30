#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servicio Shalom - Capa de Integración con FastAPI
===================================================

Proporciona una capa de servicio para usar Shalom API en aplicaciones FastAPI.
Incluye caché, validaciones, y manejo de errores.

Uso:
    from shalom_service import get_shalom_client, ShalonService

    async def my_endpoint():
        client = get_shalom_client()
        orders = client.tracking.search(numero="123")
"""

import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from functools import lru_cache
from pydantic import BaseModel, Field, validator

from shalom_api_client import (
    ShalomAPIClient,
    DocumentType,
    ShalomAPIError,
    ShalomAuthError,
    ShalomRateLimitError,
    ShalomNotFoundError,
    ShalomValidationError
)

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ════════════════════════════════════════════════════════════

class ShalomConfig:
    """Configuración centralizada para Shalom"""

    API_KEY: str = os.getenv('SHALOM_API_KEY', '')
    EMAIL: str = os.getenv('SHALOM_EMAIL', '')
    PASSWORD: str = os.getenv('SHALOM_PASSWORD', '')
    BASE_URL: str = os.getenv('SHALOM_BASE_URL', 'https://api.shalom-api-peru.com')
    TIMEOUT: int = int(os.getenv('SHALOM_TIMEOUT', '30'))
    MAX_RETRIES: int = int(os.getenv('SHALOM_MAX_RETRIES', '3'))
    VERBOSE: bool = os.getenv('SHALOM_VERBOSE', 'False').lower() == 'true'

    @classmethod
    def validate(cls) -> bool:
        """Valida que la configuración sea completa"""
        if not cls.API_KEY:
            logger.warning("SHALOM_API_KEY no configurada")
            return False
        return True


# ════════════════════════════════════════════════════════════
# SINGLETON CLIENT
# ════════════════════════════════════════════════════════════

_client_instance: Optional[ShalomAPIClient] = None


def get_shalom_client() -> ShalomAPIClient:
    """
    Obtiene instancia singleton del cliente Shalom.
    Garantiza que solo hay una instancia en toda la aplicación.
    """
    global _client_instance

    if _client_instance is None:
        if not ShalomConfig.validate():
            raise RuntimeError(
                "Configuración de Shalom incompleta. "
                "Asegúrate de establecer SHALOM_API_KEY en variables de entorno."
            )

        _client_instance = ShalomAPIClient(
            api_key=ShalomConfig.API_KEY,
            base_url=ShalomConfig.BASE_URL,
            timeout=ShalomConfig.TIMEOUT,
            max_retries=ShalomConfig.MAX_RETRIES,
            verbose=ShalomConfig.VERBOSE
        )

        logger.info("Cliente Shalom inicializado")

    return _client_instance


def reset_client():
    """Reinicia la instancia del cliente (útil para testing)"""
    global _client_instance
    _client_instance = None


# ════════════════════════════════════════════════════════════
# PYDANTIC SCHEMAS
# ════════════════════════════════════════════════════════════

class TrackingRequest(BaseModel):
    """Request para rastrear un envío"""
    numero: Optional[str] = Field(None, description="Número de guía")
    codigo: Optional[str] = Field(None, description="Código del envío")
    ose_id: Optional[str] = Field(None, description="ID del sistema")

    @validator('*', pre=True)
    def empty_string_to_none(cls, v):
        if v == '':
            return None
        return v

    class Config:
        example = {
            "numero": "123456"
        }


class AgencySearchRequest(BaseModel):
    """Request para buscar agencias"""
    q: Optional[str] = Field(None, description="Término de búsqueda")
    departamento: Optional[str] = Field(None, description="Nombre del departamento")
    provincia: Optional[str] = Field(None, description="Nombre de la provincia")
    aereo: Optional[bool] = Field(None, description="Filtrar por servicio aéreo")

    class Config:
        example = {
            "departamento": "Lima",
            "provincia": "Lima"
        }


class PersonSearchRequest(BaseModel):
    """Request para buscar datos de persona"""
    document: str = Field(..., description="Número de documento")
    doc_type: str = Field(..., description="Tipo: DNI, RUC, CE")

    @validator('doc_type')
    def validate_doc_type(cls, v):
        valid_types = ['DNI', 'RUC', 'CE']
        if v.upper() not in valid_types:
            raise ValueError(f"Tipo debe ser uno de: {valid_types}")
        return v.upper()

    class Config:
        example = {
            "document": "12345678",
            "doc_type": "DNI"
        }


class TariffRequest(BaseModel):
    """Request para calcular tarifa"""
    origin_terminal_id: str = Field(..., description="Terminal de origen")
    destiny_terminal_id: str = Field(..., description="Terminal de destino")
    product_id: Optional[str] = Field(None, description="ID del producto")
    dimensions: Optional[Dict[str, float]] = Field(None, description="Dimensiones")

    class Config:
        example = {
            "origin_terminal_id": "LIMACENTRAL",
            "destiny_terminal_id": "AREQPUERTO",
            "product_id": "CAJA_PEQUENA"
        }


class SenderReceiverData(BaseModel):
    """Datos de remitente o destinatario"""
    nombre: str
    documento: str
    documento_tipo: str = Field(..., description="DNI, RUC, CE")
    email: str
    telefono: str


class CreateOrderRequest(BaseModel):
    """Request para crear una guía de envío"""
    origin_terminal_id: str
    destiny_terminal_id: str
    product_id: str
    sender: SenderReceiverData
    receiver: SenderReceiverData
    pickup_code: str
    quantity: int = Field(1, ge=1)
    warranty: bool = False
    collection_service: bool = False
    aereo: bool = False
    documentation: Optional[str] = None
    declaracion_jurada: bool = False
    contacto_doc: Optional[str] = None

    class Config:
        example = {
            "origin_terminal_id": "LIMACENTRAL",
            "destiny_terminal_id": "AREQPUERTO",
            "product_id": "CAJA_PEQUENA",
            "sender": {
                "nombre": "Juan Pérez",
                "documento": "12345678",
                "documento_tipo": "DNI",
                "email": "juan@example.com",
                "telefono": "987654321"
            },
            "receiver": {
                "nombre": "María García",
                "documento": "87654321",
                "documento_tipo": "DNI",
                "email": "maria@example.com",
                "telefono": "912345678"
            },
            "pickup_code": "PICKUP123"
        }


# ════════════════════════════════════════════════════════════
# SERVICIO SHALOM
# ════════════════════════════════════════════════════════════

class ShalomService:
    """
    Servicio de alto nivel para operaciones con Shalom API.
    Proporciona métodos simplificados y caché opcional.
    """

    def __init__(self, client: Optional[ShalomAPIClient] = None):
        self.client = client or get_shalom_client()
        self._session_token = None

    # ─── TRACKING ────────────────────────────────────────

    async def track_order(self, request: TrackingRequest) -> Dict[str, Any]:
        """
        Rastrear un envío.

        Args:
            request: TrackingRequest con numero, codigo o ose_id

        Returns:
            Detalles del envío

        Raises:
            HTTPException: En caso de error
        """
        try:
            if not any([request.numero, request.codigo, request.ose_id]):
                raise ShalomValidationError(
                    "Se requiere al menos uno: numero, codigo, ose_id"
                )

            return self.client.tracking.search(
                numero=request.numero,
                codigo=request.codigo,
                ose_id=request.ose_id
            )
        except ShalomAPIError as e:
            logger.error(f"Error tracking: {e}")
            raise

    async def get_tracking_events(self, ose_id: str) -> List[Dict[str, Any]]:
        """Obtener eventos de un envío"""
        try:
            return self.client.tracking.get_events(ose_id)
        except ShalomAPIError as e:
            logger.error(f"Error getting events: {e}")
            raise

    async def download_tracking_voucher(self, ose_id: str) -> bytes:
        """Descargar voucher de tracking"""
        try:
            return self.client.tracking.get_voucher(ose_id)
        except ShalomAPIError as e:
            logger.error(f"Error downloading voucher: {e}")
            raise

    # ─── AGENCIAS ────────────────────────────────────────

    async def list_agencies(
        self,
        page: int = 1,
        per_page: int = 100
    ) -> Dict[str, Any]:
        """Listar agencias con paginación"""
        try:
            return self.client.agencies.list(page=page, per_page=per_page)
        except ShalomAPIError as e:
            logger.error(f"Error listing agencies: {e}")
            raise

    async def search_agencies(
        self,
        request: AgencySearchRequest
    ) -> List[Dict[str, Any]]:
        """Buscar agencias con filtros"""
        try:
            return self.client.agencies.search(
                q=request.q,
                departamento=request.departamento,
                provincia=request.provincia,
                aereo=request.aereo
            )
        except ShalomAPIError as e:
            logger.error(f"Error searching agencies: {e}")
            raise

    async def get_agency(self, agency_id: int) -> Dict[str, Any]:
        """Obtener detalles de una agencia"""
        try:
            return self.client.agencies.get(agency_id)
        except ShalomAPIError as e:
            logger.error(f"Error getting agency {agency_id}: {e}")
            raise

    # ─── UBICACIONES ─────────────────────────────────────

    async def get_departments(self) -> List[Dict[str, Any]]:
        """Obtener departamentos del Perú"""
        try:
            return self.client.locations.get_departments()
        except ShalomAPIError as e:
            logger.error(f"Error getting departments: {e}")
            raise

    async def get_provinces(self, dep_id: str) -> List[Dict[str, Any]]:
        """Obtener provincias de un departamento"""
        try:
            return self.client.locations.get_provinces(dep_id)
        except ShalomAPIError as e:
            logger.error(f"Error getting provinces: {e}")
            raise

    async def get_districts(
        self,
        dep_id: str,
        prov_id: str
    ) -> List[Dict[str, Any]]:
        """Obtener distritos de una provincia"""
        try:
            return self.client.locations.get_districts(dep_id, prov_id)
        except ShalomAPIError as e:
            logger.error(f"Error getting districts: {e}")
            raise

    # ─── ÓRDENES ────────────────────────────────────────

    async def get_products(self) -> List[Dict[str, Any]]:
        """Obtener catálogo de productos"""
        try:
            return self.client.orders.get_products()
        except ShalomAPIError as e:
            logger.error(f"Error getting products: {e}")
            raise

    async def search_person(
        self,
        request: PersonSearchRequest
    ) -> Dict[str, Any]:
        """Buscar datos de persona por documento"""
        try:
            doc_type = DocumentType[request.doc_type]
            return self.client.orders.search_person(
                document=request.document,
                doc_type=doc_type
            )
        except ShalomAPIError as e:
            logger.error(f"Error searching person: {e}")
            raise

    async def calculate_tariff(
        self,
        request: TariffRequest
    ) -> Dict[str, Any]:
        """Calcular tarifa de envío"""
        try:
            return self.client.orders.calculate_tariff(
                origin_terminal_id=request.origin_terminal_id,
                destiny_terminal_id=request.destiny_terminal_id,
                product_id=request.product_id,
                dimensions=request.dimensions
            )
        except ShalomAPIError as e:
            logger.error(f"Error calculating tariff: {e}")
            raise

    async def create_order(
        self,
        request: CreateOrderRequest
    ) -> Dict[str, Any]:
        """
        Crear nueva guía de envío.
        Requiere estar autenticado primero.
        """
        try:
            if not self._session_token:
                raise RuntimeError(
                    "No autenticado. Llama a authenticate() primero."
                )

            return self.client.orders.create(
                origin_terminal_id=request.origin_terminal_id,
                destiny_terminal_id=request.destiny_terminal_id,
                product_id=request.product_id,
                sender=request.sender.dict(),
                receiver=request.receiver.dict(),
                pickup_code=request.pickup_code,
                quantity=request.quantity,
                warranty=request.warranty,
                collection_service=request.collection_service,
                aereo=request.aereo,
                documentation=request.documentation,
                declaracion_jurada=request.declaracion_jurada,
                contacto_doc=request.contacto_doc
            )
        except ShalomAPIError as e:
            logger.error(f"Error creating order: {e}")
            raise

    async def list_orders(self) -> List[Dict[str, Any]]:
        """Listar todas las órdenes (requiere autenticación)"""
        try:
            if not self._session_token:
                raise RuntimeError("No autenticado")
            return self.client.orders.list()
        except ShalomAPIError as e:
            logger.error(f"Error listing orders: {e}")
            raise

    async def delete_order(self, order_id: str) -> bool:
        """Eliminar una orden (requiere autenticación)"""
        try:
            if not self._session_token:
                raise RuntimeError("No autenticado")
            return self.client.orders.delete(order_id)
        except ShalomAPIError as e:
            logger.error(f"Error deleting order: {e}")
            raise

    async def download_order_label(self, ose_id: str) -> bytes:
        """Descargar etiqueta de envío en PDF"""
        try:
            return self.client.orders.get_label(ose_id)
        except ShalomAPIError as e:
            logger.error(f"Error downloading label: {e}")
            raise

    async def download_order_voucher(self, ose_id: str) -> bytes:
        """Descargar voucher de orden en PDF"""
        try:
            return self.client.orders.get_voucher(ose_id)
        except ShalomAPIError as e:
            logger.error(f"Error downloading voucher: {e}")
            raise

    # ─── AUTENTICACIÓN ──────────────────────────────────

    async def authenticate(self, email: str, password: str) -> bool:
        """
        Autenticar con credenciales Shalom Pro.
        Necesario para crear/listar/eliminar órdenes.
        """
        try:
            self._session_token = self.client.authenticate(email, password)
            logger.info(f"Autenticado como: {email}")
            return True
        except ShalomAuthError as e:
            logger.error(f"Error de autenticación: {e}")
            raise

    async def revoke_session(self) -> bool:
        """Revocar session actual"""
        try:
            result = self.client.revoke_session()
            self._session_token = None
            logger.info("Sesión revocada")
            return result
        except ShalomAPIError as e:
            logger.error(f"Error revocando sesión: {e}")
            raise

    # ─── HEALTH CHECKS ──────────────────────────────────

    async def health_check(self) -> bool:
        """Verificar disponibilidad de la API"""
        try:
            return self.client.health_check()
        except Exception as e:
            logger.error(f"Health check falló: {e}")
            return False

    async def ready_check(self) -> bool:
        """Verificar si API está lista"""
        try:
            return self.client.ready_check()
        except Exception as e:
            logger.error(f"Ready check falló: {e}")
            return False


# ════════════════════════════════════════════════════════════
# SINGLETON SERVICE
# ════════════════════════════════════════════════════════════

_service_instance: Optional[ShalomService] = None


def get_shalom_service() -> ShalomService:
    """Obtiene instancia singleton del servicio Shalom"""
    global _service_instance

    if _service_instance is None:
        _service_instance = ShalomService(get_shalom_client())

    return _service_instance


# ════════════════════════════════════════════════════════════
# DEPENDENCY INJECTION PARA FASTAPI
# ════════════════════════════════════════════════════════════

async def get_service() -> ShalomService:
    """Dependency para inyectar en endpoints de FastAPI"""
    return get_shalom_service()


# Ejemplo de uso en FastAPI:
# ────────────────────────
# from fastapi import FastAPI, Depends
# from shalom_service import ShalomService, get_service
#
# app = FastAPI()
#
# @app.get("/track/{numero}")
# async def track_order(
#     numero: str,
#     service: ShalomService = Depends(get_service)
# ):
#     return await service.track_order(numero)
