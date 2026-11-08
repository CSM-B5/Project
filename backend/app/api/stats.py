from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import ActivityLog, Study, User
from app.schemas import StatsOut
from app.services.access import visible_study_ids

router = APIRouter(prefix="/api/stats", tags=["stats"])


def _count(db: Session, stmt) -> int:
    return db.scalar(select(func.count()).select_from(stmt.subquery())) or 0


@router.get("/dashboard", response_model=StatsOut)
def dashboard_stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Numbers for the StatCards on each role's dashboard."""
    ids = visible_study_ids(user)
    studies = select(Study.id).where(Study.id.in_(ids))
    approved = studies.where(Study.report_status == "Approved")

    if user.role == "admin":
        stats = {
            "registeredDoctors": _count(db, select(User.id).where(User.role == "doctor", User.is_active.is_(True))),
            "registeredPatients": _count(db, select(User.id).where(User.role == "patient", User.is_active.is_(True))),
            "mriStudies": _count(db, studies),
            "systemActivity": _count(db, select(ActivityLog.id)),
        }
    elif user.role == "doctor":
        stats = {
            "myPatients": _count(db, select(User.id).where(
                User.role == "patient", User.is_active.is_(True), User.assigned_doctor_id == user.id)),
            "mriStudies": _count(db, studies),
            "medicalReports": _count(db, approved),
            "pendingReviews": _count(db, studies.where(Study.report_status == "Pending")),
        }
    elif user.role == "radiologist":
        stats = {
            "mriScans": _count(db, studies),
            "classifications": _count(db, studies),
            "segmentations": _count(db, studies.where(Study.seg_status == "Completed")),
            "reports": _count(db, studies),
            "reportsApproved": _count(db, approved),
        }
    else:  # patient
        stats = {
            "myScans": _count(db, studies),
            "medicalReports": _count(db, approved),
            "profileStatus": "Active" if user.is_active else "Inactive",
        }
    return StatsOut(role=user.role, stats=stats)
