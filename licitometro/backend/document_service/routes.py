from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Response, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models.base import Document, Licitacion
import os
import logging
import traceback
import uuid
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# Create file handler which logs even debug messages
fh = logging.FileHandler('document_routes.log')
fh.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add formatter to ch and fh
ch.setFormatter(formatter)
fh.setFormatter(formatter)

# Add ch and fh to logger
logger.addHandler(ch)
logger.addHandler(fh)

# Create router with CORS configuration
router = APIRouter(tags=["documents"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload_multiple_files")
async def upload_multiple_files(
    request: Request,
    files: List[UploadFile] = File(default=None),
    licitacion_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Received request to upload files for licitacion {licitacion_id}")
        logger.info(f"Request headers: {request.headers}")
        
        # Check if files were provided
        if not files:
            logger.error("No files provided in request")
            raise HTTPException(
                status_code=400,
                detail="No files provided"
            )

        # Check if licitacion exists if licitacion_id is provided
        if licitacion_id:
            licitacion = db.query(Licitacion).filter(Licitacion.id == licitacion_id).first()
            if not licitacion:
                logger.error(f"Licitacion {licitacion_id} not found")
                raise HTTPException(
                    status_code=404,
                    detail=f"Licitacion {licitacion_id} not found"
                )
            
        logger.info(f"Number of files received: {len(files)}")
        uploaded_files = []
        
        for file in files:
            try:
                logger.info(f"Processing file: {file.filename}")
                
                # Generate unique filename
                file_ext = os.path.splitext(file.filename)[1]
                unique_filename = f"{uuid.uuid4()}{file_ext}"
                file_path = os.path.join(UPLOAD_DIR, unique_filename)
                
                # Ensure upload directory exists
                os.makedirs(UPLOAD_DIR, exist_ok=True)
                
                # Save file locally
                try:
                    contents = await file.read()
                    with open(file_path, "wb") as buffer:
                        buffer.write(contents)
                    logger.info(f"File saved successfully: {file_path}")
                except Exception as save_error:
                    logger.error(f"Error saving file {file.filename}: {str(save_error)}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Error saving file {file.filename}: {str(save_error)}"
                    )
                
                # Create document record
                try:
                    doc = Document(
                        nombre=file.filename,
                        tipo=file.content_type or 'application/octet-stream',
                        url=file_path,
                        contenido="",  # El contenido se procesará después si es necesario
                        processed=False,
                        licitacion_id=licitacion_id  # Asociar con la licitación
                    )
                    db.add(doc)
                    db.commit()
                    db.refresh(doc)
                    logger.info(f"Document record created: {doc.id} for licitacion {licitacion_id}")
                except Exception as db_error:
                    logger.error(f"Database error for file {file.filename}: {str(db_error)}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    # Try to delete the file if database operation fails
                    try:
                        os.remove(file_path)
                    except:
                        pass
                    raise HTTPException(
                        status_code=500,
                        detail=f"Database error for file {file.filename}: {str(db_error)}"
                    )
                
                uploaded_files.append({
                    "id": doc.id,
                    "nombre": doc.nombre,
                    "tipo": doc.tipo,
                    "url": f"/api/documents/download/{doc.id}",
                    "licitacion_id": licitacion_id
                })
                
            except Exception as e:
                logger.error(f"Error processing file {file.filename}: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error processing file {file.filename}: {str(e)}"
                )
        
        logger.info(f"Successfully processed {len(uploaded_files)} files for licitacion {licitacion_id}")
        return {"files": uploaded_files}
        
    except Exception as e:
        logger.error(f"Unhandled error in upload_multiple_files: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Server error: {str(e)}"
        )

@router.post("/upload/{licitacion_id}")
async def upload_document(
    file: UploadFile = File(...),
    licitacion_id: int = None,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Received request to upload document for licitacion {licitacion_id}")
        
        # Check if licitacion exists
        if licitacion_id:
            try:
                licitacion = db.query(Licitacion).filter(Licitacion.id == licitacion_id).first()
                if not licitacion:
                    logger.error(f"Licitacion {licitacion_id} not found")
                    raise HTTPException(status_code=404, detail="Licitacion not found")
            except Exception as licitacion_error:
                logger.error(f"Error checking licitacion {licitacion_id}: {str(licitacion_error)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise HTTPException(status_code=500, detail=f"Error checking licitacion: {str(licitacion_error)}")
        
        # Generate unique filename
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save file locally
        try:
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
        except Exception as save_error:
            logger.error(f"Error saving file {file.filename}: {str(save_error)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Error saving file: {str(save_error)}")
        
        logger.info(f"File {file.filename} saved to {file_path}")
        
        # Create document record
        try:
            doc = Document(
                nombre=file.filename,
                tipo=file.content_type or 'application/octet-stream',
                url=file_path,
                contenido="",  # El contenido se procesará después si es necesario
                processed=False
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)
        except Exception as db_error:
            logger.error(f"Error creating document record for file {file.filename}: {str(db_error)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Error creating document record: {str(db_error)}")
        
        logger.info(f"Document record created for file {file.filename}")
        
        return {
            "id": doc.id,
            "nombre": doc.nombre,
            "tipo": doc.tipo,
            "url": f"/api/documents/download/{doc.id}"
        }
        
    except Exception as e:
        logger.error(f"Error in upload_document: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{document_id}")
async def get_document(document_id: int, db: Session = Depends(get_db)):
    try:
        logger.info(f"Received request to get document {document_id}")
        
        try:
            doc = db.query(Document).filter(Document.id == document_id).first()
            if not doc:
                logger.error(f"Document {document_id} not found")
                raise HTTPException(status_code=404, detail="Document not found")
        except Exception as db_error:
            logger.error(f"Error retrieving document {document_id}: {str(db_error)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Error retrieving document: {str(db_error)}")
            
        logger.info(f"Document {document_id} found")
        
        return {
            "id": doc.id,
            "nombre": doc.nombre,
            "tipo": doc.tipo,
            "url": doc.url,
            "processed": doc.processed,
            "created_at": str(doc.created_at),
            "updated_at": str(doc.updated_at)
        }
        
    except Exception as e:
        logger.error(f"Error in get_document: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/licitacion/{licitacion_id}")
async def get_licitacion_documents(licitacion_id: int, db: Session = Depends(get_db)):
    try:
        logger.info(f"Received request to get documents for licitacion {licitacion_id}")
        
        try:
            docs = db.query(Document).filter(Document.licitacionId == licitacion_id).all()
        except Exception as db_error:
            logger.error(f"Error retrieving documents for licitacion {licitacion_id}: {str(db_error)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Error retrieving documents: {str(db_error)}")
        
        logger.info(f"Found {len(docs)} documents for licitacion {licitacion_id}")
        
        return {
            "documents": [{
                "id": doc.id,
                "nombre": doc.nombre,
                "tipo": doc.tipo,
                "url": doc.url
            } for doc in docs]
        }
    except Exception as e:
        logger.error(f"Error in get_licitacion_documents: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        logger.debug(f"Listing documents: skip={skip}, limit={limit}")
        
        # Log database connection details
        logger.debug(f"Database session: {db}")
        
        # Check if Document model exists
        from models.base import Document
        logger.debug(f"Document model: {Document}")
        
        # Verify database connection
        try:
            connection = db.bind.connect()
            logger.debug("Database connection successful")
            connection.close()
        except Exception as conn_error:
            logger.error(f"Database connection error: {str(conn_error)}")
            raise HTTPException(status_code=500, detail=f"Database connection error: {str(conn_error)}")
        
        # Attempt to query documents
        try:
            docs = db.query(Document).offset(skip).limit(limit).all()
        except Exception as query_error:
            logger.error(f"Query error: {str(query_error)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Query error: {str(query_error)}")
        
        logger.debug(f"Found {len(docs)} documents")
        
        # Log details of first document if exists
        if docs:
            first_doc = docs[0]
            logger.debug(f"First document details: {first_doc.__dict__}")
        
        # Convert to response format
        try:
            response = {
                "documents": [{
                    "id": doc.id,
                    "nombre": doc.nombre,
                    "tipo": doc.tipo,
                    "url": doc.url,
                    "processed": doc.processed,
                    "created_at": str(doc.created_at),
                    "updated_at": str(doc.updated_at)
                } for doc in docs]
            }
            logger.debug(f"Response: {response}")
            return response
        except Exception as format_error:
            logger.error(f"Error formatting response: {str(format_error)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Error formatting response: {str(format_error)}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unhandled error in list_documents: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{document_id}")
async def download_document(document_id: int, db: Session = Depends(get_db)):
    try:
        logger.info(f"Received request to download document {document_id}")
        
        try:
            doc = db.query(Document).filter(Document.id == document_id).first()
            if not doc:
                logger.error(f"Document {document_id} not found")
                raise HTTPException(status_code=404, detail="Document not found")
        except Exception as db_error:
            logger.error(f"Error retrieving document {document_id}: {str(db_error)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Error retrieving document: {str(db_error)}")
            
        if not os.path.exists(doc.filepath):
            logger.error(f"File {doc.filepath} not found")
            raise HTTPException(status_code=404, detail="File not found")
            
        try:
            with open(doc.filepath, "rb") as f:
                content = f.read()
        except Exception as read_error:
            logger.error(f"Error reading file {doc.filepath}: {str(read_error)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Error reading file: {str(read_error)}")
            
        logger.info(f"File {doc.filepath} downloaded")
        
        return Response(
            content=content,
            media_type=doc.tipo,
            headers={
                "Content-Disposition": f"attachment; filename={doc.nombre}"
            }
        )
        
    except Exception as e:
        logger.error(f"Error in download_document: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{document_id}")
async def delete_document(document_id: int, db: Session = Depends(get_db)):
    try:
        logger.info(f"Received request to delete document {document_id}")
        
        try:
            doc = db.query(Document).filter(Document.id == document_id).first()
            if not doc:
                logger.error(f"Document {document_id} not found")
                raise HTTPException(status_code=404, detail="Document not found")
        except Exception as db_error:
            logger.error(f"Error retrieving document {document_id}: {str(db_error)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Error retrieving document: {str(db_error)}")
            
        # Delete file if it exists
        if os.path.exists(doc.filepath):
            try:
                os.remove(doc.filepath)
                logger.info(f"File {doc.filepath} deleted")
            except Exception as delete_error:
                logger.error(f"Error deleting file {doc.filepath}: {str(delete_error)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise HTTPException(status_code=500, detail=f"Error deleting file: {str(delete_error)}")
            
        # Delete database record
        try:
            db.delete(doc)
            db.commit()
        except Exception as db_error:
            logger.error(f"Error deleting document {document_id}: {str(db_error)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Error deleting document: {str(db_error)}")
        
        logger.info(f"Document {document_id} deleted")
        
        return {"message": "Document deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error in delete_document: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
