"""Who may see which study."""
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Study, User


def visible_study_ids(user: User):
    """A SELECT of study ids this user is allowed to see."""
    q = select(Study.id)
    if user.role == "admin":
        return q
    if user.role == "radiologist":
        return q.where(Study.radiologist_id == user.id)
    if user.role == "doctor":
        mine = select(User.id).where(User.role == "patient", User.assigned_doctor_id == user.id)
        return q.where(Study.patient_id.in_(mine))
    if user.role == "patient":
        return q.where(Study.patient_id == user.id)
    return q.where(Study.id == -1)


def get_study_for_user(db: Session, user: User, study_id: int) -> Study:
    """404 (not 403) when not allowed, so existence of other studies is not leaked."""
    study = db.scalar(select(Study).where(Study.id == study_id, Study.id.in_(visible_study_ids(user))))
    if study is None:
        raise HTTPException(404, "Study not found.")
    return study
