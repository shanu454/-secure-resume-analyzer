from datetime import datetime, timedelta, timezone

from app.core.config import get_settings
from app.models import Document
from app.services.retention import purge_expired
from tests.conftest import JOB_DESCRIPTION, upload


def test_new_documents_get_an_expiry(client, auth):
    body = upload(client, auth).json()
    uploaded = datetime.fromisoformat(body["uploaded_at"])
    expires = datetime.fromisoformat(body["expires_at"])
    assert timedelta(days=get_settings().retention_days) - (expires - uploaded) < timedelta(seconds=2)


def test_purge_removes_expired_files_rows_and_analyses(client, auth, db_session_factory):
    old_id = upload(client, auth).json()["id"]
    new_id = upload(client, auth).json()["id"]
    client.post("/analyses", headers=auth, json={"document_id": old_id, "job_description": JOB_DESCRIPTION})

    with db_session_factory() as db:
        old = db.get(Document, __import__("uuid").UUID(old_id))
        old.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        db.commit()
        assert purge_expired(db) == 1

    upload_dir = get_settings().upload_dir
    assert len(list(upload_dir.iterdir())) == 1
    assert client.get(f"/documents/{old_id}", headers=auth).status_code == 404
    assert client.get(f"/documents/{new_id}", headers=auth).status_code == 200
    assert client.get("/analyses", headers=auth).json() == []


def test_expired_document_cannot_be_analysed(client, auth, db_session_factory):
    doc_id = upload(client, auth).json()["id"]
    with db_session_factory() as db:
        doc = db.get(Document, __import__("uuid").UUID(doc_id))
        doc.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        db.commit()
    r = client.post("/analyses", headers=auth, json={"document_id": doc_id, "job_description": JOB_DESCRIPTION})
    assert r.status_code == 410
