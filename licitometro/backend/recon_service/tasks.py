from celery import Celery
from sqlalchemy.orm import Session
from datetime import datetime
import json
import logging
import asyncio
from .scraper import Scraper
from .models import ScrapingJob, ScrapingStatus, ScrapingTemplate
from licitaciones.models import Licitacion
from core.database import SessionLocal
from licitaciones.templates import TemplateManager
import uuid

# Configurar Celery
celery = Celery('recon_tasks')
celery.conf.update(
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0',
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

template_manager = TemplateManager()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def parse_date(date_str: str) -> datetime:
    """Parse a date string in ISO format to datetime"""
    if not date_str:
        return None
    try:
        # If it's already a datetime object, return it
        if isinstance(date_str, datetime):
            return date_str
        
        # Try parsing with multiple formats
        date_formats = [
            "%Y-%m-%d",  # ISO format
            "%d/%m/%Y",  # DD/MM/YYYY
            "%m/%d/%Y",  # MM/DD/YYYY
            "%Y/%m/%d",  # YYYY/MM/DD
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(str(date_str), fmt)
            except ValueError:
                continue
        
        # If no format works, use dateutil
        from dateutil.parser import parse as dateutil_parse
        try:
            return dateutil_parse(str(date_str), fuzzy=True)
        except (ValueError, TypeError):
            logger.error(f"Could not parse date: {date_str}")
            return None
    except Exception as e:
        logger.error(f"Unexpected error parsing date: {e}")
        return None

def generate_unique_id():
    return str(uuid.uuid4())

def clean_licitacion_data(licitacion_data):
    """
    Clean and validate licitacion data before saving
    """
    # Remove None values and generate a unique ID
    cleaned_data = {k: v for k, v in licitacion_data.items() if v is not None}
    
    # Ensure a unique ID is generated
    cleaned_data['id'] = str(uuid.uuid4())
    
    # Standardize date fields
    date_fields = ['fecha_publicacion', 'fecha_apertura']
    for field in date_fields:
        if field in cleaned_data:
            try:
                # Try parsing the date, convert to datetime if possible
                cleaned_data[field] = parse_date(cleaned_data[field])
            except Exception as e:
                logger.warning(f"Could not parse date for {field}: {cleaned_data[field]}")
                cleaned_data[field] = None
    
    # Validate and clean numeric fields
    numeric_fields = ['monto', 'presupuesto']
    for field in numeric_fields:
        if field in cleaned_data:
            try:
                cleaned_data[field] = float(cleaned_data[field])
            except (ValueError, TypeError):
                cleaned_data[field] = None
    
    # Truncate text fields to prevent database errors
    text_fields = ['titulo', 'descripcion', 'organismo']
    for field in text_fields:
        if field in cleaned_data and isinstance(cleaned_data[field], str):
            cleaned_data[field] = cleaned_data[field][:500]  # Limit to 500 characters
    
    # Ensure required fields are present
    required_fields = ['titulo', 'organismo', 'estado']
    for field in required_fields:
        if field not in cleaned_data:
            logger.warning(f"Missing required field: {field}")
            cleaned_data[field] = 'N/A'
    
    return cleaned_data

def run_scraping_task(job_id: int):
    """
    Run a scraping job for a specific template
    """
    db = SessionLocal()
    try:
        # Get the job details
        job = db.query(ScrapingJob).filter(ScrapingJob.id == job_id).first()
        if not job:
            logger.error(f"No scraping job found with ID {job_id}")
            return None

        # Get the template
        template_config = db.query(ScrapingTemplate).filter(ScrapingTemplate.id == job.template_id).first()
        if not template_config:
            logger.error(f"No template found for job {job_id}")
            return None

        # Initialize scraping progress
        total_extracted = 0
        saved_count = 0
        error_count = 0

        # Run template-specific scraping
        try:
            # Get the specific template class
            template_instance = template_manager.get_template_by_url(template_config.url)
            
            if not template_instance:
                logger.error(f"No template found for URL: {template_config.url}")
                return None
            
            # Extract licitaciones
            extracted_licitaciones = template_instance.extract_licitaciones()
            total_extracted = len(extracted_licitaciones)
            
            logger.info(f"Extracted {total_extracted} licitaciones from {template_config.name}")

            # Process and save each licitacion
            for licitacion_data in extracted_licitaciones:
                try:
                    # Clean and validate data
                    cleaned_data = clean_licitacion_data(licitacion_data)
                    
                    # Log the data being saved
                    logger.debug(f"Saving licitacion: {cleaned_data}")
                    
                    # Create Licitacion object
                    db_licitacion = Licitacion(**cleaned_data)
                    db.add(db_licitacion)
                    
                    saved_count += 1
                except Exception as save_error:
                    error_count += 1
                    logger.error(f"Error saving licitacion: {save_error}")
                    logger.error(f"Problematic data: {licitacion_data}")
            
            # Commit all changes
            db.commit()
            
            logger.info(f"Job {job_id} completed. Total: {total_extracted}, Saved: {saved_count}, Errors: {error_count}")
            
            # Update job status
            job.status = ScrapingStatus.COMPLETED
            job.result = {
                "total_extracted": total_extracted,
                "saved_count": saved_count,
                "error_count": error_count
            }
            db.commit()

        except Exception as scrape_error:
            logger.error(f"Error in scraping process: {scrape_error}")
            job.status = ScrapingStatus.FAILED
            job.error_message = str(scrape_error)
            db.rollback()

    except Exception as e:
        logger.error(f"Unexpected error in run_scraping_task: {e}")
        db.rollback()
    finally:
        db.close()

    return {
        "job_id": job_id,
        "total_extracted": total_extracted,
        "saved_count": saved_count,
        "error_count": error_count
    }

@celery.task(bind=True)
def run_scraping_task_celery(self, job_id: int):
    """Execute a scraping job"""
    run_scraping_task(job_id)
