import pytest
import asyncio
from httpx import AsyncClient
from datetime import datetime, timedelta
import json
from backend.app.recon.enhanced_coordinator import EnhancedReconCoordinator
from backend.app.search.elasticsearch_service import ElasticsearchService
from backend.app.notifications.notification_service import NotificationService

@pytest.mark.asyncio
async def test_complete_recon_workflow(
    async_client: AsyncClient,
    coordinator: EnhancedReconCoordinator,
    es_service: ElasticsearchService,
    notification_service: NotificationService
):
    """Prueba el flujo completo del proceso RECON"""
    
    # 1. Crear una plantilla de prueba
    plantilla = {
        "nombre": "Plantilla de Prueba",
        "campos": {
            "titulo": {"tipo": "texto", "required": True},
            "monto": {"tipo": "numero", "required": True},
            "fecha": {"tipo": "fecha", "required": True}
        },
        "fuente": {
            "url": "https://ejemplo.com/licitaciones",
            "tipo": "web"
        }
    }

    # 2. Iniciar tarea RECON
    response = await async_client.post(
        "/api/recon/tasks",
        json={
            "plantilla_id": "test_template",
            "plantilla": plantilla,
            "prioridad": "high"
        }
    )
    assert response.status_code == 200
    task_data = response.json()
    task_id = task_data["task_id"]

    # 3. Verificar progreso de la tarea
    max_attempts = 10
    attempts = 0
    while attempts < max_attempts:
        response = await async_client.get(f"/api/recon/tasks/{task_id}")
        assert response.status_code == 200
        status = response.json()["status"]
        
        if status in ["completed", "failed"]:
            break
            
        attempts += 1
        await asyncio.sleep(1)

    assert status == "completed"

    # 4. Verificar resultados en Elasticsearch
    await asyncio.sleep(1)  # Esperar indexación
    search_results = await es_service.search(
        query="Plantilla de Prueba",
        filters={"plantilla_id": "test_template"}
    )
    assert search_results["total"] > 0

    # 5. Verificar notificaciones
    notifications = await notification_service.get_user_notifications("test_user")
    assert len(notifications) > 0
    assert any(n["type"] == "task_completed" for n in notifications)

@pytest.mark.asyncio
async def test_error_handling(
    async_client: AsyncClient,
    coordinator: EnhancedReconCoordinator
):
    """Prueba el manejo de errores en el proceso RECON"""
    
    # 1. Intentar iniciar tarea con plantilla inválida
    response = await async_client.post(
        "/api/recon/tasks",
        json={
            "plantilla_id": "invalid_template",
            "plantilla": {},  # Plantilla vacía
            "prioridad": "high"
        }
    )
    assert response.status_code == 400

    # 2. Intentar acceder a tarea inexistente
    response = await async_client.get("/api/recon/tasks/nonexistent_task")
    assert response.status_code == 404

    # 3. Verificar límite de tareas concurrentes
    tasks = []
    for _ in range(coordinator.task_queue.max_concurrent_tasks + 1):
        response = await async_client.post(
            "/api/recon/tasks",
            json={
                "plantilla_id": "test_template",
                "plantilla": {
                    "nombre": "Test",
                    "campos": {"titulo": {"tipo": "texto", "required": True}}
                },
                "prioridad": "low"
            }
        )
        tasks.append(response.json().get("task_id") if response.status_code == 200 else None)

    # Verificar que la última tarea fue rechazada
    assert None in tasks

@pytest.mark.asyncio
async def test_performance_metrics(
    async_client: AsyncClient,
    coordinator: EnhancedReconCoordinator
):
    """Prueba las métricas de rendimiento del sistema"""
    
    start_time = datetime.utcnow()
    
    # 1. Ejecutar múltiples tareas en paralelo
    task_ids = []
    for i in range(5):
        response = await async_client.post(
            "/api/recon/tasks",
            json={
                "plantilla_id": f"perf_test_{i}",
                "plantilla": {
                    "nombre": f"Test Performance {i}",
                    "campos": {"titulo": {"tipo": "texto", "required": True}}
                },
                "prioridad": "medium"
            }
        )
        assert response.status_code == 200
        task_ids.append(response.json()["task_id"])

    # 2. Esperar completación de todas las tareas
    completed_tasks = 0
    timeout = start_time + timedelta(seconds=30)
    
    while completed_tasks < len(task_ids) and datetime.utcnow() < timeout:
        completed_tasks = 0
        for task_id in task_ids:
            response = await async_client.get(f"/api/recon/tasks/{task_id}")
            if response.json()["status"] == "completed":
                completed_tasks += 1
        if completed_tasks < len(task_ids):
            await asyncio.sleep(1)

    # 3. Verificar métricas
    response = await async_client.get("/api/metrics")
    assert response.status_code == 200
    metrics = response.json()
    
    assert metrics["tasks_completed"] >= completed_tasks
    assert "avg_processing_time" in metrics
    assert "success_rate" in metrics
    assert metrics["success_rate"] >= 0.8  # 80% éxito mínimo

@pytest.fixture
async def async_client():
    from backend.app.main import app
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def coordinator():
    coordinator = EnhancedReconCoordinator(max_concurrent_tasks=3)
    await coordinator.start()
    yield coordinator
    await coordinator.stop()

@pytest.fixture
async def es_service():
    service = ElasticsearchService(hosts=["http://localhost:9200"])
    await service.initialize()
    yield service
    await service.close()

@pytest.fixture
async def notification_service():
    service = NotificationService(
        redis_url="redis://localhost:6379",
        smtp_config={
            "host": "localhost",
            "port": 1025,
            "from_email": "test@example.com",
            "username": "test",
            "password": "test"
        }
    )
    yield service
    await service.close()
