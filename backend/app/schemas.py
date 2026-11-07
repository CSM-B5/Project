"""Response/request models. Field names are camelCase on purpose so the JSON
matches the frontend's src/mockData.json exactly."""
from pydantic import BaseModel, Field


class PatientInfo(BaseModel):
    caseId: str
    name: str = "Anonymous Patient"
    scanType: str


class Classification(BaseModel):
    primaryLabel: str
    confidenceScore: float = Field(description="0-100")
    secondaryLabel: str
    secondaryScore: float = Field(description="0-100")
    anatomicalTarget: str


class Segmentation(BaseModel):
    maskActive: bool
    overlayColor: str = "#f43f5e"
    detectedRegionsCount: int
    # PNG (RGBA, transparent except the mask) as a data URL, same aspect ratio
    # as the uploaded scan. Frontend can draw it over the image with <img>.
    maskImage: str | None = None


class AnalysisResponse(BaseModel):
    caseId: str
    patientInfo: PatientInfo
    classification: Classification
    segmentation: Segmentation
    llmInitialSummary: str
    disclaimer: str = (
        "Research prototype. Not a medical device; not for clinical diagnosis."
    )


class ChatTurn(BaseModel):
    sender: str  # "user" | "ai"  (same as the frontend's message objects)
    text: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    caseId: str | None = None
    history: list[ChatTurn] = Field(default_factory=list, max_length=40)


class ChatResponse(BaseModel):
    reply: str
    caseId: str | None = None
