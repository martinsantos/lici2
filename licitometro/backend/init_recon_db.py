from database import SessionLocal, Base, engine
from recon_service.models import ScrapingTemplate
from models.user import User
from datetime import datetime

def init_recon_db():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Create a test user if it doesn't exist
        test_user = db.query(User).filter(User.email == "test@example.com").first()
        if not test_user:
            test_user = User(
                email="test@example.com",
                hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAYlGz1OhiS",  # Password: test123
                is_active=True,
                is_superuser=True
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)

        # Create sample templates if they don't exist
        sample_templates = [
            {
                "name": "Licitaciones Argentina",
                "description": "Template para scrapear licitaciones de Argentina",
                "config": {
                    "url_pattern": "https://comprar.gob.ar/BuscarAvanzado.aspx",
                    "selectors": {
                        "title": ".title",
                        "description": ".description",
                        "date": ".date"
                    }
                }
            },
            {
                "name": "Licitaciones Chile",
                "description": "Template para scrapear licitaciones de Chile",
                "config": {
                    "url_pattern": "https://www.mercadopublico.cl/Portal/Modules/Site/Busquedas/BuscadorAvanzado.aspx",
                    "selectors": {
                        "title": ".title",
                        "description": ".description",
                        "date": ".date"
                    }
                }
            }
        ]

        for template_data in sample_templates:
            template = db.query(ScrapingTemplate).filter(
                ScrapingTemplate.name == template_data["name"]
            ).first()
            
            if not template:
                template = ScrapingTemplate(
                    **template_data,
                    created_by=test_user.id,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    is_active=True
                )
                db.add(template)
        
        db.commit()
        print("Database initialized with sample data")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_recon_db()
