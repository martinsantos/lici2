from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime
from typing import List, Optional
from app.database.models import TenderModel, TenderRequirementModel, TenderDocumentModel, TenderTagModel
from app.models.tender import TenderCreate, TenderUpdate, TenderStatus, TenderFilters

def create_tender(db: Session, tender: TenderCreate) -> TenderModel:
    now = datetime.utcnow()
    db_tender = TenderModel(
        title=tender.title,
        description=tender.description,
        budget=tender.budget,
        deadline=tender.deadline,
        status=TenderStatus.DRAFT,
        category=tender.category,
        region=tender.region,
        created_at=now,
        updated_at=now
    )
    
    # Crear requisitos
    if tender.requirements:
        db_tender.requirements = [
            TenderRequirementModel(
                description=req.description,
                is_mandatory=req.is_mandatory,
                created_at=now
            ) for req in tender.requirements
        ]
    
    # Crear documentos
    if tender.documents:
        db_tender.documents = [
            TenderDocumentModel(
                name=doc.name,
                url=doc.url,
                type=doc.type,
                size=doc.size,
                uploaded_at=now
            ) for doc in tender.documents
        ]
    
    # Asociar tags existentes o crear nuevos
    if tender.tags:
        for tag_name in tender.tags:
            tag = db.query(TenderTagModel).filter(TenderTagModel.name == tag_name).first()
            if not tag:
                tag = TenderTagModel(name=tag_name, created_at=now)
                db.add(tag)
            db_tender.tags.append(tag)
    
    db.add(db_tender)
    db.commit()
    db.refresh(db_tender)
    return db_tender

def get_tenders(
    db: Session,
    filters: TenderFilters,
    skip: int = 0,
    limit: int = 100
) -> List[TenderModel]:
    query = db.query(TenderModel)
    
    # Aplicar filtros
    if filters:
        conditions = []
        
        if filters.search:
            search_term = f"%{filters.search}%"
            conditions.append(
                or_(
                    TenderModel.title.ilike(search_term),
                    TenderModel.description.ilike(search_term)
                )
            )
        
        if filters.categories:
            conditions.append(TenderModel.category.in_(filters.categories))
        
        if filters.regions:
            conditions.append(TenderModel.region.in_(filters.regions))
        
        if filters.min_budget is not None:
            conditions.append(TenderModel.budget >= filters.min_budget)
        
        if filters.max_budget is not None:
            conditions.append(TenderModel.budget <= filters.max_budget)
        
        if filters.status:
            conditions.append(TenderModel.status == filters.status)
        
        if filters.tags:
            query = query.join(TenderModel.tags).filter(TenderTagModel.name.in_(filters.tags))
        
        if conditions:
            query = query.filter(and_(*conditions))
    
    # Aplicar ordenamiento
    if filters and filters.sort_by:
        if hasattr(TenderModel, filters.sort_by):
            order_column = getattr(TenderModel, filters.sort_by)
            if filters.sort_desc:
                order_column = order_column.desc()
            query = query.order_by(order_column)
    
    return query.offset(skip).limit(limit).all()

def get_tender(db: Session, tender_id: str) -> Optional[TenderModel]:
    return db.query(TenderModel).filter(TenderModel.id == tender_id).first()

def update_tender(db: Session, tender_id: str, tender_update: TenderUpdate) -> Optional[TenderModel]:
    db_tender = get_tender(db, tender_id)
    if not db_tender:
        return None
    
    update_data = tender_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    for key, value in update_data.items():
        setattr(db_tender, key, value)
    
    db.commit()
    db.refresh(db_tender)
    return db_tender

def delete_tender(db: Session, tender_id: str) -> bool:
    db_tender = get_tender(db, tender_id)
    if not db_tender:
        return False
    
    db.delete(db_tender)
    db.commit()
    return True

def update_tender_status(db: Session, tender_id: str, status: TenderStatus) -> Optional[TenderModel]:
    db_tender = get_tender(db, tender_id)
    if not db_tender:
        return None
    
    now = datetime.utcnow()
    db_tender.status = status
    db_tender.updated_at = now
    
    # Actualizar campos de fecha según el estado
    if status == TenderStatus.PUBLISHED:
        db_tender.published_at = now
    elif status == TenderStatus.AWARDED:
        db_tender.awarded_at = now
    elif status == TenderStatus.CANCELLED:
        db_tender.cancelled_at = now
    
    db.commit()
    db.refresh(db_tender)
    return db_tender
