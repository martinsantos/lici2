import logging
import io
import uuid
from fastapi import UploadFile, HTTPException

logger = logging.getLogger(__name__)

class MinioClient:
    def __init__(self):
        logger.info("Using dummy MinIO client")
        self.files = {}  # In-memory storage for dummy implementation
    
    async def upload_file(self, file: UploadFile) -> str:
        """Upload a file and return its location"""
        try:
            content = await file.read()
            file_id = str(uuid.uuid4())
            file_location = f"documents/{file_id}/{file.filename}"
            self.files[file_location] = {
                "content": content,
                "content_type": file.content_type
            }
            return file_location
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

    async def get_file(self, file_location: str) -> tuple[bytes, str]:
        """Get a file's content and content type"""
        try:
            if file_location not in self.files:
                raise HTTPException(status_code=404, detail="File not found")
            
            file_data = self.files[file_location]
            return file_data["content"], file_data["content_type"]
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting file: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error getting file: {str(e)}")

    async def delete_file(self, file_location: str) -> None:
        """Delete a file"""
        try:
            if file_location in self.files:
                del self.files[file_location]
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")

# Use dummy client for now
minio_client = MinioClient()
