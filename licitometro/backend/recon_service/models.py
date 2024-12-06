from sqlalchemy import Column, String, DateTime, JSON, Text, Integer, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
from datetime import datetime
import enum

class ScrapingStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class ScrapingTemplate(Base):
    __tablename__ = "scraping_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    url = Column(String, nullable=False)
    fields = Column(JSON, nullable=False)  # Lista de TemplateField
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    jobs = relationship("ScrapingJob", back_populates="template")

class ScrapingJob(Base):
    __tablename__ = "scraping_jobs"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("scraping_templates.id"))
    status = Column(Enum(ScrapingStatus), default=ScrapingStatus.PENDING)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    progress_message = Column(Text, nullable=True)  # New field for progress updates
    celery_task_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    template = relationship("ScrapingTemplate", back_populates="jobs")
