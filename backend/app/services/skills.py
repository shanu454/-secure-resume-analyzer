"""Skill taxonomy and rule-based skill extraction.

Matching is done with one compiled regex per case mode. Boundaries are custom
because \b does not work for tokens like "C++", "C#" or ".NET".
"""
import json
import re
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "skills.json"

# A match must not be glued to other word characters, and must not be the tail
# of a dotted name ("js" inside "node.js").
_BEFORE = r"(?<![A-Za-z0-9+#.])"
_AFTER = r"(?![A-Za-z0-9+#]|\.[A-Za-z0-9])"


@dataclass(frozen=True)
class Skill:
    name: str
    category: str


class SkillTaxonomy:
    def __init__(self, entries: list[dict]):
        self.skills: dict[str, Skill] = {}
        self._insensitive: dict[str, str] = {}  # lowercase alias -> skill name
        self._sensitive: dict[str, str] = {}  # exact alias -> skill name

        for entry in entries:
            skill = Skill(entry["name"], entry["category"])
            if skill.name in self.skills:
                raise ValueError(f"Duplicate skill: {skill.name}")
            self.skills[skill.name] = skill
            sensitive = entry.get("case_sensitive_aliases", [])
            # Ambiguous names ("Go", "Swift") match only with the exact capitalisation.
            own_name = [] if skill.name in sensitive else [skill.name.lower()]
            for alias in {*own_name, *[a.lower() for a in entry.get("aliases", [])]}:
                if alias in self._insensitive and self._insensitive[alias] != skill.name:
                    raise ValueError(f"Alias '{alias}' maps to two skills")
                self._insensitive[alias] = skill.name
            for alias in sensitive:
                self._sensitive[alias] = skill.name

        self._re_insensitive = self._compile(self._insensitive.keys(), re.IGNORECASE)
        self._re_sensitive = self._compile(self._sensitive.keys(), 0)

    @staticmethod
    def _compile(aliases, flags: int) -> re.Pattern | None:
        ordered = sorted(aliases, key=len, reverse=True)  # longest alias wins
        if not ordered:
            return None
        body = "|".join(re.escape(a) for a in ordered)
        return re.compile(f"{_BEFORE}(?:{body}){_AFTER}", flags)

    def extract(self, text: str) -> dict[str, int]:
        """Return {skill name: number of mentions}, in order of first appearance."""
        text = unicodedata.normalize("NFKC", text)
        hits: list[tuple[int, str]] = []
        if self._re_insensitive:
            for m in self._re_insensitive.finditer(text):
                hits.append((m.start(), self._insensitive[m.group(0).lower()]))
        if self._re_sensitive:
            for m in self._re_sensitive.finditer(text):
                hits.append((m.start(), self._sensitive[m.group(0)]))
        counts: dict[str, int] = {}
        for _, name in sorted(hits):
            counts[name] = counts.get(name, 0) + 1
        return counts

    def single_word_aliases(self) -> set[str]:
        return {a for a in self._insensitive if " " not in a}


@lru_cache
def get_taxonomy() -> SkillTaxonomy:
    with DATA_FILE.open(encoding="utf-8") as fh:
        return SkillTaxonomy(json.load(fh)["skills"])


def extract_skills(text: str) -> dict[str, int]:
    return get_taxonomy().extract(text)
