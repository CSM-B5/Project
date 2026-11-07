import secrets
from datetime import datetime

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import get_settings
from app.schemas import (
    AnalysisResponse,
    ChatRequest,
    ChatResponse,
    PatientInfo,
    Segmentation,
)
from app.services import llm, store
from app.services.classifier import get_classifier
from app.services.image_io import load_scan
from app.services.segmenter import OVERLAY_HEX, MockSegmenter, get_segmenter

router = APIRouter(prefix="/api")


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(file: UploadFile = File(...)):
    """Upload a scan (png/jpg/dcm) -> classification + segmentation + summary."""
    limit = get_settings().max_upload_mb * 1024 * 1024
    data = await file.read(limit + 1)
    if len(data) > limit:
        raise HTTPException(413, f"File larger than {get_settings().max_upload_mb} MB.")
    if not data:
        raise HTTPException(400, "Empty file.")

    image, scan_type = load_scan(file.filename or "", data)

    classification = get_classifier().predict(image)
    seg = get_segmenter().segment(image)

    case_id = f"CASE-{datetime.now().year}-{secrets.token_hex(3).upper()}"
    result = AnalysisResponse(
        caseId=case_id,
        patientInfo=PatientInfo(caseId=case_id, scanType=scan_type),
        classification=classification,
        segmentation=Segmentation(
            maskActive=seg.regions > 0,
            overlayColor=OVERLAY_HEX,
            detectedRegionsCount=seg.regions,
            maskImage=MockSegmenter.to_overlay_data_url(seg, image.size),
        ),
        llmInitialSummary="",
    )
    result.llmInitialSummary = llm.initial_summary(result)
    store.save_case(result)
    return result


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Send a clinician message; optionally tie it to a caseId from /analyze."""
    case = store.get_case(req.caseId)
    if req.caseId and case is None:
        raise HTTPException(404, "Unknown caseId. Re-upload the scan.")
    reply = await llm.generate_reply(req.message, case, req.history)
    return ChatResponse(reply=reply, caseId=req.caseId)


@router.get("/cases/{case_id}", response_model=AnalysisResponse)
def get_case(case_id: str):
    case = store.get_case(case_id)
    if case is None:
        raise HTTPException(404, "Case not found.")
    return case
