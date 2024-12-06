import sqlite3
import psycopg2
from psycopg2.extras import Json
import json
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def connect_postgres():
    return psycopg2.connect(os.getenv('DATABASE_URL'))

def connect_sqlite():
    return sqlite3.connect('backend/recon.db')

def migrate_templates():
    sqlite_conn = connect_sqlite()
    pg_conn = connect_postgres()
    
    try:
        # Get templates from SQLite
        sqlite_cur = sqlite_conn.cursor()
        sqlite_cur.execute('SELECT * FROM templates')
        templates = sqlite_cur.fetchall()
        
        # Get column names
        sqlite_cur.execute('PRAGMA table_info(templates)')
        columns = [col[1] for col in sqlite_cur.fetchall()]
        
        # Insert into PostgreSQL
        pg_cur = pg_conn.cursor()
        for template in templates:
            template_dict = dict(zip(columns, template))
            pg_cur.execute(
                '''
                INSERT INTO "ReconTemplate" (name, description, config, created_at, updated_at, is_active)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (name) DO UPDATE SET
                    description = EXCLUDED.description,
                    config = EXCLUDED.config,
                    updated_at = EXCLUDED.updated_at
                ''',
                (
                    template_dict.get('name'),
                    template_dict.get('description', ''),
                    Json(json.loads(template_dict.get('config', '{}'))),
                    datetime.now(),
                    datetime.now(),
                    True
                )
            )
        
        pg_conn.commit()
        print("Templates migrated successfully")
        
    except Exception as e:
        print(f"Error migrating templates: {e}")
        pg_conn.rollback()
    finally:
        sqlite_conn.close()
        pg_conn.close()

def migrate_documents():
    sqlite_conn = connect_sqlite()
    pg_conn = connect_postgres()
    
    try:
        # Get documents from SQLite
        sqlite_cur = sqlite_conn.cursor()
        sqlite_cur.execute('SELECT * FROM documents')
        documents = sqlite_cur.fetchall()
        
        # Get column names
        sqlite_cur.execute('PRAGMA table_info(documents)')
        columns = [col[1] for col in sqlite_cur.fetchall()]
        
        # Insert into PostgreSQL
        pg_cur = pg_conn.cursor()
        for document in documents:
            doc_dict = dict(zip(columns, document))
            pg_cur.execute(
                '''
                INSERT INTO "Document" (filename, file_path, content_type, size, licitacion_id, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                ''',
                (
                    doc_dict.get('filename'),
                    doc_dict.get('file_path'),
                    doc_dict.get('content_type', 'application/octet-stream'),
                    doc_dict.get('size', 0),
                    doc_dict.get('licitacion_id'),
                    datetime.now(),
                    datetime.now()
                )
            )
        
        pg_conn.commit()
        print("Documents migrated successfully")
        
    except Exception as e:
        print(f"Error migrating documents: {e}")
        pg_conn.rollback()
    finally:
        sqlite_conn.close()
        pg_conn.close()

def migrate_licitaciones():
    sqlite_conn = connect_sqlite()
    pg_conn = connect_postgres()
    
    try:
        # Get licitaciones from SQLite
        sqlite_cur = sqlite_conn.cursor()
        sqlite_cur.execute('SELECT * FROM licitaciones')
        licitaciones = sqlite_cur.fetchall()
        
        # Get column names
        sqlite_cur.execute('PRAGMA table_info(licitaciones)')
        columns = [col[1] for col in sqlite_cur.fetchall()]
        
        # Insert into PostgreSQL
        pg_cur = pg_conn.cursor()
        for licitacion in licitaciones:
            lic_dict = dict(zip(columns, licitacion))
            pg_cur.execute(
                '''
                INSERT INTO "Licitacion" (
                    titulo, descripcion, fechaPublicacion, fechaApertura,
                    numeroExpediente, numeroLicitacion, organismo, contacto,
                    monto, estado, categoria, ubicacion, plazo, requisitos,
                    garantia, documentos, created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                ''',
                (
                    lic_dict.get('titulo'),
                    lic_dict.get('descripcion'),
                    lic_dict.get('fechaPublicacion'),
                    lic_dict.get('fechaApertura'),
                    lic_dict.get('numeroExpediente'),
                    lic_dict.get('numeroLicitacion'),
                    lic_dict.get('organismo'),
                    lic_dict.get('contacto'),
                    float(lic_dict.get('monto', 0)),
                    lic_dict.get('estado', 'Pendiente'),
                    lic_dict.get('categoria'),
                    lic_dict.get('ubicacion'),
                    lic_dict.get('plazo'),
                    json.loads(lic_dict.get('requisitos', '[]')),
                    lic_dict.get('garantia'),
                    json.loads(lic_dict.get('documentos', '[]')),
                    datetime.now(),
                    datetime.now()
                )
            )
        
        pg_conn.commit()
        print("Licitaciones migrated successfully")
        
    except Exception as e:
        print(f"Error migrating licitaciones: {e}")
        pg_conn.rollback()
    finally:
        sqlite_conn.close()
        pg_conn.close()

if __name__ == '__main__':
    print("Starting migration from SQLite to PostgreSQL...")
    migrate_templates()
    migrate_documents()
    migrate_licitaciones()
    print("Migration completed")
