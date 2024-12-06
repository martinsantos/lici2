import os
import sys

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from sqlalchemy.orm import Session
from core.database import SessionLocal, engine
from recon_service.models import ScrapingTemplate
import json

def create_templates():
    templates = [
        {
            "name": "Comprar Mendoza",
            "description": "Portal de compras de Mendoza",
            "url": "https://comprar.mendoza.gov.ar/Compras.aspx?qs=W1HXHGHtH10=",
            "fields": {
                "title": ".title",
                "date": ".date",
                "organism": ".organism",
                "status": ".status"
            },
            "is_active": True
        },
        {
            "name": "Compras Apps Mendoza",
            "description": "Portal de compras apps de Mendoza",
            "url": "https://comprasapps.mendoza.gov.ar/Compras/servlet/hli00049",
            "fields": {
                "title": ".title",
                "date": ".date",
                "organism": ".organism",
                "status": ".status"
            },
            "is_active": True
        },
        {
            "name": "Comprar Argentina",
            "description": "Portal de compras de Argentina",
            "url": "https://comprar.gob.ar/Compras.aspx?qs=W1HXHGHtH10=",
            "fields": {
                "title": ".title",
                "date": ".date",
                "organism": ".organism",
                "status": ".status"
            },
            "is_active": True
        }
    ]

    db = SessionLocal()
    try:
        # First, delete any existing templates
        db.query(ScrapingTemplate).delete()
        
        # Add new templates
        for template_data in templates:
            template = ScrapingTemplate(
                name=template_data["name"],
                description=template_data["description"],
                url=template_data["url"],
                fields=template_data["fields"],
                is_active=template_data["is_active"]
            )
            db.add(template)
        
        db.commit()
        print("Templates added successfully!")
        
        # Verify templates were added
        all_templates = db.query(ScrapingTemplate).all()
        print("\nCurrent templates:")
        for template in all_templates:
            print(f"- {template.name} ({template.url})")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_templates()
