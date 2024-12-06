from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from document_service.routes import router as document_router
from recon_service.recon_routes import router as template_router, recon_router
from licitaciones.routes import router as licitaciones_router
from documents.routes import router as documents_router
from database import Base, engine
import uvicorn
import logging
import os
import traceback
from typing import List
from fastapi.staticfiles import StaticFiles

# Configure logging
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'app.log')

# Configure logging with explicit file handler
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# File handler
try:
    file_handler = logging.FileHandler(log_file, mode='w')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
except Exception as e:
    print(f"Error setting up file logging: {e}")

# Reduce noise from other libraries
logging.getLogger('sqlalchemy').setLevel(logging.WARNING)

# Ensure logging works before creating database tables
try:
    logger.info("Starting application initialization")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Error creating database tables: {str(e)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    raise

app = FastAPI(
    title="Licitometro API",
    description="API for document and licitaciones management",
    version="1.0.0"
)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount the uploads directory with custom configuration
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR, html=True, check_dir=True), name="uploads")

# Configure CORS
origins = [
    "http://localhost:3002",
    "http://127.0.0.1:3002",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(
    document_router,
    tags=["documents"]
)

# Include licitaciones router
app.include_router(
    licitaciones_router,
    tags=["licitaciones"]
)

# Recon routes
app.include_router(
    template_router,
    tags=["recon"]
)

# If recon_router exists and is different, include it as well
if recon_router:
    app.include_router(
        recon_router,
        tags=["recon_advanced"]
    )

# Add OPTIONS handler for CORS preflight requests
@app.options("/{full_path:path}")
async def options_handler():
    return {"detail": "OK"}

@app.post("/api/documents/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    try:
        uploaded_files = []
        for file in files:
            # Generate a safe filename
            filename = file.filename
            file_path = os.path.join(UPLOAD_DIR, filename)
            
            # Save the file
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Create file URL
            file_url = f"/uploads/{filename}"
            
            uploaded_files.append({
                "filename": filename,
                "url": file_url,
                "size": len(content)
            })
        
        return uploaded_files
    except Exception as e:
        logger.error(f"Error uploading files: {str(e)}")
        raise HTTPException(status_code=500, detail="Error uploading files")

@app.get("/")
async def root():
    return {"message": "Licitometro API is running"}

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP Exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": str(exc.detail)}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
