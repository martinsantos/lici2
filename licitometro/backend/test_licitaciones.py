from database import SessionLocal
from models.base import ReconTemplate, Feature, ScrapingJob, Licitacion, Document
import logging
from datetime import datetime, timedelta
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_licitaciones():
    """Test complex operations with licitaciones"""
    db = SessionLocal()
    try:
        # Test 1: Create a complete chain (Template -> ScrapingJob -> Licitacion -> Document)
        logger.info("Test 1: Creating complete chain...")
        
        # Create template
        template = ReconTemplate(
            nombre="Template Licitaciones",
            descripcion="Template para pruebas de licitaciones",
            config={"url": "https://test.com", "frequency": "daily"}
        )
        db.add(template)
        db.commit()
        db.refresh(template)
        logger.info(f"Template created with ID: {template.id}")
        
        # Create scraping job
        job = ScrapingJob(
            template_id=template.id,
            status="completed",
            start_time=datetime.utcnow() - timedelta(hours=1),
            end_time=datetime.utcnow()
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        logger.info(f"Scraping job created with ID: {job.id}")
        
        # Create licitacion
        licitacion = Licitacion(
            template_id=template.id,
            scraping_job_id=job.id,
            titulo="Licitación de Prueba",
            descripcion="Licitación para pruebas",
            url="https://test.com/licitacion/1",
            estado="Publicada",
            fecha_publicacion=datetime.utcnow(),
            fecha_apertura=datetime.utcnow() + timedelta(days=30),
            numero_expediente="EXP-TEST-001",
            numero_licitacion="LIC-TEST-001",
            organismo="Organismo de Prueba",
            contacto={"email": "test@test.com"},
            monto=1000000.0,
            categoria="Test",
            ubicacion="Test Location",
            plazo="30 días",
            requisitos=["Requisito 1", "Requisito 2"],
            garantia={"type": "Performance Bond", "amount": "10%"},
            presupuesto=1200000.0,
            moneda="ARS",
            idioma="es",
            etapa="Publicación",
            modalidad="Public",
            area="IT"
        )
        db.add(licitacion)
        db.commit()
        db.refresh(licitacion)
        logger.info(f"Licitacion created with ID: {licitacion.id}")
        
        # Create document
        document = Document(
            licitacion_id=licitacion.id,
            nombre="documento_test.pdf",
            tipo="application/pdf",
            url="https://test.com/docs/test.pdf",
            contenido="Contenido del documento de prueba"
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        logger.info(f"Document created with ID: {document.id}")
        
        # Test 2: Verify relationships
        logger.info("Test 2: Verifying relationships...")
        
        # Check template -> licitacion relationship
        template_licitaciones = db.query(ReconTemplate).filter_by(id=template.id).first().licitaciones
        assert len(template_licitaciones) == 1, "Template should have one licitacion"
        assert template_licitaciones[0].id == licitacion.id, "Licitacion ID mismatch"
        
        # Check scraping_job -> licitacion relationship
        job_licitaciones = db.query(ScrapingJob).filter_by(id=job.id).first().licitaciones
        assert len(job_licitaciones) == 1, "Job should have one licitacion"
        assert job_licitaciones[0].id == licitacion.id, "Licitacion ID mismatch"
        
        # Check licitacion -> document relationship
        licitacion_documents = db.query(Licitacion).filter_by(id=licitacion.id).first().documentos
        assert len(licitacion_documents) == 1, "Licitacion should have one document"
        assert licitacion_documents[0].id == document.id, "Document ID mismatch"
        
        logger.info("All relationships verified successfully")
        
        # Test 3: Test cascade delete
        logger.info("Test 3: Testing cascade delete...")
        
        # Delete template (should cascade to all related entities)
        db.delete(template)
        db.commit()
        
        # Verify all related entities are deleted
        assert db.query(ReconTemplate).filter_by(id=template.id).first() is None, "Template not deleted"
        assert db.query(ScrapingJob).filter_by(id=job.id).first() is None, "Job not cascade deleted"
        assert db.query(Licitacion).filter_by(id=licitacion.id).first() is None, "Licitacion not cascade deleted"
        assert db.query(Document).filter_by(id=document.id).first() is None, "Document not cascade deleted"
        
        logger.info("Cascade delete successful")
        logger.info("All tests passed successfully!")
        
    except Exception as e:
        logger.error(f"Error during tests: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    test_licitaciones()
