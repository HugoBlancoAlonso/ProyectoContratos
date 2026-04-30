#!/usr/bin/env python
"""Script para probar la API"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_endpoints():
    """Prueba los endpoints básicos"""
    
    print("\n" + "="*60)
    print("TEST 1: GET / (Info general)")
    print("="*60)
    try:
        r = requests.get(f'{BASE_URL}/')
        print(f"Status: {r.status_code}")
        print(json.dumps(r.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*60)
    print("TEST 2: GET /health (Verificar salud)")
    print("="*60)
    try:
        r = requests.get(f'{BASE_URL}/health')
        print(f"Status: {r.status_code}")
        print(json.dumps(r.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*60)
    print("TEST 3: GET /status (Estado detallado)")
    print("="*60)
    try:
        r = requests.get(f'{BASE_URL}/status')
        print(f"Status: {r.status_code}")
        print(json.dumps(r.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*60)
    print("✅ Todos los tests completados")
    print("="*60)

if __name__ == "__main__":
    test_endpoints()
