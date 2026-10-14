# Input validation strategy

Validation happens in layers; each layer assumes the previous one can fail.

| Layer | Where | What it does |
|---|---|---|
| 1. Edge | `nginx.conf` | `client_max_body_size 6m` rejects giant bodies before the app sees them |
| 2. Header check | `main.py` middleware | Rejects requests whose `Content-Length` is far above the upload limit |
| 3. Streaming read | `api/documents.py` | Reads the upload in 64 KB chunks and aborts as soon as it passes 5 MB (413) |
| 4. File validation | `services/file_validation.py` | Extension allow-list, then content must match the extension |
| 5. Parse test | `services/parsing.py` | The file is parsed once at upload; unreadable, encrypted, image-only or oversized-text files are rejected (422) |
| 6. Schemas | `schemas/api.py` | Pydantic enforces types and lengths on every JSON body |

## File checks (`validate_upload`)

| Type | Checks |
|---|---|
| All | Extension in `.pdf`, `.docx`, `.txt`; non-empty; size <= `MAX_UPLOAD_BYTES`. The client `Content-Type` is ignored |
| PDF | Starts with `%PDF-`; rejects `/JavaScript`, `/JS`, `/Launch`, `/EmbeddedFile`, `/RichMedia`; encrypted PDFs and > 15 pages are rejected at parse time |
| DOCX | Starts with `PK`; is a ZIP containing `[Content_Types].xml` and `word/document.xml`; <= 1000 entries; no `..` or absolute paths; no `vbaProject` (macros); no encrypted entries; uncompressed size <= 30 MB; compression ratio < 100:1 for large entries (zip bombs) |
| TXT | No NUL bytes; valid UTF-8 |

## Other inputs

| Input | Rule |
|---|---|
| Filename | Reduced to a display name (directory parts, control characters and `<>:"|?*\/` removed, 255 chars). **Never used in a path** |
| Email | `EmailStr`, lowercased |
| Password | 8-128 characters, not blank; hashed with argon2 |
| Job description | 30-20,000 characters |
| Job title | <= 200 characters |
| IDs | Parsed as UUIDs (422 otherwise) |
| Pagination | `limit` 1-100, `offset` >= 0 |
| Extracted text | <= 200,000 characters |
