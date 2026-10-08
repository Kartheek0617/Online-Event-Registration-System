import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.core.config import settings
from backend.app.db.base import Base
from backend.app.db.session import get_db
from backend.app.models.user import User, UserRole
from backend.app.models.event import Event, EventStatus
from backend.app.models.registration import Registration, RegistrationStatus
from backend.app.core.security import hash_password, create_access_token

# Configure environment for testing
settings.ENVIRONMENT = "test"

# Use in-memory SQLite with StaticPool so all threads share the exact same in-memory DB
TEST_DATABASE_URL = "sqlite:///:memory:"
engine_test = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

# Precomputed hashes for test speed
ADMIN_HASH = hash_password("AdminPass123")
FACULTY_HASH = hash_password("FacultyPass123")
STUDENT_HASH = hash_password("StudentPass123")


@pytest.fixture(scope="function")
def db_session():
    """Provides a clean database schema and test data for each test."""
    Base.metadata.create_all(bind=engine_test)
    session = TestingSessionLocal()

    # Pre-populate test users
    admin = User(
        name="Admin Test",
        email="admin@test.edu",
        password_hash=ADMIN_HASH,
        role=UserRole.ADMIN,
        is_active=True
    )
    fac_a = User(
        name="Faculty A",
        email="fac_a@test.edu",
        password_hash=FACULTY_HASH,
        role=UserRole.FACULTY,
        is_active=True
    )
    fac_b = User(
        name="Faculty B",
        email="fac_b@test.edu",
        password_hash=FACULTY_HASH,
        role=UserRole.FACULTY,
        is_active=True
    )
    stud_a = User(
        name="Student A",
        email="stud_a@test.edu",
        password_hash=STUDENT_HASH,
        role=UserRole.STUDENT,
        is_active=True
    )
    stud_b = User(
        name="Student B",
        email="stud_b@test.edu",
        password_hash=STUDENT_HASH,
        role=UserRole.STUDENT,
        is_active=True
    )
    session.add_all([admin, fac_a, fac_b, stud_a, stud_b])
    session.commit()

    # Create initial events
    event_fac_a = Event(
        organizer_id=fac_a.id,
        title="Event by Faculty A",
        description="Faculty A event description",
        category="Tech",
        venue="Hall A",
        event_date="2026-11-20",
        start_time="10:00",
        end_time="12:00",
        participant_limit=5,
        registration_deadline="2026-11-19T23:59:59",
        status=EventStatus.OPEN
    )
    event_fac_b = Event(
        organizer_id=fac_b.id,
        title="Event by Faculty B",
        description="Faculty B event description",
        category="Science",
        venue="Hall B",
        event_date="2026-11-21",
        start_time="14:00",
        end_time="16:00",
        participant_limit=1,  # Strictly limited to 1 for overbooking test
        registration_deadline="2026-11-20T23:59:59",
        status=EventStatus.OPEN
    )
    event_closed = Event(
        organizer_id=fac_a.id,
        title="Closed Event",
        description="This event is closed",
        category="Tech",
        venue="Hall C",
        event_date="2026-11-10",
        start_time="10:00",
        end_time="12:00",
        participant_limit=10,
        registration_deadline="2026-11-09T23:59:59",
        status=EventStatus.CLOSED
    )
    session.add_all([event_fac_a, event_fac_b, event_closed])
    session.commit()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine_test)


@pytest.fixture(scope="function")
def client(db_session):
    """TestClient that uses TestingSessionLocal bound to StaticPool in-memory DB."""
    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def get_auth_headers_for_user(user: User) -> dict:
    """Helper to generate Authorization header for test user."""
    token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value, "email": user.email}
    )
    return {"Authorization": f"Bearer {token}"}
