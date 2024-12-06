from sqlalchemy import create_engine, Column, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Optional
from .models import UserInDB

SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"  # Cambiar en producción

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DBUser(Base):
    __tablename__ = "users"

    username = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Database:
    def __init__(self):
        self.db = SessionLocal()

    def get_user(self, username: str) -> Optional[UserInDB]:
        user = self.db.query(DBUser).filter(DBUser.username == username).first()
        if user:
            return UserInDB(
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                hashed_password=user.hashed_password,
                is_active=user.is_active
            )
        return None

    def create_user(self, user: UserInDB) -> UserInDB:
        db_user = DBUser(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=user.hashed_password,
            is_active=user.is_active
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return user

    def close(self):
        self.db.close()
