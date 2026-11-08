from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import get_db, require_roles
from app.models import ActivityLog, User
from app.schemas import ActivityOut, AdminUserCreate, AdminUserUpdate, Role, UserOut
from app.security import hash_password
from app.services.activity import log_activity

router = APIRouter(prefix="/api/admin", tags=["admin"])
admin_only = require_roles("admin")


def _check_doctor(db: Session, doctor_id: int | None) -> None:
    if doctor_id is None:
        return
    d = db.get(User, doctor_id)
    if d is None or d.role != "doctor" or not d.is_active:
        raise HTTPException(400, "assignedDoctorId must be the id of an active doctor.")


@router.get("/users", response_model=list[UserOut])
def list_users(
    role: Role | None = None,
    q: str | None = Query(default=None, max_length=100),
    db: Session = Depends(get_db),
    _: User = Depends(admin_only),
):
    stmt = select(User).order_by(User.created_at.desc())
    if role:
        stmt = stmt.where(User.role == role)
    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(User.email.like(like) | User.name.ilike(like))
    return [UserOut.model_validate(u) for u in db.scalars(stmt.limit(500))]


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(req: AdminUserCreate, db: Session = Depends(get_db), admin: User = Depends(admin_only)):
    email = req.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(409, "An account with this email already exists.")
    if req.assigned_doctor_id is not None and req.role != "patient":
        raise HTTPException(400, "Only patients can have an assigned doctor.")
    _check_doctor(db, req.assigned_doctor_id)
    user = User(
        email=email, name=req.name.strip(), password_hash=hash_password(req.password),
        role=req.role, assigned_doctor_id=req.assigned_doctor_id,
    )
    db.add(user)
    db.flush()
    log_activity(db, admin, "user_created", f"Created {req.role} account {email}")
    db.commit()
    return UserOut.model_validate(user)


@router.patch("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, req: AdminUserUpdate, db: Session = Depends(get_db), admin: User = Depends(admin_only)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(404, "User not found.")
    fields = req.model_fields_set

    if user.id == admin.id and (req.is_active is False or (req.role and req.role != "admin")):
        raise HTTPException(400, "You cannot deactivate yourself or remove your own admin role.")

    if req.name is not None:
        user.name = req.name.strip()
    if req.is_active is not None:
        user.is_active = req.is_active
    if req.role is not None:
        user.role = req.role
    if req.password is not None:
        user.password_hash = hash_password(req.password)
    if "assigned_doctor_id" in fields:  # explicit null clears the assignment
        if req.assigned_doctor_id is not None and user.role != "patient":
            raise HTTPException(400, "Only patients can have an assigned doctor.")
        _check_doctor(db, req.assigned_doctor_id)
        user.assigned_doctor_id = req.assigned_doctor_id
    if user.role != "patient":
        user.assigned_doctor_id = None

    log_activity(db, admin, "user_updated", f"Updated {user.email}: {', '.join(sorted(fields)) or 'no changes'}")
    db.commit()
    return UserOut.model_validate(user)


@router.get("/activity", response_model=list[ActivityOut])
def activity(limit: int = Query(default=50, ge=1, le=200), db: Session = Depends(get_db), _: User = Depends(admin_only)):
    rows = db.scalars(select(ActivityLog).order_by(ActivityLog.id.desc()).limit(limit))
    return [
        ActivityOut(id=r.id, action=r.action, detail=r.detail,
                    user_email=r.user.email if r.user else None, created_at=r.created_at)
        for r in rows
    ]
