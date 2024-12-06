from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Body
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from database import get_db
from .service_integration import ServiceIntegration
import logging
from datetime import datetime
from pydantic import BaseModel
import traceback

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Pydantic models for request validation
class TemplateCreate(BaseModel):
    nombre: str
    descripcion: str | None = None
    config: Dict[str, Any] = {}
    features: List[Dict[str, Any]] = []

# Create routers
router = APIRouter()
recon_router = APIRouter()

@router.get("/templates")
async def list_templates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        logger.debug(f"Listing templates: skip={skip}, limit={limit}")
        
        # Log database connection details
        logger.debug(f"Database session: {db}")
        
        # Check if Template model exists
        from models.base import ReconTemplate
        logger.debug(f"Template model: {ReconTemplate}")
        
        # Attempt to query templates
        templates = db.query(ReconTemplate).offset(skip).limit(limit).all()
        
        logger.debug(f"Found {len(templates)} templates")
        
        # Log details of first template if exists
        if templates:
            first_template = templates[0]
            logger.debug(f"First template details: {first_template.__dict__}")
        
        return {
            "templates": [{
                "id": template.id,
                "nombre": template.nombre,
                "descripcion": template.descripcion,
                "created_at": str(template.created_at),
                "updated_at": str(template.updated_at)
            } for template in templates]
        }
    except Exception as e:
        logger.error(f"Error in list_templates: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/templates")
async def create_template(template_data: TemplateCreate, db: Session = Depends(get_db)):
    """Create a new template"""
    logger.debug(f"Handling POST /templates request with data: {template_data}")
    try:
        service = ServiceIntegration(db)
        template = service.create_template(template_data.dict())
        logger.info(f"Created template with ID: {template.id}")
        return {
            "message": "Template created successfully",
            "template_id": template.id
        }
    except Exception as e:
        logger.error(f"Error creating template: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates/{template_id}")
async def get_template(template_id: int, db: Session = Depends(get_db)):
    """Get a specific template"""
    logger.debug(f"Handling GET /templates/{template_id} request")
    try:
        service = ServiceIntegration(db)
        template = service.get_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return template
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting template: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/templates/{template_id}")
async def delete_template(template_id: int, db: Session = Depends(get_db)):
    """Delete a template"""
    logger.debug(f"Handling DELETE /templates/{template_id} request")
    try:
        service = ServiceIntegration(db)
        success = service.delete_template(template_id)
        if not success:
            raise HTTPException(status_code=404, detail="Template not found")
        return {"message": "Template deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting template: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/templates/{template_id}/scrape")
async def start_scraping(template_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Start a scraping job for a specific template"""
    logger.debug(f"Handling POST /templates/{template_id}/scrape request")
    try:
        service = ServiceIntegration(db)
        job = service.start_scraping_job(template_id)
        if not job:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Add scraping task to background tasks
        background_tasks.add_task(service.run_scraping_job, job.id)
        
        return {
            "message": "Scraping job started successfully",
            "job_id": job.id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting scraping job: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates/{template_id}/status")
async def get_scraping_status(template_id: int, db: Session = Depends(get_db)):
    """Get the status of the most recent scraping job for a template"""
    logger.debug(f"Handling GET /templates/{template_id}/status request")
    try:
        service = ServiceIntegration(db)
        status = service.get_latest_job_status(template_id)
        if status is None:
            raise HTTPException(status_code=404, detail="No scraping jobs found for this template")
        return {
            "status": status.status,
            "start_time": status.start_time,
            "end_time": status.end_time,
            "error_message": status.error_message
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scraping status: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/licitaciones")
async def list_licitaciones(template_id: int = None, db: Session = Depends(get_db)):
    """List all licitaciones, optionally filtered by template"""
    logger.debug(f"Handling GET /licitaciones request")
    try:
        service = ServiceIntegration(db)
        licitaciones = service.list_licitaciones(template_id)
        return {"licitaciones": licitaciones}
    except Exception as e:
        logger.error(f"Error listing licitaciones: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/licitaciones/{licitacion_id}")
async def get_licitacion(licitacion_id: int, db: Session = Depends(get_db)):
    """Get a specific licitacion"""
    logger.debug(f"Handling GET /licitaciones/{licitacion_id} request")
    try:
        service = ServiceIntegration(db)
        licitacion = service.get_licitacion(licitacion_id)
        if not licitacion:
            raise HTTPException(status_code=404, detail="Licitacion not found")
        return licitacion
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting licitacion: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
