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

def test_upload_document(client: TestClient, test_db):
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
    
    # Subir documento
    files = {
        'file': ('test.pdf', b'test content', 'application/pdf')
    }
    metadata = {
        'description': 'Test document',
        'category': 'Technical'
    }
    
    response = client.post(
        f"/tenders/{tender_id}/documents",
        headers=get_auth_headers(manager.username),
        files=files,
        data=metadata
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "test.pdf"
    assert data["description"] == metadata["description"]
    assert data["category"] == metadata["category"]
    assert "url" in data

def test_delete_document(client: TestClient, test_db):
    # Crear manager y licitación con documento
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
    
    # Subir documento
    files = {
        'file': ('test.pdf', b'test content', 'application/pdf')
    }
    metadata = {
        'description': 'Test document',
        'category': 'Technical'
    }
    
    upload_response = client.post(
        f"/tenders/{tender_id}/documents",
        headers=get_auth_headers(manager.username),
        files=files,
        data=metadata
    )
    document_id = upload_response.json()["id"]
    
    # Eliminar documento
    response = client.delete(
        f"/tenders/{tender_id}/documents/{document_id}",
        headers=get_auth_headers(manager.username)
    )
    
    assert response.status_code == 204
    
    # Verificar que el documento fue eliminado
    tender_response = client.get(
        f"/tenders/{tender_id}",
        headers=get_auth_headers(manager.username)
    )
    assert len(tender_response.json()["documents"]) == 0

def test_update_document_metadata(client: TestClient, test_db):
    # Crear manager y licitación con documento
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
    
    # Subir documento
    files = {
        'file': ('test.pdf', b'test content', 'application/pdf')
    }
    metadata = {
        'description': 'Initial description',
        'category': 'Technical'
    }
    
    upload_response = client.post(
        f"/tenders/{tender_id}/documents",
        headers=get_auth_headers(manager.username),
        files=files,
        data=metadata
    )
    document_id = upload_response.json()["id"]
    
    # Actualizar metadatos del documento
    update_data = {
        'description': 'Updated description',
        'category': 'Legal'
    }
    
    response = client.put(
        f"/tenders/{tender_id}/documents/{document_id}",
        headers=get_auth_headers(manager.username),
        json=update_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == update_data["description"]
    assert data["category"] == update_data["category"]

def test_upload_document_unauthorized(client: TestClient, test_db):
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
    
    # Intentar subir documento como usuario normal
    files = {
        'file': ('test.pdf', b'test content', 'application/pdf')
    }
    metadata = {
        'description': 'Test document',
        'category': 'Technical'
    }
    
    response = client.post(
        f"/tenders/{tender_id}/documents",
        headers=get_auth_headers(user.username),
        files=files,
        data=metadata
    )
    
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"

def test_list_documents(client: TestClient, test_db):
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
    
    # Subir múltiples documentos
    for i in range(2):
        files = {
            'file': (f'test{i+1}.pdf', b'test content', 'application/pdf')
        }
        metadata = {
            'description': f'Test document {i+1}',
            'category': 'Technical'
        }
        
        client.post(
            f"/tenders/{tender_id}/documents",
            headers=get_auth_headers(manager.username),
            files=files,
            data=metadata
        )
    
    # Listar documentos
    response = client.get(
        f"/tenders/{tender_id}/documents",
        headers=get_auth_headers(manager.username)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["filename"] == "test1.pdf"
    assert data[1]["filename"] == "test2.pdf"
