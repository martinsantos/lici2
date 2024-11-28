from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from . import models, schemas, tasks
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter(prefix="/api/templates", tags=["templates"])

@router.get("/", response_model=List[schemas.Template])
async def list_templates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all scraping templates"""
    try:
        logger.debug("Attempting to fetch templates from database")
        templates = db.query(models.ScrapingTemplate)\
            .offset(skip)\
            .limit(limit)\
            .all()
        logger.debug(f"Successfully fetched {len(templates)} templates")
        
        # Log the first template for debugging
        if templates:
            template_dict = {
                "id": templates[0].id,
                "name": templates[0].name,
                "description": templates[0].description,
                "url": templates[0].url,
                "fields": templates[0].fields,
                "created_at": templates[0].created_at.isoformat(),
                "updated_at": templates[0].updated_at.isoformat(),
                "is_active": templates[0].is_active
            }
            logger.debug(f"First template data: {json.dumps(template_dict, indent=2)}")
            
        result = [
            {
                "id": t.id,
                "name": t.name,
                "description": t.description,
                "url": t.url,
                "fields": t.fields,
                "created_at": t.created_at.isoformat(),
                "updated_at": t.updated_at.isoformat(),
                "is_active": t.is_active
            }
            for t in templates
        ]
        
        logger.debug(f"Returning {len(result)} templates")
        return result
    except Exception as e:
        logger.error(f"Error fetching templates: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=schemas.Template)
async def create_template(
    template: schemas.TemplateCreate,
    db: Session = Depends(get_db)
):
    """Create a new scraping template"""
    try:
        logger.info("Attempting to create a new template")
        db_template = models.ScrapingTemplate(
            name=template.name,
            description=template.description,
            config=template.config
        )
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        logger.info(f"Successfully created template with id {db_template.id}")
        return db_template
    except Exception as e:
        logger.error(f"Error creating template: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{template_id}", response_model=schemas.Template)
async def get_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific template"""
    try:
        logger.info(f"Attempting to fetch template with id {template_id}")
        template = db.query(models.ScrapingTemplate)\
            .filter(models.ScrapingTemplate.id == template_id)\
            .first()
        if not template:
            logger.error(f"Template with id {template_id} not found")
            raise HTTPException(status_code=404, detail="Template not found")
        logger.info(f"Successfully fetched template with id {template_id}")
        return template
    except Exception as e:
        logger.error(f"Error fetching template: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{template_id}")
async def delete_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """Delete a template"""
    try:
        logger.info(f"Attempting to delete template with id {template_id}")
        template = db.query(models.ScrapingTemplate)\
            .filter(models.ScrapingTemplate.id == template_id)\
            .first()
        if not template:
            logger.error(f"Template with id {template_id} not found")
            raise HTTPException(status_code=404, detail="Template not found")
        db.delete(template)
        db.commit()
        logger.info(f"Successfully deleted template with id {template_id}")
        return {"ok": True}
    except Exception as e:
        logger.error(f"Error deleting template: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{template_id}", response_model=schemas.Template)
async def update_template(
    template_id: int,
    template_update: schemas.TemplateCreate,
    db: Session = Depends(get_db)
):
    """Update a scraping template"""
    try:
        template = db.query(models.ScrapingTemplate).filter(models.ScrapingTemplate.id == template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Actualizar campos
        template.name = template_update.name
        template.description = template_update.description
        template.url = template_update.url
        template.fields = template_update.fields
        template.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(template)
        return template
    except Exception as e:
        logger.error(f"Error updating template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-scraping/{template_id}")
async def test_scraping(
    template_id: int,
    db: Session = Depends(get_db)
):
    """Test scraping with a template"""
    try:
        template = db.query(models.ScrapingTemplate).filter(models.ScrapingTemplate.id == template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Importar las dependencias necesarias
        import requests
        from bs4 import BeautifulSoup
        import re
        from datetime import datetime
        
        # Realizar la petición HTTP
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(template.url, headers=headers, verify=False)
        response.raise_for_status()
        
        # Parsear el HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extraer datos según los campos definidos
        extracted_data = []
        items = soup.find_all('tr', class_='row-item')  # Ajustar según la estructura real
        
        for item in items[:5]:  # Limitar a 5 items para prueba
            data = {}
            for field in template.fields:
                try:
                    element = item.select_one(field['selector'])
                    if element:
                        value = element.text.strip()
                        # Convertir según el tipo de campo
                        if field['type'] == 'date':
                            # Intentar diferentes formatos de fecha
                            date_formats = ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']
                            for fmt in date_formats:
                                try:
                                    value = datetime.strptime(value, fmt).date()
                                    break
                                except ValueError:
                                    continue
                        elif field['type'] == 'number':
                            value = float(re.sub(r'[^\d.]', '', value))
                        
                        data[field['id']] = value
                except Exception as e:
                    logger.error(f"Error extracting field {field['id']}: {str(e)}")
                    data[field['id']] = None
            
            if any(data.values()):  # Solo agregar si se encontró algún dato
                extracted_data.append(data)
        
        return {
            "success": True,
            "message": "Scraping test completed",
            "data": extracted_data
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error making HTTP request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error accessing URL: {str(e)}")
    except Exception as e:
        logger.error(f"Error during scraping test: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run-scraping/{template_id}")
async def run_scraping(
    template_id: int,
    db: Session = Depends(get_db)
):
    """Run scraping and save results as Licitaciones"""
    try:
        # Obtener el template
        template = db.query(models.ScrapingTemplate).filter(models.ScrapingTemplate.id == template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Realizar scraping (similar a test-scraping pero sin límite)
        import requests
        from bs4 import BeautifulSoup
        import re
        from datetime import datetime
        from licitaciones.models import Licitacion
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(template.url, headers=headers, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all('tr', class_='row-item')
        
        new_licitaciones = 0
        updated_licitaciones = 0
        
        for item in items:
            data = {}
            for field in template.fields:
                try:
                    element = item.select_one(field['selector'])
                    if element:
                        value = element.text.strip()
                        if field['type'] == 'date':
                            date_formats = ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']
                            for fmt in date_formats:
                                try:
                                    value = datetime.strptime(value, fmt).date()
                                    break
                                except ValueError:
                                    continue
                        elif field['type'] == 'number':
                            value = float(re.sub(r'[^\d.]', '', value))
                        
                        data[field['id']] = value
                except Exception as e:
                    logger.error(f"Error extracting field {field['id']}: {str(e)}")
                    data[field['id']] = None
            
            if any(data.values()):
                # Verificar si la licitación ya existe
                existing_licitacion = db.query(Licitacion).filter(
                    Licitacion.codigo == data.get('numero_proceso') or 
                    Licitacion.codigo == data.get('numero_expediente') or
                    Licitacion.codigo == data.get('numero_contratacion')
                ).first()
                
                if existing_licitacion:
                    # Actualizar licitación existente
                    for key, value in data.items():
                        if hasattr(existing_licitacion, key) and value is not None:
                            setattr(existing_licitacion, key, value)
                    updated_licitaciones += 1
                else:
                    # Crear nueva licitación
                    new_licitacion = Licitacion(
                        codigo=data.get('numero_proceso') or data.get('numero_expediente') or data.get('numero_contratacion'),
                        titulo=data.get('nombre') or data.get('descripcion') or data.get('objeto'),
                        organismo=data.get('organismo_contratante') or data.get('reparticion') or data.get('organismo'),
                        monto=data.get('monto_estimado') or data.get('presupuesto'),
                        fecha_publicacion=data.get('fecha_publicacion'),
                        fecha_apertura=data.get('fecha_apertura'),
                        estado=data.get('estado') or data.get('etapa'),
                        fuente=template.name,
                        url_fuente=template.url
                    )
                    db.add(new_licitacion)
                    new_licitaciones += 1
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Scraping completed. New: {new_licitaciones}, Updated: {updated_licitaciones}",
            "new_licitaciones": new_licitaciones,
            "updated_licitaciones": updated_licitaciones
        }
        
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
