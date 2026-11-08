from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

ROLES = ("admin", "doctor", "radiologist", "patient")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(String(300))
    role: Mapped[str] = mapped_column(String(20), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # Only used for patients: the doctor responsible for them
    assigned_doctor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Study(Base):
    """One uploaded MRI scan with its AI results and report."""

    __tablename__ = "studies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    radiologist_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    scan_type: Mapped[str] = mapped_column(String(60), default="Brain MRI")
    original_filename: Mapped[str] = mapped_column(String(255), default="")

    # classification
    predicted_class: Mapped[str] = mapped_column(String(40))
    probabilities: Mapped[dict] = mapped_column(JSON)

    # segmentation
    seg_status: Mapped[str] = mapped_column(String(40))
    seg_regions: Mapped[int] = mapped_column(Integer, default=0)
    tumor_area_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    dice_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    iou_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # report: "Pending" (draft waiting for the doctor) -> "Approved"
    report_status: Mapped[str] = mapped_column(String(20), default="Pending", index=True)
    report_summary: Mapped[str] = mapped_column(Text, default="")
    approved_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    patient: Mapped[User | None] = relationship(foreign_keys=[patient_id])
    radiologist: Mapped[User] = relationship(foreign_keys=[radiologist_id])
    approved_by: Mapped[User | None] = relationship(foreign_keys=[approved_by_id])


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(60), index=True)
    detail: Mapped[str] = mapped_column(String(400), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)

    user: Mapped[User | None] = relationship(foreign_keys=[user_id])
