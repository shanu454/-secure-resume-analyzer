import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.api.documents import get_owned_document
from app.core.config import Settings, get_settings
from app.core.rate_limit import rate_limit
from app.database import get_db
from app.models import Analysis, JobDescription, User
from app.schemas.api import AnalysisCreate, AnalysisDetail, AnalysisSummary
from app.schemas.report import AnalysisReport
from app.services import storage
from app.services.analysis import analyze
from app.services.parsing import DocumentParseError, extract_text

router = APIRouter(prefix="/analyses", tags=["analyses"])


def _summary_fields(a: Analysis) -> dict:
    return {
        "id": a.id,
        "document_id": a.document_id,
        "document_filename": a.document.original_filename,
        "job_title": a.job_description.title,
        "match_score": a.match_score,
        "created_at": a.created_at,
    }


def _detail(a: Analysis) -> AnalysisDetail:
    return AnalysisDetail(**_summary_fields(a), report=AnalysisReport.model_validate(a.report))


def _get_owned(db: Session, user: User, analysis_id: uuid.UUID) -> Analysis:
    stmt = (
        select(Analysis)
        .options(joinedload(Analysis.document), joinedload(Analysis.job_description))
        .where(Analysis.id == analysis_id, Analysis.user_id == user.id)
    )
    analysis = db.scalar(stmt)
    if analysis is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Analysis not found")
    return analysis


@router.post(
    "",
    response_model=AnalysisDetail,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit(30, 3600))],
)
def create_analysis(
    body: AnalysisCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> AnalysisDetail:
    document = get_owned_document(db, user, body.document_id)
    expires_at = document.expires_at
    if expires_at.tzinfo is None:  # SQLite returns naive datetimes; they are stored as UTC
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status.HTTP_410_GONE, "This document has expired and will be deleted")
    try:
        data = storage.read_bytes(document.stored_name)
    except FileNotFoundError:
        raise HTTPException(status.HTTP_410_GONE, "The stored file is no longer available") from None
    try:
        resume_text = extract_text(data, document.file_type, settings)
    except DocumentParseError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from None

    report = analyze(resume_text, body.job_description)
    job = JobDescription(user_id=user.id, title=body.job_title, text=body.job_description)
    analysis = Analysis(
        user_id=user.id,
        document=document,
        job_description=job,
        match_score=report.match_score,
        report=report.model_dump(mode="json"),
    )
    db.add(analysis)
    db.commit()
    return _detail(analysis)


@router.get("", response_model=list[AnalysisSummary])
def list_analyses(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AnalysisSummary]:
    stmt = (
        select(Analysis)
        .options(joinedload(Analysis.document), joinedload(Analysis.job_description))
        .where(Analysis.user_id == user.id)
        .order_by(Analysis.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return [AnalysisSummary(**_summary_fields(a)) for a in db.scalars(stmt)]


@router.get("/{analysis_id}", response_model=AnalysisDetail)
def get_analysis(
    analysis_id: uuid.UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> AnalysisDetail:
    return _detail(_get_owned(db, user, analysis_id))


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_analysis(
    analysis_id: uuid.UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Response:
    db.delete(_get_owned(db, user, analysis_id))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
