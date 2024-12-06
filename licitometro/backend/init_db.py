from database import engine, SessionLocal, Base

reintenta iniciar frontend y backend

revisa status y corrige

Continua con estos próximos pasos pendientes, procede uno a uno, cuando termines cada paso evalúa lo logrado y el estado de avance, si lo consideras incompleto, itera y vuelve hasta considerarlo terminado. Sólo así prosigue con el siguiente punto, al final haz un resumen de lo realizado.from models.base import ReconTemplate, ScrapingJob, Licitacion, Document, Feature
import logging
from datetime import datetime, timedelta
import json
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def init_db():
    """Initialize database by creating all tables"""
    try:
        # Drop all tables with CASCADE
        with engine.connect() as connection:
            connection.execute(text("DROP TABLE IF EXISTS documents, licitaciones, scraping_jobs, template_features, recon_templates CASCADE"))
            connection.commit()
        logger.info("Dropped all existing tables")
        
        # Import all models to ensure they are included in Base.metadata
        from models.base import ReconTemplate, Feature, ScrapingJob, Licitacion, Document
        
        # Create tables in order
        with engine.connect() as connection:
            # Create recon_templates first
            connection.execute(text("""
                CREATE TABLE recon_templates (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(255),
                    descripcion TEXT,
                    config JSON DEFAULT '{}',
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create template_features with correct foreign key
            connection.execute(text("""
                CREATE TABLE template_features (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(255),
                    tipo VARCHAR(50),
                    descripcion TEXT,
                    requerido BOOLEAN DEFAULT FALSE,
                    configuracion JSON DEFAULT '{}',
                    template_id INTEGER REFERENCES recon_templates(id) ON DELETE CASCADE,
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create scraping_jobs with correct foreign key
            connection.execute(text("""
                CREATE TABLE scraping_jobs (
                    id SERIAL PRIMARY KEY,
                    template_id INTEGER REFERENCES recon_templates(id) ON DELETE CASCADE,
                    status VARCHAR(50) DEFAULT 'pending',
                    start_time TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP WITHOUT TIME ZONE,
                    error_message TEXT,
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create licitaciones with correct foreign keys
            connection.execute(text("""
                CREATE TABLE licitaciones (
                    id SERIAL PRIMARY KEY,
                    template_id INTEGER REFERENCES recon_templates(id) ON DELETE CASCADE,
                    scraping_job_id INTEGER REFERENCES scraping_jobs(id) ON DELETE CASCADE,
                    titulo VARCHAR(500),
                    descripcion TEXT,
                    url VARCHAR(1000),
                    estado VARCHAR(100) DEFAULT 'Pendiente',
                    fecha_publicacion TIMESTAMP WITHOUT TIME ZONE,
                    fecha_apertura TIMESTAMP WITHOUT TIME ZONE,
                    numero_expediente VARCHAR(100),
                    numero_licitacion VARCHAR(100),
                    organismo VARCHAR(255),
                    contacto JSON,
                    monto FLOAT DEFAULT 0,
                    categoria VARCHAR(100),
                    ubicacion VARCHAR(255),
                    plazo VARCHAR(100),
                    requisitos JSON DEFAULT '[]',
                    garantia JSON DEFAULT '{}',
                    presupuesto FLOAT DEFAULT 0,
                    moneda VARCHAR(50) DEFAULT 'ARS',
                    idioma VARCHAR(50) DEFAULT 'es',
                    etapa VARCHAR(100),
                    modalidad VARCHAR(100),
                    area VARCHAR(100),
                    existe BOOLEAN DEFAULT TRUE,
                    origen VARCHAR(100) DEFAULT 'manual',
                    raw_data JSON DEFAULT '{}',
                    processed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create documents with correct foreign key
            connection.execute(text("""
                CREATE TABLE documents (
                    id SERIAL PRIMARY KEY,
                    licitacion_id INTEGER REFERENCES licitaciones(id) ON DELETE CASCADE,
                    nombre VARCHAR(255),
                    tipo VARCHAR(50),
                    url VARCHAR(1000),
                    contenido TEXT,
                    processed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            connection.commit()
            
            # Verify that all tables were created
            tables = connection.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")).fetchall()
            table_names = [table[0] for table in tables]
            logger.info(f"Created tables: {table_names}")
            
            if not all(table in table_names for table in ['recon_templates', 'template_features', 'scraping_jobs', 'licitaciones', 'documents']):
                missing_tables = [table for table in ['recon_templates', 'template_features', 'scraping_jobs', 'licitaciones', 'documents'] if table not in table_names]
                raise Exception(f"Missing tables: {missing_tables}")
        
        logger.info("Created all tables successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

def create_test_data():
    """Create test data for development"""
    try:
        # Create a session
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            # Create test features
            features = [
                Feature(
                    nombre="titulo",
                    tipo="text",
                    descripcion="Título de la licitación",
                    requerido=True,
                    configuracion={"xpath": "//h1"}
                ),
                Feature(
                    nombre="descripcion",
                    tipo="text",
                    descripcion="Descripción de la licitación",
                    requerido=True,
                    configuracion={"xpath": "//div[@class='description']"}
                ),
                Feature(
                    nombre="monto",
                    tipo="number",
                    descripcion="Monto de la licitación",
                    requerido=False,
                    configuracion={"xpath": "//span[@class='budget']"}
                )
            ]
            
            # Create test template
            template = ReconTemplate(
                nombre="Plantilla de Prueba",
                descripcion="Una plantilla de prueba para desarrollo",
                config={
                    "url_pattern": "https://example.com/licitaciones/*",
                    "frequency": "daily"
                },
                features=features  # Associate features with template
            )
            
            session.add(template)
            session.flush()  # Get template ID
            
            # Create test scraping job
            job = ScrapingJob(
                template_id=template.id,
                status="completed",
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow()
            )
            
            session.add(job)
            session.flush()  # Get job ID
            
            # Create test licitacion
            licitacion = Licitacion(
                template_id=template.id,
                scraping_job_id=job.id,
                titulo="Licitación de prueba",
                descripcion="Esta es una licitación de prueba",
                url="https://example.com/licitaciones/123",
                estado="Publicada",
                fecha_publicacion=datetime.utcnow(),
                fecha_apertura=datetime.utcnow() + timedelta(days=30),
                monto=1000000.0,
                organismo="Organismo de prueba",
                raw_data={"test": "data"}
            )
            
            session.add(licitacion)
            session.flush()  # Get licitacion ID
            
            # Create test document
            document = Document(
                licitacion_id=licitacion.id,
                nombre="documento_prueba.pdf",
                tipo="pdf",
                url="https://example.com/docs/123.pdf",
                contenido="Contenido de prueba"
            )
            
            session.add(document)
            session.commit()
            logger.info("Created test data successfully")
            
        except Exception as e:
            logger.error(f"Error creating test data: {str(e)}")
            session.rollback()
            raise
            
    except Exception as e:
        logger.error(f"Error in create_test_data: {str(e)}")
        raise
    finally:
        session.close()

def verify_data():
    """Verify that test data was created correctly"""
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            # Check template
            template = session.query(ReconTemplate).first()
            if not template:
                raise Exception("No template found")
            logger.info(f"Found template: {template.nombre}")
            
            # Check features
            features = session.query(Feature).all()
            if not features:
                raise Exception("No features found")
            logger.info(f"Found {len(features)} features: {[f.nombre for f in features]}")
            
            # Check scraping job
            job = session.query(ScrapingJob).first()
            if not job:
                raise Exception("No scraping job found")
            logger.info(f"Found scraping job with status: {job.status}")
            
            # Check licitacion
            licitacion = session.query(Licitacion).first()
            if not licitacion:
                raise Exception("No licitacion found")
            logger.info(f"Found licitacion: {licitacion.titulo}")
            
            # Check document
            document = session.query(Document).first()
            if not document:
                raise Exception("No document found")
            logger.info(f"Found document: {document.nombre}")
            
            # Verify relationships
            if len(template.features) != 3:
                raise Exception(f"Template should have 3 features, found {len(template.features)}")
            
            if len(job.licitaciones) != 1:
                raise Exception(f"Job should have 1 licitacion, found {len(job.licitaciones)}")
            
            if len(licitacion.documentos) != 1:
                raise Exception(f"Licitacion should have 1 document, found {len(licitacion.documentos)}")
            
            logger.info("All relationships verified successfully")
            
        except Exception as e:
            logger.error(f"Error verifying data: {str(e)}")
            raise
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Error in verify_data: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("Initializing database...")
    init_db()
    logger.info("Creating test data...")
    create_test_data()
    logger.info("Verifying test data...")
    verify_data()
    logger.info("Database initialization completed")
