from sqlalchemy.orm import Session
from typing import Optional
from . import models, schemas

def get_document(db: Session, document_id: int):
    return db.query(models.Document).filter(models.Document.id == document_id).first()

def get_documents(db: Session, user_id: Optional[int] = None, skip: int = 0, limit: int = 100):
    query = db.query(models.Document)
    if user_id is not None:
        query = query.filter(models.Document.user_id == user_id)
    return query.offset(skip).limit(limit).all()

def create_document(db: Session, file_name: str, file_location: str, content_type: str, user_id: Optional[int] = None):
    db_document = models.Document(
        file_name=file_name,
        file_location=file_location,
        content_type=content_type,
        user_id=user_id
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def delete_document(db: Session, document_id: int):
    db_document = get_document(db, document_id=document_id)
    if db_document:
        db.delete(db_document)
        db.commit()
    return db_document
