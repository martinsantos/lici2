from sqlalchemy_utils import database_exists, create_database, drop_database
from backend.config import settings
from backend.database import engine, Base
from backend.init_db import init_db

def reset_database():
    """Reset the database and initialize it with sample data"""
    database_url = settings.database_url
    
    print(f"Checking database: {database_url}")
    
    # Drop database if exists
    if database_exists(database_url):
        print("Dropping existing database...")
        drop_database(database_url)
    
    # Create new database
    print("Creating new database...")
    create_database(database_url)
    
    # Create all tables
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    # Initialize with sample data
    print("Initializing sample data...")
    init_db()
    
    print("Database reset completed successfully!")

if __name__ == "__main__":
    reset_database()
