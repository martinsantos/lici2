import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.core.security import create_access_token
from app.database.crud_user import create_user
from app.models.user import UserCreate, UserRole
from app.models.tender import TenderCreate, TenderStatus

def create_test_user(db, role=UserRole.USER):
    user = UserCreate(
        email="test@example.com",
        username="testuser",
        password="testpass123",
        role=role
    )
    return create_user(db, user)

def get_auth_headers(username: str):
    access_token = create_access_token(data={"sub": username})
    return {"Authorization": f"Bearer {access_token}"}

def create_test_tender_data():
    return {
        "title": "Test Tender",
        "description": "Test tender description",
        "budget": 100000.0,
        "deadline": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "category": "Construction",
        "region": "North",
        "requirements": [
            {
                "description": "Test requirement",
                "is_mandatory": True
            }
        ],
        "documents": [
            {
                "name": "Test document",
                "url": "http://example.com/doc.pdf",
                "type": "pdf",
                "size": 1024
            }
        ],
        "tags": ["test", "construction"]
    }

def test_create_tender(client: TestClient, test_db):
    # Crear usuario manager
    manager = create_test_user(test_db, UserRole.MANAGER)
    
    # Crear licitación
    tender_data = create_test_tender_data()
    response = client.post(
        "/tenders/",
        headers=get_auth_headers(manager.username),
        json=tender_data
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == tender_data["title"]
    assert data["status"] == TenderStatus.DRAFT
    assert len(data["requirements"]) == 1
    assert len(data["documents"]) == 1
    assert len(data["tags"]) == 2

def test_create_tender_as_regular_user(client: TestClient, test_db):
    # Crear usuario normal
    user = create_test_user(test_db)
    
    # Intentar crear licitación
    tender_data = create_test_tender_data()
    response = client.post(
        "/tenders/",
        headers=get_auth_headers(user.username),
        json=tender_data
    )
    
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"

def test_get_tenders_list(client: TestClient, test_db):
    # Crear usuario
    user = create_test_user(test_db)
    
    # Obtener lista de licitaciones
    response = client.get(
        "/tenders/",
        headers=get_auth_headers(user.username)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_tenders_with_filters(client: TestClient, test_db):
    # Crear usuario
    user = create_test_user(test_db)
    
    # Obtener licitaciones con filtros
    response = client.get(
        "/tenders/?category=Construction&region=North&min_budget=50000&max_budget=150000",
        headers=get_auth_headers(user.username)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_tender_by_id(client: TestClient, test_db):
    # Crear manager y licitación
    manager = create_test_user(test_db, UserRole.MANAGER)
    tender_data = create_test_tender_data()
    create_response = client.post(
        "/tenders/",
        headers=get_auth_headers(manager.username),
        json=tender_data
    )
    tender_id = create_response.json()["id"]
    
    # Obtener licitación por ID
    response = client.get(
        f"/tenders/{tender_id}",
        headers=get_auth_headers(manager.username)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == tender_id
    assert data["title"] == tender_data["title"]

def test_update_tender(client: TestClient, test_db):
    # Crear manager y licitación
    manager = create_test_user(test_db, UserRole.MANAGER)
    tender_data = create_test_tender_data()
    create_response = client.post(
        "/tenders/",
        headers=get_auth_headers(manager.username),
        json=tender_data
    )
    tender_id = create_response.json()["id"]
    
    # Actualizar licitación
    update_data = {
        "title": "Updated Tender",
        "description": "Updated description"
    }
    response = client.put(
        f"/tenders/{tender_id}",
        headers=get_auth_headers(manager.username),
        json=update_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["description"] == update_data["description"]

def test_update_tender_status(client: TestClient, test_db):
    # Crear manager y licitación
    manager = create_test_user(test_db, UserRole.MANAGER)
    tender_data = create_test_tender_data()
    create_response = client.post(
        "/tenders/",
        headers=get_auth_headers(manager.username),
        json=tender_data
    )
    tender_id = create_response.json()["id"]
    
    # Actualizar estado de la licitación
    response = client.patch(
        f"/tenders/{tender_id}/status",
        headers=get_auth_headers(manager.username),
        json={"status": TenderStatus.PUBLISHED}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == TenderStatus.PUBLISHED
    assert data["published_at"] is not None

def test_delete_tender(client: TestClient, test_db):
    # Crear manager y licitación
    manager = create_test_user(test_db, UserRole.MANAGER)
    tender_data = create_test_tender_data()
    create_response = client.post(
        "/tenders/",
        headers=get_auth_headers(manager.username),
        json=tender_data
    )
    tender_id = create_response.json()["id"]
    
    # Eliminar licitación
    response = client.delete(
        f"/tenders/{tender_id}",
        headers=get_auth_headers(manager.username)
    )
    
    assert response.status_code == 204
    
    # Verificar que la licitación fue eliminada
    get_response = client.get(
        f"/tenders/{tender_id}",
        headers=get_auth_headers(manager.username)
    )
    assert get_response.status_code == 404
