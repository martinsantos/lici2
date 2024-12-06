from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from . import models
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
import traceback
import json

logger = logging.getLogger(__name__)

def validate_licitacion_data(licitacion_data: dict) -> List[str]:
    """Validate licitacion data and return list of validation errors"""
    errors = []
    
    # Validate required fields
    required_fields = ['titulo', 'organismo', 'estado']
    for field in required_fields:
        if not licitacion_data.get(field):
            errors.append(f"Campo requerido faltante: {field}")
    
    # Validate date fields
    date_fields = ['fecha_publicacion', 'fecha_apertura']
    for field in date_fields:
        if value := licitacion_data.get(field):
            if not isinstance(value, (str, datetime)):
                errors.append(f"Formato de fecha inválido para {field}")
    
    return errors

def get_licitaciones(
    db: Session, 
    skip: int = 0, 
    limit: int = 10,
    order_by: str = "fecha_publicacion",
    order_desc: bool = True
) -> List[models.Licitacion]:
    """Get list of licitaciones with pagination and ordering"""
    try:
        query = db.query(models.Licitacion)
        
        # Apply ordering
        if hasattr(models.Licitacion, order_by):
            order_column = getattr(models.Licitacion, order_by)
            if order_desc:
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column.asc())
        
        return query.offset(skip).limit(limit).all()
    except Exception as e:
        logger.error(f"Error getting licitaciones: {str(e)}\n{traceback.format_exc()}")
        raise

def get_licitacion(db: Session, licitacion_id: str) -> Optional[models.Licitacion]:
    """Get a specific licitacion by ID"""
    try:
        return db.query(models.Licitacion)\
            .filter(models.Licitacion.id == licitacion_id)\
            .first()
    except Exception as e:
        logger.error(f"Error getting licitacion {licitacion_id}: {str(e)}\n{traceback.format_exc()}")
        raise

def create_licitacion(db: Session, licitacion_data: dict) -> models.Licitacion:
    """Create a new licitacion with validation"""
    try:
        # Validate data
        validation_errors = validate_licitacion_data(licitacion_data)
        if validation_errors:
            raise ValueError(f"Errores de validación: {', '.join(validation_errors)}")
        
        # Ensure dates are datetime objects
        date_fields = ['fecha_publicacion', 'fecha_apertura']
        for field in date_fields:
            if value := licitacion_data.get(field):
                if isinstance(value, str):
                    try:
                        licitacion_data[field] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    except ValueError as e:
                        logger.error(f"Invalid date format for {field}: {value}")
                        licitacion_data[field] = None
        
        # Log the data being saved
        logger.info(f"Creating licitacion with data: {json.dumps({k: str(v) for k, v in licitacion_data.items()}, ensure_ascii=False)}")
        
        # Create licitacion
        db_licitacion = models.Licitacion(**licitacion_data)
        db.add(db_licitacion)
        db.commit()
        db.refresh(db_licitacion)
        
        logger.info(f"Successfully created licitacion: {db_licitacion.id} - {db_licitacion.titulo}")
        return db_licitacion
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating licitacion: {str(e)}\n{traceback.format_exc()}")
        raise ValueError(f"La licitación ya existe o viola restricciones de integridad: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating licitacion: {str(e)}\n{traceback.format_exc()}")
        raise ValueError(f"Error de base de datos: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating licitacion: {str(e)}\n{traceback.format_exc()}")
        raise

def update_licitacion(
    db: Session, 
    licitacion_id: str, 
    licitacion_data: dict
) -> Optional[models.Licitacion]:
    """Update an existing licitacion"""
    try:
        db_licitacion = get_licitacion(db, licitacion_id)
        if not db_licitacion:
            return None
            
        # Validate data
        validation_errors = validate_licitacion_data(licitacion_data)
        if validation_errors:
            raise ValueError(f"Errores de validación: {', '.join(validation_errors)}")
            
        # Update fields
        for key, value in licitacion_data.items():
            if hasattr(db_licitacion, key):
                setattr(db_licitacion, key, value)
        
        db.commit()
        db.refresh(db_licitacion)
        logger.info(f"Successfully updated licitacion: {db_licitacion.id}")
        return db_licitacion
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating licitacion: {str(e)}\n{traceback.format_exc()}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating licitacion: {str(e)}\n{traceback.format_exc()}")
        raise

def delete_licitacion(db: Session, licitacion_id: str) -> bool:
    """Delete a licitacion"""
    try:
        db_licitacion = get_licitacion(db, licitacion_id)
        if not db_licitacion:
            return False
            
        db.delete(db_licitacion)
        db.commit()
        
        logger.info(f"Deleted licitacion: {licitacion_id}")
        return True
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting licitacion {licitacion_id}: {str(e)}\n{traceback.format_exc()}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting licitacion {licitacion_id}: {str(e)}\n{traceback.format_exc()}")
        raise

def get_templates(db: Session) -> List[Dict[str, Any]]:
    """Get all templates"""
    try:
        templates = db.query(models.Template).all()
        return [
            {
                "id": template.id,
                "nombre": template.nombre,
                "url": template.url,
                "activo": template.activo
            }
            for template in templates
        ]
    except Exception as e:
        logger.error(f"Error getting templates: {str(e)}\n{traceback.format_exc()}")
        raise

def get_template(db: Session, template_id: str) -> Optional[models.Template]:
    """Get a specific template by ID"""
    try:
        return db.query(models.Template)\
            .filter(models.Template.id == template_id)\
            .first()
    except Exception as e:
        logger.error(f"Error getting template {template_id}: {str(e)}\n{traceback.format_exc()}")
        raise
