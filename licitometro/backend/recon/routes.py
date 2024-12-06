from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from .services import ScrapingTemplateService
from .database import DatabaseManager
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Inicializar router de FastAPI
router = APIRouter(prefix="/recon", tags=["Scraping Templates"])

# Inicializar gestor de base de datos
db_manager = DatabaseManager(os.getenv('RECON_DATABASE_URL'))

# Modelo Pydantic para validación de entrada
class ScrapingTemplateCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="Nombre único de la plantilla")
    source_url: str = Field(..., description="URL de origen para scraping")
    field_mapping: Dict[str, Dict[str, str]] = Field(..., description="Mapeo de campos")
    transformation_rules: Optional[Dict[str, Dict[str, str]]] = Field(None, description="Reglas de transformación")
    frequency_hours: int = Field(24, ge=1, le=168, description="Frecuencia de scraping en horas")
    is_active: bool = Field(True, description="Estado de la plantilla")

class ScrapingTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    source_url: Optional[str] = None
    field_mapping: Optional[Dict[str, Dict[str, str]]] = None
    transformation_rules: Optional[Dict[str, Dict[str, str]]] = None
    frequency_hours: Optional[int] = Field(None, ge=1, le=168)
    is_active: Optional[bool] = None

@router.post("/templates", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_scraping_template(template: ScrapingTemplateCreate):
    """
    Crear una nueva plantilla de scraping
    """
    try:
        template_service = ScrapingTemplateService()
        result = await template_service.create_template(
            name=template.name,
            source_url=template.source_url,
            field_mapping=template.field_mapping,
            transformation_rules=template.transformation_rules,
            frequency_hours=template.frequency_hours
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/templates", response_model=List[dict])
async def list_scraping_templates(
    is_active: Optional[bool] = None, 
    limit: int = 100, 
    offset: int = 0
):
    """
    Listar plantillas de scraping con opciones de filtrado
    """
    try:
        template_service = ScrapingTemplateService()
        templates = await template_service.list_templates(
            is_active=is_active, 
            limit=limit, 
            offset=offset
        )
        return templates
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/templates/{template_id}", response_model=dict)
async def get_scraping_template(template_id: int):
    """
    Obtener detalles de una plantilla de scraping específica
    """
    try:
        template_service = ScrapingTemplateService()
        template = await template_service.get_template(template_id)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        return template
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/templates/{template_id}", response_model=dict)
async def update_scraping_template(template_id: int, template_update: ScrapingTemplateUpdate):
    """
    Actualizar una plantilla de scraping existente
    """
    try:
        template_service = ScrapingTemplateService()
        updated_template = await template_service.update_template(
            template_id,
            template_update.dict(exclude_unset=True)
        )
        if not updated_template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        return updated_template
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scraping_template(template_id: int):
    """
    Eliminar una plantilla de scraping
    """
    try:
        template_service = ScrapingTemplateService()
        success = await template_service.delete_template(template_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/start/{template_id}", response_model=dict)
async def start_scraping_job(template_id: int):
    """
    Iniciar un trabajo de scraping para una plantilla específica
    """
    try:
        template_service = ScrapingTemplateService()
        # Verificar que la plantilla existe
        template = await template_service.get_template(template_id)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        # Crear y retornar el trabajo
        job = await template_service.start_scraping_job(template_id)
        return job
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Función para incluir el router en la aplicación principal
def include_router(app):
    """
    Incluye los endpoints de RECON en la aplicación FastAPI principal
    """
    app.include_router(router)
