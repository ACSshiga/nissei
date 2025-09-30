from sqlalchemy import Column, Date, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class WorkLog(Base):
    __tablename__ = "worklogs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    work_date = Column(Date, nullable=False, index=True)
    duration_minutes = Column(Integer, nullable=False)  # 工数（分単位）
    work_category = Column(String)  # 作業区分
    memo = Column(Text)  # メモ
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="worklogs")
    user = relationship("User")