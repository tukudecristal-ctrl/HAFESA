#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejemplos Prácticos - Shalom API Perú
====================================

Casos de uso reales para el cliente de Shalom API.
Incluye ejemplos de tracking, agencias, cálculo de tarifas y creación de guías.

Documentación: ver shalom_api_client.py
"""

from shalom_api_client import (
    ShalomAPIClient,
    DocumentType,
    ShalomAPIError,
    ShalomValidationError
)
import json
from typing import Dict, Any


# ════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ════════════════════════════════════════════════════════════

# Reemplaza con tu API Key real
API_KEY = "tu-api-key-aqui"
SHALOM_EMAIL = "tu-email@ejemplo.com"
SHALOM_PASSWORD = "tu-contraseña"


# ════════════════════════════════════════════════════════════
# UTILIDADES
# ════════════════════════════════════════════════════════════

def pretty_print(title: str, data: Any):
    """Imprime datos con formato bonito"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")
    print(json.dumps(data, indent=2, ensure_ascii=False, default=str))


def print_section(title: str):
    """Imprime un título de sección"""
    print(f"\n{'─'*70}")
    print(f"  {title}")
    print(f"{'─'*70}")


# ════════════════════════════════════════════════════════════
# EJEMPLO 1: TRACKING DE ENVÍOS
# ════════════════════════════════════════════════════════════

def example_tracking(client: ShalomAPIClient):
    """Ejemplo: Rastrear un envío existente"""
    print_section("EJEMPLO 1: RASTREAR ENVÍO")

    try:
        # Opción 1: Buscar por número de guía
        print("\n1. Buscando envío por número...")
        # order = client.tracking.search(numero="NGN01123456")
        # pretty_print("Detalles del Envío", order)

        # Opción 2: Buscar por código
        print("\n2. Buscando envío por código...")
        # order = client.tracking.search(codigo="ABC123")
        # pretty_print("Detalles del Envío", order)

        # Opción 3: Obtener eventos/hitos del envío
        print("\n3. Obteniendo eventos del envío...")
        # ose_id = "NGN01-123456-001"  # Del resultado anterior
        # events = client.tracking.get_events(ose_id)
        # pretty_print("Eventos del Envío", events)

        # Opción 4: Descargar voucher
        print("\n4. Descargando voucher (PDF)...")
        # voucher_pdf = client.tracking.get_voucher(ose_id)
        # with open('voucher.pdf', 'wb') as f:
        #     f.write(voucher_pdf)
        # print("✓ Voucher descargado: voucher.pdf")

        print("\n(Descomenta las líneas para ejecutar con datos reales)")

    except ShalomAPIError as e:
        print(f"❌ Error de API: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


# ════════════════════════════════════════════════════════════
# EJEMPLO 2: BÚSQUEDA DE AGENCIAS
# ════════════════════════════════════════════════════════════

def example_agencies(client: ShalomAPIClient):
    """Ejemplo: Listar y buscar agencias"""
    print_section("EJEMPLO 2: AGENCIAS")

    try:
        # Opción 1: Listar todas las agencias
        print("\n1. Listando primeras 10 agencias...")
        agencies_page = client.agencies.list(page=1, per_page=10)
        if agencies_page.get('agencies'):
            for agency in agencies_page['agencies'][:5]:
                print(f"  - {agency.get('nombre')} (ID: {agency.get('id')})")
        print(f"Total en esta página: {len(agencies_page.get('agencies', []))}")

        # Opción 2: Buscar agencias en Lima
        print("\n2. Buscando agencias en Lima...")
        lima_agencies = client.agencies.search(
            departamento="Lima",
            provincia="Lima"
        )
        print(f"Encontradas {len(lima_agencies)} agencias en Lima")
        if lima_agencies:
            print(f"  Ejemplo: {lima_agencies[0].get('nombre')}")

        # Opción 3: Buscar agencias con servicio aéreo
        print("\n3. Buscando agencias con servicio aéreo...")
        air_agencies = client.agencies.search(aereo=True)
        print(f"Encontradas {len(air_agencies)} agencias con servicio aéreo")

        # Opción 4: Obtener detalles de una agencia específica
        if lima_agencies:
            agency_id = lima_agencies[0].get('id')
            print(f"\n4. Obteniendo detalles de agencia {agency_id}...")
            agency_detail = client.agencies.get(agency_id)
            pretty_print(f"Detalles de Agencia {agency_id}", agency_detail)

    except ShalomAPIError as e:
        print(f"❌ Error de API: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


# ════════════════════════════════════════════════════════════
# EJEMPLO 3: UBICACIONES GEOGRÁFICAS
# ════════════════════════════════════════════════════════════

def example_locations(client: ShalomAPIClient):
    """Ejemplo: Obtener departamentos, provincias y distritos"""
    print_section("EJEMPLO 3: UBICACIONES GEOGRÁFICAS")

    try:
        # Obtener departamentos
        print("\n1. Obteniendo departamentos del Perú...")
        departments = client.locations.get_departments()
        print(f"Total departamentos: {len(departments)}")
        print(f"Primeros 5: {[d.get('nombre') for d in departments[:5]]}")

        # Obtener provincias de un departamento
        if departments:
            dept = departments[0]
            dept_id = dept.get('id')
            print(f"\n2. Obteniendo provincias de {dept.get('nombre')} (ID: {dept_id})...")
            provinces = client.locations.get_provinces(dept_id)
            print(f"Total provincias: {len(provinces)}")
            print(f"Primeras 3: {[p.get('nombre') for p in provinces[:3]]}")

            # Obtener distritos de una provincia
            if provinces:
                prov = provinces[0]
                prov_id = prov.get('id')
                print(f"\n3. Obteniendo distritos de {prov.get('nombre')} (ID: {prov_id})...")
                districts = client.locations.get_districts(dept_id, prov_id)
                print(f"Total distritos: {len(districts)}")
                print(f"Primeros 5: {[d.get('nombre') for d in districts[:5]]}")

    except ShalomAPIError as e:
        print(f"❌ Error de API: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


# ════════════════════════════════════════════════════════════
# EJEMPLO 4: PRODUCTOS Y BÚSQUEDA DE PERSONAS
# ════════════════════════════════════════════════════════════

def example_products_and_persons(client: ShalomAPIClient):
    """Ejemplo: Obtener productos y resolver datos de personas"""
    print_section("EJEMPLO 4: PRODUCTOS Y BÚSQUEDA DE PERSONAS")

    try:
        # Obtener productos disponibles
        print("\n1. Obteniendo catálogo de productos...")
        products = client.orders.get_products()
        print(f"Total productos: {len(products)}")
        print("\nProductos disponibles:")
        for product in products[:10]:
            print(f"  - {product.get('nombre')} (ID: {product.get('id')})")
            dims = product.get('default_dimensions', {})
            if dims:
                print(f"    Dimensiones: {dims.get('length')} x {dims.get('width')} x {dims.get('height')} cm")

        # Buscar persona por DNI
        print("\n2. Buscando persona por DNI...")
        # Reemplaza con un DNI válido
        # person = client.orders.search_person(
        #     document="12345678",
        #     doc_type=DocumentType.DNI
        # )
        # pretty_print("Datos de la Persona", person)

        # Buscar persona por RUC
        print("   (Descomenta para buscar con un DNI válido)")

    except ShalomValidationError as e:
        print(f"❌ Error de validación: {e}")
    except ShalomAPIError as e:
        print(f"❌ Error de API: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


# ════════════════════════════════════════════════════════════
# EJEMPLO 5: CÁLCULO DE TARIFAS
# ════════════════════════════════════════════════════════════

def example_tariff_calculation(client: ShalomAPIClient):
    """Ejemplo: Calcular tarifas de envío"""
    print_section("EJEMPLO 5: CÁLCULO DE TARIFAS")

    try:
        print("\n1. Calculando tarifa Lima → Arequipa...")
        # Estos IDs de terminal son ejemplos - obtener los reales de la API
        # origin_terminal_id = "LIMACENTRAL"
        # destiny_terminal_id = "AREQPUERTO"

        # tariff = client.orders.calculate_tariff(
        #     origin_terminal_id=origin_terminal_id,
        #     destiny_terminal_id=destiny_terminal_id
        # )
        # pretty_print("Desglose de Tarifa", tariff)

        print("   (Descomenta para calcular con IDs de terminal válidos)")

        # Con producto específico
        print("\n2. Calculando tarifa con producto específico...")
        # tariff_product = client.orders.calculate_tariff(
        #     origin_terminal_id=origin_terminal_id,
        #     destiny_terminal_id=destiny_terminal_id,
        #     product_id="SOBRE_GRANDE"
        # )
        # pretty_print("Tarifa para Producto", tariff_product)

        # Con dimensiones personalizadas
        print("\n3. Calculando tarifa con dimensiones personalizadas...")
        # tariff_custom = client.orders.calculate_tariff(
        #     origin_terminal_id=origin_terminal_id,
        #     destiny_terminal_id=destiny_terminal_id,
        #     dimensions={'length': 50, 'width': 40, 'height': 30}
        # )
        # pretty_print("Tarifa Personalizada", tariff_custom)

    except ShalomAPIError as e:
        print(f"❌ Error de API: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


# ════════════════════════════════════════════════════════════
# EJEMPLO 6: CREAR GUÍA DE ENVÍO (requiere autenticación)
# ════════════════════════════════════════════════════════════

def example_create_order(client: ShalomAPIClient):
    """Ejemplo: Crear una nueva guía de envío"""
    print_section("EJEMPLO 6: CREAR GUÍA DE ENVÍO")

    try:
        # Paso 1: Autenticar con credenciales Shalom Pro
        print("\n1. Autenticando con Shalom Pro...")
        # session = client.authenticate(email=SHALOM_EMAIL, password=SHALOM_PASSWORD)
        # print(f"✓ Autenticado. Token expira en: {session.expires_at}")

        # Paso 2: Crear envío
        print("\n2. Creando guía de envío...")
        # new_order = client.orders.create(
        #     origin_terminal_id="LIMACENTRAL",
        #     destiny_terminal_id="AREQPUERTO",
        #     product_id="CAJA_PEQUENA",
        #     sender={
        #         'nombre': 'Juan Pérez',
        #         'documento': '12345678',
        #         'documento_tipo': 'DNI',
        #         'email': 'juan@example.com',
        #         'telefono': '987654321'
        #     },
        #     receiver={
        #         'nombre': 'María García',
        #         'documento': '87654321',
        #         'documento_tipo': 'DNI',
        #         'email': 'maria@example.com',
        #         'telefono': '912345678'
        #     },
        #     pickup_code="PICKUP123",
        #     quantity=1,
        #     warranty=True,
        #     collection_service=False
        # )
        # pretty_print("Guía Creada", new_order)
        # ose_id = new_order.get('codigo')

        # Paso 3: Descargar etiqueta
        # if ose_id:
        #     print(f"\n3. Descargando etiqueta para {ose_id}...")
        #     label_pdf = client.orders.get_label(ose_id)
        #     with open('etiqueta.pdf', 'wb') as f:
        #         f.write(label_pdf)
        #     print("✓ Etiqueta descargada: etiqueta.pdf")

        # Paso 4: Revocar sesión
        # print("\n4. Revocando sesión...")
        # client.revoke_session()
        # print("✓ Sesión revocada")

        print("   (Descomenta para ejecutar con credenciales válidas)")

    except ShalomAPIError as e:
        print(f"❌ Error de API: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


# ════════════════════════════════════════════════════════════
# EJEMPLO 7: LISTAR Y GESTIONAR ÓRDENES
# ════════════════════════════════════════════════════════════

def example_manage_orders(client: ShalomAPIClient):
    """Ejemplo: Listar, descargar y eliminar órdenes"""
    print_section("EJEMPLO 7: GESTIONAR ÓRDENES")

    try:
        # Autenticar primero
        print("\n1. Autenticando...")
        # session = client.authenticate(email=SHALOM_EMAIL, password=SHALOM_PASSWORD)
        # print(f"✓ Autenticado")

        # Listar órdenes
        print("\n2. Listando todas las órdenes...")
        # orders = client.orders.list()
        # print(f"Total órdenes: {len(orders)}")
        # for order in orders[:5]:
        #     print(f"  - Guía: {order.get('guia')}, Código: {order.get('codigo')}")

        # Descargar voucher de orden
        # if orders:
        #     ose_id = orders[0].get('codigo')
        #     print(f"\n3. Descargando voucher de {ose_id}...")
        #     voucher = client.orders.get_voucher(ose_id)
        #     with open('voucher_orden.pdf', 'wb') as f:
        #         f.write(voucher)
        #     print("✓ Voucher descargado")

        # Eliminar orden
        # print(f"\n4. Eliminando orden {ose_id}...")
        # deleted = client.orders.delete(ose_id)
        # if deleted:
        #     print("✓ Orden eliminada")

        # Revocar sesión
        # print("\n5. Revocando sesión...")
        # client.revoke_session()

        print("   (Descomenta para ejecutar con credenciales válidas)")

    except ShalomAPIError as e:
        print(f"❌ Error de API: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


# ════════════════════════════════════════════════════════════
# EJEMPLO 8: MANEJO DE ERRORES
# ════════════════════════════════════════════════════════════

def example_error_handling():
    """Ejemplo: Manejo robusto de errores"""
    print_section("EJEMPLO 8: MANEJO DE ERRORES")

    client = ShalomAPIClient(api_key=API_KEY)

    print("\n1. API Key inválida:")
    try:
        bad_client = ShalomAPIClient(api_key="api-key-invalida")
        bad_client.agencies.list(per_page=1)
    except Exception as e:
        print(f"   ✓ Capturado: {type(e).__name__}")

    print("\n2. Parámetros inválidos:")
    try:
        # Sin parámetros de búsqueda
        client.tracking.search()
    except ShalomValidationError as e:
        print(f"   ✓ Capturado: {type(e).__name__}: {e}")

    print("\n3. Recurso no encontrado:")
    try:
        client.agencies.get(999999999)
    except Exception as e:
        print(f"   ✓ Capturado: {type(e).__name__}")

    print("\n4. Rate limiting:")
    print("   El cliente maneja automáticamente:")
    print("   - Esperas cuando se alcanza el límite")
    print("   - Reintentos con backoff exponencial")
    print("   - Logging de intentos")


# ════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════

def main():
    """Ejecuta todos los ejemplos"""
    print("\n" + "="*70)
    print("  EJEMPLOS DE USO - SHALOM API CLIENTE PYTHON")
    print("="*70)

    # Inicializar cliente
    client = ShalomAPIClient(api_key=API_KEY, verbose=False)

    # Verificar que la API esté disponible
    print("\nVerificando disponibilidad de la API...")
    if not client.health_check():
        print("⚠️  La API no está disponible. Algunos ejemplos pueden fallar.")
    else:
        print("✓ API disponible")

    # Ejecutar ejemplos
    example_tracking(client)
    example_agencies(client)
    example_locations(client)
    example_products_and_persons(client)
    example_tariff_calculation(client)
    example_create_order(client)
    example_manage_orders(client)
    example_error_handling()

    print("\n" + "="*70)
    print("  FIN DE EJEMPLOS")
    print("="*70)
    print("""
PRÓXIMOS PASOS:

1. Reemplaza tu API_KEY en la línea 13
2. Para ejemplos que requieren autenticación, también actualiza:
   - SHALOM_EMAIL (línea 14)
   - SHALOM_PASSWORD (línea 15)
3. Descomenta los ejemplos que quieras ejecutar
4. Ejecuta: python3 shalom_examples.py

DOCUMENTACIÓN:
- Ver docstrings en shalom_api_client.py para detalles completos
- Consulta https://shalom-api-peru.com/docs para especificaciones API

INTEGRACIÓN EN VERDE:
- Copiar shalom_api_client.py a tu backend
- Importar: from .shalom_api_client import ShalomAPIClient
- Usar en vistas/servicios de FastAPI
    """)


if __name__ == '__main__':
    main()
