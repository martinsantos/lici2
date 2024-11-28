from datetime import datetime
from core.database import engine, Base, get_db
from recon_service.models import ScrapingTemplate, ScrapingJob, ScrapingStatus
from licitaciones.models import Licitacion

# Drop all tables and recreate them
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

def init_db():
    # Drop all tables and recreate them
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = next(get_db())
    try:
        # Templates para portales de licitaciones de Argentina
        templates = [
            {
                "name": "Comprar Argentina Nacional",
                "description": "Portal Nacional de Contratación Pública de Argentina",
                "url": "https://comprar.gob.ar/Compras.aspx?qs=W1HXHGHtH10=",
                "fields": [
                    {
                        "id": "numero_proceso",
                        "name": "Número de Proceso",
                        "selector": ".proceso-numero",
                        "type": "text",
                        "required": True
                    },
                    {
                        "id": "nombre",
                        "name": "Nombre del Procedimiento",
                        "selector": ".nombre-procedimiento",
                        "type": "text",
                        "required": True
                    },
                    {
                        "id": "organismo_contratante",
                        "name": "Organismo Contratante",
                        "selector": ".organismo",
                        "type": "text",
                        "required": True
                    },
                    {
                        "id": "monto_estimado",
                        "name": "Monto Estimado",
                        "selector": ".monto",
                        "type": "number",
                        "required": False
                    },
                    {
                        "id": "fecha_publicacion",
                        "name": "Fecha de Publicación",
                        "selector": ".fecha-publicacion",
                        "type": "date",
                        "required": True
                    },
                    {
                        "id": "fecha_apertura",
                        "name": "Fecha de Apertura",
                        "selector": ".fecha-apertura",
                        "type": "date",
                        "required": True
                    }
                ]
            },
            {
                "name": "Comprar Mendoza",
                "description": "Portal de Compras de la Provincia de Mendoza",
                "url": "https://comprar.mendoza.gov.ar/Compras.aspx?qs=W1HXHGHtH10=",
                "fields": [
                    {
                        "id": "numero_expediente",
                        "name": "Número de Expediente",
                        "selector": ".expediente",
                        "type": "text",
                        "required": True
                    },
                    {
                        "id": "descripcion",
                        "name": "Descripción de la Contratación",
                        "selector": ".descripcion",
                        "type": "text",
                        "required": True
                    },
                    {
                        "id": "reparticion",
                        "name": "Repartición",
                        "selector": ".reparticion",
                        "type": "text",
                        "required": True
                    },
                    {
                        "id": "presupuesto",
                        "name": "Presupuesto Oficial",
                        "selector": ".presupuesto",
                        "type": "number",
                        "required": False
                    },
                    {
                        "id": "estado",
                        "name": "Estado del Proceso",
                        "selector": ".estado",
                        "type": "text",
                        "required": True
                    }
                ]
            },
            {
                "name": "Compras Mendoza Apps",
                "description": "Sistema de Compras y Contrataciones de Mendoza",
                "url": "https://comprasapps.mendoza.gov.ar/Compras/servlet/hli00049",
                "fields": [
                    {
                        "id": "numero_contratacion",
                        "name": "Número de Contratación",
                        "selector": ".contratacion-numero",
                        "type": "text",
                        "required": True
                    },
                    {
                        "id": "objeto",
                        "name": "Objeto de la Contratación",
                        "selector": ".objeto-contratacion",
                        "type": "text",
                        "required": True
                    },
                    {
                        "id": "organismo",
                        "name": "Organismo Solicitante",
                        "selector": ".organismo-solicitante",
                        "type": "text",
                        "required": True
                    },
                    {
                        "id": "fecha_publicacion",
                        "name": "Fecha de Publicación",
                        "selector": ".fecha-publicacion",
                        "type": "date",
                        "required": True
                    },
                    {
                        "id": "fecha_apertura",
                        "name": "Fecha de Apertura",
                        "selector": ".fecha-apertura",
                        "type": "date",
                        "required": True
                    },
                    {
                        "id": "etapa",
                        "name": "Etapa del Proceso",
                        "selector": ".etapa-proceso",
                        "type": "text",
                        "required": True
                    }
                ]
            }
        ]

        # Agregar los templates a la base de datos
        for template_data in templates:
            template = ScrapingTemplate(
                name=template_data["name"],
                description=template_data["description"],
                url=template_data["url"],
                fields=template_data["fields"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                is_active=True
            )
            db.add(template)
        
        db.commit()
        print("Database initialized successfully with Argentina scraping templates!")
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
