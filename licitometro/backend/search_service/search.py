from typing import List, Optional, Dict
from elasticsearch import AsyncElasticsearch
from core.api_config import api_config

class SearchService:
    def __init__(self):
        self.es = AsyncElasticsearch([api_config.service_urls['search']])
        self.index_name = 'licitaciones'

    async def index_document(self, document: Dict):
        """
        Indexa un documento en Elasticsearch
        """
        await self.es.index(
            index=self.index_name,
            id=document['id'],
            document=document
        )

    async def search(self, query: str, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Realiza una búsqueda en el índice de licitaciones
        """
        search_query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["titulo^3", "descripcion^2", "organismo", "categoria"]
                            }
                        }
                    ]
                }
            }
        }

        # Agregar filtros si existen
        if filters:
            filter_conditions = []
            if filters.get('estado'):
                filter_conditions.append({"term": {"estado": filters['estado']}})
            if filters.get('categoria'):
                filter_conditions.append({"term": {"categoria": filters['categoria']}})
            if filters.get('organismo'):
                filter_conditions.append({"term": {"organismo": filters['organismo']}})
            if filters.get('fecha_desde'):
                filter_conditions.append({
                    "range": {
                        "fecha_publicacion": {
                            "gte": filters['fecha_desde']
                        }
                    }
                })
            if filters.get('fecha_hasta'):
                filter_conditions.append({
                    "range": {
                        "fecha_publicacion": {
                            "lte": filters['fecha_hasta']
                        }
                    }
                })
            if filters.get('monto_min'):
                filter_conditions.append({
                    "range": {
                        "monto": {
                            "gte": filters['monto_min']
                        }
                    }
                })
            if filters.get('monto_max'):
                filter_conditions.append({
                    "range": {
                        "monto": {
                            "lte": filters['monto_max']
                        }
                    }
                })
            
            search_query["query"]["bool"]["filter"] = filter_conditions

        response = await self.es.search(
            index=self.index_name,
            body=search_query,
            size=50  # Limitar resultados a 50 por página
        )

        return [hit['_source'] for hit in response['hits']['hits']]

    async def delete_document(self, document_id: int):
        """
        Elimina un documento del índice
        """
        await self.es.delete(
            index=self.index_name,
            id=document_id
        )

    async def update_document(self, document_id: int, update_data: Dict):
        """
        Actualiza un documento en el índice
        """
        await self.es.update(
            index=self.index_name,
            id=document_id,
            body={"doc": update_data}
        )
