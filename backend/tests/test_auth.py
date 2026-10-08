from backend.app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from backend.app.models.user import User, UserRole
from backend.tests.conftest import get_auth_headers_for_user


def test_password_hashing():
    raw_pass = "TestPassword@2026"
    hashed = hash_password(raw_pass)
    assert hashed != raw_pass
    assert verify_password(raw_pass, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_token_creation_and_validation():
    data = {"sub": "42", "role": "STUDENT", "email": "test@test.edu"}
    token = create_access_token(data)
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "42"
    assert decoded["role"] == "STUDENT"


def test_login_success_and_me(client, db_session):
    login_payload = {"email": "stud_a@test.edu", "password": "StudentPass123"}
    resp = client.post("/api/auth/login", json=login_payload)
    assert resp.status_code == 200
    json_data = resp.json()
    assert "access_token" in json_data
    assert json_data["user"]["email"] == "stud_a@test.edu"
    assert json_data["user"]["role"] == "STUDENT"

    token = json_data["access_token"]
    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["name"] == "Student A"


def test_login_invalid_password(client):
    login_payload = {"email": "stud_a@test.edu", "password": "WrongPassword"}
    resp = client.post("/api/auth/login", json=login_payload)
    assert resp.status_code == 401
    assert "invalid email or password" in resp.json()["detail"].lower()


def test_inactive_user_cannot_login(client, db_session):
    inactive_user = User(
        name="Deactivated User",
        email="inactive@test.edu",
        password_hash=hash_password("InactivePass123"),
        role=UserRole.STUDENT,
        is_active=False
    )
    db_session.add(inactive_user)
    db_session.commit()

    login_payload = {"email": "inactive@test.edu", "password": "InactivePass123"}
    resp = client.post("/api/auth/login", json=login_payload)
    assert resp.status_code == 403
    assert "deactivated" in resp.json()["detail"].lower()
