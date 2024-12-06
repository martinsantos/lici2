from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..auth.database import Base, SQLALCHEMY_DATABASE_URL
from ..auth.models import User
from ..models import Licitacion, Documento, Plantilla
from ..auth.security import get_password_hash

def init_db():
    # Crear el motor de base de datos
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    # Crear una sesión
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Verificar si ya existe un usuario administrador
        admin = db.query(User).filter(User.email == "admin@licitometro.com").first()
        if not admin:
            # Crear usuario administrador por defecto
            admin_user = User(
                email="admin@licitometro.com",
                username="admin",
                hashed_password=get_password_hash("admin123"),  # Cambiar en producción
                is_active=True,
                is_superuser=True
            )
            db.add(admin_user)
            db.commit()
            print("Usuario administrador creado con éxito")
        
        # Aquí puedes agregar más datos iniciales si es necesario
        
    except Exception as e:
        print(f"Error inicializando la base de datos: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Inicializando base de datos...")
    init_db()
    print("Base de datos inicializada con éxito")
