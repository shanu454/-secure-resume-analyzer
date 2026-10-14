"""Validate uploaded files before anything is stored or parsed.

Checks (all must pass):
  1. extension is on the allow-list;
  2. size is within the limit;
  3. the content (magic bytes / structure) matches the extension;
  4. type-specific safety checks (PDF active content, DOCX zip bombs and macros).

The client-supplied Content-Type header is never trusted.
"""
import io
import re
import unicodedata
import zipfile
from pathlib import PurePosixPath, PureWindowsPath

from app.core.config import Settings

ALLOWED_EXTENSIONS = {".pdf": "pdf", ".docx": "docx", ".txt": "txt"}

_PDF_ACTIVE_CONTENT = re.compile(
    rb"/(?:JavaScript|JS|Launch|EmbeddedFile|RichMedia)(?![A-Za-z0-9])"
)
MAX_ZIP_ENTRIES = 1000
MAX_COMPRESSION_RATIO = 100


class UploadValidationError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def sanitize_filename(filename: str | None) -> str:
    """Return a display-only filename. It is never used as a filesystem path."""
    name = filename or "resume"
    name = PureWindowsPath(PurePosixPath(name).name).name  # drop any directory part
    name = unicodedata.normalize("NFKC", name)
    name = "".join(ch for ch in name if ch.isprintable() and ch not in '<>:"|?*\\/')
    name = name.strip(" .") or "resume"
    return name[:255]


def _extension(filename: str) -> str:
    dot = filename.rfind(".")
    return filename[dot:].lower() if dot != -1 else ""


def _check_pdf(data: bytes) -> None:
    if not data.startswith(b"%PDF-"):
        raise UploadValidationError("File content is not a PDF.", 415)
    if _PDF_ACTIVE_CONTENT.search(data):
        raise UploadValidationError("PDFs with scripts or embedded files are not accepted.", 422)


def _check_docx(data: bytes, settings: Settings) -> None:
    if not data.startswith(b"PK\x03\x04"):
        raise UploadValidationError("File content is not a DOCX document.", 415)
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            infos = zf.infolist()
            if len(infos) > MAX_ZIP_ENTRIES:
                raise UploadValidationError("DOCX has too many internal files.", 422)
            names = {i.filename for i in infos}
            if "word/document.xml" not in names or "[Content_Types].xml" not in names:
                raise UploadValidationError("File content is not a DOCX document.", 415)
            if any(n.startswith("/") or ".." in PurePosixPath(n).parts for n in names):
                raise UploadValidationError("DOCX contains unsafe paths.", 422)
            if any("vbaProject" in n for n in names):
                raise UploadValidationError("Documents with macros are not accepted.", 422)
            total = 0
            for info in infos:
                if info.flag_bits & 0x1:
                    raise UploadValidationError("Encrypted documents are not accepted.", 422)
                total += info.file_size
                ratio = info.file_size / max(info.compress_size, 1)
                if info.file_size > 1_000_000 and ratio > MAX_COMPRESSION_RATIO:
                    raise UploadValidationError("DOCX looks like a compression bomb.", 422)
            if total > settings.max_docx_uncompressed_bytes:
                raise UploadValidationError("DOCX expands to too much data.", 422)
    except zipfile.BadZipFile:
        raise UploadValidationError("File content is not a DOCX document.", 415) from None


def _check_txt(data: bytes) -> None:
    if b"\x00" in data:
        raise UploadValidationError("File content is not plain text.", 415)
    try:
        data.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise UploadValidationError("Text files must be UTF-8 encoded.", 415) from None


def validate_upload(filename: str, data: bytes, settings: Settings) -> str:
    """Validate the upload and return its file type ('pdf', 'docx' or 'txt')."""
    file_type = ALLOWED_EXTENSIONS.get(_extension(filename))
    if file_type is None:
        raise UploadValidationError("Only .pdf, .docx and .txt files are accepted.", 415)
    if not data:
        raise UploadValidationError("The file is empty.", 400)
    if len(data) > settings.max_upload_bytes:
        raise UploadValidationError(
            f"File is larger than {settings.max_upload_bytes // (1024 * 1024)} MB.", 413
        )
    if file_type == "pdf":
        _check_pdf(data)
    elif file_type == "docx":
        _check_docx(data, settings)
    else:
        _check_txt(data)
    return file_type
