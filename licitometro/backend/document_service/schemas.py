from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class DocumentBase(BaseModel):
    file_name: str
    content_type: str
    file_location: str

class DocumentCreate(DocumentBase):
    user_id: Optional[int] = None

class Document(DocumentBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DocumentResponse(Document):
    """
    Schema para respuestas de documentos, hereda de Document
    """
    licitacion_id: Optional[int] = None

class FileUploadResponse(BaseModel):
    filename: str
    document_id: int
    file_location: str

class MultiFileUploadResponse(BaseModel):
    files: List[FileUploadResponse]
