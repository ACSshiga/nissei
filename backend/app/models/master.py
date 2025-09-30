"""
マスタデータのモデル定義

進捗マスタ、作業区分マスタ、問い合わせマスタ、機種シリーズマスタを定義
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.core.database import Base


class MasterShinchoku(Base):
    """進捗マスタ

    案件の進捗ステータスを管理
    トリガー設定により仕掛日・完了日を自動入力
    """
    __tablename__ = "master_shinchoku"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status_name = Column(String(100), unique=True, nullable=False, comment="進捗ステータス名")
    background_color = Column(String(20), comment="背景色（HEXコード）")
    completion_trigger = Column(Boolean, default=False, comment="完了日トリガー")
    start_date_trigger = Column(Boolean, default=False, comment="仕掛日トリガー")
    sort_order = Column(Integer, default=0, comment="並び順")
    is_active = Column(Boolean, default=True, comment="有効フラグ")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MasterSagyouKubun(Base):
    """作業区分マスタ

    作業の分類（盤配、線加工、委託など）を管理
    """
    __tablename__ = "master_sagyou_kubun"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kubun_name = Column(String(100), unique=True, nullable=False, comment="作業区分名")
    background_color = Column(String(20), comment="背景色（HEXコード）")
    sort_order = Column(Integer, default=0, comment="並び順")
    is_active = Column(Boolean, default=True, comment="有効フラグ")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MasterToiawase(Base):
    """問い合わせマスタ

    問い合わせステータスを管理
    """
    __tablename__ = "master_toiawase"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status_name = Column(String(100), unique=True, nullable=False, comment="問い合わせステータス名")
    background_color = Column(String(20), comment="背景色（HEXコード）")
    sort_order = Column(Integer, default=0, comment="並び順")
    is_active = Column(Boolean, default=True, comment="有効フラグ")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MachineSeriesMaster(Base):
    """機種シリーズマスタ

    機種シリーズ（NEX, FNX, TNSなど）の情報を管理
    """
    __tablename__ = "machine_series_master"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    series_name = Column(String(50), unique=True, nullable=False, comment="シリーズ名")
    display_name = Column(String(100), nullable=False, comment="表示名")
    description = Column(String(500), comment="説明")
    category = Column(String(50), comment="カテゴリ（標準/特殊）")
    checklist_template_category = Column(String(50), comment="注意点テンプレート紐付け")
    sort_order = Column(Integer, default=0, comment="並び順")
    is_active = Column(Boolean, default=True, comment="有効フラグ")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# 後方互換性のため既存モデルをエイリアス
StatusMaster = MasterShinchoku
WorkCategory = MasterSagyouKubun
InquiryType = MasterToiawase