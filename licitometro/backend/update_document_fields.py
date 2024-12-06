from sqlalchemy import create_engine, text
from database import DATABASE_URL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_document_fields():
    try:
        # Crear conexión a la base de datos
        engine = create_engine(DATABASE_URL)
        
        # Definir las alteraciones de la tabla
        alterations = [
            "ALTER TABLE documents ALTER COLUMN url TYPE VARCHAR(255);",
            "ALTER TABLE documents ALTER COLUMN nombre TYPE VARCHAR(100);",
            "ALTER TABLE documents ALTER COLUMN tipo TYPE VARCHAR(100);"
        ]
        
        # Ejecutar cada alteración
        with engine.connect() as connection:
            for alter_statement in alterations:
                try:
                    logger.info(f"Executing: {alter_statement}")
                    connection.execute(text(alter_statement))
                    connection.commit()
                    logger.info("Statement executed successfully")
                except Exception as e:
                    logger.error(f"Error executing {alter_statement}: {str(e)}")
                    raise
                
        logger.info("All alterations completed successfully")
        
    except Exception as e:
        logger.error(f"Error updating document fields: {str(e)}")
        raise

if __name__ == "__main__":
    update_document_fields()
