from datetime import date

from app.services.analysis import analyze
from app.services.experience import estimate_years, required_years
from app.services.jd import classify_skills
from app.services.keywords import missing_keywords
from tests.conftest import JOB_DESCRIPTION, RESUME_TEXT

TODAY = date(2026, 1, 15)


def test_jd_required_vs_preferred():
    required, preferred = classify_skills(JOB_DESCRIPTION)
    assert {"Python", "FastAPI", "PostgreSQL", "Docker", "Kubernetes"} <= set(required)
    assert set(preferred) == {"Kafka", "Terraform"}


def test_inline_plus_marker_makes_skill_preferred():
    required, preferred = classify_skills("Must know Python.\nExperience with Redis is a plus.")
    assert required == ["Python"] and preferred == ["Redis"]


def test_skill_in_both_places_stays_required():
    required, preferred = classify_skills("Requirements:\nPython\nNice to have:\nPython, Redis")
    assert "Python" in required and "Python" not in preferred
    assert preferred == ["Redis"]


def test_full_report():
    report = analyze(RESUME_TEXT, JOB_DESCRIPTION, today=TODAY)
    matched = {s.name for s in report.matched_skills}
    missing = {s.name: s.importance for s in report.missing_skills}
    assert {"Python", "FastAPI", "PostgreSQL", "Docker"} <= matched
    assert missing == {"Kubernetes": "required", "Kafka": "preferred", "Terraform": "preferred"}
    # required: 4 of 5 matched (weight 2) ; preferred: 0 of 2  -> 8 / (10 + 2)
    assert report.match_score == 66.7
    assert report.required_coverage == 80.0
    assert report.preferred_coverage == 0.0
    assert "Git" in {s.name for s in report.additional_skills}
    assert report.experience.estimated_years == 3.2
    assert report.experience.required_years == 3
    assert report.experience.meets_requirement is True
    assert any("FastAPI" in line for line in report.relevant_experience)
    assert not any(line.startswith("Python, SQL") for line in report.relevant_experience)


def test_perfect_and_zero_scores():
    assert analyze("I use Python and Docker daily at work.", "Requirements: Python, Docker").match_score == 100.0
    assert analyze("I paint landscapes.", "Requirements: Python, Docker").match_score == 0.0


def test_unrecognised_job_description_gives_warning_not_crash():
    report = analyze(RESUME_TEXT, "We are a friendly company that likes snacks and long walks outside.")
    assert report.match_score == 0.0
    assert any("job description" in w.lower() for w in report.warnings)


def test_experience_years():
    text = "EXPERIENCE\nDev, A  Jan 2018 - Jan 2020\nDev, B  Jun 2019 - Jun 2021\n"
    assert estimate_years(text, TODAY) == 3.4  # overlapping ranges are merged: Jan 2018 - Jun 2021
    assert estimate_years("EXPERIENCE\nDev  2020 - Present", TODAY) == 5.6  # year-only start = mid-year
    assert estimate_years("EXPERIENCE\nDev  03/2021 - 09/2021", TODAY) == 0.5
    assert estimate_years("no dates here at all", TODAY) is None


def test_education_dates_are_ignored_without_experience_heading():
    text = "B.Tech, State University 2012 - 2016\nDeveloper at Acme 2018 - 2020"
    assert estimate_years(text, TODAY) == 2.0


def test_required_years_from_jd():
    assert required_years("5+ years of experience with Python") == 5
    assert required_years("3-5 years experience") == 5
    assert required_years("We value experience. Free coffee for 10 years.") is None


def test_missing_keywords():
    jd = "We need payments expertise. Payments systems and ledger design. Ledger knowledge helps. Python."
    resume = "I know Python and databases."
    assert missing_keywords(jd, resume) == ["ledger", "payment"] or missing_keywords(jd, resume) == ["payment", "ledger"]
    assert "python" not in missing_keywords(jd, resume)


def test_uppercase_skill_line_is_not_a_heading():
    required, preferred = classify_skills("Nice to have:\nDocker\nAWS\nKubernetes")
    assert required == [] and preferred == ["Docker", "AWS", "Kubernetes"]


def test_preferred_marker_applies_to_its_own_sentence_only():
    required, preferred = classify_skills("We need SQL and Tableau experience. Knowledge of Python is desirable.")
    assert required == ["SQL", "Tableau"] and preferred == ["Python"]


def test_ml_abbreviation_is_recognised_but_not_lowercase_ml():
    from app.services.skills import extract_skills

    assert "Machine Learning" in extract_skills("Built ML models")
    assert "Machine Learning" not in extract_skills("add 5 ml of water")
