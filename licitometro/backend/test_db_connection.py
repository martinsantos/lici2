import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/licitometro')

def test_database_connection():
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Create a session
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        # Test connection by executing a simple query
        result = session.execute(text("SELECT 1")).scalar()
        print(f"Database connection successful. Test query result: {result}")
        
        # Check database version
        version = session.execute(text("SELECT version()")).scalar()
        print(f"PostgreSQL Version: {version}")
        
        # List tables in the public schema
        tables = session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)).fetchall()
        print("Tables in the database:")
        for table in tables:
            print(table[0])
        
        session.close()
        return True
    
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return False

if __name__ == '__main__':
    test_database_connection()
