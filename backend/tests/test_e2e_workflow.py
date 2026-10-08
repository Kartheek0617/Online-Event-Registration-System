from backend.app.models.event import EventStatus


def test_e2e_student_workflow(client):
    """
    E2E Student Workflow:
    Login -> View events -> View details -> Register -> View registration -> Cancel registration
    """
    # 1. Login
    login_resp = client.post("/api/auth/login", json={"email": "stud_a@test.edu", "password": "StudentPass123"})
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. View available events
    events_resp = client.get("/api/events", headers=headers)
    assert events_resp.status_code == 200
    events = events_resp.json()
    assert len(events) > 0
    target_event = next(e for e in events if e["status"] == "OPEN" and e["available_seats"] > 0)

    # 3. View details
    detail_resp = client.get(f"/api/events/{target_event['id']}", headers=headers)
    assert detail_resp.status_code == 200
    assert detail_resp.json()["id"] == target_event["id"]
    assert detail_resp.json()["is_registered_by_user"] is False

    # 4. Register
    reg_resp = client.post(f"/api/events/{target_event['id']}/register", headers=headers)
    assert reg_resp.status_code == 201
    reg_id = reg_resp.json()["registration"]["id"]

    # 5. View my registrations
    my_regs_resp = client.get("/api/registrations/me", headers=headers)
    assert my_regs_resp.status_code == 200
    my_regs = my_regs_resp.json()
    assert any(r["id"] == reg_id for r in my_regs)

    # 6. Cancel registration
    cancel_resp = client.delete(f"/api/registrations/{reg_id}", headers=headers)
    assert cancel_resp.status_code == 200


def test_e2e_faculty_workflow(client):
    """
    E2E Faculty Workflow:
    Login -> Create event -> Set limit -> View participants -> Close registration
    """
    # 1. Login
    login_resp = client.post("/api/auth/login", json={"email": "fac_a@test.edu", "password": "FacultyPass123"})
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create event with participant limit
    event_payload = {
        "title": "Faculty End-to-End Cybersecurity Showcase",
        "description": "Comprehensive demonstration of secure software architecture.",
        "category": "Security",
        "venue": "Digital Lab 5",
        "event_date": "2026-12-15",
        "start_time": "11:00",
        "end_time": "14:00",
        "participant_limit": 15,
        "registration_deadline": "2026-12-14T23:59:59"
    }
    create_resp = client.post("/api/events", json=event_payload, headers=headers)
    assert create_resp.status_code == 201
    created_event_id = create_resp.json()["id"]

    # 3. View participants
    parts_resp = client.get(f"/api/events/{created_event_id}/participants", headers=headers)
    assert parts_resp.status_code == 200
    assert len(parts_resp.json()) == 0  # No participants registered yet

    # 4. Close registration
    close_resp = client.post(f"/api/events/{created_event_id}/close", headers=headers)
    assert close_resp.status_code == 200
    assert close_resp.json()["status"] == EventStatus.CLOSED.value


def test_e2e_admin_workflow(client):
    """
    E2E Admin Workflow:
    Login -> View users/events -> View audit logs -> View system stats
    """
    # 1. Login
    login_resp = client.post("/api/auth/login", json={"email": "admin@test.edu", "password": "AdminPass123"})
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. View users
    users_resp = client.get("/api/admin/users", headers=headers)
    assert users_resp.status_code == 200
    assert len(users_resp.json()) >= 5

    # 3. View events oversight
    events_resp = client.get("/api/admin/events", headers=headers)
    assert events_resp.status_code == 200
    assert len(events_resp.json()) >= 3

    # 4. View system statistics
    stats_resp = client.get("/api/admin/stats", headers=headers)
    assert stats_resp.status_code == 200
    stats = stats_resp.json()
    assert "total_users" in stats
    assert "total_events" in stats

    # 5. View security audit logs
    audits_resp = client.get("/api/admin/audit-logs", headers=headers)
    assert audits_resp.status_code == 200
    assert len(audits_resp.json()) > 0
