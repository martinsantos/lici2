from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.sql import select
from datetime import datetime
from models.base import ReconTemplate, Feature, Licitacion, Document, ScrapingJob
from database import get_db
import logging

logger = logging.getLogger(__name__)

class ServiceIntegration:
    def __init__(self, db: Session):
        self.db = db

    def list_templates(self) -> List[Dict[str, Any]]:
        """
        List all active RECON templates with their features
        """
        templates = self.db.query(ReconTemplate).filter(ReconTemplate.activo == True).all()
        return [{
            'id': template.id,
            'nombre': template.nombre,
            'descripcion': template.descripcion,
            'features': [{
                'id': feature.id,
                'nombre': feature.nombre,
                'tipo': feature.tipo,
                'descripcion': feature.descripcion,
                'requerido': feature.requerido,
                'configuracion': feature.configuracion
            } for feature in template.features],
            'config': template.config,
            'createdAt': template.createdAt.isoformat(),
            'updatedAt': template.updatedAt.isoformat()
        } for template in templates]

    def get_template(self, template_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific template by ID
        """
        template = self.db.query(ReconTemplate).filter(
            ReconTemplate.id == template_id,
            ReconTemplate.activo == True
        ).first()
        
        if not template:
            return None
            
        return {
            'id': template.id,
            'nombre': template.nombre,
            'descripcion': template.descripcion,
            'features': [{
                'id': feature.id,
                'nombre': feature.nombre,
                'tipo': feature.tipo,
                'descripcion': feature.descripcion,
                'requerido': feature.requerido,
                'configuracion': feature.configuracion
            } for feature in template.features],
            'config': template.config,
            'createdAt': template.createdAt.isoformat(),
            'updatedAt': template.updatedAt.isoformat()
        }

    def create_template(self, template_data: Dict[str, Any]) -> ReconTemplate:
        """
        Create a new RECON template
        """
        logger.debug(f"Creating template with data: {template_data}")
        try:
            template = ReconTemplate(
                nombre=template_data['nombre'],
                descripcion=template_data.get('descripcion'),
                config=template_data.get('config', {}),
                activo=True,
                createdAt=datetime.utcnow(),
                updatedAt=datetime.utcnow()
            )
            
            self.db.add(template)
            self.db.flush()  # Get the template ID
            
            # Add features if provided
            features = template_data.get('features', [])
            for feature_data in features:
                feature = Feature(
                    nombre=feature_data['nombre'],
                    tipo=feature_data.get('tipo', 'text'),
                    descripcion=feature_data.get('descripcion'),
                    requerido=feature_data.get('requerido', False),
                    configuracion=feature_data.get('configuracion', {}),
                    template_id=template.id
                )
                self.db.add(feature)
            
            self.db.commit()
            return template
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating template: {str(e)}", exc_info=True)
            raise

    def delete_template(self, template_id: int) -> bool:
        """
        Delete a template by ID
        """
        try:
            template = self.db.query(ReconTemplate).filter(
                ReconTemplate.id == template_id,
                ReconTemplate.activo == True
            ).first()
            
            if not template:
                return False
                
            template.activo = False
            template.updatedAt = datetime.utcnow()
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting template: {str(e)}", exc_info=True)
            raise

    def start_scraping_job(self, template_id: int) -> Optional[ScrapingJob]:
        """
        Start a new scraping job for a template
        """
        try:
            template = self.db.query(ReconTemplate).filter(
                ReconTemplate.id == template_id,
                ReconTemplate.activo == True
            ).first()
            
            if not template:
                return None
                
            job = ScrapingJob(
                template_id=template_id,
                status="pending",
                start_time=datetime.utcnow()
            )
            
            self.db.add(job)
            self.db.commit()
            return job
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error starting scraping job: {str(e)}", exc_info=True)
            raise

    def run_scraping_job(self, job_id: int):
        """
        Execute a scraping job
        """
        try:
            job = self.db.query(ScrapingJob).filter(ScrapingJob.id == job_id).first()
            if not job:
                logger.error(f"Job {job_id} not found")
                return
                
            job.status = "running"
            self.db.commit()
            
            try:
                # TODO: Implement actual scraping logic here
                # For now, just simulate success
                job.status = "completed"
                job.end_time = datetime.utcnow()
                
            except Exception as e:
                job.status = "failed"
                job.error_message = str(e)
                job.end_time = datetime.utcnow()
                logger.error(f"Error running scraping job {job_id}: {str(e)}", exc_info=True)
                
            finally:
                self.db.commit()
                
        except Exception as e:
            logger.error(f"Error managing scraping job {job_id}: {str(e)}", exc_info=True)
            raise

    def get_latest_job_status(self, template_id: int) -> Optional[ScrapingJob]:
        """
        Get the status of the most recent scraping job for a template
        """
        try:
            job = self.db.query(ScrapingJob).filter(
                ScrapingJob.template_id == template_id
            ).order_by(ScrapingJob.start_time.desc()).first()
            
            return job
            
        except Exception as e:
            logger.error(f"Error getting job status: {str(e)}", exc_info=True)
            raise

    def list_licitaciones(self, template_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List all licitaciones, optionally filtered by template
        """
        query = self.db.query(Licitacion)
        if template_id is not None:
            query = query.filter(Licitacion.templateId == template_id)
            
        licitaciones = query.all()
        return [{
            'id': lic.id,
            'titulo': lic.titulo,
            'descripcion': lic.descripcion,
            'fechaPublicacion': lic.fechaPublicacion.isoformat(),
            'fechaApertura': lic.fechaApertura.isoformat() if lic.fechaApertura else None,
            'numeroExpediente': lic.numeroExpediente,
            'numeroLicitacion': lic.numeroLicitacion,
            'organismo': lic.organismo,
            'contacto': lic.contacto,
            'monto': lic.monto,
            'estado': lic.estado,
            'categoria': lic.categoria,
            'ubicacion': lic.ubicacion,
            'plazo': lic.plazo,
            'requisitos': lic.requisitos,
            'garantia': lic.garantia,
            'presupuesto': lic.presupuesto,
            'moneda': lic.moneda,
            'idioma': lic.idioma,
            'etapa': lic.etapa,
            'modalidad': lic.modalidad,
            'area': lic.area,
            'existe': lic.existe,
            'origen': lic.origen,
            'documentos': [{
                'id': doc.id,
                'filename': doc.filename,
                'mimetype': doc.mimetype,
                'size': doc.size,
                'uploadDate': doc.uploadDate.isoformat(),
                'metadata': doc.metadata
            } for doc in lic.documentos],
            'createdAt': lic.createdAt.isoformat(),
            'updatedAt': lic.updatedAt.isoformat()
        } for lic in licitaciones]

    def get_licitacion(self, licitacion_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific licitacion by ID
        """
        licitacion = self.db.query(Licitacion).filter(Licitacion.id == licitacion_id).first()
        
        if not licitacion:
            return None
            
        return {
            'id': licitacion.id,
            'titulo': licitacion.titulo,
            'descripcion': licitacion.descripcion,
            'fechaPublicacion': licitacion.fechaPublicacion.isoformat(),
            'fechaApertura': licitacion.fechaApertura.isoformat() if licitacion.fechaApertura else None,
            'numeroExpediente': licitacion.numeroExpediente,
            'numeroLicitacion': licitacion.numeroLicitacion,
            'organismo': licitacion.organismo,
            'contacto': licitacion.contacto,
            'monto': licitacion.monto,
            'estado': licitacion.estado,
            'categoria': licitacion.categoria,
            'ubicacion': licitacion.ubicacion,
            'plazo': licitacion.plazo,
            'requisitos': licitacion.requisitos,
            'garantia': licitacion.garantia,
            'presupuesto': licitacion.presupuesto,
            'moneda': licitacion.moneda,
            'idioma': licitacion.idioma,
            'etapa': licitacion.etapa,
            'modalidad': licitacion.modalidad,
            'area': licitacion.area,
            'existe': licitacion.existe,
            'origen': licitacion.origen,
            'documentos': [{
                'id': doc.id,
                'filename': doc.filename,
                'mimetype': doc.mimetype,
                'size': doc.size,
                'uploadDate': doc.uploadDate.isoformat(),
                'metadata': doc.metadata
            } for doc in licitacion.documentos],
            'createdAt': licitacion.createdAt.isoformat(),
            'updatedAt': licitacion.updatedAt.isoformat()
        }
