from datetime import datetime, timedelta, timezone

from app.core.security import create_access_token, decode_access_token
from tests.conftest import register_and_login


def test_register_and_login_and_me(client):
    headers = register_and_login(client)
    r = client.get("/auth/me", headers=headers)
    assert r.status_code == 200
    assert r.json()["email"] == "jane@example.com"
    assert "password" not in r.text


def test_email_is_normalised(client):
    client.post("/auth/register", json={"email": "Jane@Example.COM", "password": "S3cure-pass!"})
    r = client.post("/auth/login", data={"username": "jane@example.com", "password": "S3cure-pass!"})
    assert r.status_code == 200


def test_duplicate_email_rejected(client):
    body = {"email": "a@example.com", "password": "S3cure-pass!"}
    assert client.post("/auth/register", json=body).status_code == 201
    assert client.post("/auth/register", json=body).status_code == 409


def test_weak_or_invalid_input_rejected(client):
    assert client.post("/auth/register", json={"email": "a@example.com", "password": "short"}).status_code == 422
    assert client.post("/auth/register", json={"email": "not-an-email", "password": "S3cure-pass!"}).status_code == 422
    assert client.post("/auth/register", json={"email": "a@example.com", "password": "x" * 200}).status_code == 422


def test_wrong_password_and_unknown_user_look_the_same(client):
    client.post("/auth/register", json={"email": "a@example.com", "password": "S3cure-pass!"})
    bad_pw = client.post("/auth/login", data={"username": "a@example.com", "password": "wrong-password"})
    no_user = client.post("/auth/login", data={"username": "nobody@example.com", "password": "wrong-password"})
    assert bad_pw.status_code == no_user.status_code == 401
    assert bad_pw.json() == no_user.json()


def test_protected_routes_need_a_token(client):
    for path in ("/documents", "/analyses", "/auth/me"):
        assert client.get(path).status_code == 401
    assert client.get("/documents", headers={"Authorization": "Bearer garbage"}).status_code == 401


def test_expired_and_tampered_tokens_rejected(client):
    old = create_access_token("00000000-0000-0000-0000-000000000000", now=datetime.now(timezone.utc) - timedelta(days=1))
    assert decode_access_token(old) is None
    good = create_access_token("abc")
    assert decode_access_token(good) == "abc"
    assert decode_access_token(good[:-2] + "xx") is None


def test_token_for_deleted_user_rejected(client):
    token = create_access_token("00000000-0000-0000-0000-000000000000")
    assert client.get("/auth/me", headers={"Authorization": f"Bearer {token}"}).status_code == 401
