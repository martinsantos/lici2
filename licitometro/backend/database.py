from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging
from urllib.parse import quote_plus
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Database configuration
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "licitometro")

# Create database URL with proper URL encoding for special characters
DATABASE_URL = f"postgresql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

logger.debug(f"Using database URL: {DATABASE_URL}")

try:
    # Create SQLAlchemy engine with connection pooling and logging
    engine = create_engine(
        DATABASE_URL,
        echo=True,  # Log all SQL statements
        pool_size=5,  # Maximum number of connections in the pool
        max_overflow=10,  # Maximum number of connections that can be created beyond pool_size
        pool_timeout=30,  # Timeout for getting a connection from the pool
        pool_recycle=1800,  # Recycle connections after 30 minutes
    )
    
    # Test database connection
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        logger.info("Database connection test successful")
        
except Exception as e:
    logger.error(f"Error connecting to database: {str(e)}")
    raise

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for declarative models
Base = declarative_base()

# Import models to ensure they are included in the Base metadata
from models.base import (
    ReconTemplate,
    Feature,
    ScrapingJob,
    Licitacion,
    Document,
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        logger.debug("Opening new database session")
        yield db
    finally:
        logger.debug("Closing database session")
        db.close()

# Function to initialize database
def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise
