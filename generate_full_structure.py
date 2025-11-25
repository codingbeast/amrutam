import os

MODULE_MODELS = {
    "identity": """
from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.infra.db.base import Base
import uuid


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[str] = mapped_column(String(50))
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, onupdate=func.now())
""",

    "doctors": """
from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.infra.db.base import Base
import uuid


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(255), index=True)
    specialization: Mapped[str] = mapped_column(String(255))
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    fee: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
""",

    "availability": """
from sqlalchemy import DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from app.infra.db.base import Base
import uuid


class AvailabilitySlot(Base):
    __tablename__ = "availability_slots"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    doctor_id: Mapped[str] = mapped_column(ForeignKey("doctors.id"))
    start_time: Mapped[DateTime] = mapped_column(DateTime)
    end_time: Mapped[DateTime] = mapped_column(DateTime)
    is_booked: Mapped[bool] = mapped_column(Boolean, default=False)
    version: Mapped[int] = mapped_column(default=1)  # optimistic locking
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
""",

    "booking": """
from sqlalchemy import ForeignKey, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.infra.db.base import Base
import uuid


class Consultation(Base):
    __tablename__ = "consultations"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(255))
    doctor_id: Mapped[str] = mapped_column(String(255))
    slot_id: Mapped[str] = mapped_column(ForeignKey("availability_slots.id"))
    status: Mapped[str] = mapped_column(String(50), default="PENDING")
    payment_id: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
""",

    "consultations": """
from sqlalchemy import ForeignKey, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.infra.db.base import Base
import uuid


class ConsultationEvent(Base):
    __tablename__ = "consultation_events"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    consultation_id: Mapped[str] = mapped_column(ForeignKey("consultations.id"))
    event_type: Mapped[str] = mapped_column(String(50))
    metadata: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
""",

    "prescriptions": """
from sqlalchemy import ForeignKey, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.infra.db.base import Base
import uuid


class Prescription(Base):
    __tablename__ = "prescriptions"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    consultation_id: Mapped[str] = mapped_column(ForeignKey("consultations.id"))
    doctor_id: Mapped[str] = mapped_column(String(255))
    notes: Mapped[str] = mapped_column(String(1000))
    pdf_url: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
""",

    "payments": """
from sqlalchemy import String, DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column
from app.infra.db.base import Base
import uuid


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(255))
    consultation_id: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50))
    amount: Mapped[int] = mapped_column(Integer)
    provider_txn_id: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
""",

    "audit": """
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.infra.db.base import Base
import uuid


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(255))
    action: Mapped[str] = mapped_column(String(255))
    ip: Mapped[str] = mapped_column(String(50))
    payload: Mapped[str] = mapped_column(String(2000))
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
""",

    "notifications": """
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.infra.db.base import Base
import uuid


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(255))
    channel: Mapped[str] = mapped_column(String(50))  # SMS/Email/Push
    content: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
"""
}

# -----------------------------------------------------
# GENERATOR FUNCTION
# -----------------------------------------------------

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def generate_models():
    print("\nGenerating Async SQLAlchemy models...\n")

    for module, model_content in MODULE_MODELS.items():
        output_path = f"app/modules/{module}/infrastructure/models.py"
        create_file(output_path, model_content)
        print(f"✔ Model generated for {module}")

    print("\n🎉 All Async SQLAlchemy models generated!\n")


if __name__ == "__main__":
    generate_models()
