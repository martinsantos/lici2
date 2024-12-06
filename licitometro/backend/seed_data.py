from datetime import datetime, timedelta
from database import SessionLocal
from models.licitacion import Licitacion
import traceback

def seed_licitaciones():
    db = SessionLocal()
    try:
        # Check if we already have data
        existing = db.query(Licitacion).first()
        if existing:
            print("[SEED] Data already exists, skipping seed")
            return

        # Create multiple sample licitaciones
        sample_licitaciones = [
            {
                "titulo": "Construcción de Hospital Regional",
                "descripcion": "Proyecto de construcción de un nuevo hospital regional con capacidad para 200 camas",
                "url": "https://example.com/licitacion/1",
                "estado": "Abierta",
                "fecha_publicacion": datetime.now(),
                "fecha_cierre": datetime.now() + timedelta(days=30),
                "monto": "$5,000,000.00",
                "entidad": "Ministerio de Salud",
                "raw_data": {
                    "numero_expediente": "EXP-2024-001",
                    "numero_licitacion": "LIC-2024-001",
                    "contacto": {
                        "nombre": "Juan Pérez",
                        "email": "juan.perez@salud.gob",
                        "telefono": "+1234567890"
                    },
                    "categoria": "Infraestructura",
                    "ubicacion": "Ciudad Capital",
                    "plazo": "18 meses",
                    "requisitos": ["Experiencia previa en construcción hospitalaria", "Certificación ISO 9001"],
                },
                "processed": True
            },
            {
                "titulo": "Adquisición de Equipos Médicos",
                "descripcion": "Compra de equipamiento médico especializado para unidades de cuidados intensivos",
                "url": "https://example.com/licitacion/2",
                "estado": "Abierta",
                "fecha_publicacion": datetime.now(),
                "fecha_cierre": datetime.now() + timedelta(days=45),
                "monto": "$2,500,000.00",
                "entidad": "Hospital Central",
                "raw_data": {
                    "numero_expediente": "EXP-2024-002",
                    "numero_licitacion": "LIC-2024-002",
                    "contacto": {
                        "nombre": "María González",
                        "email": "maria.gonzalez@hospital.gob",
                        "telefono": "+1234567891"
                    },
                    "categoria": "Equipamiento",
                    "ubicacion": "Ciudad Capital",
                    "plazo": "6 meses",
                    "requisitos": ["Distribuidor autorizado", "Servicio técnico local"],
                },
                "processed": True
            }
        ]

        # Add the sample licitaciones to the database
        for licitacion_data in sample_licitaciones:
            licitacion = Licitacion(**licitacion_data)
            db.add(licitacion)

        db.commit()
        print("[SEED] Successfully seeded licitaciones data")

    except Exception as e:
        print(f"[SEED] Error seeding data: {str(e)}")
        print(traceback.format_exc())
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_licitaciones()
