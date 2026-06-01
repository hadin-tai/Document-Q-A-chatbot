from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base
import uuid

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    file_name = Column(String, nullable=False)
    pinecone_file_id = Column(String, nullable=False)
    upload_status = Column(String, default="completed")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
