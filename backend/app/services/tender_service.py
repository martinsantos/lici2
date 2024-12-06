from typing import List, Optional, Tuple
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import select, or_, and_, desc, asc
from sqlalchemy.orm import Session
from app.models.tender import Tender, TenderCreate, TenderUpdate, TenderFilters, TenderStatus
from app.database.models import TenderModel, TenderTagModel
from app.database.session import get_db
import uuid

class TenderService:
    def __init__(self, db: Session):
        self.db = db

    def create_tender(self, tender: TenderCreate) -> Tender:
        tender_dict = tender.dict()
        tender_dict["id"] = str(uuid.uuid4())
        tender_dict["status"] = TenderStatus.DRAFT
        
        # Crear las etiquetas
        tags = []
        for tag_name in tender_dict.pop("tags", []):
            tag = TenderTagModel(
                id=str(uuid.uuid4()),
                name=tag_name,
                created_at=datetime.utcnow()
            )
            tags.append(tag)
        
        # Crear la licitación
        db_tender = TenderModel(**tender_dict)
        db_tender.tags = tags
        
        self.db.add(db_tender)
        self.db.commit()
        self.db.refresh(db_tender)
        
        return Tender.from_orm(db_tender)

    def get_tenders(self, filters: TenderFilters) -> Tuple[List[Tender], int]:
        query = select(TenderModel)
        
        # Aplicar filtros
        if filters.search:
            search_filter = or_(
                TenderModel.title.ilike(f"%{filters.search}%"),
                TenderModel.description.ilike(f"%{filters.search}%")
            )
            query = query.where(search_filter)
        
        if filters.categories:
            query = query.where(TenderModel.category.in_(filters.categories))
        
        if filters.regions:
            query = query.where(TenderModel.region.in_(filters.regions))
        
        if filters.budget_range:
            min_budget, max_budget = map(float, filters.budget_range.split("-"))
            if max_budget == -1:  # Sin límite superior
                query = query.where(TenderModel.budget >= min_budget)
            else:
                query = query.where(and_(
                    TenderModel.budget >= min_budget,
                    TenderModel.budget <= max_budget
                ))
        
        if filters.status:
            query = query.where(TenderModel.status.in_(filters.status))
        
        if filters.tags:
            query = query.join(TenderModel.tags).where(
                TenderTagModel.name.in_(filters.tags)
            )
        
        # Aplicar ordenamiento
        if filters.sort_by == "newest":
            query = query.order_by(desc(TenderModel.created_at))
        elif filters.sort_by == "oldest":
            query = query.order_by(asc(TenderModel.created_at))
        elif filters.sort_by == "budget_high":
            query = query.order_by(desc(TenderModel.budget))
        elif filters.sort_by == "budget_low":
            query = query.order_by(asc(TenderModel.budget))
        elif filters.sort_by == "deadline_close":
            query = query.order_by(asc(TenderModel.deadline))
        
        # Obtener el total de resultados
        total_count = self.db.execute(
            select(func.count()).select_from(query.subquery())
        ).scalar()
        
        # Aplicar paginación
        query = query.offset((filters.page - 1) * filters.page_size)
        query = query.limit(filters.page_size)
        
        # Ejecutar la consulta
        results = self.db.execute(query).scalars().all()
        
        return [Tender.from_orm(tender) for tender in results], total_count

    def get_tender(self, tender_id: str) -> Optional[Tender]:
        tender = self.db.execute(
            select(TenderModel).where(TenderModel.id == tender_id)
        ).scalar_one_or_none()
        
        if not tender:
            raise HTTPException(status_code=404, detail="Licitación no encontrada")
        
        return Tender.from_orm(tender)

    def update_tender(self, tender_id: str, tender_update: TenderUpdate) -> Tender:
        db_tender = self.db.execute(
            select(TenderModel).where(TenderModel.id == tender_id)
        ).scalar_one_or_none()
        
        if not db_tender:
            raise HTTPException(status_code=404, detail="Licitación no encontrada")
        
        update_data = tender_update.dict(exclude_unset=True)
        
        # Actualizar etiquetas si se proporcionan
        if "tags" in update_data:
            tags = []
            for tag_name in update_data.pop("tags"):
                tag = self.db.execute(
                    select(TenderTagModel).where(TenderTagModel.name == tag_name)
                ).scalar_one_or_none()
                
                if not tag:
                    tag = TenderTagModel(
                        id=str(uuid.uuid4()),
                        name=tag_name,
                        created_at=datetime.utcnow()
                    )
                
                tags.append(tag)
            
            db_tender.tags = tags
        
        # Actualizar otros campos
        for field, value in update_data.items():
            setattr(db_tender, field, value)
        
        db_tender.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_tender)
        
        return Tender.from_orm(db_tender)

    def delete_tender(self, tender_id: str) -> None:
        db_tender = self.db.execute(
            select(TenderModel).where(TenderModel.id == tender_id)
        ).scalar_one_or_none()
        
        if not db_tender:
            raise HTTPException(status_code=404, detail="Licitación no encontrada")
        
        self.db.delete(db_tender)
        self.db.commit()

    def update_tender_status(self, tender_id: str, status: TenderStatus) -> Tender:
        db_tender = self.db.execute(
            select(TenderModel).where(TenderModel.id == tender_id)
        ).scalar_one_or_none()
        
        if not db_tender:
            raise HTTPException(status_code=404, detail="Licitación no encontrada")
        
        db_tender.status = status
        db_tender.updated_at = datetime.utcnow()
        
        if status == TenderStatus.AWARDED:
            db_tender.awarded_at = datetime.utcnow()
        elif status == TenderStatus.CANCELLED:
            db_tender.cancelled_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_tender)
        
        return Tender.from_orm(db_tender)
