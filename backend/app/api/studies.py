from datetime import datetime, timezone

import numpy as np
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from PIL import Image
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.config import get_settings
from app.deps import get_current_user, get_db, require_roles
from app.models import Study, User
from app.schemas import ApproveRequest, StudyAssign, StudyOut, StudySummary
from app.services import llm, presenter, storage, visuals
from app.services.access import get_study_for_user, visible_study_ids
from app.services.activity import log_activity
from app.services.classifier import NO_TUMOR, get_classifier
from app.services.image_io import load_mask, load_scan
from app.services.metrics import dice_iou
from app.services.segmenter import get_segmenter

router = APIRouter(prefix="/api/studies", tags=["studies"])


def _read_limited(upload: UploadFile, what: str) -> bytes:
    limit = get_settings().max_upload_mb * 1024 * 1024
    data = upload.file.read(limit + 1)
    if len(data) > limit:
        raise HTTPException(413, f"{what} is larger than {get_settings().max_upload_mb} MB.")
    if not data:
        raise HTTPException(400, f"{what} is empty.")
    return data


def _check_patient(db: Session, patient_id: int | None) -> None:
    if patient_id is None:
        return
    p = db.get(User, patient_id)
    if p is None or p.role != "patient" or not p.is_active:
        raise HTTPException(400, "patientId must be the id of an active patient.")


# NOTE: plain `def` (not async) on purpose: model inference is CPU work and FastAPI
# runs sync endpoints in a thread pool, so the server stays responsive.
@router.post("", response_model=StudyOut, status_code=201)
def create_study(
    file: UploadFile = File(...),
    patient_id: int | None = Form(default=None, alias="patientId"),
    ground_truth_mask: UploadFile | None = File(default=None, alias="groundTruthMask"),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("radiologist")),
):
    """Upload a brain MRI (png/jpg/dcm) -> classification + segmentation + draft report.
    Optional `groundTruthMask` lets the backend compute Dice and IoU scores."""
    _check_patient(db, patient_id)
    data = _read_limited(file, "File")
    image = load_scan(file.filename or "", data)

    gt_img = None
    if ground_truth_mask is not None and ground_truth_mask.filename:
        gt_img = load_mask(_read_limited(ground_truth_mask, "Ground-truth mask"))

    original = visuals.prepare_original(image)
    cls = get_classifier().predict(image)
    seg = get_segmenter().segment(image, tumor_expected=cls.predicted_class != NO_TUMOR)
    mask = visuals.upscale_mask(seg.mask, original.size)

    dice = iou = None
    if gt_img is not None:
        truth = np.asarray(gt_img.resize(original.size, Image.NEAREST)) > 127
        dice, iou = dice_iou(mask, truth)

    study = Study(
        patient_id=patient_id,
        radiologist_id=user.id,
        scan_type="Brain MRI",
        original_filename=(file.filename or "")[:255],
        predicted_class=cls.predicted_class,
        probabilities=cls.probabilities,
        seg_status="Completed" if seg.regions > 0 else "No tumor region detected",
        seg_regions=seg.regions,
        tumor_area_percent=seg.area_percent,
        dice_score=dice,
        iou_score=iou,
        report_status="Pending",
        report_summary=llm.draft_report(cls.predicted_class, cls.probabilities, seg.regions, seg.area_percent),
    )
    db.add(study)
    try:
        db.flush()  # gives the study its id
        storage.save_images(
            study.id,
            visuals.image_png(original),
            visuals.mask_png(mask),
            visuals.overlay_png(original, mask),
        )
        log_activity(db, user, "study_created", f"Study {study.id}: {cls.predicted_class}")
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(500, "Could not save the study.")
    return presenter.study_detail(study, user)


@router.get("", response_model=list[StudySummary])
def list_studies(
    report_status: str | None = Query(default=None, alias="reportStatus", pattern="^(Pending|Approved)$"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    stmt = (
        select(Study)
        .where(Study.id.in_(visible_study_ids(user)))
        .options(selectinload(Study.patient))
        .order_by(Study.created_at.desc(), Study.id.desc())
        .limit(200)
    )
    if report_status:
        stmt = stmt.where(Study.report_status == report_status)
    return [presenter.study_summary(s, user) for s in db.scalars(stmt)]


@router.get("/{study_id}", response_model=StudyOut)
def get_study(study_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return presenter.study_detail(get_study_for_user(db, user, study_id), user)


@router.patch("/{study_id}", response_model=StudyOut)
def assign_patient(
    study_id: int,
    req: StudyAssign,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("radiologist", "admin")),
):
    """Link (or unlink) a study to a patient after upload."""
    study = get_study_for_user(db, user, study_id)
    _check_patient(db, req.patient_id)
    study.patient_id = req.patient_id
    log_activity(db, user, "study_assigned", f"Study {study.id} -> patient {req.patient_id}")
    db.commit()
    db.refresh(study)
    return presenter.study_detail(study, user)


@router.post("/{study_id}/report/approve", response_model=StudyOut)
def approve_report(
    study_id: int,
    req: ApproveRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("doctor")),
):
    """The responsible doctor approves (and may edit) the AI-drafted report."""
    study = get_study_for_user(db, user, study_id)  # only doctors assigned to the patient
    if study.report_status == "Approved":
        raise HTTPException(409, "This report is already approved.")
    if req.summary:
        study.report_summary = req.summary.strip()
    study.report_status = "Approved"
    study.approved_by_id = user.id
    study.approved_at = datetime.now(timezone.utc)
    log_activity(db, user, "report_approved", f"Study {study.id} approved")
    db.commit()
    db.refresh(study)
    return presenter.study_detail(study, user)
