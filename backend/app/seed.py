import logging
from datetime import datetime, timezone
from backend.app.db.session import SessionLocal, init_db
from backend.app.core.security import hash_password
from backend.app.models.user import User, UserRole
from backend.app.models.event import Event, EventStatus
from backend.app.models.registration import Registration, RegistrationStatus
from backend.app.models.audit_log import AuditLog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed")


def seed_database():
    """Populates the database with safe, structured demo data."""
    init_db()
    db = SessionLocal()

    try:
        # Check if users already exist
        if db.query(User).count() > 0:
            logger.info("Database already seeded with initial records. Skipping.")
            return

        logger.info("Seeding users...")
        users = [
            User(
                name="System Administrator",
                email="admin@college.edu",
                password_hash=hash_password("Admin@Secure123"),
                role=UserRole.ADMIN,
                is_active=True
            ),
            User(
                name="Dr. Ramesh Sharma",
                email="faculty.sharma@college.edu",
                password_hash=hash_password("Faculty@Secure123"),
                role=UserRole.FACULTY,
                is_active=True
            ),
            User(
                name="Prof. Priya Patel",
                email="faculty.patel@college.edu",
                password_hash=hash_password("Faculty@Secure123"),
                role=UserRole.FACULTY,
                is_active=True
            ),
            User(
                name="Aarav Kumar",
                email="student.aarav@college.edu",
                password_hash=hash_password("Student@Secure123"),
                role=UserRole.STUDENT,
                is_active=True
            ),
            User(
                name="Ananya Singh",
                email="student.ananya@college.edu",
                password_hash=hash_password("Student@Secure123"),
                role=UserRole.STUDENT,
                is_active=True
            ),
            User(
                name="Rohan Verma",
                email="student.rohan@college.edu",
                password_hash=hash_password("Student@Secure123"),
                role=UserRole.STUDENT,
                is_active=True
            ),
        ]
        db.add_all(users)
        db.commit()

        # Retrieve inserted users for IDs
        admin = db.query(User).filter(User.email == "admin@college.edu").first()
        f_sharma = db.query(User).filter(User.email == "faculty.sharma@college.edu").first()
        f_patel = db.query(User).filter(User.email == "faculty.patel@college.edu").first()
        s_aarav = db.query(User).filter(User.email == "student.aarav@college.edu").first()
        s_ananya = db.query(User).filter(User.email == "student.ananya@college.edu").first()
        s_rohan = db.query(User).filter(User.email == "student.rohan@college.edu").first()

        logger.info("Seeding realistic college events...")
        events = [
            Event(
                organizer_id=f_sharma.id,
                title="Cybersecurity Awareness Workshop",
                description="Comprehensive hands-on workshop covering OWASP Top 10, network defense, threat modeling, and defensive coding practices.",
                category="Cybersecurity",
                venue="Auditorium A, CS Block",
                event_date="2026-11-15",
                start_time="10:00",
                end_time="13:00",
                participant_limit=50,
                registration_deadline="2026-11-14T23:59:59",
                status=EventStatus.OPEN
            ),
            Event(
                organizer_id=f_patel.id,
                title="AI Innovation Hackathon 2026",
                description="24-hour inter-departmental hackathon focused on building generative AI and autonomous agent applications for social impact.",
                category="Artificial Intelligence",
                venue="Innovation Center Lab 3",
                event_date="2026-11-20",
                start_time="09:00",
                end_time="18:00",
                participant_limit=30,
                registration_deadline="2026-11-19T23:59:59",
                status=EventStatus.OPEN
            ),
            Event(
                organizer_id=f_sharma.id,
                title="Web Development Bootcamp",
                description="Intensive bootcamp covering full-stack architecture with React, TypeScript, FastAPI, and containerized microservices.",
                category="Web Engineering",
                venue="Seminar Hall 2",
                event_date="2026-11-25",
                start_time="14:00",
                end_time="17:00",
                participant_limit=40,
                registration_deadline="2026-11-24T23:59:59",
                status=EventStatus.OPEN
            ),
            Event(
                organizer_id=f_patel.id,
                title="Annual College Cultural Fest",
                description="Celebration of talent featuring music, drama, dance competitions, and cultural exhibitions.",
                category="Cultural",
                venue="Open Air Amphitheatre",
                event_date="2026-12-05",
                start_time="17:00",
                end_time="22:00",
                participant_limit=150,
                registration_deadline="2026-12-04T23:59:59",
                status=EventStatus.OPEN
            ),
            Event(
                organizer_id=f_sharma.id,
                title="National Technical Symposium",
                description="Academic research paper presentation, coding competitions, and panel discussions with industry technology leaders.",
                category="Symposium",
                venue="Convention Hall Main",
                event_date="2026-12-12",
                start_time="09:30",
                end_time="16:30",
                participant_limit=60,
                registration_deadline="2026-12-11T23:59:59",
                status=EventStatus.OPEN
            ),
            Event(
                organizer_id=f_sharma.id,
                title="Advanced Robotics Seminar [Closed]",
                description="Specialized seminar on ROS2 and autonomous robotics. Registration is now closed.",
                category="Robotics",
                venue="Robotics Lab 1",
                event_date="2026-11-10",
                start_time="11:00",
                end_time="13:00",
                participant_limit=20,
                registration_deadline="2026-11-09T23:59:59",
                status=EventStatus.CLOSED
            ),
            Event(
                organizer_id=f_patel.id,
                title="Micro Quantum Computing Seminar [Full]",
                description="Intimate round-table discussion on quantum cryptography. Strictly limited to 2 participants.",
                category="Quantum",
                venue="Conference Room C",
                event_date="2026-11-18",
                start_time="15:00",
                end_time="17:00",
                participant_limit=2,
                registration_deadline="2026-11-17T23:59:59",
                status=EventStatus.OPEN
            ),
        ]
        db.add_all(events)
        db.commit()

        cyber_ev = db.query(Event).filter(Event.title.like("%Cybersecurity%")).first()
        hack_ev = db.query(Event).filter(Event.title.like("%AI Innovation%")).first()
        full_ev = db.query(Event).filter(Event.title.like("%Micro Quantum%")).first()

        logger.info("Seeding initial registrations...")
        registrations = [
            Registration(
                event_id=cyber_ev.id,
                student_id=s_aarav.id,
                status=RegistrationStatus.CONFIRMED
            ),
            Registration(
                event_id=hack_ev.id,
                student_id=s_ananya.id,
                status=RegistrationStatus.CONFIRMED
            ),
            # Fill the Micro Quantum event to test capacity limits
            Registration(
                event_id=full_ev.id,
                student_id=s_aarav.id,
                status=RegistrationStatus.CONFIRMED
            ),
            Registration(
                event_id=full_ev.id,
                student_id=s_ananya.id,
                status=RegistrationStatus.CONFIRMED
            ),
        ]
        db.add_all(registrations)

        # Initial audit log
        audit = AuditLog(
            actor_id=admin.id,
            action="SYSTEM_INIT_SEED",
            entity_type="SYSTEM",
            entity_id=1,
            source_ip="127.0.0.1",
            result="SUCCESS",
            metadata_json='{"status": "Database initialized with secure demo data"}'
        )
        db.add(audit)
        db.commit()
        logger.info("Seed data successfully injected into database.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
