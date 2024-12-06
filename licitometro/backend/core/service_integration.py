from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from models.base import Licitacion, Document, ReconTemplate
from document_service.minio_client import MinioClient
from recon_service.scraper import Scraper as ReconScraper
from search_service.search import SearchService

class ServiceIntegration:
    def __init__(self, db: Session):
        self.db = db
        self.minio_client = MinioClient()
        self.recon_scraper = ReconScraper(config={})
        self.search_service = SearchService()

    async def process_licitacion(self, licitacion_data: dict) -> Licitacion:
        """
        Procesa una licitación, integrando todos los servicios necesarios
        """
        # 1. Crear la licitación en la base de datos
        licitacion = Licitacion(**licitacion_data)
        self.db.add(licitacion)
        self.db.commit()
        self.db.refresh(licitacion)

        # 2. Procesar documentos adjuntos
        if licitacion_data.get('documentos'):
            for doc in licitacion_data['documentos']:
                await self.process_document(doc, licitacion.id)

        # 3. Indexar en el servicio de búsqueda
        await self.index_licitacion(licitacion)

        return licitacion

    async def process_document(self, document_data: dict, licitacion_id: int) -> Document:
        """
        Procesa un documento, subiéndolo a MinIO y creando el registro en la base de datos
        """
        # 1. Subir archivo a MinIO
        file_path = await self.minio_client.upload_file(
            document_data['file'],
            document_data['filename']
        )

        # 2. Crear registro del documento
        document = Document(
            filename=document_data['filename'],
            file_path=file_path,
            content_type=document_data.get('content_type', 'application/octet-stream'),
            size=document_data.get('size', 0),
            licitacion_id=licitacion_id
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)

        return document

    async def index_licitacion(self, licitacion: Licitacion):
        """
        Indexa una licitación en el servicio de búsqueda
        """
        licitacion_data = {
            'id': licitacion.id,
            'titulo': licitacion.titulo,
            'descripcion': licitacion.descripcion,
            'organismo': licitacion.organismo,
            'fecha_publicacion': licitacion.fechaPublicacion.isoformat(),
            'estado': licitacion.estado,
            'categoria': licitacion.categoria,
            'ubicacion': licitacion.ubicacion,
            'monto': licitacion.monto
        }
        await self.search_service.index_document(licitacion_data)

    async def scrape_and_process(self, template_id: int):
        """
        Ejecuta un scraping basado en una plantilla y procesa los resultados
        """
        # 1. Obtener la plantilla
        template = self.db.query(ReconTemplate).filter_by(id=template_id).first()
        if not template:
            raise ValueError(f"Template {template_id} not found")

        # 2. Ejecutar el scraping
        results = await self.recon_scraper.scrape(template.config)

        # 3. Procesar cada resultado
        processed_licitaciones = []
        for result in results:
            licitacion = await self.process_licitacion(result)
            processed_licitaciones.append(licitacion)

        # 4. Actualizar la plantilla
        template.last_run = datetime.utcnow()
        self.db.commit()

        return processed_licitaciones

    async def search_licitaciones(self, query: str, filters: Optional[dict] = None) -> List[dict]:
        """
        Busca licitaciones usando el servicio de búsqueda
        """
        results = await self.search_service.search(query, filters)
        
        # Enriquecer resultados con datos de la base de datos
        licitaciones = []
        for result in results:
            licitacion = self.db.query(Licitacion).get(result['id'])
            if licitacion:
                licitaciones.append({
                    **result,
                    'documentos': [doc.filename for doc in licitacion.documents],
                    'requisitos': licitacion.requisitos,
                    'garantia': licitacion.garantia
                })
        
        return licitaciones

    async def get_licitacion(self, licitacion_id: int) -> Optional[Licitacion]:
        """
        Obtiene una licitación por su ID, incluyendo documentos relacionados
        """
        licitacion = self.db.query(Licitacion).filter(Licitacion.id == licitacion_id).first()
        
        if not licitacion:
            return None
        
        # Cargar documentos relacionados
        documentos = self.db.query(Document).filter(Document.licitacion_id == licitacion_id).all()
        
        # Convertir a diccionario para poder agregar documentos
        licitacion_dict = {
            **{c.name: getattr(licitacion, c.name) for c in licitacion.__table__.columns},
            'documentos': [
                {
                    'id': doc.id, 
                    'filename': doc.filename, 
                    'file_path': doc.file_path,
                    'content_type': doc.content_type,
                    'size': doc.size
                } for doc in documentos
            ]
        }
        
        return licitacion_dict

    async def list_templates(self) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de todos los templates de RECON
        """
        templates = self.db.query(ReconTemplate).all()
        return [
            {
                'id': template.id,
                'nombre': template.name,
                'descripcion': template.description,
                'activo': template.is_active,
                'ultima_ejecucion': template.last_run,
                'config': template.config
            } for template in templates
        ]

    async def list_licitaciones(self, skip: int = 0, limit: int = 100, order_by: str = 'fechaPublicacion', order_desc: bool = True) -> List[Dict[str, Any]]:
        """
        Obtiene una lista de licitaciones con paginación y ordenamiento
        """
        # Mapeo de nombres de campos para evitar inyección de SQL
        order_field_map = {
            'fechaPublicacion': Licitacion.fechaPublicacion,
            'titulo': Licitacion.titulo,
            'organismo': Licitacion.organismo,
            'estado': Licitacion.estado
        }

        # Validar el campo de ordenamiento
        if order_by not in order_field_map:
            order_by = 'fechaPublicacion'

        # Obtener el campo de ordenamiento
        order_column = order_field_map[order_by]

        # Aplicar ordenamiento
        query = self.db.query(Licitacion)
        if order_desc:
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        # Aplicar paginación
        licitaciones = query.offset(skip).limit(limit).all()

        # Convertir a diccionarios con información adicional
        return [
            {
                'id': licitacion.id,
                'titulo': licitacion.titulo,
                'descripcion': licitacion.descripcion,
                'fechaPublicacion': licitacion.fechaPublicacion,
                'organismo': licitacion.organismo,
                'estado': licitacion.estado,
                'categoria': licitacion.categoria,
                'documentos_count': len(licitacion.documents)
            } for licitacion in licitaciones
        ]
