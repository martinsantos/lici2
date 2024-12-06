from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from core.database import Base

class Document(Base):
    """
    Model for storing document metadata
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    file_location = Column(String, nullable=False)
    content_type = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Optional user_id, set to nullable
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    def __repr__(self):
        return f"<Document {self.file_name}>"
