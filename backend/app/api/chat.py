from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_db, require_roles
from app.models import User
from app.schemas import ChatRequest, ChatResponse
from app.services import llm
from app.services.access import get_study_for_user

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "doctor", "radiologist")),
):
    """Clinician chat about a study. The caller must be allowed to see that study."""
    study = get_study_for_user(db, user, req.study_id) if req.study_id else None
    reply = await llm.generate_reply(req.message, study, req.history)
    return ChatResponse(reply=reply, study_id=req.study_id)
