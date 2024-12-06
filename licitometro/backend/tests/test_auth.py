from fastapi import status
import pytest
from backend.config import settings

def test_create_user(client, test_user):
    response = client.post(
        f"{settings.api_v1_prefix}/auth/users",
        json=test_user
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user["email"]
    assert data["username"] == test_user["username"]
    assert "password" not in data

def test_create_user_duplicate_email(client, test_user):
    # Create first user
    client.post(f"{settings.api_v1_prefix}/auth/users", json=test_user)
    
    # Try to create second user with same email
    duplicate_user = test_user.copy()
    duplicate_user["username"] = "different_username"
    response = client.post(
        f"{settings.api_v1_prefix}/auth/users",
        json=duplicate_user
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_create_user_duplicate_username(client, test_user):
    # Create first user
    client.post(f"{settings.api_v1_prefix}/auth/users", json=test_user)
    
    # Try to create second user with same username
    duplicate_user = test_user.copy()
    duplicate_user["email"] = "different@example.com"
    response = client.post(
        f"{settings.api_v1_prefix}/auth/users",
        json=duplicate_user
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_login_user(client, test_user):
    # First create user
    client.post(f"{settings.api_v1_prefix}/auth/users", json=test_user)
    
    # Then try to login
    response = client.post(
        f"{settings.api_v1_prefix}/auth/token",
        data={
            "username": test_user["username"],
            "password": test_user["password"]
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_get_current_user(client, test_user, test_user_token):
    response = client.get(
        f"{settings.api_v1_prefix}/auth/users/me",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user["email"]
    assert data["username"] == test_user["username"]

def test_login_wrong_password(client, test_user):
    # First create user
    client.post(f"{settings.api_v1_prefix}/auth/users", json=test_user)
    
    # Then try to login with wrong password
    response = client.post(
        f"{settings.api_v1_prefix}/auth/token",
        data={
            "username": test_user["username"],
            "password": "wrongpassword"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_user_unauthorized(client):
    response = client.get(f"{settings.api_v1_prefix}/auth/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_user_invalid_token(client):
    response = client.get(
        f"{settings.api_v1_prefix}/auth/users/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_login_nonexistent_user(client):
    response = client.post(
        f"{settings.api_v1_prefix}/auth/token",
        data={
            "username": "nonexistent",
            "password": "password123"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
