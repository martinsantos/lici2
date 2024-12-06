import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_test_database():
    # Connect to PostgreSQL server
    conn = psycopg2.connect(
        dbname='postgres',
        user='postgres',
        password='postgres',
        host='localhost',
        port='5432'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Check if database exists
    cursor.execute("SELECT 1 FROM pg_database WHERE datname='licitometro_test'")
    exists = cursor.fetchone()
    
    if not exists:
        cursor.execute('CREATE DATABASE licitometro_test')
        print("Test database created successfully!")
    else:
        print("Test database already exists!")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_test_database()
