from elasticsearch import AsyncElasticsearch
from typing import Dict, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ElasticsearchService:
    def __init__(self, hosts: List[str], index_name: str = "licitaciones"):
        self.client = AsyncElasticsearch(hosts=hosts)
        self.index_name = index_name

    async def initialize(self):
        """Inicializa el índice con el mapping correcto"""
        mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "titulo": {"type": "text", "analyzer": "spanish"},
                    "descripcion": {"type": "text", "analyzer": "spanish"},
                    "monto": {"type": "float"},
                    "fecha_publicacion": {"type": "date"},
                    "estado": {"type": "keyword"},
                    "entidad": {"type": "keyword"},
                    "ubicacion": {"type": "geo_point"},
                    "tags": {"type": "keyword"}
                }
            },
            "settings": {
                "analysis": {
                    "analyzer": {
                        "spanish": {
                            "type": "spanish"
                        }
                    }
                }
            }
        }
        
        if not await self.client.indices.exists(index=self.index_name):
            await self.client.indices.create(index=self.index_name, body=mapping)
            logger.info(f"Índice {self.index_name} creado con éxito")

    async def index_document(self, document: Dict) -> bool:
        """Indexa un documento en Elasticsearch"""
        try:
            await self.client.index(
                index=self.index_name,
                id=document["id"],
                body=document,
                refresh=True
            )
            return True
        except Exception as e:
            logger.error(f"Error al indexar documento: {e}")
            return False

    async def search(self, query: str, filters: Optional[Dict] = None, 
                    from_: int = 0, size: int = 10) -> Dict:
        """Realiza una búsqueda en el índice"""
        search_query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["titulo^2", "descripcion"],
                                "type": "most_fields"
                            }
                        }
                    ]
                }
            },
            "from": from_,
            "size": size,
            "sort": [
                {"_score": "desc"},
                {"fecha_publicacion": "desc"}
            ]
        }

        if filters:
            search_query["query"]["bool"]["filter"] = []
            for field, value in filters.items():
                search_query["query"]["bool"]["filter"].append(
                    {"term": {field: value}}
                )

        try:
            response = await self.client.search(
                index=self.index_name,
                body=search_query
            )
            return {
                "total": response["hits"]["total"]["value"],
                "results": [hit["_source"] for hit in response["hits"]["hits"]]
            }
        except Exception as e:
            logger.error(f"Error en la búsqueda: {e}")
            return {"total": 0, "results": []}

    async def delete_document(self, doc_id: str) -> bool:
        """Elimina un documento del índice"""
        try:
            await self.client.delete(
                index=self.index_name,
                id=doc_id,
                refresh=True
            )
            return True
        except Exception as e:
            logger.error(f"Error al eliminar documento: {e}")
            return False

    async def close(self):
        """Cierra la conexión con Elasticsearch"""
        await self.client.close()
