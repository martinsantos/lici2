import pytest
from fastapi.testclient import TestClient
from app.core.security import create_access_token
from app.database.crud_user import create_user
from app.models.user import UserCreate, UserRole

def create_test_user(db, role=UserRole.USER):
    user = UserCreate(
        email="test@example.com",
        username="testuser",
        password="testpass123",
        role=role
    )
    return create_user(db, user)

def create_test_admin(db):
    admin = UserCreate(
        email="admin@example.com",
        username="adminuser",
        password="adminpass123",
        role=UserRole.ADMIN
    )
    return create_user(db, admin)

def get_auth_headers(username: str):
    access_token = create_access_token(data={"sub": username})
    return {"Authorization": f"Bearer {access_token}"}

def test_create_user_as_admin(client: TestClient, test_db):
    # Crear admin
    admin = create_test_admin(test_db)
    
    # Crear nuevo usuario
    response = client.post(
        "/users/",
        headers=get_auth_headers(admin.username),
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "newpass123",
            "role": UserRole.USER
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"
    assert "password" not in data

def test_create_user_as_non_admin(client: TestClient, test_db):
    # Crear usuario normal
    user = create_test_user(test_db)
    
    # Intentar crear nuevo usuario
    response = client.post(
        "/users/",
        headers=get_auth_headers(user.username),
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "newpass123",
            "role": UserRole.USER
        }
    )
    
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"

def test_get_users_list_as_admin(client: TestClient, test_db):
    # Crear admin y algunos usuarios
    admin = create_test_admin(test_db)
    create_test_user(test_db)
    create_test_user(test_db, UserRole.MANAGER)
    
    # Obtener lista de usuarios
    response = client.get(
        "/users/",
        headers=get_auth_headers(admin.username)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3  # Admin + 2 usuarios creados

def test_get_users_list_as_non_admin(client: TestClient, test_db):
    # Crear usuario normal
    user = create_test_user(test_db)
    
    # Intentar obtener lista de usuarios
    response = client.get(
        "/users/",
        headers=get_auth_headers(user.username)
    )
    
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"

def test_get_own_user_profile(client: TestClient, test_db):
    # Crear usuario
    user = create_test_user(test_db)
    
    # Obtener propio perfil
    response = client.get(
        f"/users/{user.id}",
        headers=get_auth_headers(user.username)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user.email
    assert data["username"] == user.username

def test_get_other_user_profile_as_non_admin(client: TestClient, test_db):
    # Crear dos usuarios
    user1 = create_test_user(test_db)
    user2 = create_test_user(test_db)
    
    # Intentar obtener perfil de otro usuario
    response = client.get(
        f"/users/{user2.id}",
        headers=get_auth_headers(user1.username)
    )
    
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"

def test_update_own_profile(client: TestClient, test_db):
    # Crear usuario
    user = create_test_user(test_db)
    
    # Actualizar propio perfil
    response = client.put(
        f"/users/{user.id}",
        headers=get_auth_headers(user.username),
        json={
            "email": "updated@example.com",
            "username": "updateduser",
            "full_name": "Updated User"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "updated@example.com"
    assert data["username"] == "updateduser"
    assert data["full_name"] == "Updated User"

def test_delete_user_as_admin(client: TestClient, test_db):
    # Crear admin y usuario
    admin = create_test_admin(test_db)
    user = create_test_user(test_db)
    
    # Eliminar usuario
    response = client.delete(
        f"/users/{user.id}",
        headers=get_auth_headers(admin.username)
    )
    
    assert response.status_code == 204

def test_delete_user_as_non_admin(client: TestClient, test_db):
    # Crear dos usuarios
    user1 = create_test_user(test_db)
    user2 = create_test_user(test_db)
    
    # Intentar eliminar otro usuario
    response = client.delete(
        f"/users/{user2.id}",
        headers=get_auth_headers(user1.username)
    )
    
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"
