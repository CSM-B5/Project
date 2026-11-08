from tests.conftest import login, make_user


def test_health(client):
    assert client.get("/health").json()["status"] == "ok"


def test_login_success_and_me(client, world):
    h = login(client, "doc1@example.com", "doctor")
    me = client.get("/api/auth/me", headers=h).json()
    assert me["role"] == "doctor" and me["email"] == "doc1@example.com"
    assert "passwordHash" not in me and "password_hash" not in me


def test_login_email_is_case_insensitive(client, world):
    login(client, "DOC1@Example.com", "doctor")


def test_login_wrong_password_wrong_role_unknown_user_all_401(client, world):
    for body in (
        {"email": "doc1@example.com", "password": "nope-nope", "role": "doctor"},
        {"email": "doc1@example.com", "password": "Password1!", "role": "admin"},   # wrong role
        {"email": "ghost@example.com", "password": "Password1!", "role": "doctor"},
    ):
        r = client.post("/api/auth/login", json=body)
        assert r.status_code == 401
        assert r.json()["detail"] == "Invalid email, password or role."


def test_inactive_user_cannot_login(client):
    make_user("off@example.com", "doctor", active=False)
    r = client.post("/api/auth/login", json={"email": "off@example.com", "password": "Password1!", "role": "doctor"})
    assert r.status_code == 401


def test_login_rate_limit(client, world):
    bad = {"email": "doc1@example.com", "password": "wrong-wrong", "role": "doctor"}
    for _ in range(5):
        assert client.post("/api/auth/login", json=bad).status_code == 401
    assert client.post("/api/auth/login", json=bad).status_code == 429
    # even the right password is blocked while locked
    good = {"email": "doc1@example.com", "password": "Password1!", "role": "doctor"}
    assert client.post("/api/auth/login", json=good).status_code == 429


def test_protected_routes_need_token(client):
    for path in ("/api/auth/me", "/api/studies", "/api/stats/dashboard", "/api/patients"):
        assert client.get(path).status_code == 401
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer garbage"}).status_code == 401


def test_register_creates_patient_only(client):
    r = client.post("/api/auth/register", json={"name": "New P", "email": "new@example.com", "password": "longenough1"})
    assert r.status_code == 201
    assert r.json()["user"]["role"] == "patient"
    dup = client.post("/api/auth/register", json={"name": "X", "email": "NEW@example.com", "password": "longenough1"})
    assert dup.status_code == 409
    weak = client.post("/api/auth/register", json={"name": "X", "email": "w@example.com", "password": "short"})
    assert weak.status_code == 422
    # role field is ignored / cannot escalate
    esc = client.post("/api/auth/register",
                      json={"name": "E", "email": "e@example.com", "password": "longenough1", "role": "admin"})
    assert esc.json()["user"]["role"] == "patient"
