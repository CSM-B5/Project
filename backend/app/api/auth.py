import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.deps import get_current_user, get_db
from app.models import User
from app.schemas import LoginRequest, RegisterRequest, TokenResponse, UserOut
from app.security import DUMMY_HASH, create_access_token, hash_password, verify_password
from app.services.activity import log_activity

router = APIRouter(prefix="/api/auth", tags=["auth"])

# --- simple brute-force protection (in memory, per email) ---
MAX_FAILS = 5
WINDOW_SECONDS = 15 * 60
_failures: dict[str, list[float]] = {}


def _recent_failures(key: str) -> list[float]:
    now = time.time()
    fails = [t for t in _failures.get(key, []) if now - t < WINDOW_SECONDS]
    _failures[key] = fails
    return fails


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    email = req.email.lower()
    if len(_recent_failures(email)) >= MAX_FAILS:
        raise HTTPException(429, "Too many failed attempts. Try again in 15 minutes.")

    user = db.scalar(select(User).where(User.email == email))
    password_ok = verify_password(req.password, user.password_hash if user else DUMMY_HASH)
    # One generic message for every failure so attackers learn nothing.
    if not (user and password_ok and user.is_active and user.role == req.role):
        _failures.setdefault(email, []).append(time.time())
        raise HTTPException(401, "Invalid email, password or role.")

    _failures.pop(email, None)
    log_activity(db, user, "login", f"{user.email} signed in as {user.role}")
    db.commit()
    return TokenResponse(access_token=create_access_token(user.id, user.role), user=UserOut.model_validate(user))


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """Self-registration. Always creates a *patient* account."""
    if not get_settings().allow_patient_registration:
        raise HTTPException(403, "Self-registration is disabled. Ask an administrator.")
    email = req.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(409, "An account with this email already exists.")
    user = User(email=email, name=req.name.strip(), password_hash=hash_password(req.password), role="patient")
    db.add(user)
    db.flush()
    log_activity(db, user, "register", f"New patient account {email}")
    db.commit()
    return TokenResponse(access_token=create_access_token(user.id, user.role), user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return UserOut.model_validate(user)
