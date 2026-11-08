from sqlalchemy.orm import Session

from app.models import ActivityLog, User


def log_activity(db: Session, user: User | None, action: str, detail: str = "") -> None:
    """Adds an audit-log row (committed together with the caller's transaction)."""
    db.add(ActivityLog(user_id=user.id if user else None, action=action, detail=detail[:400]))
