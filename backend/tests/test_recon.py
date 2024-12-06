import asyncio
import json
import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def load_template(template_name: str):
    """Carga una plantilla desde el directorio de templates."""
    template_path = Path(__file__).parent.parent / 'app' / 'recon' / 'templates' / template_name
    with open(template_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def test_iniciar_recon():
    """Prueba el inicio de una tarea de reconocimiento."""
    template = load_template('secop_ii.json')
    
    response = client.post("/recon/iniciar", json=template)
    assert response.status_code == 200
    assert "task_id" in response.json()
    
    task_id = response.json()["task_id"]
    return task_id

def test_obtener_estado():
    """Prueba la obtención del estado de una tarea."""
    task_id = test_iniciar_recon()
    
    # Esperar un momento para que la tarea inicie
    asyncio.run(asyncio.sleep(1))
    
    response = client.get(f"/recon/estado/{task_id}")
    assert response.status_code == 200
    
    estado = response.json()
    assert estado["task_id"] == task_id
    assert estado["estado"] in ["iniciado", "en_progreso", "completado", "error"]

def test_cancelar_tarea():
    """Prueba la cancelación de una tarea."""
    task_id = test_iniciar_recon()
    
    # Esperar un momento para asegurarnos de que la tarea esté en progreso
    asyncio.run(asyncio.sleep(0.5))
    
    # Verificar que la tarea está en progreso
    estado_inicial = client.get(f"/recon/estado/{task_id}").json()
    assert estado_inicial["estado"] in ["iniciado", "en_progreso"]
    
    # Intentar cancelar la tarea
    response = client.delete(f"/recon/cancelar/{task_id}")
    assert response.status_code == 200
    
    # Esperar un momento para que se procese la cancelación
    asyncio.run(asyncio.sleep(0.5))
    
    # Verificar que la tarea fue cancelada
    estado_final = client.get(f"/recon/estado/{task_id}").json()
    assert estado_final["estado"] == "cancelado"

def test_limpiar_cache():
    """Prueba la limpieza del cache."""
    response = client.post("/recon/limpiar-cache", params={"max_age_hours": 1})
    assert response.status_code == 200
    assert response.json()["mensaje"] == "Limpieza de cache iniciada"

if __name__ == "__main__":
    # Ejecutar pruebas
    pytest.main([__file__, "-v"])
