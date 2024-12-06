# Authentication has been disabled
# This file is kept for potential future use or reference

from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from core.database import get_db
from .models import User
from config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/token")

def no_auth_placeholder():
    """
    Placeholder function to indicate authentication is disabled
    """
    return None

def get_db():
    # This function is still needed for other parts of the application
    # It is not removed to avoid breaking other functionality
    return get_db()

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    # This function is kept to avoid breaking other functionality
    # It will always raise an exception since authentication is disabled
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    raise credentials_exception
