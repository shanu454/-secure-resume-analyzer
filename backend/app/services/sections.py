"""Split resume text into rough sections based on common headings."""
import re
from dataclasses import dataclass, field

_KINDS = {
    "experience": {
        "experience", "work experience", "professional experience", "employment",
        "employment history", "work history", "relevant experience", "internships",
        "internship experience", "career history",
    },
    "education": {"education", "academic background", "qualifications"},
    "skills": {"skills", "technical skills", "key skills", "core skills", "skills summary", "tech stack"},
    "projects": {"projects", "personal projects", "academic projects", "selected projects"},
    "other": {
        "summary", "profile", "professional summary", "objective", "about me",
        "certifications", "achievements", "awards", "publications", "languages",
        "interests", "references", "volunteering",
    },
}
_HEADING_TO_KIND = {h: kind for kind, hs in _KINDS.items() for h in hs}


@dataclass
class Section:
    name: str
    kind: str
    lines: list[str] = field(default_factory=list)


def heading_kind(line: str) -> str | None:
    cleaned = re.sub(r"[^a-z ]", " ", line.lower())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if len(line) > 40:
        return None
    return _HEADING_TO_KIND.get(cleaned)


def parse_sections(text: str) -> list[Section]:
    sections = [Section("header", "header")]
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        kind = heading_kind(line)
        if kind:
            sections.append(Section(line.rstrip(":").strip().lower(), kind))
        else:
            sections[-1].lines.append(line)
    return sections
