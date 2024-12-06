import asyncio
import json
from pathlib import Path
import requests
import time

# URL base de la API (ajustar según tu configuración)
API_BASE = "http://localhost:8000"

def cargar_plantilla(nombre_plantilla: str):
    """Carga una plantilla desde el directorio de templates."""
    ruta_plantilla = Path(__file__).parent.parent / 'app' / 'recon' / 'templates' / nombre_plantilla
    with open(ruta_plantilla, 'r', encoding='utf-8') as f:
        return json.load(f)

async def ejecutar_recon():
    """Ejemplo de uso del módulo RECON."""
    
    # 1. Cargar plantilla
    plantilla = cargar_plantilla('secop_ii.json')
    
    # 2. Iniciar tarea de reconocimiento
    response = requests.post(f"{API_BASE}/recon/iniciar", json=plantilla)
    task_id = response.json()["task_id"]
    print(f"Tarea iniciada con ID: {task_id}")
    
    # 3. Monitorear progreso
    while True:
        response = requests.get(f"{API_BASE}/recon/estado/{task_id}")
        estado = response.json()
        
        print(f"Estado actual: {estado['estado']}")
        
        if estado['estado'] in ['completado', 'error']:
            if 'resultados' in estado:
                print("\nResultados:")
                for resultado in estado['resultados']:
                    print(f"\nDocumento: {resultado['documento']}")
                    print(f"Estado: {resultado['resultado']['estado']}")
                    if resultado['resultado']['estado'] == 'completado':
                        print("Datos extraídos:")
                        for campo, valor in resultado['resultado']['resultados'].items():
                            print(f"  {campo}: {valor}")
            
            if estado['estado'] == 'error' and 'error' in estado:
                print(f"\nError: {estado['error']}")
            
            break
        
        await asyncio.sleep(5)  # Esperar 5 segundos antes de consultar de nuevo

def main():
    """Función principal de ejemplo."""
    print("Iniciando ejemplo de uso del módulo RECON...")
    
    # Verificar que el servidor esté corriendo
    try:
        requests.get(f"{API_BASE}/docs")
    except requests.exceptions.ConnectionError:
        print("Error: El servidor FastAPI no está corriendo.")
        print("Inicia el servidor con: uvicorn app.main:app --reload")
        return
    
    # Ejecutar el ejemplo
    asyncio.run(ejecutar_recon())

if __name__ == "__main__":
    main()
