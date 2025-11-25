# app/infra/outbox/models.py
from sqlalchemy import String, DateTime, func, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.infra.db.base import Base
import uuid


class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    aggregate_type: Mapped[str] = mapped_column(String(100))
    aggregate_id: Mapped[str] = mapped_column(String(255))
    event_type: Mapped[str] = mapped_column(String(100))
    payload: Mapped[str] = mapped_column(Text)  # JSON string
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    processed_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
