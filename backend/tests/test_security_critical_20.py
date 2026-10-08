import concurrent.futures
from sqlalchemy import text
from backend.app.models.user import User, UserRole
from backend.app.models.event import Event, EventStatus
from backend.app.models.registration import Registration, RegistrationStatus
from backend.app.models.audit_log import AuditLog
from backend.app.core.rate_limit import limiter
from backend.tests.conftest import get_auth_headers_for_user


def test_01_student_a_cannot_view_student_b_registration(client, db_session):
    """TEST 1: Student A cannot view Student B's registration."""
    stud_a = db_session.query(User).filter(User.email == "stud_a@test.edu").first()
    stud_b = db_session.query(User).filter(User.email == "stud_b@test.edu").first()
    event_a = db_session.query(Event).filter(Event.title == "Event by Faculty A").first()

    # Register Student B for event A
    reg_b = Registration(event_id=event_a.id, student_id=stud_b.id, status=RegistrationStatus.CONFIRMED)
    db_session.add(reg_b)
    db_session.commit()

    # Student A queries their registrations (/api/registrations/me)
    headers_a = get_auth_headers_for_user(stud_a)
    resp = client.get("/api/registrations/me", headers=headers_a)
    assert resp.status_code == 200
    registrations = resp.json()

    # Registration B must NOT appear in Student A's result
    reg_ids = [r["id"] for r in registrations]
    assert reg_b.id not in reg_ids


def test_02_student_a_cannot_cancel_student_b_registration(client, db_session):
    """TEST 2: Student A cannot cancel Student B's registration."""
    stud_a = db_session.query(User).filter(User.email == "stud_a@test.edu").first()
    stud_b = db_session.query(User).filter(User.email == "stud_b@test.edu").first()
    event_a = db_session.query(Event).filter(Event.title == "Event by Faculty A").first()

    reg_b = Registration(event_id=event_a.id, student_id=stud_b.id, status=RegistrationStatus.CONFIRMED)
    db_session.add(reg_b)
    db_session.commit()

    # Student A tries to cancel Student B's registration
    headers_a = get_auth_headers_for_user(stud_a)
    resp = client.delete(f"/api/registrations/{reg_b.id}", headers=headers_a)

    # Must be rejected with 403 Forbidden
    assert resp.status_code == 403
    assert "not authorized" in resp.json()["detail"].lower()

    # Verify registration in DB remains CONFIRMED
    db_session.refresh(reg_b)
    assert reg_b.status == RegistrationStatus.CONFIRMED


def test_03_student_cannot_create_event(client, db_session):
    """TEST 3: Student cannot create an event."""
    stud_a = db_session.query(User).filter(User.email == "stud_a@test.edu").first()
    headers_a = get_auth_headers_for_user(stud_a)

    event_payload = {
        "title": "Unauthorized Student Event",
        "description": "Attempted event creation by student",
        "category": "Tech",
        "venue": "Lab 1",
        "event_date": "2026-12-01",
        "start_time": "10:00",
        "end_time": "12:00",
        "participant_limit": 50,
        "registration_deadline": "2026-11-30T23:59:59"
    }

    resp = client.post("/api/events", json=event_payload, headers=headers_a)
    assert resp.status_code == 403
    assert "access denied" in resp.json()["detail"].lower()


def test_04_student_cannot_close_event(client, db_session):
    """TEST 4: Student cannot close an event."""
    stud_a = db_session.query(User).filter(User.email == "stud_a@test.edu").first()
    event_a = db_session.query(Event).filter(Event.title == "Event by Faculty A").first()
    headers_a = get_auth_headers_for_user(stud_a)

    resp = client.post(f"/api/events/{event_a.id}/close", headers=headers_a)
    assert resp.status_code == 403
    assert "access denied" in resp.json()["detail"].lower()


def test_05_faculty_a_cannot_view_faculty_b_participant_list(client, db_session):
    """TEST 5: Faculty A cannot view Faculty B's participant list."""
    fac_a = db_session.query(User).filter(User.email == "fac_a@test.edu").first()
    event_b = db_session.query(Event).filter(Event.title == "Event by Faculty B").first()
    headers_a = get_auth_headers_for_user(fac_a)

    # Faculty A requests participants of Faculty B's event
    resp = client.get(f"/api/events/{event_b.id}/participants", headers=headers_a)
    assert resp.status_code == 403
    assert "own events" in resp.json()["detail"].lower()


def test_06_faculty_a_cannot_modify_faculty_b_event(client, db_session):
    """TEST 6: Faculty A cannot modify Faculty B's event."""
    fac_a = db_session.query(User).filter(User.email == "fac_a@test.edu").first()
    event_b = db_session.query(Event).filter(Event.title == "Event by Faculty B").first()
    headers_a = get_auth_headers_for_user(fac_a)

    update_payload = {"title": "Tampered Title by Faculty A"}
    resp = client.put(f"/api/events/{event_b.id}", json=update_payload, headers=headers_a)
    assert resp.status_code == 403
    assert "cannot modify an event organized by another faculty" in resp.json()["detail"].lower()


def test_07_admin_only_endpoint_rejects_student(client, db_session):
    """TEST 7: Admin-only endpoint rejects Student."""
    stud_a = db_session.query(User).filter(User.email == "stud_a@test.edu").first()
    headers_a = get_auth_headers_for_user(stud_a)

    resp_users = client.get("/api/admin/users", headers=headers_a)
    assert resp_users.status_code == 403

    resp_audits = client.get("/api/admin/audit-logs", headers=headers_a)
    assert resp_audits.status_code == 403

    resp_stats = client.get("/api/admin/stats", headers=headers_a)
    assert resp_stats.status_code == 403


def test_08_student_cannot_register_twice_for_same_event(client, db_session):
    """TEST 8: Student cannot register twice for the same event."""
    stud_a = db_session.query(User).filter(User.email == "stud_a@test.edu").first()
    event_a = db_session.query(Event).filter(Event.title == "Event by Faculty A").first()
    headers_a = get_auth_headers_for_user(stud_a)

    # First registration -> 201 Created
    resp1 = client.post(f"/api/events/{event_a.id}/register", headers=headers_a)
    assert resp1.status_code == 201

    # Second registration attempt -> 409 Conflict
    resp2 = client.post(f"/api/events/{event_a.id}/register", headers=headers_a)
    assert resp2.status_code == 409
    assert "already registered" in resp2.json()["detail"].lower()


def test_09_registration_cannot_exceed_participant_limit(client, db_session):
    """TEST 9: Registration cannot exceed participant limit."""
    stud_a = db_session.query(User).filter(User.email == "stud_a@test.edu").first()
    stud_b = db_session.query(User).filter(User.email == "stud_b@test.edu").first()
    # Event B has participant_limit = 1
    event_b = db_session.query(Event).filter(Event.title == "Event by Faculty B").first()

    headers_a = get_auth_headers_for_user(stud_a)
    headers_b = get_auth_headers_for_user(stud_b)

    # Student A registers for the 1 available seat -> succeeds
    resp_a = client.post(f"/api/events/{event_b.id}/register", headers=headers_a)
    assert resp_a.status_code == 201

    # Student B tries to register for full event -> 400 Bad Request
    resp_b = client.post(f"/api/events/{event_b.id}/register", headers=headers_b)
    assert resp_b.status_code == 400
    assert "capacity reached" in resp_b.json()["detail"].lower()


def test_10_closed_event_rejects_registration(client, db_session):
    """TEST 10: Closed event rejects registration."""
    stud_a = db_session.query(User).filter(User.email == "stud_a@test.edu").first()
    event_closed = db_session.query(Event).filter(Event.status == EventStatus.CLOSED).first()
    headers_a = get_auth_headers_for_user(stud_a)

    resp = client.post(f"/api/events/{event_closed.id}/register", headers=headers_a)
    assert resp.status_code == 400
    assert "closed" in resp.json()["detail"].lower()


def test_11_invalid_event_id_is_handled_safely(client, db_session):
    """TEST 11: Invalid event ID is handled safely without leaking stack traces."""
    stud_a = db_session.query(User).filter(User.email == "stud_a@test.edu").first()
    headers_a = get_auth_headers_for_user(stud_a)

    # Non-existent integer ID
    resp = client.get("/api/events/99999")
    assert resp.status_code == 404
    assert "detail" in resp.json()

    # Non-existent ID registration
    resp_reg = client.post("/api/events/99999/register", headers=headers_a)
    assert resp_reg.status_code == 404

    # String format instead of integer
    resp_str = client.get("/api/events/invalid_id")
    assert resp_str.status_code == 422


def test_12_unauthenticated_registration_is_rejected(client, db_session):
    """TEST 12: Unauthenticated registration is rejected."""
    event_a = db_session.query(Event).filter(Event.title == "Event by Faculty A").first()

    # No authorization header / cookie provided (Guest user)
    resp = client.post(f"/api/events/{event_a.id}/register")
    assert resp.status_code == 401
    assert "authentication required" in resp.json()["detail"].lower()


def test_13_malformed_input_is_rejected_safely(client, db_session):
    """TEST 13: Malformed input is rejected safely."""
    fac_a = db_session.query(User).filter(User.email == "fac_a@test.edu").first()
    headers_a = get_auth_headers_for_user(fac_a)

    # Negative participant limit
    malformed_payload = {
        "title": "Valid Title",
        "description": "Valid Description",
        "category": "Tech",
        "venue": "Hall",
        "event_date": "2026-11-20",
        "start_time": "10:00",
        "end_time": "12:00",
        "participant_limit": -5,
        "registration_deadline": "2026-11-19T23:59:59"
    }
    resp = client.post("/api/events", json=malformed_payload, headers=headers_a)
    assert resp.status_code == 422
    assert "detail" in resp.json()


def test_14_passwords_are_never_returned_by_apis(client, db_session):
    """TEST 14: Passwords are never returned by APIs."""
    admin = db_session.query(User).filter(User.role == UserRole.ADMIN).first()
    headers_admin = get_auth_headers_for_user(admin)

    # 1. Login response
    login_resp = client.post("/api/auth/login", json={"email": "admin@test.edu", "password": "AdminPass123"})
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert "password" not in data["user"]
    assert "password_hash" not in data["user"]

    # 2. Get profile /me
    me_resp = client.get("/api/auth/me", headers=headers_admin)
    assert "password" not in me_resp.json()
    assert "password_hash" not in me_resp.json()

    # 3. Admin get users
    users_resp = client.get("/api/admin/users", headers=headers_admin)
    for u in users_resp.json():
        assert "password" not in u
        assert "password_hash" not in u


def test_15_sensitive_tokens_secrets_are_not_logged(db_session):
    """TEST 15: Sensitive tokens/secrets are not logged in Audit Logs."""
    logs = db_session.query(AuditLog).all()
    for log in logs:
        if log.metadata_json:
            meta_lower = log.metadata_json.lower()
            assert "password" not in meta_lower
            assert "bearer" not in meta_lower
            assert "token" not in meta_lower
            assert "secret" not in meta_lower


def test_16_concurrent_registrations_cannot_cause_capacity_overflow(client, db_session):
    """TEST 16: Concurrent registrations cannot cause capacity overflow."""
    # Create an event with strictly 1 seat
    fac_a = db_session.query(User).filter(User.email == "fac_a@test.edu").first()
    limited_event = Event(
        organizer_id=fac_a.id,
        title="Exclusive 1-Seat Seminar",
        description="Strict capacity of 1 participant",
        category="Tech",
        venue="Room 101",
        event_date="2026-11-20",
        start_time="10:00",
        end_time="12:00",
        participant_limit=1,
        registration_deadline="2026-11-19T23:59:59",
        status=EventStatus.OPEN
    )
    db_session.add(limited_event)
    db_session.commit()

    stud_a = db_session.query(User).filter(User.email == "stud_a@test.edu").first()
    stud_b = db_session.query(User).filter(User.email == "stud_b@test.edu").first()

    headers_a = get_auth_headers_for_user(stud_a)
    headers_b = get_auth_headers_for_user(stud_b)

    results = []
    def attempt_reg(headers):
        return client.post(f"/api/events/{limited_event.id}/register", headers=headers)

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(attempt_reg, headers_a)
        f2 = executor.submit(attempt_reg, headers_b)
        results = [f1.result(), f2.result()]

    status_codes = [r.status_code for r in results]
    # Exactly one request must succeed (201) and the other must be rejected (400)
    assert 201 in status_codes
    assert 400 in status_codes

    # Total confirmed count in DB must be exactly 1
    confirmed_count = db_session.query(Registration).filter(
        Registration.event_id == limited_event.id,
        Registration.status == RegistrationStatus.CONFIRMED
    ).count()
    assert confirmed_count == 1


def test_17_authentication_brute_force_attempts_are_controlled(client):
    """TEST 17: Authentication brute-force attempts are controlled by rate limiter."""
    limiter.clear_all()
    # Trigger 5 failed login attempts
    for _ in range(5):
        resp = client.post("/api/auth/login", json={"email": "stud_a@test.edu", "password": "WrongPassword!"})
        assert resp.status_code == 401

    # 6th attempt should be blocked with 429 Too Many Requests
    resp_rate = client.post("/api/auth/login", json={"email": "stud_a@test.edu", "password": "WrongPassword!"})
    assert resp_rate.status_code == 429
    assert "too many" in resp_rate.json()["detail"].lower()
    limiter.clear_all()


def test_18_sql_injection_payloads_do_not_alter_database_behavior(client, db_session):
    """TEST 18: SQL injection payloads do not alter database behavior."""
    sql_payload = "'; DROP TABLE events; --"
    resp = client.get(f"/api/events?search={sql_payload}")
    assert resp.status_code == 200

    # Ensure events table was not dropped
    count = db_session.query(Event).count()
    assert count > 0


def test_19_unauthorized_api_calls_generate_audit_events(client, db_session):
    """TEST 19: Unauthorized API calls generate audit/security events where appropriate."""
    stud_a = db_session.query(User).filter(User.email == "stud_a@test.edu").first()
    event_b = db_session.query(Event).filter(Event.title == "Event by Faculty B").first()
    headers_a = get_auth_headers_for_user(stud_a)

    # Student attempts to access admin users endpoint
    client.get("/api/admin/users", headers=headers_a)

    # Verify audit log captures RBAC denial
    rbac_logs = db_session.query(AuditLog).filter(
        AuditLog.action == "RBAC_ACCESS_DENIED",
        AuditLog.actor_id == stud_a.id
    ).all()
    assert len(rbac_logs) >= 1
    assert rbac_logs[0].result == "DENIED"


def test_20_logout_invalidates_access_appropriately(client, db_session):
    """TEST 20: Logout invalidates/ends authenticated access appropriately."""
    # Login as student
    login_resp = client.post("/api/auth/login", json={"email": "stud_a@test.edu", "password": "StudentPass123"})
    assert login_resp.status_code == 200

    # Extract cookie
    cookies = login_resp.cookies
    assert "access_token" in cookies

    # Access /me with cookie
    me_resp = client.get("/api/auth/me", cookies=cookies)
    assert me_resp.status_code == 200

    # Logout
    logout_resp = client.post("/api/auth/logout", cookies=cookies)
    assert logout_resp.status_code == 200

    # Cookie was instructed to delete (max-age 0 / empty value)
    cleared_cookie = logout_resp.cookies.get("access_token")
    assert cleared_cookie is None or cleared_cookie == ""
