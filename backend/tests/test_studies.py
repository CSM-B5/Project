import io

import numpy as np
import pytest
from PIL import Image

from app.services.classifier import CLASSES, ClassificationResult
from tests.conftest import login, png_bytes


def upload(client, headers, patient_id=None, name="scan.png", data=None, mime="image/png", extra_files=None):
    files = {"file": (name, data if data is not None else png_bytes(), mime)}
    files.update(extra_files or {})
    return client.post("/api/studies", headers=headers, files=files,
                       data={"patientId": str(patient_id)} if patient_id else {})


def test_upload_returns_frontend_shape(client, world):
    rad = login(client, "radio@example.com", "radiologist")
    r = upload(client, rad, world["patient"])
    assert r.status_code == 201, r.text
    b = r.json()
    assert set(b) >= {"id", "caseId", "patientInfo", "classification", "segmentation", "report"}
    assert b["patientInfo"]["scanType"] == "Brain MRI"
    probs = b["classification"]["probabilities"]
    assert set(probs) == set(CLASSES) and abs(sum(probs.values()) - 100) < 0.11
    assert b["classification"]["predictedClass"] in CLASSES
    seg = b["segmentation"]
    for k in ("originalImage", "predictedMask", "overlayImage"):
        assert seg[k].startswith("data:image/png;base64,")
    assert seg["diceScore"] is None and seg["iouScore"] is None   # no ground truth supplied
    assert b["report"]["status"] == "Pending" and b["report"]["summary"]


def test_only_radiologists_can_upload(client, world):
    for email, role in (("doc1@example.com", "doctor"), ("pat@example.com", "patient"), ("admin@example.com", "admin")):
        assert upload(client, login(client, email, role)).status_code == 403
    assert client.post("/api/studies", files={"file": ("a.png", png_bytes(), "image/png")}).status_code == 401


def test_upload_validation(client, world):
    rad = login(client, "radio@example.com", "radiologist")
    assert upload(client, rad, name="x.txt", data=b"hello", mime="text/plain").status_code == 415
    assert upload(client, rad, name="x.png", data=b"notanimage").status_code == 400
    assert upload(client, rad, name="x.png", data=b"").status_code == 400
    assert upload(client, rad, patient_id=99999).status_code == 400            # unknown patient
    assert upload(client, rad, patient_id=world["doctor"]).status_code == 400  # not a patient


def test_upload_size_limit(client, world, monkeypatch):
    from app.config import get_settings
    monkeypatch.setattr(get_settings(), "max_upload_mb", 0)
    rad = login(client, "radio@example.com", "radiologist")
    assert upload(client, rad).status_code == 413


def test_ground_truth_gives_dice_and_iou(client, world, monkeypatch):
    import app.api.studies as studies_mod

    class Stub:
        def predict(self, image):
            return ClassificationResult("Glioma", {"Glioma": 91.0, "Meningioma": 5.0, "Pituitary": 3.0, "No Tumor": 1.0})
    monkeypatch.setattr(studies_mod, "get_classifier", lambda: Stub())

    rad = login(client, "radio@example.com", "radiologist")
    # all-white ground truth vs any predicted mask -> dice/iou are valid numbers in [0,1]
    gt = io.BytesIO()
    Image.fromarray(np.full((128, 128), 255, dtype="uint8")).save(gt, format="PNG")
    r = upload(client, rad, extra_files={"groundTruthMask": ("gt.png", gt.getvalue(), "image/png")})
    seg = r.json()["segmentation"]
    assert 0 <= seg["diceScore"] <= 1 and 0 <= seg["iouScore"] <= 1
    assert seg["iouScore"] <= seg["diceScore"]


def test_tumor_class_gets_a_mask(client, world, monkeypatch):
    import app.api.studies as studies_mod

    class Stub:
        def predict(self, image):
            return ClassificationResult("Meningioma", {"Glioma": 4.0, "Meningioma": 90.0, "Pituitary": 5.0, "No Tumor": 1.0})
    monkeypatch.setattr(studies_mod, "get_classifier", lambda: Stub())
    rad = login(client, "radio@example.com", "radiologist")
    seg = upload(client, rad).json()["segmentation"]
    assert seg["status"] == "Completed" and seg["detectedRegionsCount"] >= 1 and seg["tumorAreaPercent"] > 0


def test_no_tumor_gives_empty_mask(client, world, monkeypatch):
    import app.api.studies as studies_mod

    class Stub:
        def predict(self, image):
            return ClassificationResult("No Tumor", {"Glioma": 3.0, "Meningioma": 2.0, "Pituitary": 1.0, "No Tumor": 94.0})
    monkeypatch.setattr(studies_mod, "get_classifier", lambda: Stub())
    rad = login(client, "radio@example.com", "radiologist")
    b = upload(client, rad).json()
    assert b["segmentation"]["status"] == "No tumor region detected"
    assert b["segmentation"]["detectedRegionsCount"] == 0
    assert "no features of a brain tumour" in b["report"]["summary"]


def test_visibility_and_approval_workflow(client, world):
    rad = login(client, "radio@example.com", "radiologist")
    doc = login(client, "doc1@example.com", "doctor")
    doc2 = login(client, "doc2@example.com", "doctor")
    pat = login(client, "pat@example.com", "patient")
    admin = login(client, "admin@example.com", "admin")

    sid = upload(client, rad, world["patient"]).json()["id"]

    # assigned doctor, radiologist (owner) and admin can see; other doctor cannot (404, not 403)
    assert client.get(f"/api/studies/{sid}", headers=doc).status_code == 200
    assert client.get(f"/api/studies/{sid}", headers=rad).status_code == 200
    assert client.get(f"/api/studies/{sid}", headers=admin).status_code == 200
    assert client.get(f"/api/studies/{sid}", headers=doc2).status_code == 404
    assert client.get("/api/studies", headers=doc2).json() == []

    # patient sees the record exists but NOT the AI results until approval
    d = client.get(f"/api/studies/{sid}", headers=pat).json()
    assert d["resultsVisible"] is False
    assert d["classification"]["predictedClass"] is None
    assert d["segmentation"]["overlayImage"] is None and d["report"]["summary"] is None
    row = client.get("/api/studies", headers=pat).json()[0]
    assert row["predictedClass"] is None and row["reportStatus"] == "Pending"

    # who may approve
    assert client.post(f"/api/studies/{sid}/report/approve", headers=pat, json={}).status_code == 403
    assert client.post(f"/api/studies/{sid}/report/approve", headers=rad, json={}).status_code == 403
    assert client.post(f"/api/studies/{sid}/report/approve", headers=doc2, json={}).status_code == 404

    ok = client.post(f"/api/studies/{sid}/report/approve", headers=doc, json={"summary": "Edited by doctor."})
    assert ok.status_code == 200
    assert ok.json()["report"]["status"] == "Approved" and ok.json()["report"]["approvedBy"] == "doc1"
    assert client.post(f"/api/studies/{sid}/report/approve", headers=doc, json={}).status_code == 409

    d = client.get(f"/api/studies/{sid}", headers=pat).json()
    assert d["resultsVisible"] is True
    assert d["report"]["summary"] == "Edited by doctor."
    assert d["classification"]["predictedClass"] in CLASSES
    assert d["segmentation"]["overlayImage"].startswith("data:image/png")


def test_patient_cannot_see_other_patients_studies(client, world):
    from tests.conftest import make_user
    other = make_user("pat2@example.com", "patient", doctor_id=world["doctor"])
    rad = login(client, "radio@example.com", "radiologist")
    sid = upload(client, rad, world["patient"]).json()["id"]
    h2 = login(client, "pat2@example.com", "patient")
    assert client.get(f"/api/studies/{sid}", headers=h2).status_code == 404
    assert client.get("/api/studies", headers=h2).json() == []
    assert other


def test_radiologist_only_sees_own_studies(client, world):
    from tests.conftest import make_user
    make_user("radio2@example.com", "radiologist")
    r1 = login(client, "radio@example.com", "radiologist")
    r2 = login(client, "radio2@example.com", "radiologist")
    sid = upload(client, r1).json()["id"]
    assert client.get(f"/api/studies/{sid}", headers=r2).status_code == 404
    assert len(client.get("/api/studies", headers=r1).json()) == 1
    assert client.get("/api/studies", headers=r2).json() == []


def test_assign_patient_after_upload_and_filter(client, world):
    rad = login(client, "radio@example.com", "radiologist")
    doc = login(client, "doc1@example.com", "doctor")
    sid = upload(client, rad).json()["id"]
    assert client.get("/api/studies", headers=doc).json() == []           # not linked yet
    r = client.patch(f"/api/studies/{sid}", headers=rad, json={"patientId": world["patient"]})
    assert r.status_code == 200 and r.json()["patientId"] == world["patient"]
    assert len(client.get("/api/studies?reportStatus=Pending", headers=doc).json()) == 1
    assert client.get("/api/studies?reportStatus=Approved", headers=doc).json() == []
    assert client.get("/api/studies?reportStatus=bogus", headers=doc).status_code == 422


def test_patients_list_scoped(client, world):
    rad = login(client, "radio@example.com", "radiologist")
    doc2 = login(client, "doc2@example.com", "doctor")
    doc1 = login(client, "doc1@example.com", "doctor")
    assert len(client.get("/api/patients", headers=rad).json()) == 1
    assert client.get("/api/patients", headers=doc2).json() == []
    assert len(client.get("/api/patients", headers=doc1).json()) == 1
    assert client.get("/api/patients", headers=login(client, "pat@example.com", "patient")).status_code == 403


def test_chat(client, world):
    rad = login(client, "radio@example.com", "radiologist")
    pat = login(client, "pat@example.com", "patient")
    doc2 = login(client, "doc2@example.com", "doctor")
    sid = upload(client, rad, world["patient"]).json()["id"]

    r = client.post("/api/chat", headers=rad, json={"message": "Draft a report", "studyId": sid})
    assert r.status_code == 200 and "DRAFT REPORT" in r.json()["reply"]
    assert "select or upload" in client.post("/api/chat", headers=rad, json={"message": "hi"}).json()["reply"]
    assert client.post("/api/chat", headers=doc2, json={"message": "hi", "studyId": sid}).status_code == 404
    assert client.post("/api/chat", headers=pat, json={"message": "hi"}).status_code == 403
    assert client.post("/api/chat", json={"message": "hi"}).status_code == 401
