import hashlib
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import Settings, get_settings
from app.core.rate_limit import rate_limit
from app.database import get_db
from app.models import Document, User
from app.schemas.api import DocumentOut
from app.services import storage
from app.services.file_validation import (
    ALLOWED_EXTENSIONS,
    UploadValidationError,
    sanitize_filename,
    validate_upload,
)
from app.services.parsing import DocumentParseError, extract_text
from app.services.retention import delete_document

router = APIRouter(prefix="/documents", tags=["documents"])

_CHUNK = 64 * 1024


def get_owned_document(db: Session, user: User, document_id: uuid.UUID) -> Document:
    """Return the document if it belongs to the user, else 404 (never 403)."""
    document = db.scalar(
        select(Document).where(Document.id == document_id, Document.user_id == user.id)
    )
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
    return document


def _read_limited(upload: UploadFile, limit: int) -> bytes:
    """Read the upload in chunks and stop as soon as it exceeds the limit."""
    buf = bytearray()
    while chunk := upload.file.read(_CHUNK):
        buf += chunk
        if len(buf) > limit:
            raise UploadValidationError(f"File is larger than {limit // (1024 * 1024)} MB.", 413)
    return bytes(buf)


@router.post(
    "",
    response_model=DocumentOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit(20, 3600))],
)
def upload_document(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Document:
    count = db.scalar(select(func.count()).select_from(Document).where(Document.user_id == user.id))
    if (count or 0) >= settings.max_documents_per_user:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"Document limit reached ({settings.max_documents_per_user}). Delete one first.",
        )

    display_name = sanitize_filename(file.filename)
    try:
        data = _read_limited(file, settings.max_upload_bytes)
        file_type = validate_upload(display_name, data, settings)
        extract_text(data, file_type, settings)  # reject unreadable files up front; text is discarded
    except UploadValidationError as exc:
        raise HTTPException(exc.status_code, exc.message) from None
    except DocumentParseError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from None

    stored_name = storage.save_bytes(data)
    now = datetime.now(timezone.utc)
    document = Document(
        user_id=user.id,
        original_filename=display_name,
        stored_name=stored_name,
        file_type=file_type,
        size_bytes=len(data),
        sha256=hashlib.sha256(data).hexdigest(),
        uploaded_at=now,
        expires_at=now + timedelta(days=settings.retention_days),
    )
    db.add(document)
    try:
        db.commit()
    except Exception:
        db.rollback()
        storage.delete(stored_name)  # do not leave an orphan file behind
        raise
    return document


@router.get("", response_model=list[DocumentOut])
def list_documents(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[Document]:
    stmt = select(Document).where(Document.user_id == user.id).order_by(Document.uploaded_at.desc())
    return list(db.scalars(stmt))


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(
    document_id: uuid.UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Document:
    return get_owned_document(db, user, document_id)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_document(
    document_id: uuid.UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Response:
    """Deletes the file and every analysis made from it."""
    document = get_owned_document(db, user, document_id)
    delete_document(db, document)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


__all__ = ["router", "get_owned_document", "ALLOWED_EXTENSIONS"]
