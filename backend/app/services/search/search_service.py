from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self, elasticsearch_url: str = "http://localhost:9200"):
        self.app = FastAPI()
        self.es = AsyncElasticsearch([elasticsearch_url])
        self._setup_routes()

    def _setup_routes(self):
        @self.app.post("/index/{index_name}")
        async def index_document(index_name: str, document: Dict[str, Any]):
            try:
                response = await self.es.index(index=index_name, document=document)
                return {"status": "success", "id": response["_id"]}
            except Exception as e:
                logger.error(f"Error indexing document: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/search/{index_name}")
        async def search(
            index_name: str,
            query: str,
            filters: Optional[Dict[str, Any]] = None,
            from_: int = 0,
            size: int = 10
        ):
            try:
                search_query = {
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "multi_match": {
                                        "query": query,
                                        "fields": ["*"],
                                        "type": "best_fields",
                                        "fuzziness": "AUTO"
                                    }
                                }
                            ]
                        }
                    },
                    "from": from_,
                    "size": size
                }

                if filters:
                    search_query["query"]["bool"]["filter"] = [
                        {"term": {k: v}} for k, v in filters.items()
                    ]

                response = await self.es.search(
                    index=index_name,
                    body=search_query
                )

                hits = response["hits"]["hits"]
                total = response["hits"]["total"]["value"]

                results = [
                    {
                        "id": hit["_id"],
                        "score": hit["_score"],
                        "source": hit["_source"]
                    }
                    for hit in hits
                ]

                return {
                    "total": total,
                    "results": results,
                    "page": {
                        "current": from_ // size + 1,
                        "size": size,
                        "total": (total + size - 1) // size
                    }
                }

            except Exception as e:
                logger.error(f"Error performing search: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.delete("/index/{index_name}/{document_id}")
        async def delete_document(index_name: str, document_id: str):
            try:
                response = await self.es.delete(index=index_name, id=document_id)
                return {"status": "success", "response": response}
            except Exception as e:
                logger.error(f"Error deleting document: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

    async def create_index(self, index_name: str, mappings: Dict[str, Any]):
        """Create a new index with the specified mappings"""
        try:
            if not await self.es.indices.exists(index=index_name):
                await self.es.indices.create(
                    index=index_name,
                    body={"mappings": mappings}
                )
                return {"status": "success", "message": f"Index {index_name} created"}
            return {"status": "exists", "message": f"Index {index_name} already exists"}
        except Exception as e:
            logger.error(f"Error creating index: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def bulk_index(self, index_name: str, documents: List[Dict[str, Any]]):
        """Bulk index multiple documents"""
        try:
            body = []
            for doc in documents:
                body.extend([
                    {"index": {"_index": index_name}},
                    doc
                ])
            
            response = await self.es.bulk(body=body)
            return {"status": "success", "response": response}
        except Exception as e:
            logger.error(f"Error bulk indexing documents: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def close(self):
        """Close the Elasticsearch client connection"""
        await self.es.close()
