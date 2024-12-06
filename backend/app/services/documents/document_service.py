from fastapi import FastAPI, UploadFile, File, HTTPException
from minio import Minio
from minio.error import S3Error
import hashlib
import logging
from typing import Optional, List
from datetime import timedelta
import io

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(
        self,
        minio_url: str = "localhost:9000",
        access_key: str = "minioadmin",
        secret_key: str = "minioadmin",
        secure: bool = False
    ):
        self.app = FastAPI()
        self.client = Minio(
            minio_url,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )
        self._setup_routes()

    def _setup_routes(self):
        @self.app.post("/upload/{bucket_name}")
        async def upload_document(
            bucket_name: str,
            file: UploadFile = File(...),
            metadata: Optional[dict] = None
        ):
            try:
                # Asegurar que el bucket existe
                await self.ensure_bucket_exists(bucket_name)

                # Leer el contenido del archivo
                content = await file.read()
                
                # Calcular el hash del archivo
                file_hash = hashlib.sha256(content).hexdigest()
                
                # Crear metadata si no existe
                if metadata is None:
                    metadata = {}
                
                # Agregar información adicional a metadata
                metadata.update({
                    "filename": file.filename,
                    "content-type": file.content_type,
                    "hash": file_hash
                })

                # Subir el archivo
                result = await self.upload_file(
                    bucket_name=bucket_name,
                    object_name=file_hash,
                    data=io.BytesIO(content),
                    length=len(content),
                    content_type=file.content_type,
                    metadata=metadata
                )

                return {
                    "status": "success",
                    "object_name": file_hash,
                    "metadata": metadata
                }

            except Exception as e:
                logger.error(f"Error uploading document: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/download/{bucket_name}/{object_name}")
        async def download_document(bucket_name: str, object_name: str):
            try:
                # Generar URL presignada para descarga
                url = await self.get_presigned_url(
                    bucket_name=bucket_name,
                    object_name=object_name,
                    expires=timedelta(minutes=30)
                )
                return {"download_url": url}

            except Exception as e:
                logger.error(f"Error generating download URL: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/list/{bucket_name}")
        async def list_documents(bucket_name: str, prefix: Optional[str] = None):
            try:
                objects = await self.list_objects(bucket_name, prefix)
                return {"objects": objects}

            except Exception as e:
                logger.error(f"Error listing documents: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.delete("/delete/{bucket_name}/{object_name}")
        async def delete_document(bucket_name: str, object_name: str):
            try:
                await self.remove_object(bucket_name, object_name)
                return {"status": "success", "message": f"Object {object_name} deleted"}

            except Exception as e:
                logger.error(f"Error deleting document: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

    async def ensure_bucket_exists(self, bucket_name: str):
        """Asegura que el bucket existe, creándolo si es necesario"""
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
        except S3Error as e:
            logger.error(f"Error ensuring bucket exists: {str(e)}")
            raise

    async def upload_file(
        self,
        bucket_name: str,
        object_name: str,
        data: io.BytesIO,
        length: int,
        content_type: str,
        metadata: dict
    ):
        """Sube un archivo a MinIO"""
        try:
            result = self.client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=data,
                length=length,
                content_type=content_type,
                metadata=metadata
            )
            return result
        except S3Error as e:
            logger.error(f"Error uploading file: {str(e)}")
            raise

    async def get_presigned_url(
        self,
        bucket_name: str,
        object_name: str,
        expires: timedelta
    ) -> str:
        """Genera una URL presignada para descarga"""
        try:
            url = self.client.presigned_get_object(
                bucket_name=bucket_name,
                object_name=object_name,
                expires=int(expires.total_seconds())
            )
            return url
        except S3Error as e:
            logger.error(f"Error generating presigned URL: {str(e)}")
            raise

    async def list_objects(
        self,
        bucket_name: str,
        prefix: Optional[str] = None
    ) -> List[dict]:
        """Lista objetos en un bucket"""
        try:
            objects = self.client.list_objects(
                bucket_name=bucket_name,
                prefix=prefix,
                recursive=True
            )
            return [
                {
                    "object_name": obj.object_name,
                    "size": obj.size,
                    "last_modified": obj.last_modified,
                    "etag": obj.etag
                }
                for obj in objects
            ]
        except S3Error as e:
            logger.error(f"Error listing objects: {str(e)}")
            raise

    async def remove_object(self, bucket_name: str, object_name: str):
        """Elimina un objeto del bucket"""
        try:
            self.client.remove_object(
                bucket_name=bucket_name,
                object_name=object_name
            )
        except S3Error as e:
            logger.error(f"Error removing object: {str(e)}")
            raise
