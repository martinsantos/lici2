from pydantic import BaseModel, ConfigDict, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from .models import ScrapingStatus

class TemplateField(BaseModel):
    id: Optional[str] = None
    name: str
    selector: str
    type: str
    required: Optional[bool] = None

class TemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    url: str
    fields: Dict[str, Any]  # Changed from List[TemplateField] to Dict[str, Any] to match JSON column
    is_active: Optional[bool] = True

class TemplateCreate(TemplateBase):
    pass

class Template(TemplateBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class JobBase(BaseModel):
    template_id: int

class JobCreate(JobBase):
    pass

class Job(JobBase):
    id: int
    status: ScrapingStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    celery_task_id: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class JobUpdate(BaseModel):
    status: Optional[ScrapingStatus] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class JobList(BaseModel):
    jobs: List[Job]
    total: int
    skip: int
    limit: int
