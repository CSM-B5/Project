"""Creates the first admin / demo users at startup (only if they don't exist)."""
import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import User
from app.security import hash_password

log = logging.getLogger("neuroai.seed")

# DEVELOPMENT ONLY — these passwords are public.
DEMO_USERS = [
    ("admin@example.com", "Demo Admin", "admin", "Admin@12345"),
    ("doctor@example.com", "Dr. Demo", "doctor", "Doctor@12345"),
    ("radiologist@example.com", "Demo Radiologist", "radiologist", "Radio@12345"),
    ("patient@example.com", "Demo Patient", "patient", "Patient@12345"),
]


def _ensure(db: Session, email: str, name: str, role: str, password: str) -> User:
    user = db.scalar(select(User).where(User.email == email))
    if user is None:
        user = User(email=email, name=name, role=role, password_hash=hash_password(password))
        db.add(user)
        db.flush()
    return user


def seed(db: Session) -> None:
    s = get_settings()
    if s.admin_email and s.admin_password:
        if len(s.admin_password) < 8:
            log.warning("ADMIN_PASSWORD is shorter than 8 characters; admin not created.")
        else:
            _ensure(db, s.admin_email.lower(), "Administrator", "admin", s.admin_password)
    if s.seed_demo_users:
        made = {role: _ensure(db, e, n, role, pw) for e, n, role, pw in DEMO_USERS}
        made["patient"].assigned_doctor_id = made["doctor"].id
        log.warning("SEED_DEMO_USERS is on: public demo accounts exist. Turn it off outside development.")
    db.commit()
