from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile, Form
from sqlalchemy.orm import Session, joinedload
from typing import List, Dict, Any, Optional
from database import get_db
from models.base import Licitacion, Document, ReconTemplate
import logging
from sqlalchemy import desc, asc
from datetime import datetime
import traceback
import os
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)

router = APIRouter(tags=["licitaciones"])

@router.get("/api/licitaciones")
async def list_licitaciones(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        logger.info("Starting list_licitaciones endpoint")
        logger.info(f"Database session: {db}")
        
        # Query licitaciones with eager loading of documents
        try:
            query = db.query(Licitacion).options(
                joinedload(Licitacion.documentos)
            )
            logger.info(f"Query built: {str(query)}")
            
            # Add filters
            query = query.filter(Licitacion.existe == True)
            logger.info("Added existe filter")
            
            # Add ordering
            query = query.order_by(desc(Licitacion.fecha_publicacion))
            logger.info("Added ordering")
            
            # Execute query
            licitaciones = query.offset(skip).limit(limit).all()
            logger.info(f"Query executed, found {len(licitaciones)} results")
            
            # Format response
            response = []
            for licitacion in licitaciones:
                licitacion_dict = {
                    "id": licitacion.id,
                    "titulo": licitacion.titulo,
                    "descripcion": licitacion.descripcion,
                    "organismo": licitacion.organismo,
                    "fecha_publicacion": licitacion.fecha_publicacion.isoformat() if licitacion.fecha_publicacion else None,
                    "fecha_apertura": licitacion.fecha_apertura.isoformat() if licitacion.fecha_apertura else None,
                    "numero_expediente": licitacion.numero_expediente,
                    "numero_licitacion": licitacion.numero_licitacion,
                    "estado": licitacion.estado,
                    "categoria": licitacion.categoria,
                    "ubicacion": licitacion.ubicacion,
                    "plazo": licitacion.plazo,
                    "requisitos": licitacion.requisitos,
                    "garantia": licitacion.garantia,
                    "presupuesto": float(licitacion.presupuesto) if licitacion.presupuesto else None,
                    "monto": float(licitacion.monto) if licitacion.monto else None,
                    "moneda": licitacion.moneda,
                    "idioma": licitacion.idioma,
                    "etapa": licitacion.etapa,
                    "modalidad": licitacion.modalidad,
                    "area": licitacion.area,
                    "documentos": [
                        {
                            "id": doc.id,
                            "nombre": doc.nombre,
                            "tipo": doc.tipo,
                            "url": doc.full_url
                        } for doc in licitacion.documentos
                    ] if licitacion.documentos else []
                }
                response.append(licitacion_dict)
            
            return response
            
        except Exception as db_error:
            logger.error(f"Database error: {str(db_error)}")
            raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(db_error)}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing licitaciones: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/licitaciones/{licitacion_id}")
async def get_licitacion(licitacion_id: int, db: Session = Depends(get_db)):
    try:
        logger.info(f"Getting licitacion with id {licitacion_id}")
        licitacion = db.query(Licitacion).options(
            joinedload(Licitacion.documentos)
        ).filter(
            Licitacion.id == licitacion_id,
            Licitacion.existe == True
        ).first()
        
        if not licitacion:
            logger.warning(f"Licitacion {licitacion_id} not found")
            raise HTTPException(status_code=404, detail="Licitación no encontrada")
        
        logger.info(f"Found licitacion: {licitacion.titulo}")
        logger.info(f"Documents count: {len(licitacion.documentos or [])}")
        
        response = {
            "id": licitacion.id,
            "titulo": licitacion.titulo,
            "organismo": licitacion.organismo,
            "descripcion": licitacion.descripcion,
            "fechaPublicacion": licitacion.fecha_publicacion.isoformat() if licitacion.fecha_publicacion else None,
            "fechaApertura": licitacion.fecha_apertura.isoformat() if licitacion.fecha_apertura else None,
            "presupuesto": float(licitacion.presupuesto) if licitacion.presupuesto else None,
            "monto": float(licitacion.monto) if licitacion.monto else None,
            "moneda": licitacion.moneda or "ARS",
            "idioma": licitacion.idioma or "es",
            "estado": licitacion.estado or "Pendiente",
            "categoria": licitacion.categoria,
            "ubicacion": licitacion.ubicacion,
            "plazo": licitacion.plazo,
            "etapa": licitacion.etapa,
            "modalidad": licitacion.modalidad,
            "area": licitacion.area,
            "requisitos": licitacion.requisitos,
            "garantia": licitacion.garantia,
            "documentos": [
                {
                    "id": str(doc.id),
                    "nombre": doc.nombre,
                    "tipo": doc.tipo,
                    "url": f"/uploads/{doc.url}" if doc.url else None,
                    "licitacion_id": doc.licitacion_id
                } for doc in licitacion.documentos
            ] if licitacion.documentos else []
        }
        
        logger.info(f"Response prepared with {len(response['documentos'])} documents")
        return response
        
    except Exception as e:
        logger.error(f"Error getting licitacion {licitacion_id}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/licitaciones")
async def create_licitacion(licitacion: Dict[str, Any], db: Session = Depends(get_db)):
    try:
        # Convert string dates to datetime
        if "fecha_publicacion" in licitacion and licitacion["fecha_publicacion"]:
            licitacion["fecha_publicacion"] = datetime.fromisoformat(licitacion["fecha_publicacion"].replace("Z", "+00:00"))
            
        if "fecha_apertura" in licitacion and licitacion["fecha_apertura"]:
            licitacion["fecha_apertura"] = datetime.fromisoformat(licitacion["fecha_apertura"].replace("Z", "+00:00"))
            
        # Create new licitacion
        new_licitacion = Licitacion(
            titulo=licitacion.get("titulo"),
            descripcion=licitacion.get("descripcion"),
            organismo=licitacion.get("organismo"),
            fecha_publicacion=licitacion.get("fecha_publicacion"),
            fecha_apertura=licitacion.get("fecha_apertura"),
            numero_expediente=licitacion.get("numero_expediente"),
            numero_licitacion=licitacion.get("numero_licitacion"),
            estado=licitacion.get("estado", "Pendiente"),
            categoria=licitacion.get("categoria"),
            ubicacion=licitacion.get("ubicacion"),
            plazo=licitacion.get("plazo"),
            requisitos=licitacion.get("requisitos", []),
            garantia=licitacion.get("garantia", {}),
            presupuesto=licitacion.get("presupuesto", 0),
            monto=licitacion.get("monto", 0),
            moneda=licitacion.get("moneda", "ARS"),
            idioma=licitacion.get("idioma", "es"),
            etapa=licitacion.get("etapa"),
            modalidad=licitacion.get("modalidad"),
            area=licitacion.get("area"),
            url=licitacion.get("url", ""),
            existe=licitacion.get("existe", True),
            origen=licitacion.get("origen", "manual"),
            processed=licitacion.get("processed", False),
            raw_data=licitacion.get("raw_data", {}),
            contacto=licitacion.get("contacto", {})
        )
        
        db.add(new_licitacion)
        db.commit()
        db.refresh(new_licitacion)
        
        return {
            "id": new_licitacion.id,
            "titulo": new_licitacion.titulo,
            "descripcion": new_licitacion.descripcion,
            "fecha_publicacion": new_licitacion.fecha_publicacion.isoformat() if new_licitacion.fecha_publicacion else None,
            "fecha_apertura": new_licitacion.fecha_apertura.isoformat() if new_licitacion.fecha_apertura else None,
            "numero_expediente": new_licitacion.numero_expediente,
            "numero_licitacion": new_licitacion.numero_licitacion,
            "organismo": new_licitacion.organismo,
            "contacto": new_licitacion.contacto,
            "monto": new_licitacion.monto,
            "estado": new_licitacion.estado,
            "categoria": new_licitacion.categoria,
            "ubicacion": new_licitacion.ubicacion,
            "plazo": new_licitacion.plazo,
            "requisitos": new_licitacion.requisitos,
            "garantia": new_licitacion.garantia,
            "presupuesto": new_licitacion.presupuesto,
            "moneda": new_licitacion.moneda,
            "idioma": new_licitacion.idioma,
            "etapa": new_licitacion.etapa,
            "modalidad": new_licitacion.modalidad,
            "area": new_licitacion.area,
            "existe": new_licitacion.existe,
            "origen": new_licitacion.origen
        }
    except Exception as e:
        logger.error(f"Error creating licitacion: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/api/licitaciones/{licitacion_id}")
async def update_licitacion(
    licitacion_id: int,
    titulo: str = Form(None),
    descripcion: str = Form(None),
    presupuesto: str = Form(None),
    fecha_inicio: str = Form(None),
    fecha_fin: str = Form(None),
    estado: str = Form(None),
    documentos: List[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Updating licitacion {licitacion_id}")
        
        # Get existing licitacion
        licitacion = db.query(Licitacion).filter(Licitacion.id == licitacion_id).first()
        if not licitacion:
            raise HTTPException(status_code=404, detail="Licitación no encontrada")
            
        # Update fields if provided
        if titulo is not None:
            licitacion.titulo = titulo
        if descripcion is not None:
            licitacion.descripcion = descripcion
        if presupuesto is not None:
            licitacion.presupuesto = presupuesto
        if fecha_inicio is not None:
            licitacion.fecha_inicio = fecha_inicio
        if fecha_fin is not None:
            licitacion.fecha_fin = fecha_fin
        if estado is not None:
            licitacion.estado = estado
            
        # Handle document uploads
        if documentos:
            for doc in documentos:
                try:
                    # Generate a safe filename
                    filename = f"{licitacion_id}-{doc.filename}"
                    file_path = os.path.join("uploads", filename)
                    
                    # Ensure uploads directory exists
                    os.makedirs("uploads", exist_ok=True)
                    
                    # Save the file
                    with open(file_path, "wb") as buffer:
                        buffer.write(await doc.read())
                    
                    # Create document record with clean path
                    document = Document(
                        nombre=doc.filename,
                        tipo=doc.content_type,
                        url=filename,  # Store just the filename
                        licitacion_id=licitacion_id
                    )
                    db.add(document)
                    
                except Exception as e:
                    logger.error(f"Error saving document: {str(e)}")
                    logger.error(traceback.format_exc())
                    raise HTTPException(status_code=500, detail=f"Error saving document: {str(e)}")
        
        db.commit()
        logger.info(f"Successfully updated licitacion {licitacion_id}")
        
        return {"message": "Licitación actualizada exitosamente", "id": licitacion_id}
        
    except Exception as e:
        logger.error(f"Error updating licitacion: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/licitaciones/scrape/{template_id}")
async def start_scraping(
    template_id: str,
    db: Session = Depends(get_db)
):
    """Iniciar tarea de scraping para un template"""
    try:
        template = db.query(ReconTemplate).filter(ReconTemplate.id == template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="Template no encontrado")
        
        if not template.activo:
            raise HTTPException(status_code=400, detail="Template inactivo")
        
        # Start celery task
        task = run_scraping_task.delay(template_id)
        
        return {
            "task_id": task.id,
            "status": "started",
            "template": {
                "id": template.id,
                "nombre": template.nombre,
                "url": template.url
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting scraping task: {str(e)}")
        raise HTTPException(status_code=500, detail="Error iniciando tarea de scraping")

@router.get("/api/licitaciones/scrape/status/{task_id}")
async def get_scraping_status(task_id: str):
    """Obtener estado de una tarea de scraping con información detallada de progreso"""
    try:
        logger.info(f"Getting status for task {task_id}")
        return {"status": "completed"}
    except Exception as e:
        logger.error(f"Error getting licitacion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/licitaciones/templates", response_model=List[Dict[str, Any]])
async def list_templates(
    db: Session = Depends(get_db)
):
    """Obtener lista de templates disponibles"""
    try:
        templates = db.query(ReconTemplate).all()
        return [{
            "id": template.id,
            "nombre": template.nombre,
            "url": template.url,
            "activo": template.activo
        } for template in templates]
    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}")
        raise HTTPException(status_code=500, detail="Error obteniendo templates")

@router.get("/api/licitaciones/scrape/active")
async def get_active_tasks():
    """Obtener lista de tareas de scraping activas"""
    try:
        # Get active tasks from Celery
        active_tasks = run_scraping_task.app.control.inspect().active()
        
        if not active_tasks:
            return []
            
        # Format task information
        tasks = []
        for worker, worker_tasks in active_tasks.items():
            for task in worker_tasks:
                if task['name'] == 'licitaciones.tasks.run_scraping_task':
                    task_result = AsyncResult(task['id'])
                    tasks.append({
                        'task_id': task['id'],
                        'status': task_result.status,
                        'progress': task_result.info if task_result.info else {},
                        'worker': worker
                    })
        
        return tasks
    except Exception as e:
        logger.error(f"Error getting active tasks: {str(e)}")
        raise HTTPException(status_code=500, detail="Error obteniendo tareas activas")

@router.get("/api/licitaciones/search", response_model=List[Dict[str, Any]])
async def search_licitaciones(
    query: str,
    estado: str = None,
    categoria: str = None,
    organismo: str = None,
    db: Session = Depends(get_db)
):
    try:
        filters = {
            "estado": estado,
            "categoria": categoria,
            "organismo": organismo
        }
        filters = {k: v for k, v in filters.items() if v is not None}
        
        licitaciones = db.query(Licitacion).filter(
            Licitacion.titulo.like(f"%{query}%") | 
            Licitacion.descripcion.like(f"%{query}%") | 
            Licitacion.numeroExpediente.like(f"%{query}%") | 
            Licitacion.numeroLicitacion.like(f"%{query}%") | 
            Licitacion.organismo.like(f"%{query}%") | 
            Licitacion.contacto.like(f"%{query}%")
        )
        
        for key, value in filters.items():
            licitaciones = licitaciones.filter(getattr(Licitacion, key) == value)
        
        licitaciones = licitaciones.all()
        
        return [{
            "id": lic.id,
            "titulo": lic.titulo,
            "organismo": lic.organismo,
            "descripcion": lic.descripcion,
            "fechaPublicacion": lic.fecha_publicacion.isoformat() if lic.fecha_publicacion else None,
            "fechaApertura": lic.fecha_apertura.isoformat() if lic.fecha_apertura else None,
            "presupuesto": lic.presupuesto,
            "moneda": lic.moneda,
            "estado": lic.estado,
            "documentos": [
                {
                    "id": doc.id,
                    "nombre": doc.nombre,
                    "tipo": doc.tipo,
                    "url": doc.full_url
                } for doc in (lic.documentos or [])
            ]
        } for lic in licitaciones]
    except Exception as e:
        logger.error(f"Error searching licitaciones: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/licitaciones/{licitacion_id}", response_model=Dict[str, Any])
async def get_licitacion(
    licitacion_id: int,
    db: Session = Depends(get_db)
):
    try:
        licitacion = db.query(Licitacion).filter(Licitacion.id == licitacion_id).first()
        if not licitacion:
            raise HTTPException(status_code=404, detail="Licitación no encontrada")
        
        return {
            "id": licitacion.id,
            "titulo": licitacion.titulo,
            "descripcion": licitacion.descripcion,
            "fechaPublicacion": licitacion.fechaPublicacion.isoformat(),
            "fechaApertura": licitacion.fechaApertura.isoformat() if licitacion.fechaApertura else None,
            "numeroExpediente": licitacion.numeroExpediente,
            "numeroLicitacion": licitacion.numeroLicitacion,
            "organismo": licitacion.organismo,
            "contacto": licitacion.contacto,
            "monto": licitacion.monto,
            "estado": licitacion.estado,
            "categoria": licitacion.categoria,
            "ubicacion": licitacion.ubicacion,
            "plazo": licitacion.plazo,
            "requisitos": licitacion.requisitos,
            "garantia": licitacion.garantia,
            "presupuesto": licitacion.presupuesto,
            "moneda": licitacion.moneda,
            "idioma": licitacion.idioma,
            "etapa": licitacion.etapa,
            "modalidad": licitacion.modalidad,
            "area": licitacion.area,
            "existe": licitacion.existe,
            "origen": licitacion.origen,
            "documentos": [{
                "id": doc.id,
                "filename": doc.filename,
                "mimetype": doc.mimetype,
                "size": doc.size,
                "uploadDate": doc.uploadDate.isoformat()
            } for doc in licitacion.documentos]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting licitacion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

origins = ["*"]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
