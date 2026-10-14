# Test cases

Run with `cd backend && pytest`. The suite has **95 tests** and runs on SQLite by default; set `TEST_DATABASE_URL` to run it against PostgreSQL (CI does).

| File | What it proves |
|---|---|
| `test_auth.py` | Register/login/me; email normalised; duplicate email 409; weak password and bad email 422; wrong password and unknown user look identical; protected routes need a token; expired, tampered and orphaned tokens rejected |
| `test_file_validation.py` | Valid PDF/DOCX/TXT accepted; `.exe/.html/.docm/.svg/no extension` rejected; empty and oversized files; executable renamed `.pdf`; PDF<->DOCX swaps; PDF with JavaScript; ZIP that is not a DOCX; macros; `../` entries; compression bomb; NUL bytes and non-UTF-8 text; filename sanitising (traversal, Windows paths, control chars, length) |
| `test_parsing.py` | Text extraction from PDF, DOCX (including tables) and TXT with BOM; corrupt files give a generic error that does not echo content; image-only PDF, too many pages and too much text rejected; normalisation |
| `test_skills.py` | `C++`, `C#`, `.NET`, `Node.js`, `CI/CD` boundaries; `Java` vs `JavaScript`; `js` inside `Node.js`; substrings (`trustworthy`) not matched; case-sensitive `Go`/`Swift`; mention counts; longest alias wins |
| `test_analysis.py` | Required vs preferred classification (headings, inline "a plus", per-sentence markers, all-caps skill lines); full report and exact score; perfect/zero score; unrecognised JD warning; experience years (merged overlaps, "Present", MM/YYYY, education ignored); required years; missing keywords |
| `test_documents_api.py` | Upload of all three types; auth required; disguised and wrong-type files leave nothing on disk; oversized upload; unreadable PDF; hostile filename never reaches the path and file mode is 0600; per-user quota; **user B cannot read or delete user A's document**; delete removes file and row |
| `test_analyses_api.py` | Full flow; history ordering and pagination; input validation; **cross-user access returns 404**; deleting an analysis; deleting a document cascades to analyses and job descriptions; security headers |
| `test_rate_limit.py` | Limiter allows, blocks and recovers (fake clock); login is limited over HTTP with `Retry-After` |
| `test_retention.py` | New documents get an expiry; purge removes expired files, rows and analyses and keeps fresh ones; expired documents cannot be analysed (410) |
| `test_logging.py` | Emails masked; a unique string from a resume, the password and resume skills never appear in any log record during upload and analysis |
| `test_evaluation.py` | Extraction F1/recall and classification F1 stay >= 0.9 on the labelled set |

CI also runs lint (`ruff`), the evaluation script, `pip-audit`, `npm audit` and a production build of the frontend and Docker images.
