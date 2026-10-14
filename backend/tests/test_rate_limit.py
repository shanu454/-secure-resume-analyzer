from app.core import rate_limit as rl
from app.core.rate_limit import RateLimiter


def test_limiter_allows_then_blocks_then_recovers():
    now = [0.0]
    limiter = RateLimiter(limit=3, window_seconds=60, clock=lambda: now[0])
    assert [limiter.check("ip") for _ in range(3)] == [None, None, None]
    retry = limiter.check("ip")
    assert retry is not None and 1 <= retry <= 61
    assert limiter.check("other-ip") is None
    now[0] = 61.0
    assert limiter.check("ip") is None


def test_login_is_rate_limited_over_http(client, monkeypatch):
    monkeypatch.setattr(rl, "_enabled", lambda: True)
    codes = [
        client.post("/auth/login", data={"username": "a@example.com", "password": "wrong-password"}).status_code
        for _ in range(12)
    ]
    assert codes[:10] == [401] * 10
    assert codes[10:] == [429, 429]
    r = client.post("/auth/login", data={"username": "a@example.com", "password": "wrong-password"})
    assert r.status_code == 429 and int(r.headers["retry-after"]) >= 1
