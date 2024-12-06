from typing import List, Optional, Tuple
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.tender import (
    Tender,
    TenderCreate,
    TenderUpdate,
    TenderFilters,
    TenderStatus,
)
from app.services.tender_service import TenderService

router = APIRouter()

@router.post("/tenders/", response_model=Tender, status_code=status.HTTP_201_CREATED,
    summary="Crear nueva licitación",
    description="""
    Crea una nueva licitación en el sistema.
    Solo los usuarios con rol de manager o admin pueden crear licitaciones.
    """,
    responses={
        201: {
            "description": "Licitación creada exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "title": "Nueva Licitación",
                        "description": "Descripción de la licitación",
                        "budget": 100000.0,
                        "deadline": "2024-12-31T23:59:59",
                        "status": "DRAFT",
                        "category": "Construction",
                        "region": "North",
                        "requirements": [
                            {
                                "description": "Requisito 1",
                                "is_mandatory": True
                            }
                        ],
                        "documents": [
                            {
                                "name": "Documento 1",
                                "url": "http://example.com/doc.pdf",
                                "type": "pdf",
                                "size": 1024
                            }
                        ],
                        "tags": ["construccion", "obra-publica"]
                    }
                }
            }
        },
        403: {
            "description": "Permisos insuficientes",
            "content": {
                "application/json": {
                    "example": {"detail": "Not enough permissions"}
                }
            }
        }
    }
)
async def create_tender(
    tender: TenderCreate,
    db: Session = Depends(get_db)
):
    """
    Crea una nueva licitación con los siguientes datos:
    
    - **title**: Título de la licitación
    - **description**: Descripción detallada
    - **budget**: Presupuesto en la moneda local
    - **deadline**: Fecha límite de presentación
    - **category**: Categoría de la licitación
    - **region**: Región donde se ejecutará
    - **requirements**: Lista de requisitos
    - **documents**: Lista de documentos adjuntos
    - **tags**: Lista de etiquetas
    """
    service = TenderService(db)
    return service.create_tender(tender)

@router.get("/tenders/", response_model=Tuple[List[Tender], int],
    summary="Listar licitaciones",
    description="""
    Obtiene la lista de licitaciones con opciones de filtrado y paginación.
    Los filtros son opcionales y se pueden combinar.
    """,
    responses={
        200: {
            "description": "Lista de licitaciones obtenida exitosamente",
            "content": {
                "application/json": {
                    "example": [{
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "title": "Licitación 1",
                        "status": "PUBLISHED",
                        "budget": 100000.0,
                        "category": "Construction",
                        "region": "North"
                    }]
                }
            }
        }
    }
)
async def get_tenders(
    search: Optional[str] = None,
    categories: List[str] = Query(default=[]),
    regions: List[str] = Query(default=[]),
    budget_range: Optional[str] = None,
    status: List[TenderStatus] = Query(default=[]),
    tags: List[str] = Query(default=[]),
    sort_by: str = "newest",
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
) -> Tuple[List[Tender], int]:
    """
    Obtiene la lista de licitaciones con los siguientes filtros opcionales:
    
    - **search**: Término de búsqueda en título y descripción
    - **categories**: Lista de categorías
    - **regions**: Lista de regiones
    - **min_budget**: Presupuesto mínimo
    - **max_budget**: Presupuesto máximo
    - **status**: Estado de la licitación
    - **tags**: Lista de etiquetas
    - **sort_by**: Campo por el cual ordenar
    - **sort_desc**: Orden descendente si es True
    - **skip**: Número de registros a saltar
    - **limit**: Número máximo de registros a retornar
    """
    filters = TenderFilters(
        search=search,
        categories=categories,
        regions=regions,
        budget_range=budget_range,
        status=status,
        tags=tags,
        sort_by=sort_by,
        page=page,
        page_size=page_size
    )
    
    service = TenderService(db)
    return service.get_tenders(filters)

@router.get("/tenders/{tender_id}", response_model=Tender,
    summary="Obtener licitación",
    description="""
    Obtiene una licitación específica por ID.
    """,
    responses={
        200: {
            "description": "Licitación obtenida exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "title": "Licitación 1",
                        "status": "PUBLISHED",
                        "budget": 100000.0,
                        "category": "Construction",
                        "region": "North"
                    }
                }
            }
        },
        404: {
            "description": "Licitación no encontrada",
            "content": {
                "application/json": {
                    "example": {"detail": "Tender not found"}
                }
            }
        }
    }
)
async def get_tender(
    tender_id: str,
    db: Session = Depends(get_db)
) -> Tender:
    """
    Obtiene una licitación específica por ID.
    """
    service = TenderService(db)
    return service.get_tender(tender_id)

@router.put("/tenders/{tender_id}", response_model=Tender,
    summary="Actualizar licitación",
    description="""
    Actualiza una licitación existente.
    Solo los usuarios con rol de manager o admin pueden actualizar licitaciones.
    """,
    responses={
        200: {
            "description": "Licitación actualizada exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "title": "Licitación 1",
                        "status": "PUBLISHED",
                        "budget": 100000.0,
                        "category": "Construction",
                        "region": "North"
                    }
                }
            }
        },
        403: {
            "description": "Permisos insuficientes",
            "content": {
                "application/json": {
                    "example": {"detail": "Not enough permissions"}
                }
            }
        },
        404: {
            "description": "Licitación no encontrada",
            "content": {
                "application/json": {
                    "example": {"detail": "Tender not found"}
                }
            }
        }
    }
)
async def update_tender(
    tender_id: str,
    tender_update: TenderUpdate,
    db: Session = Depends(get_db)
) -> Tender:
    """
    Actualiza una licitación existente con los siguientes datos:
    
    - **title**: Título de la licitación
    - **description**: Descripción detallada
    - **budget**: Presupuesto en la moneda local
    - **deadline**: Fecha límite de presentación
    - **category**: Categoría de la licitación
    - **region**: Región donde se ejecutará
    - **requirements**: Lista de requisitos
    - **documents**: Lista de documentos adjuntos
    - **tags**: Lista de etiquetas
    """
    service = TenderService(db)
    return service.update_tender(tender_id, tender_update)

@router.delete("/tenders/{tender_id}",
    summary="Eliminar licitación",
    description="""
    Elimina una licitación existente.
    Solo los usuarios con rol de manager o admin pueden eliminar licitaciones.
    """,
    responses={
        200: {
            "description": "Licitación eliminada exitosamente",
            "content": {
                "application/json": {
                    "example": {"message": "Licitación eliminada correctamente"}
                }
            }
        },
        403: {
            "description": "Permisos insuficientes",
            "content": {
                "application/json": {
                    "example": {"detail": "Not enough permissions"}
                }
            }
        },
        404: {
            "description": "Licitación no encontrada",
            "content": {
                "application/json": {
                    "example": {"detail": "Tender not found"}
                }
            }
        }
    }
)
async def delete_tender(
    tender_id: str,
    db: Session = Depends(get_db)
) -> None:
    """
    Elimina una licitación existente.
    """
    service = TenderService(db)
    service.delete_tender(tender_id)
    return {"message": "Licitación eliminada correctamente"}

@router.patch("/tenders/{tender_id}/status", response_model=Tender,
    summary="Actualizar estado de licitación",
    description="""
    Actualiza el estado de una licitación existente.
    Solo los usuarios con rol de manager o admin pueden actualizar el estado de las licitaciones.
    """,
    responses={
        200: {
            "description": "Estado de licitación actualizado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "title": "Licitación 1",
                        "status": "PUBLISHED",
                        "budget": 100000.0,
                        "category": "Construction",
                        "region": "North"
                    }
                }
            }
        },
        403: {
            "description": "Permisos insuficientes",
            "content": {
                "application/json": {
                    "example": {"detail": "Not enough permissions"}
                }
            }
        },
        404: {
            "description": "Licitación no encontrada",
            "content": {
                "application/json": {
                    "example": {"detail": "Tender not found"}
                }
            }
        }
    }
)
async def update_tender_status(
    tender_id: str,
    status: TenderStatus,
    db: Session = Depends(get_db)
) -> Tender:
    """
    Actualiza el estado de una licitación existente.
    """
    service = TenderService(db)
    return service.update_tender_status(tender_id, status)
