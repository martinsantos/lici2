from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.base import get_db
from app.database.crud_user import (
    create_user,
    get_user,
    get_users,
    update_user,
    delete_user,
    get_user_by_email,
    get_user_by_username,
)
from app.models.user import User, UserCreate, UserUpdate
from app.api.endpoints.auth import get_current_user

router = APIRouter()

@router.post("/users/", response_model=User, status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo usuario",
    description="""
    Crea un nuevo usuario en el sistema.
    Solo los administradores pueden crear nuevos usuarios.
    """,
    responses={
        201: {
            "description": "Usuario creado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "email": "user@example.com",
                        "username": "newuser",
                        "full_name": "New User",
                        "role": "user",
                        "is_active": True
                    }
                }
            }
        },
        400: {
            "description": "Error de validación",
            "content": {
                "application/json": {
                    "example": {"detail": "Email already registered"}
                }
            }
        },
        403: {
            "description": "Permisos insuficientes",
            "content": {
                "application/json": {
                    "example": {"detail": "Not enough permissions"}
                }
            }
        }
    }
)
async def create_new_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea un nuevo usuario con los siguientes datos:
    
    - **email**: Email único del usuario
    - **username**: Nombre de usuario único
    - **password**: Contraseña del usuario
    - **full_name**: Nombre completo (opcional)
    - **role**: Rol del usuario (user, manager, admin)
    """
    # Solo los administradores pueden crear usuarios
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Verificar si el email ya existe
    if get_user_by_email(db, email=user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Verificar si el username ya existe
    if get_user_by_username(db, username=user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    return create_user(db=db, user=user)

@router.get("/users/", response_model=List[User],
    summary="Listar usuarios",
    description="Obtiene la lista de todos los usuarios registrados. Solo accesible para administradores.",
    responses={
        200: {
            "description": "Lista de usuarios obtenida exitosamente",
            "content": {
                "application/json": {
                    "example": [{
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "email": "user@example.com",
                        "username": "user1",
                        "full_name": "User One",
                        "role": "user",
                        "is_active": True
                    }]
                }
            }
        },
        403: {
            "description": "Permisos insuficientes",
            "content": {
                "application/json": {
                    "example": {"detail": "Not enough permissions"}
                }
            }
        }
    }
)
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene la lista de usuarios con paginación:
    
    - **skip**: Número de registros a saltar
    - **limit**: Número máximo de registros a retornar
    """
    # Solo los administradores pueden ver la lista de usuarios
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    users = get_users(db, skip=skip, limit=limit)
    return users

@router.get("/users/{user_id}", response_model=User,
    summary="Obtener usuario",
    description="Obtiene la información de un usuario específico.",
    responses={
        200: {
            "description": "Usuario obtenido exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "email": "user@example.com",
                        "username": "user1",
                        "full_name": "User One",
                        "role": "user",
                        "is_active": True
                    }
                }
            }
        },
        404: {
            "description": "Usuario no encontrado",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found"}
                }
            }
        },
        403: {
            "description": "Permisos insuficientes",
            "content": {
                "application/json": {
                    "example": {"detail": "Not enough permissions"}
                }
            }
        }
    }
)
async def read_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene la información de un usuario específico:
    
    - **user_id**: ID del usuario a obtener
    """
    # Un usuario puede ver su propio perfil o un admin puede ver cualquier perfil
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user

@router.put("/users/{user_id}", response_model=User,
    summary="Actualizar usuario",
    description="Actualiza la información de un usuario específico.",
    responses={
        200: {
            "description": "Usuario actualizado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "email": "user@example.com",
                        "username": "user1",
                        "full_name": "User One",
                        "role": "user",
                        "is_active": True
                    }
                }
            }
        },
        400: {
            "description": "Error de validación",
            "content": {
                "application/json": {
                    "example": {"detail": "Email already registered"}
                }
            }
        },
        404: {
            "description": "Usuario no encontrado",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found"}
                }
            }
        },
        403: {
            "description": "Permisos insuficientes",
            "content": {
                "application/json": {
                    "example": {"detail": "Not enough permissions"}
                }
            }
        }
    }
)
async def update_user_info(
    user_id: str,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza la información de un usuario específico:
    
    - **user_id**: ID del usuario a actualizar
    - **email**: Email del usuario (opcional)
    - **username**: Nombre de usuario del usuario (opcional)
    - **full_name**: Nombre completo del usuario (opcional)
    - **role**: Rol del usuario (opcional)
    """
    # Un usuario puede actualizar su propio perfil o un admin puede actualizar cualquier perfil
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Verificar si el email ya existe (si se está actualizando)
    if user.email:
        existing_user = get_user_by_email(db, email=user.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Verificar si el username ya existe (si se está actualizando)
    if user.username:
        existing_user = get_user_by_username(db, username=user.username)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
    
    updated_user = update_user(db=db, user_id=user_id, user=user)
    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return updated_user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar usuario",
    description="Elimina un usuario específico.",
    responses={
        204: {
            "description": "Usuario eliminado exitosamente"
        },
        404: {
            "description": "Usuario no encontrado",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found"}
                }
            }
        },
        403: {
            "description": "Permisos insuficientes",
            "content": {
                "application/json": {
                    "example": {"detail": "Not enough permissions"}
                }
            }
        }
    }
)
async def delete_user_account(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina un usuario específico:
    
    - **user_id**: ID del usuario a eliminar
    """
    # Solo los administradores pueden eliminar usuarios
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    if not delete_user(db=db, user_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
