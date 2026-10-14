import logging

from app.core.logging import RedactingFilter
from tests.conftest import JOB_DESCRIPTION, upload

SENTINEL = "ZXQ-UNIQUE-RESUME-SENTINEL"


def test_email_addresses_are_redacted():
    record = logging.LogRecord("t", logging.INFO, "", 0, "user %s logged in", ("jane.doe@example.com",), None)
    RedactingFilter().filter(record)
    assert "jane.doe@example.com" not in record.getMessage()
    assert "[email-redacted]" in record.getMessage()


def test_resume_content_and_emails_never_reach_logs(client, caplog):
    caplog.set_level(logging.DEBUG)
    headers = {}
    client.post("/auth/register", json={"email": "private.person@example.com", "password": "S3cure-pass!"})
    token = client.post(
        "/auth/login", data={"username": "private.person@example.com", "password": "S3cure-pass!"}
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    text = f"EXPERIENCE\nBuilt things with Python and FastAPI. {SENTINEL} 2019 - 2022\n".encode()
    doc = upload(client, headers, "cv.txt", text, "text/plain").json()
    r = client.post(
        "/analyses", headers=headers, json={"document_id": doc["id"], "job_description": JOB_DESCRIPTION}
    )
    assert r.status_code == 201

    logged = "\n".join(rec.getMessage() for rec in caplog.records)
    assert logged, "expected request logs to exist"
    assert SENTINEL not in logged
    assert "S3cure-pass!" not in logged
    assert "FastAPI" not in logged
