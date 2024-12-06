import psycopg2

def test_connection():
    try:
        conn = psycopg2.connect(
            dbname='licitometro',
            user='postgres',
            password='postgres',
            host='localhost',
            port='5432'
        )
        print("Connection successful!")
        
        # Get PostgreSQL version
        cursor = conn.cursor()
        cursor.execute('SELECT version()')
        db_version = cursor.fetchone()
        print(f"PostgreSQL version: {db_version[0]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_connection()
