from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.base import Document, Licitacion
import logging
import os
from datetime import datetime
import shutil
import uuid
import traceback
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(
    tags=["documents"],
    responses={
        200: {"description": "Success"},
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)

UPLOAD_DIR = "uploads"
MAX_FILENAME_LENGTH = 45  # Leave room for extension

class DocumentResponse(BaseModel):
    id: int
    nombre: str
    tipo: str
    url: str
    licitacion_id: int | None
    processed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

def truncate_filename(filename: str, max_length: int = MAX_FILENAME_LENGTH) -> str:
    """Truncate filename while preserving extension"""
    name, ext = os.path.splitext(filename)
    max_name_length = max_length - len(ext)  # Reserve space for extension
    if max_name_length < 1:  # If extension is too long, truncate it too
        return filename[:max_length]
    truncated_name = name[:max_name_length]
    return truncated_name + ext

# Asegurar que el directorio de uploads exista
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.options("/upload_multiple_files")
async def options_upload():
    return {
        "allow_methods": ["POST", "OPTIONS"],
        "allow_headers": ["*"],
        "allow_credentials": True
    }

@router.post("/upload_multiple_files", response_model=dict)
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    licitacion_id: int = Form(None),
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Uploading {len(files)} files for licitacion_id: {licitacion_id}")
        
        # Add CORS headers explicitly
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
        
        if not licitacion_id:
            raise HTTPException(
                status_code=400,
                detail="licitacion_id is required"
            )
            
        # Verificar que la licitación existe
        licitacion = db.query(Licitacion).filter(Licitacion.id == licitacion_id).first()
        if not licitacion:
            raise HTTPException(
                status_code=404,
                detail=f"Licitacion with id {licitacion_id} not found"
            )
            
        uploaded_files = []

        for file in files:
            try:
                # Generar un nombre de archivo único usando UUID para almacenamiento
                file_uuid = str(uuid.uuid4())
                file_ext = os.path.splitext(file.filename)[1]
                storage_filename = f"{file_uuid}{file_ext}"
                file_path = os.path.join(UPLOAD_DIR, storage_filename)

                # Truncar el nombre original del archivo para la base de datos
                display_filename = truncate_filename(file.filename)
                logger.info(f"Processing file {file.filename} -> display: {display_filename}, storage: {storage_filename}")

                # Guardar el archivo físicamente
                try:
                    with open(file_path, "wb") as buffer:
                        shutil.copyfileobj(file.file, buffer)
                    logger.info(f"File saved to {file_path}")
                except Exception as e:
                    logger.error(f"Error saving file {file.filename}: {str(e)}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Error saving file {file.filename}"
                    )

                # Crear registro en la base de datos
                try:
                    db_file = Document(
                        licitacion_id=licitacion_id,
                        nombre=display_filename,
                        tipo=file.content_type,
                        url=f"/api/documents/download/{file_uuid}",
                        contenido="",
                        processed=False
                    )
                    db.add(db_file)
                    db.flush()  # Para obtener el ID
                    
                    # Actualizar la URL con el ID real
                    db_file.url = f"/api/documents/download/{db_file.id}"
                    
                    uploaded_files.append({
                        "id": db_file.id,
                        "nombre": db_file.nombre,
                        "tipo": db_file.tipo,
                        "url": db_file.url,
                        "licitacion_id": db_file.licitacion_id
                    })
                    logger.info(f"Database record created for file {display_filename} with ID {db_file.id}")
                    
                    # Commit después de cada archivo exitoso
                    db.commit()
                    logger.info(f"Successfully committed file {display_filename}")
                    
                except Exception as e:
                    db.rollback()
                    logger.error(f"Database error for file {display_filename}: {str(e)}")
                    logger.error(traceback.format_exc())
                    # Limpiar el archivo si hay error en la base de datos
                    try:
                        os.remove(file_path)
                    except:
                        pass
                    raise HTTPException(
                        status_code=500,
                        detail=f"Database error for file {display_filename}: {str(e)}"
                    )

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Unexpected error processing file {file.filename}: {str(e)}")
                logger.error(traceback.format_exc())
                raise HTTPException(
                    status_code=500,
                    detail=f"Error processing file {file.filename}: {str(e)}"
                )

        return {"files": uploaded_files, "headers": headers}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in upload_multiple_files: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{document_id}")
async def download_document(document_id: int, db: Session = Depends(get_db)):
    """
    Endpoint para descargar documentos por ID.
    """
    try:
        # Obtener el documento de la base de datos
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Documento no encontrado")

        # Construir la ruta completa al archivo
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            UPLOAD_DIR,
            os.path.basename(document.url)
        )

        # Verificar si el archivo existe
        if not os.path.exists(file_path):
            logger.error(f"Archivo no encontrado en: {file_path}")
            raise HTTPException(
                status_code=404,
                detail=f"Archivo no encontrado en el servidor"
            )

        # Determinar el tipo de contenido
        content_type = document.tipo or "application/octet-stream"

        # Retornar el archivo
        return FileResponse(
            path=file_path,
            filename=document.nombre,
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={document.nombre}"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al descargar documento {document_id}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al descargar el documento: {str(e)}"
        )
