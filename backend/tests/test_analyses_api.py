from tests.conftest import JOB_DESCRIPTION, upload


def create(client, headers, doc_id, jd=JOB_DESCRIPTION, **extra):
    return client.post("/analyses", headers=headers, json={"document_id": doc_id, "job_description": jd, **extra})


def test_full_flow(client, auth):
    doc_id = upload(client, auth).json()["id"]
    r = create(client, auth, doc_id, job_title="Backend Engineer")
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["job_title"] == "Backend Engineer"
    assert body["document_filename"] == "resume.pdf"
    assert body["report"]["match_score"] == body["match_score"] > 0
    assert {s["name"] for s in body["report"]["missing_skills"]} >= {"Kubernetes"}

    history = client.get("/analyses", headers=auth).json()
    assert [h["id"] for h in history] == [body["id"]]
    assert "report" not in history[0]

    detail = client.get(f"/analyses/{body['id']}", headers=auth)
    assert detail.status_code == 200 and detail.json()["report"] == body["report"]


def test_history_is_newest_first_and_paginated(client, auth):
    doc_id = upload(client, auth).json()["id"]
    ids = [create(client, auth, doc_id, job_title=f"Job {i}").json()["id"] for i in range(3)]
    listed = client.get("/analyses", headers=auth).json()
    assert [a["id"] for a in listed] == ids[::-1]
    page = client.get("/analyses?limit=1&offset=1", headers=auth).json()
    assert [a["id"] for a in page] == [ids[1]]
    assert client.get("/analyses?limit=1000", headers=auth).status_code == 422


def test_validation_errors(client, auth):
    doc_id = upload(client, auth).json()["id"]
    assert create(client, auth, doc_id, jd="too short").status_code == 422
    assert create(client, auth, doc_id, jd="x" * 25_000).status_code == 422
    assert create(client, auth, "not-a-uuid").status_code == 422
    assert create(client, auth, "00000000-0000-0000-0000-000000000000").status_code == 404


def test_cannot_analyse_or_read_other_users_data(client, auth, other_auth):
    doc_id = upload(client, auth).json()["id"]
    assert create(client, other_auth, doc_id).status_code == 404

    analysis_id = create(client, auth, doc_id).json()["id"]
    assert client.get(f"/analyses/{analysis_id}", headers=other_auth).status_code == 404
    assert client.delete(f"/analyses/{analysis_id}", headers=other_auth).status_code == 404
    assert client.get("/analyses", headers=other_auth).json() == []


def test_delete_analysis(client, auth):
    doc_id = upload(client, auth).json()["id"]
    analysis_id = create(client, auth, doc_id).json()["id"]
    assert client.delete(f"/analyses/{analysis_id}", headers=auth).status_code == 204
    assert client.get(f"/analyses/{analysis_id}", headers=auth).status_code == 404
    assert client.get(f"/documents/{doc_id}", headers=auth).status_code == 200


def test_deleting_document_deletes_its_analyses(client, auth, db_session_factory):
    from app.models import Analysis, JobDescription

    doc_id = upload(client, auth).json()["id"]
    create(client, auth, doc_id)
    client.delete(f"/documents/{doc_id}", headers=auth)
    assert client.get("/analyses", headers=auth).json() == []
    with db_session_factory() as db:
        assert db.query(Analysis).count() == 0
        assert db.query(JobDescription).count() == 0


def test_security_headers_present(client):
    r = client.get("/health")
    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["x-frame-options"] == "DENY"
    assert r.headers["cache-control"] == "no-store"
    assert r.headers["x-request-id"]
