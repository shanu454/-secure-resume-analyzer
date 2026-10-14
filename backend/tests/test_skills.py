import pytest

from app.services.skills import extract_skills, get_taxonomy


def names(text):
    return set(extract_skills(text))


def test_taxonomy_loads_without_alias_conflicts():
    assert len(get_taxonomy().skills) > 100


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Built services in C++ and C#.", {"C++", "C#"}),
        ("Strong Node.js and React.js skills", {"Node.js", "React"}),
        ("Wrote Java and JavaScript code", {"Java", "JavaScript"}),
        ("I know Java.", {"Java"}),
        ("Used Postgres, Mongo and K8s", {"PostgreSQL", "MongoDB", "Kubernetes"}),
        ("CI/CD pipelines with GitHub Actions", {"CI/CD", "GitHub Actions"}),
        ("Experience with .NET and ASP.NET Core", {".NET", "ASP.NET"}),
        ("scikit-learn, sklearn and PyTorch", {"scikit-learn", "PyTorch"}),
        ("built RAG pipelines with large language models", {"RAG", "LLMs"}),
    ],
)
def test_extraction(text, expected):
    assert expected <= names(text)


def test_js_inside_dotted_names_is_not_javascript():
    assert "JavaScript" not in names("Node.js and Vue.js developer")
    assert "JavaScript" in names("Knows js and Node.js")


def test_substrings_are_not_matched():
    assert names("javascripty rusty swiftly cassandras") == set()
    assert "Java" not in names("javascript only")
    assert "Rust" not in names("trustworthy and frustrating")


def test_case_sensitive_aliases_for_ambiguous_words():
    assert "Go" in names("Languages: Go, Rust")
    assert "Go" not in names("we want people who go above and beyond")
    assert "Swift" in names("iOS developer using Swift")
    assert "Swift" not in names("swift delivery of projects")


def test_counts_mentions():
    assert extract_skills("Python python PYTHON")["Python"] == 3


def test_longest_alias_wins():
    found = extract_skills("Ruby on Rails")
    assert "Ruby on Rails" in found
