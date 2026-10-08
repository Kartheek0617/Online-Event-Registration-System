import pytest
from backend.app.models.user import User
from backend.app.models.event import Event
from backend.tests.conftest import get_auth_headers_for_user


def test_fuzzing_event_creation_boundaries(client, db_session):
    """Fuzzing input boundaries for event creation."""
    fac_a = db_session.query(User).filter(User.email == "fac_a@test.edu").first()
    headers = get_auth_headers_for_user(fac_a)

    base_payload = {
        "title": "Boundary Test Event",
        "description": "Standard description for testing",
        "category": "Testing",
        "venue": "Test Venue",
        "event_date": "2026-11-20",
        "start_time": "10:00",
        "end_time": "12:00",
        "participant_limit": 10,
        "registration_deadline": "2026-11-19T23:59:59"
    }

    test_cases = [
        # 1. Empty title
        ({"title": ""}, 422),
        # 2. Whitespace-only title
        ({"title": "     "}, 422),
        # 3. Super long title (> 200 chars)
        ({"title": "A" * 250}, 422),
        # 4. Zero participant limit
        ({"participant_limit": 0}, 422),
        # 5. Negative participant limit
        ({"participant_limit": -100}, 422),
        # 6. Absurdly large integer (> 10000)
        ({"participant_limit": 99999999}, 422),
        # 7. Unexpected string type for integer
        ({"participant_limit": "not_a_number"}, 422),
        # 8. Empty description
        ({"description": ""}, 422),
        # 9. Super long description (> 4000 chars)
        ({"description": "D" * 5000}, 422),
        # 10. Null/None values for required fields
        ({"venue": None}, 422),
    ]

    for override, expected_status in test_cases:
        fuzzed_payload = {**base_payload, **override}
        resp = client.post("/api/events", json=fuzzed_payload, headers=headers)
        assert resp.status_code == expected_status, f"Fuzzing failed for case {override}: got {resp.status_code}"
        assert "detail" in resp.json()


def test_fuzzing_event_id_path_parameters(client, db_session):
    """Fuzzing event ID path parameter boundaries."""
    stud_a = db_session.query(User).filter(User.email == "stud_a@test.edu").first()
    headers = get_auth_headers_for_user(stud_a)

    fuzz_ids = [
        "-1",
        "0",
        "999999999",
        "NaN",
        "true",
        "%20",
        "<script>alert(1)</script>",
        "../../etc/passwd",
        "SELECT*FROM",
    ]

    for fid in fuzz_ids:
        # Test GET /api/events/{fid}
        resp_get = client.get(f"/api/events/{fid}")
        assert resp_get.status_code in [404, 422], f"GET /api/events/{fid} returned unexpected {resp_get.status_code}"

        # Test POST /api/events/{fid}/register
        resp_post = client.post(f"/api/events/{fid}/register", headers=headers)
        assert resp_post.status_code in [404, 422], f"POST register/{fid} returned unexpected {resp_post.status_code}"
