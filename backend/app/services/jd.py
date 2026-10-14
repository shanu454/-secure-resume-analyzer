"""Split job-description skills into 'required' and 'preferred'."""
import re

from app.services.skills import extract_skills

_PREFERRED = re.compile(
    r"nice[- ]to[- ]have|preferred|bonus|a plus|is a plus|are a plus|good to have|"
    r"desirable|optional|advantageous|would be a plus|ideally|an advantage",
    re.IGNORECASE,
)
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")
_BULLET = re.compile(r"^\s*(?:[-*•–·]|\d+[.)])\s*")
_KNOWN_HEADING = re.compile(
    r"^(requirements?|qualifications?|responsibilities|about (the )?(role|team|us|you)|"
    r"what you('|’)ll (do|need)|what we('|’)re looking for|must[- ]haves?|"
    r"nice[- ]to[- ]haves?|preferred( qualifications| skills)?|bonus( points)?|"
    r"required( skills| qualifications)?|key skills|benefits|we offer)\W*$",
    re.IGNORECASE,
)


def _is_heading(line: str) -> bool:
    stripped = line.strip()
    if not stripped or _BULLET.match(stripped) or len(stripped) > 80:
        return False
    if stripped.endswith(":") or _KNOWN_HEADING.match(stripped):
        return True
    # An all-caps line is a heading unless it is really a skill ("AWS", "SQL").
    return stripped.isupper() and not extract_skills(stripped)


def classify_skills(jd_text: str) -> tuple[list[str], list[str]]:
    """Return (required, preferred) skill names, each in order of first appearance.

    A skill is preferred only if every mention sits in a 'preferred' context
    (under a nice-to-have heading, or on a line saying 'a plus', 'bonus', ...).
    """
    mode = "required"
    required: dict[str, None] = {}
    preferred: dict[str, None] = {}
    for line in jd_text.splitlines():
        if not line.strip():
            continue
        if _is_heading(line):
            mode = "preferred" if _PREFERRED.search(line) else "required"
            # A heading like "Preferred: Kafka, Redis" can also carry skills.
        # Markers like "a plus" apply to their own sentence, not the whole line.
        for sentence in _SENTENCE_END.split(line):
            sentence_mode = "preferred" if _PREFERRED.search(sentence) else mode
            for skill in extract_skills(sentence):
                (preferred if sentence_mode == "preferred" else required)[skill] = None
    preferred_only = [s for s in preferred if s not in required]
    return list(required), preferred_only
