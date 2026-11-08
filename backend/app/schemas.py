"""Request/response models. JSON uses camelCase to match the React frontend."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic.alias_generators import to_camel

Role = Literal["admin", "doctor", "radiologist", "patient"]


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


# ---------------- auth / users ----------------
class LoginRequest(CamelModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)
    role: Role


class RegisterRequest(CamelModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserOut(CamelModel):
    id: int
    email: str
    name: str
    role: Role
    is_active: bool
    assigned_doctor_id: int | None = None
    created_at: datetime


class TokenResponse(CamelModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class AdminUserCreate(CamelModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: Role
    assigned_doctor_id: int | None = None


class AdminUserUpdate(CamelModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    is_active: bool | None = None
    role: Role | None = None
    assigned_doctor_id: int | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)


class PatientBrief(CamelModel):
    id: int
    name: str
    email: str


class ActivityOut(CamelModel):
    id: int
    action: str
    detail: str
    user_email: str | None = None
    created_at: datetime


# ---------------- studies (same shape as the frontend's mockData.json) ----------------
class PatientInfo(CamelModel):
    case_id: str
    name: str
    scan_type: str


class ClassificationOut(CamelModel):
    predicted_class: str | None = None
    probabilities: dict[str, float] | None = None


class SegmentationOut(CamelModel):
    status: str
    original_image: str | None = None   # data URL (PNG)
    predicted_mask: str | None = None   # data URL (PNG, white = tumor)
    overlay_image: str | None = None    # data URL (PNG, tumor tinted red)
    dice_score: float | None = None     # only when a ground-truth mask was supplied
    iou_score: float | None = None
    detected_regions_count: int | None = None
    tumor_area_percent: float | None = None


class ReportOut(CamelModel):
    status: str
    summary: str | None = None
    approved_by: str | None = None
    approved_at: datetime | None = None


class StudyOut(CamelModel):
    id: int
    case_id: str
    created_at: datetime
    patient_id: int | None = None
    radiologist_name: str
    results_visible: bool = True
    patient_info: PatientInfo
    classification: ClassificationOut
    segmentation: SegmentationOut
    report: ReportOut
    disclaimer: str = "Research prototype. Not a medical device; not for clinical diagnosis."


class StudySummary(CamelModel):
    id: int
    case_id: str
    created_at: datetime
    scan_type: str
    patient_id: int | None = None
    patient_name: str
    predicted_class: str | None = None
    segmentation_status: str | None = None
    report_status: str


class StudyAssign(CamelModel):
    patient_id: int | None = None


class ApproveRequest(CamelModel):
    summary: str | None = Field(default=None, min_length=1, max_length=5000)


# ---------------- stats / chat ----------------
class StatsOut(CamelModel):
    role: Role
    stats: dict[str, int | str]


class ChatRequest(CamelModel):
    message: str = Field(min_length=1, max_length=4000)
    study_id: int | None = None
    history: list["ChatTurn"] = Field(default_factory=list, max_length=40)


class ChatTurn(CamelModel):
    sender: str  # "user" | "ai"
    text: str = Field(max_length=8000)


class ChatResponse(CamelModel):
    reply: str
    study_id: int | None = None


ChatRequest.model_rebuild()
