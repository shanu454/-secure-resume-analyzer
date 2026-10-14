import io
import os

# Must be set before the app is imported.
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ["RETENTION_SWEEP_ENABLED"] = "false"
os.environ["ENVIRONMENT"] = "dev"

import pytest  # noqa: E402
from docx import Document as DocxDocument  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from reportlab.pdfgen import canvas  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.core.rate_limit import reset_all_limiters  # noqa: E402
from app.database import Base, get_db, make_engine  # noqa: E402
from app.main import app  # noqa: E402

RESUME_LINES = [
    "Jane Doe",
    "SUMMARY",
    "Backend developer who ships reliable services.",
    "EXPERIENCE",
    "Software Engineer, Acme Corp  Jan 2020 - Mar 2023",
    "- Built REST APIs with FastAPI and PostgreSQL serving 2M requests a day.",
    "- Containerised services with Docker and automated deploys using GitHub Actions.",
    "EDUCATION",
    "B.Tech Computer Science 2015 - 2019",
    "SKILLS",
    "Python, SQL, Docker, Git, Pytest",
]
RESUME_TEXT = "\n".join(RESUME_LINES)

JOB_DESCRIPTION = """Backend Engineer
Requirements:
- 3+ years of experience building services in Python
- Strong knowledge of FastAPI and PostgreSQL
- Experience with Docker and Kubernetes
Nice to have:
- Kafka
- Terraform
"""


def make_pdf_bytes(lines: list[str] = RESUME_LINES) -> bytes:
    buf = io.BytesIO()
    pdf = canvas.Canvas(buf)
    y = 800
    for line in lines:
        pdf.drawString(50, y, line)
        y -= 18
    pdf.save()
    return buf.getvalue()


def make_docx_bytes(lines: list[str] = RESUME_LINES) -> bytes:
    doc = DocxDocument()
    for line in lines:
        doc.add_paragraph(line)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "upload_dir", tmp_path / "uploads")
    reset_all_limiters()
    yield


@pytest.fixture()
def db_session_factory():
    # Set TEST_DATABASE_URL to run the whole suite against PostgreSQL (CI does this).
    engine = make_engine(os.environ.get("TEST_DATABASE_URL", "sqlite://"))
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    yield factory
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def client(db_session_factory):
    def override_get_db():
        db = db_session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def register_and_login(client: TestClient, email: str = "jane@example.com", password: str = "S3cure-pass!") -> dict:
    r = client.post("/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201, r.text
    r = client.post("/auth/login", data={"username": email, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture()
def auth(client):
    return register_and_login(client)


@pytest.fixture()
def other_auth(client):
    return register_and_login(client, "mallory@example.com")


def upload(client, headers, name="resume.pdf", data=None, content_type="application/pdf"):
    if data is None:
        data = make_pdf_bytes()
    return client.post("/documents", headers=headers, files={"file": (name, data, content_type)})
