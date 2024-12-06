from database import SessionLocal, engine
from models.base import Document, Licitacion, ReconTemplate
from sqlalchemy import text
import logging
import sys
import traceback

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def check_table_exists(table_name):
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = '{table_name}'
                );
            """))
            exists = result.scalar()
            logger.info(f"Table {table_name}: {'exists' if exists else 'does not exist'}")
            return exists
    except Exception as e:
        logger.error(f"Error checking table {table_name}: {str(e)}")
        return False

def check_table_columns(table_name):
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = '{table_name}';
            """))
            columns = result.fetchall()
            logger.info(f"Columns in {table_name}:")
            for col in columns:
                logger.info(f"  - {col[0]}: {col[1]}")
            return columns
    except Exception as e:
        logger.error(f"Error checking columns for {table_name}: {str(e)}")
        return []

def check_table_count(table_name):
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name};"))
            count = result.scalar()
            logger.info(f"Row count in {table_name}: {count}")
            return count
    except Exception as e:
        logger.error(f"Error counting rows in {table_name}: {str(e)}")
        return 0

def main():
    try:
        # Test database connection
        logger.info("Testing database connection...")
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")

        # Check tables
        tables = ['documents', 'licitaciones', 'recon_templates']
        for table in tables:
            logger.info(f"\nChecking table: {table}")
            if check_table_exists(table):
                check_table_columns(table)
                check_table_count(table)

        # Test session creation
        logger.info("\nTesting session creation...")
        db = SessionLocal()
        try:
            # Try to query each model
            docs = db.query(Document).limit(1).all()
            logger.info(f"Documents query successful, found {len(docs)} records")
            
            lics = db.query(Licitacion).limit(1).all()
            logger.info(f"Licitaciones query successful, found {len(lics)} records")
            
            templates = db.query(ReconTemplate).limit(1).all()
            logger.info(f"Templates query successful, found {len(templates)} records")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error("Diagnostic failed:")
        logger.error(str(e))
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
