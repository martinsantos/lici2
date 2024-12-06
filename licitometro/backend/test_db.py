from database import SessionLocal
from models.base import ReconTemplate, Feature, ScrapingJob, Licitacion, Document
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_crud_operations():
    """Test basic CRUD operations on all models"""
    db = SessionLocal()
    try:
        # Test 1: Create and read a template
        logger.info("Test 1: Creating template...")
        template = ReconTemplate(
            nombre="Template de Prueba",
            descripcion="Template para pruebas CRUD",
            config={"url": "https://test.com"}
        )
        db.add(template)
        db.commit()
        db.refresh(template)
        
        # Verify template was created
        saved_template = db.query(ReconTemplate).filter_by(id=template.id).first()
        assert saved_template is not None, "Template not found!"
        logger.info(f"Template created successfully with ID: {template.id}")

        # Test 2: Create and read features
        logger.info("Test 2: Creating features...")
        feature = Feature(
            nombre="Feature de Prueba",
            tipo="text",
            descripcion="Feature para pruebas",
            template_id=template.id
        )
        db.add(feature)
        db.commit()
        db.refresh(feature)

        # Verify feature was created and is linked to template
        saved_feature = db.query(Feature).filter_by(id=feature.id).first()
        assert saved_feature is not None, "Feature not found!"
        assert saved_feature.template_id == template.id, "Feature not linked to template!"
        logger.info(f"Feature created successfully with ID: {feature.id}")

        # Test 3: Update operations
        logger.info("Test 3: Testing update operations...")
        template.descripcion = "Descripción actualizada"
        db.commit()
        db.refresh(template)
        
        updated_template = db.query(ReconTemplate).filter_by(id=template.id).first()
        assert updated_template.descripcion == "Descripción actualizada", "Update failed!"
        logger.info("Update operation successful")

        # Test 4: Delete operations
        logger.info("Test 4: Testing delete operations...")
        db.delete(template)  # This should cascade delete the feature
        db.commit()

        deleted_template = db.query(ReconTemplate).filter_by(id=template.id).first()
        deleted_feature = db.query(Feature).filter_by(id=feature.id).first()
        
        assert deleted_template is None, "Template not deleted!"
        assert deleted_feature is None, "Feature not cascade deleted!"
        logger.info("Delete operation successful")

        logger.info("All CRUD tests passed successfully!")
        
    except Exception as e:
        logger.error(f"Error during CRUD tests: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    test_crud_operations()
