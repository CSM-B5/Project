import os
import tempfile

# Must be set BEFORE the app is imported
_tmp = tempfile.mkdtemp(prefix="neuroai-test-")
os.environ["DATABASE_URL"] = "sqlite://"          # in-memory
os.environ["STORAGE_DIR"] = _tmp
os.environ["SEED_DEMO_USERS"] = "false"
os.environ["ADMIN_EMAIL"] = ""
os.environ["ADMIN_PASSWORD"] = ""
os.environ["SECRET_KEY"] = "test-secret-key-for-pytest-only-0123456789"
os.environ["LLM_PROVIDER"] = "mock"
os.environ["ALLOW_PATIENT_REGISTRATION"] = "true"

import io  # noqa: E402

import numpy as np  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from PIL import Image  # noqa: E402

from app.api import auth as auth_module  # noqa: E402
from app.database import Base, SessionLocal, engine, init_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import User  # noqa: E402
from app.security import hash_password  # noqa: E402


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(engine)
    init_db()
    auth_module._failures.clear()
    yield


@pytest.fixture
def client():
    return TestClient(app)


def make_user(email, role, password="Password1!", name=None, doctor_id=None, active=True):
    with SessionLocal() as db:
        u = User(email=email, name=name or email.split("@")[0], role=role,
                 password_hash=hash_password(password), assigned_doctor_id=doctor_id, is_active=active)
        db.add(u)
        db.commit()
        return u.id


def login(client, email, role, password="Password1!"):
    r = client.post("/api/auth/login", json={"email": email, "password": password, "role": role})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['accessToken']}"}


def png_bytes(seed=1, size=128) -> bytes:
    rng = np.random.default_rng(seed)
    arr = (rng.random((size, size)) * 255).astype("uint8")
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def world(client):
    """admin, one doctor, a second doctor, radiologist, patient assigned to doctor1."""
    ids = {}
    ids["admin"] = make_user("admin@example.com", "admin")
    ids["doctor"] = make_user("doc1@example.com", "doctor")
    ids["doctor2"] = make_user("doc2@example.com", "doctor")
    ids["radio"] = make_user("radio@example.com", "radiologist")
    ids["patient"] = make_user("pat@example.com", "patient", doctor_id=ids["doctor"])
    return ids
