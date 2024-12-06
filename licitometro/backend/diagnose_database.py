import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
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

def diagnose_database():
    try:
        # Create SQLAlchemy engine
        engine = create_engine(
            DATABASE_URL,
            echo=True,  # Log all SQL statements
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
        )
        
        # Test database connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("Basic database connection successful")
        
        # Create a session
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Inspect database
        inspector = inspect(engine)
        
        # List all tables in the database
        logger.info("Tables in the database:")
        for table_name in inspector.get_table_names():
            logger.info(f"- {table_name}")
            
            # Inspect table columns
            columns = inspector.get_columns(table_name)
            logger.info(f"  Columns in {table_name}:")
            for column in columns:
                logger.info(f"  - {column['name']}: {column['type']}")
        
        # Attempt to query from each table
        tables_to_check = ['documents', 'licitaciones', 'recon_templates']
        for table in tables_to_check:
            try:
                result = session.execute(text(f"SELECT * FROM {table} LIMIT 5"))
                logger.info(f"Successfully queried {table} table")
                for row in result:
                    logger.info(f"Sample row from {table}: {row}")
            except Exception as e:
                logger.warning(f"Could not query {table} table: {str(e)}")
        
        session.close()
        
    except Exception as e:
        logger.error(f"Comprehensive database diagnosis failed: {str(e)}")
        logger.error(f"Database URL used: {DATABASE_URL}")
        raise

if __name__ == "__main__":
    diagnose_database()
