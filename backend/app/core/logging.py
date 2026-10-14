"""Logging setup that avoids leaking personal data.

Rules:
  * request logs contain method, path, status, duration and a request id only;
  * request bodies, uploaded text and extracted text are never logged;
  * a filter masks email addresses as a second line of defence.
"""
import logging
import re

_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


class RedactingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        redacted = _EMAIL.sub("[email-redacted]", message)
        if redacted != message:
            record.msg = redacted
            record.args = None
        return True


def configure_logging() -> None:
    root = logging.getLogger()
    if any(getattr(h, "_resume_api", False) for h in root.handlers):
        return
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    handler.addFilter(RedactingFilter())
    handler._resume_api = True  # type: ignore[attr-defined]
    root.addHandler(handler)
    root.setLevel(logging.INFO)
