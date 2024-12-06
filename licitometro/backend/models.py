from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    descripcion = Column(String, nullable=True)
    config = Column(JSON, default={})
    features = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    scraping_jobs = relationship("ScrapingJob", back_populates="template")
    licitaciones = relationship("Licitacion", back_populates="template")

class ScrapingJob(Base):
    __tablename__ = "scraping_jobs"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("templates.id"))
    status = Column(String, default="pending")  # pending, running, completed, failed
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    template = relationship("Template", back_populates="scraping_jobs")
    licitaciones = relationship("Licitacion", back_populates="scraping_job")

class Licitacion(Base):
    __tablename__ = "licitaciones"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("templates.id"))
    scraping_job_id = Column(Integer, ForeignKey("scraping_jobs.id"))
    titulo = Column(String, index=True)
    descripcion = Column(String, nullable=True)
    url = Column(String)
    estado = Column(String)
    fecha_publicacion = Column(DateTime, nullable=True)
    fecha_cierre = Column(DateTime, nullable=True)
    monto = Column(String, nullable=True)
    entidad = Column(String, nullable=True)
    raw_data = Column(JSON, default={})
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    template = relationship("Template", back_populates="licitaciones")
    scraping_job = relationship("ScrapingJob", back_populates="licitaciones")
    documents = relationship("Document", back_populates="licitacion")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    licitacion_id = Column(Integer, ForeignKey("licitaciones.id"))
    nombre = Column(String)
    tipo = Column(String)
    url = Column(String)
    contenido = Column(String, nullable=True)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    licitacion = relationship("Licitacion", back_populates="documents")
