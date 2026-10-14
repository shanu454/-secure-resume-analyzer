import io
import zipfile

import pytest

from app.core.config import get_settings
from app.services.file_validation import UploadValidationError, sanitize_filename, validate_upload
from tests.conftest import make_docx_bytes, make_pdf_bytes

S = get_settings()


def code(name, data):
    with pytest.raises(UploadValidationError) as exc:
        validate_upload(name, data, S)
    return exc.value.status_code


def test_valid_files_accepted():
    assert validate_upload("cv.pdf", make_pdf_bytes(), S) == "pdf"
    assert validate_upload("cv.DOCX", make_docx_bytes(), S) == "docx"
    assert validate_upload("cv.txt", b"plain resume text here", S) == "txt"


@pytest.mark.parametrize("name", ["cv.exe", "cv.html", "cv.pdf.exe", "cv", "cv.docm", "cv.svg"])
def test_disallowed_extensions(name):
    assert code(name, b"%PDF-1.4 data") == 415


def test_empty_file():
    assert code("cv.pdf", b"") == 400


def test_oversized_file():
    big = b"%PDF-" + b"a" * (S.max_upload_bytes + 1)
    assert code("cv.pdf", big) == 413


def test_executable_renamed_to_pdf():
    assert code("cv.pdf", b"MZ\x90\x00 this is a windows executable") == 415


def test_pdf_renamed_to_docx_and_back():
    assert code("cv.docx", make_pdf_bytes()) == 415
    assert code("cv.pdf", make_docx_bytes()) == 415


def test_pdf_with_javascript_rejected():
    evil = b"%PDF-1.4\n1 0 obj<< /Type /Catalog /OpenAction << /S /JavaScript /JS (app.alert(1)) >> >>endobj"
    assert code("cv.pdf", evil) == 422


def _zip(files: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    return buf.getvalue()


def test_zip_that_is_not_docx():
    assert code("cv.docx", _zip({"hello.txt": b"hi"})) == 415


def test_docx_with_macros_rejected():
    data = _zip({"[Content_Types].xml": b"<x/>", "word/document.xml": b"<x/>", "word/vbaProject.bin": b"x"})
    assert code("cv.docx", data) == 422


def test_docx_path_traversal_entry_rejected():
    data = _zip({"[Content_Types].xml": b"<x/>", "word/document.xml": b"<x/>", "../evil.txt": b"x"})
    assert code("cv.docx", data) == 422


def test_docx_compression_bomb_rejected():
    bomb = _zip({"[Content_Types].xml": b"<x/>", "word/document.xml": b"<x/>", "word/big.xml": b"0" * 20_000_000})
    assert len(bomb) < 1_000_000
    assert code("cv.docx", bomb) == 422


def test_text_with_null_bytes_or_bad_encoding():
    assert code("cv.txt", b"abc\x00def") == 415
    assert code("cv.txt", b"\xff\xfe\xfa invalid utf8") == 415


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("../../etc/passwd", "passwd"),
        ("..\\..\\windows\\system32\\cmd.exe", "cmd.exe"),
        ("my<resume>.pdf", "myresume.pdf"),
        ("", "resume"),
        (None, "resume"),
        ("...", "resume"),
        ("a" * 400 + ".pdf", None),
    ],
)
def test_sanitize_filename(raw, expected):
    result = sanitize_filename(raw)
    assert "/" not in result and "\\" not in result and ".." not in result.replace("...", "")
    assert len(result) <= 255
    if expected:
        assert result == expected
