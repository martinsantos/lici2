from sqlalchemy import Column, String, Float, DateTime, Boolean, ForeignKey, Table, Enum
from sqlalchemy.orm import relationship
from app.database.base import Base
from app.models.tender import TenderStatus
import uuid
from datetime import datetime

# Tabla de asociación para la relación muchos a muchos entre licitaciones y etiquetas
tender_tags = Table(
    'tender_tags',
    Base.metadata,
    Column('tender_id', String, ForeignKey('tenders.id')),
    Column('tag_id', String, ForeignKey('tags.id')),
)

class TenderModel(Base):
    __tablename__ = 'tenders'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    budget = Column(Float, nullable=False)
    deadline = Column(DateTime, nullable=False)
    status = Column(Enum(TenderStatus), nullable=False, default=TenderStatus.DRAFT)
    category = Column(String, nullable=False)
    region = Column(String, nullable=False)
    
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    published_at = Column(DateTime, nullable=True)
    awarded_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)

    # Relaciones
    requirements = relationship("TenderRequirementModel", back_populates="tender", cascade="all, delete-orphan")
    documents = relationship("TenderDocumentModel", back_populates="tender", cascade="all, delete-orphan")
    tags = relationship("TenderTagModel", secondary=tender_tags, back_populates="tenders")

class TenderRequirementModel(Base):
    __tablename__ = 'tender_requirements'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tender_id = Column(String, ForeignKey('tenders.id'), nullable=False)
    description = Column(String, nullable=False)
    is_mandatory = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False)

    # Relaciones
    tender = relationship("TenderModel", back_populates="requirements")

class TenderDocumentModel(Base):
    __tablename__ = 'tender_documents'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tender_id = Column(String, ForeignKey('tenders.id'), nullable=False)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    type = Column(String, nullable=False)
    size = Column(Float, nullable=False)
    uploaded_at = Column(DateTime, nullable=False)

    # Relaciones
    tender = relationship("TenderModel", back_populates="documents")

class TenderTagModel(Base):
    __tablename__ = 'tags'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False)

    # Relaciones
    tenders = relationship("TenderModel", secondary=tender_tags, back_populates="tags")

class UserModel(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    full_name = Column(String)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
