#!/usr/bin/env python3
"""
Script para probar conexión a Decolecta de forma aislada
Uso: python3 test_decolecta.py <DNI>
"""
import sys
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

from decolecta_service import consultar_dni_decolecta, DniLookupError

def main():
    if len(sys.argv) < 2:
        print("❌ Uso: python3 test_decolecta.py <DNI>")
        print("   Ejemplo: python3 test_decolecta.py 12345678")
        sys.exit(1)

    dni = sys.argv[1]

    # Validar DNI
    if not dni.isdigit() or len(dni) != 8:
        print(f"❌ DNI inválido: debe tener exactamente 8 dígitos")
        sys.exit(1)

    # Verificar que la API key esté configurada
    api_key = os.getenv("DECOLECTA_API_TOKEN", "").strip()
    if not api_key:
        print("❌ DECOLECTA_API_TOKEN no está configurado en .env")
        sys.exit(1)

    print(f"🔍 Buscando DNI: {dni}")
    print(f"🔑 API Token: {api_key[:20]}...")
    print()

    try:
        resultado = consultar_dni_decolecta(dni)
        print("✅ Éxito! Datos obtenidos de Decolecta:")
        print()
        for key, value in resultado.items():
            print(f"  • {key:20s}: {value}")
    except DniLookupError as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
