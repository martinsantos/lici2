from sqlalchemy import create_engine
from backend.models.user import Base
from backend.config import settings

def create_tables():
    # Create engine for test database
    engine = create_engine("postgresql://postgres:postgres@localhost:5432/licitometro_test")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    create_tables()
