"""Compare a resume with a job description and build the report."""
from datetime import date

from app.schemas.report import (
    AnalysisReport,
    ExperienceInfo,
    ResumeSkill,
    SkillMatch,
)
from app.services.experience import estimate_years, required_years
from app.services.jd import classify_skills
from app.services.keywords import missing_keywords
from app.services.sections import parse_sections
from app.services.skills import extract_skills, get_taxonomy

REQUIRED_WEIGHT = 2
PREFERRED_WEIGHT = 1
MAX_RELEVANT_LINES = 8
MAX_LINE_CHARS = 220


def _pct(part: int, whole: int) -> float | None:
    return round(100 * part / whole, 1) if whole else None


def _relevant_lines(resume_text: str, wanted: set[str]) -> list[str]:
    scored: list[tuple[int, int, str]] = []
    order = 0
    for section in parse_sections(resume_text):
        if section.kind in {"skills", "education"}:
            continue
        for line in section.lines:
            order += 1
            if len(line) < 25:
                continue
            hits = len(wanted & set(extract_skills(line)))
            if hits:
                scored.append((-hits, order, line[:MAX_LINE_CHARS]))
    scored.sort()
    return [line for _, _, line in scored[:MAX_RELEVANT_LINES]]


def analyze(resume_text: str, jd_text: str, today: date | None = None) -> AnalysisReport:
    taxonomy = get_taxonomy()
    warnings: list[str] = []

    resume_skills = extract_skills(resume_text)
    required, preferred = classify_skills(jd_text)

    if not required and not preferred:
        warnings.append(
            "No known skills were found in the job description, so the score is 0. "
            "Check that the full description was pasted."
        )
    if not resume_skills:
        warnings.append("No known skills were found in the resume.")

    def item(name: str, importance: str) -> SkillMatch:
        return SkillMatch(name=name, category=taxonomy.skills[name].category, importance=importance)  # type: ignore[arg-type]

    matched = [item(s, "required") for s in required if s in resume_skills]
    matched += [item(s, "preferred") for s in preferred if s in resume_skills]
    missing = [item(s, "required") for s in required if s not in resume_skills]
    missing += [item(s, "preferred") for s in preferred if s not in resume_skills]

    req_hit = sum(1 for m in matched if m.importance == "required")
    pref_hit = sum(1 for m in matched if m.importance == "preferred")
    total_weight = REQUIRED_WEIGHT * len(required) + PREFERRED_WEIGHT * len(preferred)
    got_weight = REQUIRED_WEIGHT * req_hit + PREFERRED_WEIGHT * pref_hit
    score = round(100 * got_weight / total_weight, 1) if total_weight else 0.0

    jd_all = set(required) | set(preferred)
    additional = [
        ResumeSkill(name=s, category=taxonomy.skills[s].category)
        for s in resume_skills
        if s not in jd_all
    ]

    est = estimate_years(resume_text, today)
    need = required_years(jd_text)
    meets = None if est is None or need is None else est >= need
    if est is None:
        warnings.append("Could not find dated work-experience ranges in the resume.")

    return AnalysisReport(
        match_score=score,
        required_coverage=_pct(req_hit, len(required)),
        preferred_coverage=_pct(pref_hit, len(preferred)),
        matched_skills=matched,
        missing_skills=missing,
        additional_skills=additional,
        missing_keywords=missing_keywords(jd_text, resume_text),
        experience=ExperienceInfo(estimated_years=est, required_years=need, meets_requirement=meets),
        relevant_experience=_relevant_lines(resume_text, set(resume_skills) & jd_all),
        warnings=warnings,
    )
