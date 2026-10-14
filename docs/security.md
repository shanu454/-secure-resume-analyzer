# Security considerations

## Threats and mitigations

| Threat | Mitigation | Where |
|---|---|---|
| Malicious file disguised as a resume | Extension allow-list + magic-byte/structure checks, PDF active-content rejection, macro and zip-bomb checks | `file_validation.py` |
| Path traversal via filename | Random 32-hex stored name, regex-checked before any path is built; display name sanitised | `storage.py`, `file_validation.py` |
| Resource exhaustion | 5 MB cap while streaming, page and text caps, per-user document quota, rate limits, nginx body limit | `documents.py`, `parsing.py`, `rate_limit.py` |
| Broken access control (IDOR) | Every query filters by `user_id`; other users' objects return 404; covered by tests | `api/*.py`, `tests/test_*_api.py` |
| Credential theft | argon2 password hashes, no plaintext anywhere, generic login error, constant-ish login timing via dummy hash | `core/security.py`, `api/auth.py` |
| Brute force / abuse | Per-IP sliding-window limits on login, register, upload, analysis | `core/rate_limit.py` |
| Token misuse | Signed HS256 JWT with `exp`; algorithm pinned on decode; 30-minute lifetime | `core/security.py` |
| Personal data in logs | Request logs hold only method, path, status, timing, request id; an email-masking filter; exception *types* only; a test asserts resume text never reaches logs | `core/logging.py`, `main.py`, `tests/test_logging.py` |
| Data kept too long | `expires_at` per document, hourly sweep, manual delete, cascade to analyses | `services/retention.py` |
| Clickjacking / MIME sniffing / caching | `X-Frame-Options`, `X-Content-Type-Options`, `Cache-Control: no-store`, strict CSP | `main.py`, `nginx.conf` |
| Weak production config | `ENVIRONMENT=prod` refuses to start without a 32+ character `SECRET_KEY`; Swagger disabled in prod | `core/config.py`, `main.py` |
| Container compromise | Non-root user, upload volume only, DB not published to the host | `Dockerfile`, `docker-compose.yml` |
| Vulnerable dependencies | `pip-audit` and `npm audit` in CI | `.github/workflows/ci.yml` |

## File retention and deletion

- Every upload gets `expires_at = uploaded_at + RETENTION_DAYS` (default 30), shown in the UI.
- A background task runs hourly and deletes expired files, rows and analyses; expired documents cannot be analysed (410).
- Users can delete a document at any time; the file is removed first, then the rows.
- Deleting a user cascades to everything they own.

## Not covered (be honest in interviews)

See `known-limitations.md`: no antivirus scan, no email verification, no refresh tokens or revocation, in-memory rate limiting, parsing happens in the API process, and the token is kept in `sessionStorage`.
