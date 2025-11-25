from sqlalchemy import Column, String, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.infra.db.base import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, index=True)

    full_name = Column(String(100), nullable=False)
    specialization = Column(String(100), nullable=False)
    bio = Column(Text, nullable=True)
    experience_years = Column(String(10), nullable=True)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="doctor_profile")
