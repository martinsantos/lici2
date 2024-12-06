import pytest
from fastapi.testclient import TestClient
from app.core.security import create_access_token
from app.database.crud_user import create_user
from app.models.user import UserCreate, UserRole
from app.models.tender import TenderStatus

def get_auth_headers(username: str):
    access_token = create_access_token(data={"sub": username})
    return {"Authorization": f"Bearer {access_token}"}

def create_test_user(db, role=UserRole.USER):
    user = UserCreate(
        email="test@example.com",
        username="testuser",
        password="testpass123",
        role=role
    )
    return create_user(db, user)

def test_add_requirement(client: TestClient, test_db):
    # Crear manager y licitación
    manager = create_test_user(test_db, UserRole.MANAGER)
    tender_data = {
        "title": "Test Tender",
        "description": "Test Description",
        "budget": 100000.0
    }
    
    create_response = client.post(
        "/tenders/",
        headers=get_auth_headers(manager.username),
        json=tender_data
    )
    tender_id = create_response.json()["id"]
    
    # Agregar requerimiento
    requirement_data = {
        "description": "New requirement",
        "is_mandatory": True,
        "category": "Technical"
    }
    
    response = client.post(
        f"/tenders/{tender_id}/requirements",
        headers=get_auth_headers(manager.username),
        json=requirement_data
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["description"] == requirement_data["description"]
    assert data["is_mandatory"] == requirement_data["is_mandatory"]
    assert data["category"] == requirement_data["category"]

def test_update_requirement(client: TestClient, test_db):
    # Crear manager y licitación con requerimiento
    manager = create_test_user(test_db, UserRole.MANAGER)
    tender_data = {
        "title": "Test Tender",
        "description": "Test Description",
        "budget": 100000.0,
        "requirements": [
            {
                "description": "Initial requirement",
                "is_mandatory": True,
                "category": "Technical"
            }
        ]
    }
    
    create_response = client.post(
        "/tenders/",
        headers=get_auth_headers(manager.username),
        json=tender_data
    )
    tender_id = create_response.json()["id"]
    requirement_id = create_response.json()["requirements"][0]["id"]
    
    # Actualizar requerimiento
    update_data = {
        "description": "Updated requirement",
        "is_mandatory": False,
        "category": "Legal"
    }
    
    response = client.put(
        f"/tenders/{tender_id}/requirements/{requirement_id}",
        headers=get_auth_headers(manager.username),
        json=update_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == update_data["description"]
    assert data["is_mandatory"] == update_data["is_mandatory"]
    assert data["category"] == update_data["category"]

def test_delete_requirement(client: TestClient, test_db):
    # Crear manager y licitación con requerimiento
    manager = create_test_user(test_db, UserRole.MANAGER)
    tender_data = {
        "title": "Test Tender",
        "description": "Test Description",
        "budget": 100000.0,
        "requirements": [
            {
                "description": "Test requirement",
                "is_mandatory": True,
                "category": "Technical"
            }
        ]
    }
    
    create_response = client.post(
        "/tenders/",
        headers=get_auth_headers(manager.username),
        json=tender_data
    )
    tender_id = create_response.json()["id"]
    requirement_id = create_response.json()["requirements"][0]["id"]
    
    # Eliminar requerimiento
    response = client.delete(
        f"/tenders/{tender_id}/requirements/{requirement_id}",
        headers=get_auth_headers(manager.username)
    )
    
    assert response.status_code == 204
    
    # Verificar que el requerimiento fue eliminado
    tender_response = client.get(
        f"/tenders/{tender_id}",
        headers=get_auth_headers(manager.username)
    )
    assert len(tender_response.json()["requirements"]) == 0

def test_add_requirement_unauthorized(client: TestClient, test_db):
    # Crear usuario normal y manager
    user = create_test_user(test_db)
    manager = create_test_user(test_db, UserRole.MANAGER)
    
    # Crear licitación como manager
    tender_data = {
        "title": "Test Tender",
        "description": "Test Description",
        "budget": 100000.0
    }
    
    create_response = client.post(
        "/tenders/",
        headers=get_auth_headers(manager.username),
        json=tender_data
    )
    tender_id = create_response.json()["id"]
    
    # Intentar agregar requerimiento como usuario normal
    requirement_data = {
        "description": "New requirement",
        "is_mandatory": True,
        "category": "Technical"
    }
    
    response = client.post(
        f"/tenders/{tender_id}/requirements",
        headers=get_auth_headers(user.username),
        json=requirement_data
    )
    
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"

def test_list_requirements(client: TestClient, test_db):
    # Crear manager y licitación con múltiples requerimientos
    manager = create_test_user(test_db, UserRole.MANAGER)
    tender_data = {
        "title": "Test Tender",
        "description": "Test Description",
        "budget": 100000.0,
        "requirements": [
            {
                "description": "Requirement 1",
                "is_mandatory": True,
                "category": "Technical"
            },
            {
                "description": "Requirement 2",
                "is_mandatory": False,
                "category": "Legal"
            }
        ]
    }
    
    create_response = client.post(
        "/tenders/",
        headers=get_auth_headers(manager.username),
        json=tender_data
    )
    tender_id = create_response.json()["id"]
    
    # Listar requerimientos
    response = client.get(
        f"/tenders/{tender_id}/requirements",
        headers=get_auth_headers(manager.username)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["description"] == "Requirement 1"
    assert data[1]["description"] == "Requirement 2"
