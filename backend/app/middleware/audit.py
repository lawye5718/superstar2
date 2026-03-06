"""Audit logging helpers — record admin/sensitive operations."""

import logging
from typing import Optional
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def log_action(
    db: Session,
    action_type: str,
    actor_user_id: Optional[str] = None,
    details: Optional[dict] = None,
) -> None:
    """Append an entry to the audit_log table.

    Parameters
    ----------
    db:             Active synchronous SQLAlchemy session.
    action_type:    Short string identifying the action (e.g. "user.delete",
                    "admin.credits_update").
    actor_user_id:  ID of the user performing the action; None for system events.
    details:        Arbitrary JSON-serialisable dict with extra context.
    """
    try:
        from app.models.database import AuditLog

        entry = AuditLog(
            actor_user_id=actor_user_id,
            action_type=action_type,
            details=details or {},
        )
        db.add(entry)
        db.flush()  # persist within the caller's transaction; caller commits
    except Exception:
        # Audit failures must never break the main request
        logger.exception("Failed to write audit log entry: action=%s", action_type)
