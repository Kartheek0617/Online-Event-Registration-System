from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.db.session import get_db

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check(response: Response, db: Session = Depends(get_db)):
    """Liveness and readiness probe for container orchestrators (Kubernetes / Docker)."""
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "UP" if db_status == "healthy" else "DOWN",
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "Online Event Registration System"
    }
