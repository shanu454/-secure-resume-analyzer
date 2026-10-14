# API endpoints

Interactive docs: `http://localhost:8000/docs` (disabled when `ENVIRONMENT=prod`).
All routes except `/health`, `/auth/register` and `/auth/login` need `Authorization: Bearer <token>`.

| Method | Path | Auth | Rate limit | Purpose |
|---|---|---|---|---|
| GET | `/health` | no | - | Liveness check |
| POST | `/auth/register` | no | 10 / hour / IP | Create account. JSON `{email, password}` |
| POST | `/auth/login` | no | 10 / 5 min / IP | OAuth2 password form: `username` (email) + `password`. Returns `{access_token, token_type}` |
| GET | `/auth/me` | yes | - | Current user |
| POST | `/documents` | yes | 20 / hour / IP | Multipart upload, field `file` (.pdf, .docx, .txt, max 5 MB) |
| GET | `/documents` | yes | - | List my documents, newest first |
| GET | `/documents/{id}` | yes | - | Document metadata |
| DELETE | `/documents/{id}` | yes | - | Delete the file **and** its analyses |
| POST | `/analyses` | yes | 30 / hour / IP | JSON `{document_id, job_title?, job_description}` -> full report |
| GET | `/analyses?limit=20&offset=0` | yes | - | History (summaries, no report body) |
| GET | `/analyses/{id}` | yes | - | Full report |
| DELETE | `/analyses/{id}` | yes | - | Delete one analysis |

## Status codes

| Code | Meaning |
|---|---|
| 201 / 204 | Created / deleted |
| 400 | Empty file |
| 401 | Missing, invalid or expired token; wrong credentials |
| 404 | Not found **or not yours** (the API never reveals that another user's object exists) |
| 409 | Email already registered; per-user document quota reached |
| 410 | Document expired or its file is gone |
| 413 | Upload larger than the limit |
| 415 | Wrong or disguised file type |
| 422 | Invalid input, unsafe file content, or unreadable document |
| 429 | Rate limit hit (`Retry-After` header set) |

## Example

```bash
curl -X POST localhost:8000/auth/register -H 'Content-Type: application/json' \
     -d '{"email":"me@example.com","password":"a-long-passphrase"}'

TOKEN=$(curl -s -X POST localhost:8000/auth/login \
     -d 'username=me@example.com&password=a-long-passphrase' | python -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')

DOC=$(curl -s -X POST localhost:8000/documents -H "Authorization: Bearer $TOKEN" \
     -F file=@resume.pdf | python -c 'import sys,json;print(json.load(sys.stdin)["id"])')

curl -X POST localhost:8000/analyses -H "Authorization: Bearer $TOKEN" \
     -H 'Content-Type: application/json' \
     -d "{\"document_id\":\"$DOC\",\"job_description\":\"Requirements: Python, FastAPI, Docker. Nice to have: Kafka.\"}"
```
