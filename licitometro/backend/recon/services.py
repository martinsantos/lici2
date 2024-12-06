from typing import Dict, Any, Optional, List
from prisma import Prisma
from datetime import datetime

class ScrapingTemplateService:
    def __init__(self):
        """
        Inicializa el servicio de plantillas de scraping usando Prisma
        """
        self.db = Prisma()

    async def create_template(self, 
                      name: str, 
                      source_url: str, 
                      field_mapping: Dict[str, Any], 
                      transformation_rules: Optional[Dict[str, Any]] = None,
                      frequency_hours: int = 24) -> Dict[str, Any]:
        """
        Crea una nueva plantilla de scraping
        
        :param name: Nombre único de la plantilla
        :param source_url: URL de origen para el scraping
        :param field_mapping: Mapeo de campos de origen a destino
        :param transformation_rules: Reglas de transformación opcional
        :param frequency_hours: Frecuencia de scraping en horas
        :return: Plantilla de scraping creada
        """
        await self.db.connect()
        try:
            template = await self.db.scrapingtemplate.create(
                data={
                    'name': name,
                    'source_url': source_url,
                    'field_mapping': field_mapping,
                    'transformation_rules': transformation_rules,
                    'frequency_hours': frequency_hours,
                    'is_active': True
                }
            )
            return template.dict()
        finally:
            await self.db.disconnect()

    async def get_template(self, template_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene una plantilla de scraping por su ID
        
        :param template_id: ID de la plantilla
        :return: Plantilla de scraping o None si no existe
        """
        await self.db.connect()
        try:
            template = await self.db.scrapingtemplate.find_unique(
                where={
                    'id': template_id
                }
            )
            return template.dict() if template else None
        finally:
            await self.db.disconnect()

    async def list_templates(self, 
                     is_active: Optional[bool] = None, 
                     limit: int = 100, 
                     offset: int = 0) -> List[Dict[str, Any]]:
        """
        Lista todas las plantillas de scraping
        
        :param is_active: Filtrar por estado activo/inactivo
        :param limit: Límite de resultados
        :param offset: Desplazamiento para paginación
        :return: Lista de plantillas
        """
        await self.db.connect()
        try:
            where = {}
            if is_active is not None:
                where['is_active'] = is_active

            templates = await self.db.scrapingtemplate.find_many(
                where=where,
                take=limit,
                skip=offset,
                order={
                    'created_at': 'desc'
                }
            )
            return [t.dict() for t in templates]
        finally:
            await self.db.disconnect()

    async def update_template(self, 
                      template_id: int, 
                      data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Actualiza una plantilla de scraping
        
        :param template_id: ID de la plantilla
        :param data: Datos a actualizar
        :return: Plantilla actualizada o None si no existe
        """
        await self.db.connect()
        try:
            template = await self.db.scrapingtemplate.update(
                where={
                    'id': template_id
                },
                data=data
            )
            return template.dict() if template else None
        finally:
            await self.db.disconnect()

    async def delete_template(self, template_id: int) -> bool:
        """
        Elimina una plantilla de scraping
        
        :param template_id: ID de la plantilla
        :return: True si se eliminó correctamente
        """
        await self.db.connect()
        try:
            await self.db.scrapingtemplate.delete(
                where={
                    'id': template_id
                }
            )
            return True
        except Exception:
            return False
        finally:
            await self.db.disconnect()

    async def start_scraping_job(self, template_id: int) -> Dict[str, Any]:
        """
        Inicia un trabajo de scraping
        
        :param template_id: ID de la plantilla
        :return: Trabajo de scraping creado
        """
        await self.db.connect()
        try:
            job = await self.db.scrapingjob.create(
                data={
                    'template_id': template_id,
                    'status': 'pending',
                    'start_time': datetime.now()
                }
            )
            return job.dict()
        finally:
            await self.db.disconnect()

    async def update_job_status(self, 
                        job_id: int, 
                        status: str, 
                        error_message: Optional[str] = None,
                        results: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Actualiza el estado de un trabajo de scraping
        
        :param job_id: ID del trabajo
        :param status: Nuevo estado
        :param error_message: Mensaje de error opcional
        :param results: Resultados del scraping opcional
        :return: Trabajo actualizado
        """
        await self.db.connect()
        try:
            data = {
                'status': status,
                'end_time': datetime.now() if status in ['completed', 'failed'] else None
            }
            if error_message:
                data['error_message'] = error_message
            if results:
                data['results'] = results

            job = await self.db.scrapingjob.update(
                where={
                    'id': job_id
                },
                data=data
            )
            return job.dict()
        finally:
            await self.db.disconnect()
