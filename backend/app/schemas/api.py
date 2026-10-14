"""Request and response models for the HTTP API."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.report import AnalysisReport


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def _lower(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("password")
    @classmethod
    def _not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Password cannot be blank")
        return v


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    email: EmailStr
    created_at: datetime


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    original_filename: str
    file_type: str
    size_bytes: int
    uploaded_at: datetime
    expires_at: datetime


class AnalysisCreate(BaseModel):
    document_id: uuid.UUID
    job_title: str | None = Field(default=None, max_length=200)
    job_description: str = Field(min_length=30, max_length=20_000)

    @field_validator("job_description")
    @classmethod
    def _strip(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 30:
            raise ValueError("Job description is too short")
        return v

    @field_validator("job_title")
    @classmethod
    def _title(cls, v: str | None) -> str | None:
        return v.strip() or None if v else None


class AnalysisSummary(BaseModel):
    id: uuid.UUID
    document_id: uuid.UUID
    document_filename: str
    job_title: str | None
    match_score: float
    created_at: datetime


class AnalysisDetail(AnalysisSummary):
    report: AnalysisReport
