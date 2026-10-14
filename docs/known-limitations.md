# Known limitations

## Matching quality
- **Fixed vocabulary.** Only the 131 skills in `data/skills.json` are recognised. Anything else is invisible to the score (it can still show up under "missing keywords").
- **Ambiguous words.** "Express" and "React" also match the lowercase verbs ("react quickly to incidents"). The evaluation shows this false positive. "Go" and "Swift" are matched only when capitalised, so lowercase mentions are missed.
- **Abbreviations.** Only the aliases in the taxonomy are mapped; `ML` is handled, many others are not.
- **No semantic understanding.** "Built an API layer in Python" and "Python" are equal; skill depth, recency and seniority are not judged. "Implied" skills (GitHub Actions implies Git) are not inferred.
- **Required vs preferred** is decided from headings and phrases like "a plus"; unusual formatting falls back to "required".
- **Years of experience** come from date ranges. Roles without dates, overlapping part-time jobs and gaps are approximate; a year with no month is treated as mid-year.
- **English only.**

## Documents
- Scanned/image-only PDFs are rejected (no OCR). Multi-column and table-heavy PDFs may extract in odd order.
- PDF/DOCX parsing runs inside the API process. A hostile file that triggers a parser bug could hang a worker. Production should parse in a separate sandboxed worker with a hard timeout.
- No antivirus scan. The checks reduce risk but do not replace ClamAV or similar.

## Security and operations
- Rate limiting is **in memory and per process**; with several workers or instances use Redis. It keys on the direct client IP, which is the proxy's IP behind nginx unless forwarded headers are handled.
- No email verification, password reset, refresh tokens, or token revocation. A stolen token works until it expires (30 minutes).
- Registration returns 409 for an existing email, which reveals that the email is registered.
- The frontend stores the token in `sessionStorage` (readable by scripts on the page). HttpOnly cookies plus CSRF protection would be stronger.
- Uploaded files are stored unencrypted on the volume (permissions 0600). Use an encrypted volume or object storage with server-side encryption in production.
- Tables are created by `create_all`, not migrations. Add Alembic before changing the schema on real data.
- The retention sweep runs inside the API process; with multiple instances it runs on each (harmless but redundant).
- Deleting a file from disk does not securely erase it from backups or snapshots.

## Evaluation
- The labelled set is small (15 resumes, 6 job descriptions), synthetic, and was used while developing the matcher. Reported scores are optimistic.
- Gold labels include only skills that are named or aliased in the text.
