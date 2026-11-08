"""Converts database rows into the JSON the frontend expects."""
from app.models import Study, User
from app.schemas import (
    ClassificationOut,
    PatientInfo,
    ReportOut,
    SegmentationOut,
    StudyOut,
    StudySummary,
)
from app.services import storage


def case_id(study: Study) -> str:
    return f"CASE-{study.created_at.year}-{study.id:05d}"


def _patient_name(study: Study) -> str:
    return study.patient.name if study.patient else "Unassigned Patient"


def _results_visible(study: Study, viewer: User) -> bool:
    # Patients only see AI results after a doctor approved the report.
    return not (viewer.role == "patient" and study.report_status != "Approved")


def study_summary(study: Study, viewer: User) -> StudySummary:
    visible = _results_visible(study, viewer)
    return StudySummary(
        id=study.id,
        case_id=case_id(study),
        created_at=study.created_at,
        scan_type=study.scan_type,
        patient_id=study.patient_id,
        patient_name=_patient_name(study),
        predicted_class=study.predicted_class if visible else None,
        segmentation_status=study.seg_status if visible else None,
        report_status=study.report_status,
    )


def study_detail(study: Study, viewer: User) -> StudyOut:
    visible = _results_visible(study, viewer)
    imgs = storage.load_data_urls(study.id) if visible else {}
    return StudyOut(
        id=study.id,
        case_id=case_id(study),
        created_at=study.created_at,
        patient_id=study.patient_id,
        radiologist_name=study.radiologist.name,
        results_visible=visible,
        patient_info=PatientInfo(case_id=case_id(study), name=_patient_name(study), scan_type=study.scan_type),
        classification=ClassificationOut(
            predicted_class=study.predicted_class if visible else None,
            probabilities=study.probabilities if visible else None,
        ),
        segmentation=SegmentationOut(
            status=study.seg_status if visible else "Pending approval",
            original_image=imgs.get("original"),
            predicted_mask=imgs.get("mask"),
            overlay_image=imgs.get("overlay"),
            dice_score=study.dice_score if visible else None,
            iou_score=study.iou_score if visible else None,
            detected_regions_count=study.seg_regions if visible else None,
            tumor_area_percent=study.tumor_area_percent if visible else None,
        ),
        report=ReportOut(
            status=study.report_status,
            summary=study.report_summary if visible else None,
            approved_by=study.approved_by.name if study.approved_by else None,
            approved_at=study.approved_at,
        ),
    )
