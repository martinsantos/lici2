from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base, ReconTemplate, Document, Licitacion
import sqlite3
import json
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL connection
pg_url = os.getenv('DATABASE_URL')
if not pg_url:
    raise ValueError("DATABASE_URL environment variable not set")

pg_engine = create_engine(pg_url)
Session = sessionmaker(bind=pg_engine)

def create_tables():
    """Create all tables in PostgreSQL"""
    Base.metadata.create_all(pg_engine)
    print("Tables created successfully")

def connect_sqlite():
    """Connect to SQLite database"""
    return sqlite3.connect('backend/recon.db')

def migrate_templates():
    """Migrate templates from SQLite to PostgreSQL"""
    sqlite_conn = connect_sqlite()
    session = Session()
    
    try:
        # Get templates from SQLite
        sqlite_cur = sqlite_conn.cursor()
        sqlite_cur.execute('SELECT * FROM templates')
        templates = sqlite_cur.fetchall()
        
        # Get column names
        sqlite_cur.execute('PRAGMA table_info(templates)')
        columns = [col[1] for col in sqlite_cur.fetchall()]
        
        # Insert into PostgreSQL
        for template in templates:
            template_dict = dict(zip(columns, template))
            recon_template = ReconTemplate(
                name=template_dict.get('name'),
                description=template_dict.get('description', ''),
                config=json.loads(template_dict.get('config', '{}')),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                is_active=True
            )
            session.add(recon_template)
        
        session.commit()
        print("Templates migrated successfully")
        
    except Exception as e:
        print(f"Error migrating templates: {e}")
        session.rollback()
    finally:
        sqlite_conn.close()
        session.close()

def migrate_documents():
    """Migrate documents from SQLite to PostgreSQL"""
    sqlite_conn = connect_sqlite()
    session = Session()
    
    try:
        # Get documents from SQLite
        sqlite_cur = sqlite_conn.cursor()
        sqlite_cur.execute('SELECT * FROM documents')
        documents = sqlite_cur.fetchall()
        
        # Get column names
        sqlite_cur.execute('PRAGMA table_info(documents)')
        columns = [col[1] for col in sqlite_cur.fetchall()]
        
        # Insert into PostgreSQL
        for document in documents:
            doc_dict = dict(zip(columns, document))
            doc = Document(
                filename=doc_dict.get('filename'),
                file_path=doc_dict.get('file_path'),
                content_type=doc_dict.get('content_type', 'application/octet-stream'),
                size=doc_dict.get('size', 0),
                licitacion_id=doc_dict.get('licitacion_id'),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(doc)
        
        session.commit()
        print("Documents migrated successfully")
        
    except Exception as e:
        print(f"Error migrating documents: {e}")
        session.rollback()
    finally:
        sqlite_conn.close()
        session.close()

def migrate_licitaciones():
    """Migrate licitaciones from SQLite to PostgreSQL"""
    sqlite_conn = connect_sqlite()
    session = Session()
    
    try:
        # Get licitaciones from SQLite
        sqlite_cur = sqlite_conn.cursor()
        sqlite_cur.execute('SELECT * FROM licitaciones')
        licitaciones = sqlite_cur.fetchall()
        
        # Get column names
        sqlite_cur.execute('PRAGMA table_info(licitaciones)')
        columns = [col[1] for col in sqlite_cur.fetchall()]
        
        # Insert into PostgreSQL
        for licitacion in licitaciones:
            lic_dict = dict(zip(columns, licitacion))
            
            # Handle JSON fields that might be None
            requisitos = lic_dict.get('requisitos')
            if requisitos is None:
                requisitos = '[]'
            elif not isinstance(requisitos, (str, bytes, bytearray)):
                requisitos = json.dumps(requisitos)
                
            documentos = lic_dict.get('documentos')
            if documentos is None:
                documentos = '[]'
            elif not isinstance(documentos, (str, bytes, bytearray)):
                documentos = json.dumps(documentos)
            
            # Handle numeric fields
            monto = lic_dict.get('monto')
            if monto is None:
                monto = 0.0
            else:
                try:
                    monto = float(monto)
                except (ValueError, TypeError):
                    monto = 0.0
            
            lic = Licitacion(
                titulo=lic_dict.get('titulo'),
                descripcion=lic_dict.get('descripcion'),
                fechaPublicacion=datetime.fromisoformat(lic_dict.get('fechaPublicacion')) if lic_dict.get('fechaPublicacion') else None,
                fechaApertura=datetime.fromisoformat(lic_dict.get('fechaApertura')) if lic_dict.get('fechaApertura') else None,
                numeroExpediente=lic_dict.get('numeroExpediente'),
                numeroLicitacion=lic_dict.get('numeroLicitacion'),
                organismo=lic_dict.get('organismo'),
                contacto=lic_dict.get('contacto'),
                monto=monto,
                estado=lic_dict.get('estado', 'Pendiente'),
                categoria=lic_dict.get('categoria'),
                ubicacion=lic_dict.get('ubicacion'),
                plazo=lic_dict.get('plazo'),
                requisitos=json.loads(requisitos),
                garantia=lic_dict.get('garantia'),
                documentos=json.loads(documentos),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(lic)
        
        session.commit()
        print("Licitaciones migrated successfully")
        
    except Exception as e:
        print(f"Error migrating licitaciones: {e}")
        session.rollback()
    finally:
        sqlite_conn.close()
        session.close()

if __name__ == '__main__':
    print("Starting migration process...")
    print("Creating tables in PostgreSQL...")
    create_tables()
    print("Migrating data from SQLite to PostgreSQL...")
    migrate_templates()
    migrate_documents()
    migrate_licitaciones()
    print("Migration completed")
