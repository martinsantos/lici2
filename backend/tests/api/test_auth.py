import pytest
from fastapi.testclient import TestClient
from app.core.security import create_access_token
from app.database.crud_user import create_user
from app.models.user import UserCreate, UserRole

def test_login_success(client: TestClient, test_db):
    # Crear usuario de prueba
    user = UserCreate(
        email="test@example.com",
        username="testuser",
        password="testpass123",
        role=UserRole.USER
    )
    db_user = create_user(test_db, user)
    
    # Intentar login
    response = client.post(
        "/token",
        data={
            "username": "testuser",
            "password": "testpass123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client: TestClient, test_db):
    # Crear usuario de prueba
    user = UserCreate(
        email="test@example.com",
        username="testuser",
        password="testpass123",
        role=UserRole.USER
    )
    create_user(test_db, user)
    
    # Intentar login con contraseña incorrecta
    response = client.post(
        "/token",
        data={
            "username": "testuser",
            "password": "wrongpass"
        }
    )
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_protected_route_with_token(client: TestClient, test_db):
    # Crear usuario de prueba
    user = UserCreate(
        email="test@example.com",
        username="testuser",
        password="testpass123",
        role=UserRole.USER
    )
    db_user = create_user(test_db, user)
    
    # Crear token
    access_token = create_access_token(data={"sub": db_user.username})
    
    # Acceder a ruta protegida
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"

def test_protected_route_without_token(client: TestClient):
    # Intentar acceder a ruta protegida sin token
    response = client.get("/users/me")
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_protected_route_invalid_token(client: TestClient):
    # Intentar acceder con token inválido
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"
