"""Structured analysis report. Stored as JSON and returned by the API."""
from typing import Literal

from pydantic import BaseModel


class SkillMatch(BaseModel):
    name: str
    category: str
    importance: Literal["required", "preferred"]


class ResumeSkill(BaseModel):
    name: str
    category: str


class ExperienceInfo(BaseModel):
    estimated_years: float | None = None
    required_years: int | None = None
    meets_requirement: bool | None = None


class AnalysisReport(BaseModel):
    report_version: int = 1
    match_score: float
    required_coverage: float | None = None
    preferred_coverage: float | None = None
    matched_skills: list[SkillMatch]
    missing_skills: list[SkillMatch]
    additional_skills: list[ResumeSkill]
    missing_keywords: list[str]
    experience: ExperienceInfo
    relevant_experience: list[str]
    warnings: list[str]
