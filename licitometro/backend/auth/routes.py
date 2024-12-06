from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from . import crud, models, schemas

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

# Removed authentication routes
# This is now an open system without user management
