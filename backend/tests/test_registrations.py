from backend.app.models.user import User
from backend.app.models.event import Event
from backend.app.models.registration import Registration, RegistrationStatus
from backend.tests.conftest import get_auth_headers_for_user


def test_student_register_and_cancel_lifecycle(client, db_session):
    stud_a = db_session.query(User).filter(User.email == "stud_a@test.edu").first()
    event_a = db_session.query(Event).filter(Event.title == "Event by Faculty A").first()
    headers_a = get_auth_headers_for_user(stud_a)

    # 1. Register
    reg_resp = client.post(f"/api/events/{event_a.id}/register", headers=headers_a)
    assert reg_resp.status_code == 201
    reg_data = reg_resp.json()["registration"]
    assert reg_data["status"] == RegistrationStatus.CONFIRMED.value
    reg_id = reg_data["id"]

    # 2. Check event available seats decreased
    ev_resp = client.get(f"/api/events/{event_a.id}", headers=headers_a)
    assert ev_resp.status_code == 200
    assert ev_resp.json()["registered_count"] == 1
    assert ev_resp.json()["is_registered_by_user"] is True

    # 3. View my registrations
    my_regs = client.get("/api/registrations/me", headers=headers_a)
    assert my_regs.status_code == 200
    assert any(r["id"] == reg_id for r in my_regs.json())

    # 4. Cancel registration
    cancel_resp = client.delete(f"/api/registrations/{reg_id}", headers=headers_a)
    assert cancel_resp.status_code == 200

    # 5. Check event available seats restored
    ev_resp_after = client.get(f"/api/events/{event_a.id}", headers=headers_a)
    assert ev_resp_after.json()["registered_count"] == 0
    assert ev_resp_after.json()["is_registered_by_user"] is False
