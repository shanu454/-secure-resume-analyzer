"""Find frequent job-description words that never appear in the resume."""
import re
from collections import Counter

from app.services.skills import get_taxonomy

_WORD = re.compile(r"[a-z][a-z+#\-]{2,}")

_STOPWORDS = set(
    """
    the and for with that this are you your our will from have has can not but all any one two out who
    what when where how why their they them its use used using such also more most other than then into
    over under about across within without per via able etc including include includes well new best good
    great strong excellent ability abilities skills skill experience experienced years year role roles team
    teams work working works company job position candidate candidates looking join help helps make making
    must should may might would could each both many much very high level based knowledge understanding
    responsibilities requirements required preferred plus bonus nice need needs needed seeking opportunity
    environment business customers customer product products projects project etc develop developing
    development build building design designing support supporting ensure ensuring collaborate collaboration
    communication degree related relevant field equivalent minimum least proven demonstrated familiarity
    familiar hands-on handson part full time salary benefits offer apply application applicants
    """.split()
)


def _stem(word: str) -> str:
    return word[:-1] if word.endswith("s") and len(word) > 4 else word


def missing_keywords(jd_text: str, resume_text: str, limit: int = 10) -> list[str]:
    known_aliases = get_taxonomy().single_word_aliases()
    resume_words = {_stem(w) for w in _WORD.findall(resume_text.lower())}
    counts: Counter[str] = Counter()
    for word in _WORD.findall(jd_text.lower()):
        if word in _STOPWORDS or word in known_aliases:
            continue
        counts[_stem(word)] += 1
    candidates = [(w, n) for w, n in counts.items() if n >= 2 and w not in resume_words]
    candidates.sort(key=lambda item: (-item[1], item[0]))
    return [w for w, _ in candidates[:limit]]
