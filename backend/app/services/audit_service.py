import json
import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.audit_log import AuditLog

logger = logging.getLogger("security_audit")


class AuditService:
    @staticmethod
    def log_event(
        db: Session,
        action: str,
        entity_type: str,
        actor_id: Optional[int] = None,
        entity_id: Optional[int] = None,
        source_ip: Optional[str] = None,
        result: str = "SUCCESS",
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """
        Record a security audit log entry.
        Never stores passwords, authorization tokens, or sensitive payload secrets.
        """
        clean_metadata = None
        if metadata:
            sanitized = {}
            for k, v in metadata.items():
                # Filter out any sensitive keys
                if any(sec in k.lower() for sec in ["pass", "token", "secret", "auth", "cred"]):
                    continue
                sanitized[k] = str(v)
            clean_metadata = json.dumps(sanitized)

        log_entry = AuditLog(
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            source_ip=source_ip,
            result=result,
            metadata_json=clean_metadata
        )
        try:
            db.add(log_entry)
            db.commit()
            db.refresh(log_entry)
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to record audit log: {e}")

        logger.info(
            f"AUDIT: action={action} actor_id={actor_id} entity={entity_type}:{entity_id} "
            f"result={result} ip={source_ip}"
        )
        return log_entry
