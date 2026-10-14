"""File-retention and deletion behaviour.

* Every document gets an `expires_at` (upload time + RETENTION_DAYS).
* A background sweep deletes expired files, their analyses and the stored job
  descriptions. Deleting a document by hand does the same immediately.
"""
import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.database import SessionLocal
from app.models import Document
from app.services import storage

log = logging.getLogger(__name__)


def delete_document(db: Session, document: Document) -> None:
    """Delete the file first, then the rows (analyses cascade)."""
    storage.delete(document.stored_name)
    db.delete(document)


def purge_expired(db: Session, now: datetime | None = None) -> int:
    now = now or datetime.now(timezone.utc)
    expired = db.scalars(select(Document).where(Document.expires_at <= now)).all()
    for document in expired:
        delete_document(db, document)
    db.commit()
    return len(expired)


def _sweep_once() -> int:
    with SessionLocal() as db:
        return purge_expired(db)


async def sweep_loop() -> None:
    interval = get_settings().retention_sweep_interval_seconds
    while True:
        try:
            removed = await asyncio.to_thread(_sweep_once)
            if removed:
                log.info("retention sweep removed %d expired documents", removed)
        except Exception as exc:  # keep the loop alive; log the type only
            log.error("retention sweep failed: %s", type(exc).__name__)
        await asyncio.sleep(interval)
