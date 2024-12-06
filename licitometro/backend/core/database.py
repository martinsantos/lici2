from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# PostgreSQL configuration
SQLALCHEMY_DATABASE_URL = os.getenv(
    'DATABASE_URL', 
    "postgresql://postgres:postgres@localhost:5432/licitometro"
)

def create_db_engine():
    try:
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            pool_pre_ping=True,  # Test connection before using
            pool_size=10,  # Adjust based on your needs
            max_overflow=20  # Allow additional connections during peak load
        )
        
        # Test the connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            conn.commit()
        
        logger.info("Successfully connected to PostgreSQL database")
        return engine
            
    except OperationalError as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        raise

# Create engine
engine = create_db_engine()

Base = declarative_base()

SessionLocal = sessionmaker(
    bind=engine, 
    autocommit=False, 
    autoflush=False
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
