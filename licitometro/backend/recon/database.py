from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy_utils import database_exists, create_database
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Base para modelos declarativos
Base = declarative_base()

class DatabaseManager:
    def __init__(self, database_url=None):
        """
        Inicializa el gestor de base de datos
        
        :param database_url: URL de conexión a la base de datos, 
                             por defecto usa variable de entorno
        """
        self.database_url = database_url or os.getenv('DATABASE_URL', 
            'postgresql://licitometro:password@localhost/licitometro_recon')
        
        # Crear base de datos si no existe
        if not database_exists(self.database_url):
            create_database(self.database_url)
        
        # Crear motor de base de datos
        self.engine = create_engine(self.database_url, echo=True)
        
        # Crear sesión
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_all_tables(self):
        """
        Crea todas las tablas definidas en los modelos
        """
        # Importar modelos localmente para evitar importaciones circulares
        from .models import ScrapingTemplate, ScrapingJob
        
        # Crear todas las tablas
        Base.metadata.create_all(self.engine)
        print("Todas las tablas han sido creadas exitosamente.")

    def drop_all_tables(self):
        """
        Elimina todas las tablas (usar con precaución)
        """
        Base.metadata.drop_all(self.engine)
        print("Todas las tablas han sido eliminadas.")

    def get_session(self):
        """
        Obtiene una nueva sesión de base de datos
        
        :return: Sesión de SQLAlchemy
        """
        return self.SessionLocal()

# Función de inicialización
def init_database(database_url=None):
    """
    Inicializa la base de datos
    
    :param database_url: URL de conexión personalizada
    """
    db_manager = DatabaseManager(database_url)
    db_manager.create_all_tables()
    return db_manager

# Script de ejecución directa
if __name__ == '__main__':
    # Ejemplo de uso
    db_manager = init_database()
    
    # Ejemplo de uso de sesión
    with db_manager.get_session() as session:
        # Aquí puedes realizar operaciones con la sesión
        pass
