from sqlalchemy import Column, Integer, String, JSON, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ScrapingTemplate(Base):
    """
    Modelo para definir plantillas de scraping configurables
    """
    __tablename__ = 'scraping_templates'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    source_url = Column(String, nullable=False)
    
    # Configuración de mapeo de campos
    field_mapping = Column(JSON, nullable=False)
    
    # Reglas de transformación y validación
    transformation_rules = Column(JSON, nullable=True)
    
    # Configuración de frecuencia de scraping
    frequency_hours = Column(Integer, default=24)
    
    # Estado de la plantilla
    is_active = Column(Boolean, default=True)
    
    # Metadatos de auditoría
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ScrapingJob(Base):
    """
    Modelo para rastrear trabajos de scraping individuales
    """
    __tablename__ = 'scraping_jobs'

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, nullable=False)
    status = Column(String, default='pending')  # pending, running, completed, failed
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    
    # Resultados y métricas del scraping
    items_scraped = Column(Integer, default=0)
    errors = Column(JSON, nullable=True)
