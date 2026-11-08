from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import get_db, require_roles
from app.models import User
from app.schemas import PatientBrief

router = APIRouter(prefix="/api", tags=["patients"])


@router.get("/patients", response_model=list[PatientBrief])
def list_patients(db: Session = Depends(get_db), user: User = Depends(require_roles("admin", "doctor", "radiologist"))):
    """Patients the caller may select. Doctors only see their own assigned patients."""
    stmt = select(User).where(User.role == "patient", User.is_active.is_(True)).order_by(User.name)
    if user.role == "doctor":
        stmt = stmt.where(User.assigned_doctor_id == user.id)
    return [PatientBrief.model_validate(u) for u in db.scalars(stmt.limit(500))]
