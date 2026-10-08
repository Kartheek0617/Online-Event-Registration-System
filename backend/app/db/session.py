import logging
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from backend.app.core.config import settings
from backend.app.db.base import Base

# Ensure all models are imported so Base.metadata knows about them
from backend.app.models.user import User
from backend.app.models.event import Event
from backend.app.models.registration import Registration
from backend.app.models.audit_log import AuditLog

logger = logging.getLogger("database")

def create_db_engine():
    """Initializes database engine with PostgreSQL or SQLite fallback."""
    db_url = settings.DATABASE_URL
    try:
        if db_url.startswith("postgresql"):
            test_engine = create_engine(
                db_url,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
                connect_args={"connect_timeout": 3}
            )
            # Test connectivity
            with test_engine.connect() as conn:
                conn.execute(select(1))
            logger.info("Successfully connected to primary PostgreSQL database.")
            return test_engine
        else:
            return create_engine(db_url, connect_args={"check_same_thread": False})
    except Exception as e:
        if settings.USE_SQLITE_IF_PG_UNAVAILABLE:
            logger.warning(
                f"PostgreSQL connection to {db_url} failed ({e}). "
                f"Falling back to local SQLite database at {settings.SQLITE_TEST_DB}."
            )
            return create_engine(
                settings.SQLITE_TEST_DB,
                connect_args={"check_same_thread": False}
            )
        raise e


engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI database session dependency."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
