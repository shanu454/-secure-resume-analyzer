"""Estimate years of experience from date ranges in a resume."""
import re
from datetime import date

from app.services.sections import parse_sections

_MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}
_MONTH_NAMES = (
    r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|"
    r"aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
)
_YEAR = r"(?:19|20)\d{2}"
_DATE = rf"(?:{_MONTH_NAMES}\.?,?\s+{_YEAR}|(?:0?[1-9]|1[0-2])[/.]{_YEAR}|{_YEAR})"
_PRESENT = r"present|current|now|ongoing|till date|to date|today"
_RANGE = re.compile(
    rf"(?<![\w/.])({_DATE})\s*(?:-|–|—|to|until|till)\s*({_DATE}|{_PRESENT})(?![\w/])",
    re.IGNORECASE,
)
_EDUCATION_WORDS = re.compile(
    r"\b(university|college|school|b\.?tech|m\.?tech|b\.?sc|m\.?sc|bachelor|master|ph\.?d|diploma|degree|cgpa|gpa)\b",
    re.IGNORECASE,
)
# "5+ years of (relevant) experience" and "experience: 5 years" - the number must sit
# close to the word "experience" within the same sentence.
_YEARS_THEN_EXP = re.compile(
    r"(\d{1,2})\s*\+?\s*(?:years?|yrs?)\b[^.\n]{0,40}?\bexperience", re.IGNORECASE
)
_EXP_THEN_YEARS = re.compile(
    r"\bexperience\b[^.\n\d]{0,30}?(\d{1,2})\s*\+?\s*(?:years?|yrs?)\b", re.IGNORECASE
)


def _month_index(token: str, today: date) -> int:
    token = token.strip().lower()
    if re.fullmatch(_PRESENT, token):
        return today.year * 12 + today.month - 1
    year = int(re.search(_YEAR, token).group(0))  # type: ignore[union-attr]
    month = 6  # no month given: use mid-year so the estimate is not biased either way
    named = re.match(r"([a-z]{3})", token)
    if named and named.group(1) in _MONTHS:
        month = _MONTHS[named.group(1)]
    else:
        numeric = re.match(r"(\d{1,2})[/.]", token)
        if numeric:
            month = int(numeric.group(1))
    return year * 12 + month - 1


def _experience_text(text: str) -> str:
    sections = parse_sections(text)
    chosen = [s for s in sections if s.kind == "experience"]
    if chosen:
        return "\n".join("\n".join(s.lines) for s in chosen)
    # No recognisable experience heading: use everything except education-looking lines.
    lines = [ln for s in sections for ln in s.lines if not _EDUCATION_WORDS.search(ln)]
    return "\n".join(lines)


def estimate_years(text: str, today: date | None = None) -> float | None:
    today = today or date.today()
    intervals: list[tuple[int, int]] = []
    for m in _RANGE.finditer(_experience_text(text)):
        start, end = _month_index(m.group(1), today), _month_index(m.group(2), today)
        if end < start or (end - start) > 12 * 50:
            continue
        if start > today.year * 12 + today.month - 1 + 12:
            continue
        intervals.append((start, end))
    if not intervals:
        return None
    intervals.sort()
    merged = [intervals[0]]
    for s, e in intervals[1:]:
        last_s, last_e = merged[-1]
        if s <= last_e:
            merged[-1] = (last_s, max(last_e, e))
        else:
            merged.append((s, e))
    months = sum(e - s for s, e in merged)
    return round(months / 12, 1)


def required_years(jd_text: str) -> int | None:
    """Highest 'N years ... experience' figure in the job description."""
    found = []
    for pattern in (_YEARS_THEN_EXP, _EXP_THEN_YEARS):
        found += [int(n) for n in pattern.findall(jd_text)]
    found = [n for n in found if 0 < n <= 40]
    return max(found) if found else None
