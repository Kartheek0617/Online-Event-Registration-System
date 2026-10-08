from backend.app.models.user import User
from backend.app.models.event import Event, EventStatus
from backend.tests.conftest import get_auth_headers_for_user


def test_public_event_listing_and_filtering(client):
    # Public unauthenticated listing
    resp = client.get("/api/events")
    assert resp.status_code == 200
    events = resp.json()
    assert len(events) >= 3

    # Filter by category
    resp_tech = client.get("/api/events?category=Tech")
    assert resp_tech.status_code == 200
    for e in resp_tech.json():
        assert e["category"] == "Tech"

    # Search by title
    resp_search = client.get("/api/events?search=Faculty A")
    assert resp_search.status_code == 200
    assert len(resp_search.json()) >= 1


def test_faculty_create_and_close_event(client, db_session):
    fac_a = db_session.query(User).filter(User.email == "fac_a@test.edu").first()
    headers_a = get_auth_headers_for_user(fac_a)

    payload = {
        "title": "New Emerging Technologies Workshop",
        "description": "Comprehensive workshop on cloud security and microservices architecture.",
        "category": "Technology",
        "venue": "Lab 4, Innovation Hub",
        "event_date": "2026-11-28",
        "start_time": "10:00",
        "end_time": "13:00",
        "participant_limit": 25,
        "registration_deadline": "2026-11-27T23:59:59"
    }

    create_resp = client.post("/api/events", json=payload, headers=headers_a)
    assert create_resp.status_code == 201
    created_id = create_resp.json()["id"]

    # Close event
    close_resp = client.post(f"/api/events/{created_id}/close", headers=headers_a)
    assert close_resp.status_code == 200
    assert close_resp.json()["status"] == EventStatus.CLOSED.value
