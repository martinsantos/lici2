from typing import Dict
from pydantic import BaseModel

class APIEndpoints(BaseModel):
    # Licitaciones endpoints
    LICITACIONES_BASE: str = "/api/v1/licitaciones"
    LICITACION_DETAIL: str = "/api/v1/licitaciones/{id}"
    LICITACION_DOCUMENTS: str = "/api/v1/licitaciones/{id}/documents"
    LICITACION_SEARCH: str = "/api/v1/licitaciones/search"
    
    # RECON endpoints
    RECON_BASE: str = "/api/v1/recon"
    RECON_TEMPLATES: str = "/api/v1/recon/templates"
    RECON_FEATURES: str = "/api/v1/recon/features"
    RECON_SCRAPE: str = "/api/v1/recon/scrape"
    
    # Document endpoints
    DOCUMENTS_BASE: str = "/api/v1/documents"
    DOCUMENT_UPLOAD: str = "/api/v1/documents/upload"
    DOCUMENT_DOWNLOAD: str = "/api/v1/documents/{id}"
    
    # Search endpoints
    SEARCH_BASE: str = "/api/v1/search"
    SEARCH_QUERY: str = "/api/v1/search/query"
    
    # Authentication endpoints
    AUTH_LOGIN: str = "/api/v1/auth/login"
    AUTH_REFRESH: str = "/api/v1/auth/refresh"
    AUTH_PROFILE: str = "/api/v1/auth/profile"

class ExternalAPIs(BaseModel):
    # External API configurations
    COMPRAR_AR_BASE: str = "https://comprar.gob.ar"
    CHILE_COMPRA_BASE: str = "https://www.mercadopublico.cl"
    
    # Add more external APIs as needed

class APIConfig:
    def __init__(self):
        self.endpoints = APIEndpoints()
        self.external = ExternalAPIs()
        
        # API versions
        self.API_VERSION = "v1"
        self.BASE_PATH = f"/api/{self.API_VERSION}"
        
        # Service configurations
        self.service_urls = {
            "frontend": "http://localhost:3000",
            "backend": "http://localhost:5000",
            "search": "http://localhost:8000",
            "documents": "http://localhost:9000",
        }
        
        # CORS configuration
        self.cors_origins = [
            "http://localhost:3000",  # Frontend
            "http://127.0.0.1:3000",  # Frontend alternative
            "http://localhost:5000",  # Backend
            "http://127.0.0.1:5000",  # Backend alternative
        ]
        
        # Rate limiting
        self.rate_limit = {
            "requests": 100,
            "period": 60  # seconds
        }

# Create a singleton instance
api_config = APIConfig()
