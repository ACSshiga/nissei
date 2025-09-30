from sqlalchemy import Column, String, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class Material(Base):
    __tablename__ = "materials"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    material_type = Column(String, nullable=False)  # 機種 or 機番
    key = Column(String, nullable=False, index=True)  # 機種名 or 機番
    title = Column(String, nullable=False)
    content_type = Column(String, nullable=False)  # URL or FILE
    url = Column(String)  # URL の場合
    file_path = Column(String)  # ファイルの場合（MinIOパス）
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="materials")
    uploader = relationship("User")