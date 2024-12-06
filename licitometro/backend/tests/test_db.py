import pytest
from sqlalchemy.orm import Session
from backend.models.user import User
from backend.auth.security import get_password_hash

def test_create_user_db(db_session: Session):
    user_data = {
        "email": "create@example.com",
        "username": "createuser",
        "full_name": "Create User",
        "hashed_password": get_password_hash("testpassword")
    }
    
    db_user = User(**user_data)
    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)
    
    assert db_user.id is not None
    assert db_user.email == user_data["email"]
    assert db_user.username == user_data["username"]
    assert db_user.is_active is True

def test_get_user_by_email(db_session: Session):
    # First create a user
    user_data = {
        "email": "email@example.com",
        "username": "emailuser",
        "full_name": "Email User",
        "hashed_password": get_password_hash("testpassword")
    }
    db_user = User(**user_data)
    db_session.add(db_user)
    db_session.commit()
    
    # Then try to get it by email
    user = db_session.query(User).filter(User.email == user_data["email"]).first()
    assert user is not None
    assert user.email == user_data["email"]
    assert user.username == user_data["username"]

def test_get_user_by_username(db_session: Session):
    # First create a user
    user_data = {
        "email": "username@example.com",
        "username": "usernameuser",
        "full_name": "Username User",
        "hashed_password": get_password_hash("testpassword")
    }
    db_user = User(**user_data)
    db_session.add(db_user)
    db_session.commit()
    
    # Then try to get it by username
    user = db_session.query(User).filter(User.username == user_data["username"]).first()
    assert user is not None
    assert user.email == user_data["email"]
    assert user.username == user_data["username"]

def test_update_user(db_session: Session):
    # First create a user
    user_data = {
        "email": "update@example.com",
        "username": "updateuser",
        "full_name": "Update User",
        "hashed_password": get_password_hash("testpassword")
    }
    db_user = User(**user_data)
    db_session.add(db_user)
    db_session.commit()
    
    # Update the user
    new_email = "newemail@example.com"
    db_user.email = new_email
    db_session.commit()
    db_session.refresh(db_user)
    
    assert db_user.email == new_email

def test_delete_user(db_session: Session):
    # First create a user
    user_data = {
        "email": "delete@example.com",
        "username": "deleteuser",
        "full_name": "Delete User",
        "hashed_password": get_password_hash("testpassword")
    }
    db_user = User(**user_data)
    db_session.add(db_user)
    db_session.commit()
    
    # Delete the user
    db_session.delete(db_user)
    db_session.commit()
    
    # Try to get the deleted user
    user = db_session.query(User).filter(User.email == user_data["email"]).first()
    assert user is None
