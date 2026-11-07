import io

import numpy as np
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

client = TestClient(app)


def _png() -> bytes:
    arr = (np.random.default_rng(1).random((256, 256)) * 255).astype("uint8")
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, format="PNG")
    return buf.getvalue()


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_analyze_and_chat_flow():
    r = client.post("/api/analyze", files={"file": ("scan.png", _png(), "image/png")})
    assert r.status_code == 200, r.text
    body = r.json()
    for key in ("patientInfo", "classification", "segmentation", "llmInitialSummary"):
        assert key in body
    assert 0 <= body["classification"]["confidenceScore"] <= 100
    assert body["segmentation"]["maskImage"].startswith("data:image/png;base64,")

    c = client.post(
        "/api/chat", json={"message": "Draft a report", "caseId": body["caseId"]}
    )
    assert c.status_code == 200
    assert "DRAFT REPORT" in c.json()["reply"]


def test_rejects_bad_type():
    r = client.post("/api/analyze", files={"file": ("x.txt", b"hello", "text/plain")})
    assert r.status_code == 415


def test_rejects_corrupt_image():
    r = client.post("/api/analyze", files={"file": ("x.png", b"notanimage", "image/png")})
    assert r.status_code == 400


def test_chat_unknown_case():
    r = client.post("/api/chat", json={"message": "hi", "caseId": "nope"})
    assert r.status_code == 404
