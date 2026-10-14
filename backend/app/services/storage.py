"""Filesystem storage for uploaded files.

Files are written under a random name that never comes from the client, with
owner-only permissions. Paths are rebuilt from the stored name each time and
the name is checked against a strict pattern, so no user input can reach a path.
"""
import os
import re
import uuid
from pathlib import Path

from app.core.config import get_settings

_STORED_NAME = re.compile(r"^[0-9a-f]{32}$")


def _dir() -> Path:
    path = get_settings().upload_dir
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    return path


def _path(stored_name: str) -> Path:
    if not _STORED_NAME.fullmatch(stored_name):
        raise ValueError("invalid stored name")
    return _dir() / stored_name


def save_bytes(data: bytes) -> str:
    stored_name = uuid.uuid4().hex
    fd = os.open(_path(stored_name), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as fh:
        fh.write(data)
    return stored_name


def read_bytes(stored_name: str) -> bytes:
    return _path(stored_name).read_bytes()


def delete(stored_name: str) -> None:
    _path(stored_name).unlink(missing_ok=True)
