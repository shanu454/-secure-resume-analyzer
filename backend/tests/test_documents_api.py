import os

from app.core.config import get_settings
from tests.conftest import make_docx_bytes, make_pdf_bytes, upload


def stored_files():
    d = get_settings().upload_dir
    return list(d.iterdir()) if d.exists() else []


def test_upload_pdf_docx_txt(client, auth):
    assert upload(client, auth).status_code == 201
    r = upload(client, auth, "cv.docx", make_docx_bytes(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    assert r.status_code == 201
    r = upload(client, auth, "cv.txt", b"Python developer with Docker and FastAPI experience", "text/plain")
    assert r.status_code == 201
    body = r.json()
    assert body["file_type"] == "txt" and "stored_name" not in body and "sha256" not in body
    assert len(client.get("/documents", headers=auth).json()) == 3


def test_upload_requires_auth(client):
    r = client.post("/documents", files={"file": ("cv.pdf", make_pdf_bytes(), "application/pdf")})
    assert r.status_code == 401


def test_rejects_wrong_type_even_with_pdf_content_type(client, auth):
    r = upload(client, auth, "payload.exe", b"MZ\x90 binary", "application/pdf")
    assert r.status_code == 415
    assert stored_files() == []


def test_rejects_disguised_file(client, auth):
    r = upload(client, auth, "cv.pdf", b"MZ\x90\x00 definitely not a pdf", "application/pdf")
    assert r.status_code == 415
    assert stored_files() == []


def test_rejects_oversized_upload(client, auth, monkeypatch):
    monkeypatch.setattr(get_settings(), "max_upload_bytes", 1000)
    r = upload(client, auth, "cv.txt", b"python " * 400, "text/plain")
    assert r.status_code == 413
    assert stored_files() == []


def test_rejects_unreadable_pdf(client, auth):
    r = upload(client, auth, "cv.pdf", b"%PDF-1.4\nnot a real document", "application/pdf")
    assert r.status_code == 422
    assert stored_files() == []


def test_malicious_filename_never_reaches_disk_path(client, auth):
    r = upload(client, auth, "../../etc/passwd.pdf")
    assert r.status_code == 201
    assert r.json()["original_filename"] == "passwd.pdf"
    (f,) = stored_files()
    assert len(f.name) == 32 and all(c in "0123456789abcdef" for c in f.name)
    if os.name == "posix":
        assert oct(f.stat().st_mode & 0o777) == "0o600"


def test_per_user_document_quota(client, auth, monkeypatch):
    monkeypatch.setattr(get_settings(), "max_documents_per_user", 2)
    assert upload(client, auth).status_code == 201
    assert upload(client, auth).status_code == 201
    assert upload(client, auth).status_code == 409


def test_users_cannot_see_or_delete_each_others_documents(client, auth, other_auth):
    doc_id = upload(client, auth).json()["id"]
    assert client.get(f"/documents/{doc_id}", headers=other_auth).status_code == 404
    assert client.delete(f"/documents/{doc_id}", headers=other_auth).status_code == 404
    assert client.get("/documents", headers=other_auth).json() == []
    assert client.get(f"/documents/{doc_id}", headers=auth).status_code == 200
    assert len(stored_files()) == 1


def test_delete_removes_file_and_row(client, auth):
    doc_id = upload(client, auth).json()["id"]
    assert len(stored_files()) == 1
    assert client.delete(f"/documents/{doc_id}", headers=auth).status_code == 204
    assert stored_files() == []
    assert client.get(f"/documents/{doc_id}", headers=auth).status_code == 404


def test_invalid_id_format(client, auth):
    assert client.get("/documents/not-a-uuid", headers=auth).status_code == 422
