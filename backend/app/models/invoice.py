from sqlalchemy import Column, String, Integer, Date, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    year_month = Column(String, nullable=False, index=True)  # YYYY-MM形式
    executed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    executed_at = Column(DateTime, nullable=False)
    is_locked = Column(Boolean, default=False)  # 締め確定フラグ
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    executor = relationship("User")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    management_no = Column(String, nullable=False)  # 管理No
    commission_content = Column(String)  # 業務委託内容
    actual_hours_decimal = Column(Integer)  # 実工数（時間、小数）※100倍して整数で保存
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    invoice = relationship("Invoice", back_populates="items")
    project = relationship("Project")