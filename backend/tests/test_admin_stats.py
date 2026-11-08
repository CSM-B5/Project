from tests.conftest import login, png_bytes


def test_admin_user_management(client, world):
    h = login(client, "admin@example.com", "admin")
    r = client.post("/api/admin/users", headers=h, json={
        "name": "Dr New", "email": "new.doc@example.com", "password": "Longpass1", "role": "doctor"})
    assert r.status_code == 201
    new_id = r.json()["id"]

    assert client.post("/api/admin/users", headers=h, json={
        "name": "Dup", "email": "NEW.DOC@example.com", "password": "Longpass1", "role": "doctor"}).status_code == 409

    # new account can log in, then gets deactivated
    login(client, "new.doc@example.com", "doctor", "Longpass1")
    assert client.patch(f"/api/admin/users/{new_id}", headers=h, json={"isActive": False}).json()["isActive"] is False
    assert client.post("/api/auth/login", json={
        "email": "new.doc@example.com", "password": "Longpass1", "role": "doctor"}).status_code == 401

    users = client.get("/api/admin/users?role=doctor", headers=h).json()
    assert {u["email"] for u in users} >= {"doc1@example.com", "doc2@example.com", "new.doc@example.com"}


def test_admin_cannot_lock_self_out(client, world):
    h = login(client, "admin@example.com", "admin")
    me = client.get("/api/auth/me", headers=h).json()["id"]
    assert client.patch(f"/api/admin/users/{me}", headers=h, json={"isActive": False}).status_code == 400
    assert client.patch(f"/api/admin/users/{me}", headers=h, json={"role": "patient"}).status_code == 400


def test_assign_doctor_rules(client, world):
    h = login(client, "admin@example.com", "admin")
    pid, d2, rad = world["patient"], world["doctor2"], world["radio"]
    r = client.patch(f"/api/admin/users/{pid}", headers=h, json={"assignedDoctorId": d2})
    assert r.json()["assignedDoctorId"] == d2
    assert client.patch(f"/api/admin/users/{pid}", headers=h, json={"assignedDoctorId": rad}).status_code == 400
    assert client.patch(f"/api/admin/users/{pid}", headers=h, json={"assignedDoctorId": None}).json()["assignedDoctorId"] is None


def test_non_admins_blocked_from_admin_api(client, world):
    for email, role in (("doc1@example.com", "doctor"), ("radio@example.com", "radiologist"), ("pat@example.com", "patient")):
        h = login(client, email, role)
        assert client.get("/api/admin/users", headers=h).status_code == 403
        assert client.get("/api/admin/activity", headers=h).status_code == 403


def test_activity_log_records_events(client, world):
    h = login(client, "admin@example.com", "admin")
    acts = client.get("/api/admin/activity", headers=h).json()
    assert any(a["action"] == "login" and a["userEmail"] == "admin@example.com" for a in acts)


def test_dashboard_stats_per_role(client, world):
    admin = login(client, "admin@example.com", "admin")
    doc = login(client, "doc1@example.com", "doctor")
    rad = login(client, "radio@example.com", "radiologist")
    pat = login(client, "pat@example.com", "patient")

    s = client.get("/api/stats/dashboard", headers=admin).json()
    assert s["role"] == "admin"
    assert s["stats"]["registeredDoctors"] == 2 and s["stats"]["registeredPatients"] == 1
    assert s["stats"]["mriStudies"] == 0 and s["stats"]["systemActivity"] >= 4

    client.post("/api/studies", headers=rad, files={"file": ("a.png", png_bytes(), "image/png")},
                data={"patientId": str(world["patient"])})

    assert client.get("/api/stats/dashboard", headers=rad).json()["stats"]["mriScans"] == 1
    d = client.get("/api/stats/dashboard", headers=doc).json()["stats"]
    assert d["myPatients"] == 1 and d["mriStudies"] == 1 and d["pendingReviews"] == 1 and d["medicalReports"] == 0
    p = client.get("/api/stats/dashboard", headers=pat).json()["stats"]
    assert p["myScans"] == 1 and p["medicalReports"] == 0 and p["profileStatus"] == "Active"
    other = login(client, "doc2@example.com", "doctor")
    assert client.get("/api/stats/dashboard", headers=other).json()["stats"]["mriStudies"] == 0
