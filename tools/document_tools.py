from __future__ import annotations

import io
import re
from pathlib import Path
from typing import Union


# ============================================================
# SUPPORTED FILE TYPES
# ============================================================

TEXT_TYPES = {
    ".pdf",
    ".docx",
    ".txt",
    ".md",
}

IMAGE_TYPES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
}

IMAGE_MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}

ALLOWED_TYPES = TEXT_TYPES | IMAGE_TYPES

MAGIC_SIGNATURES = {
    ".pdf": (b"%PDF-",),
    ".png": (b"\x89PNG\r\n\x1a\n",),
    ".jpg": (b"\xff\xd8\xff",),
    ".jpeg": (b"\xff\xd8\xff",),
    ".docx": (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"),
}


def _magic_matches(suffix: str, data: bytes) -> bool:
    signatures = MAGIC_SIGNATURES.get(suffix)
    if not signatures:
        return True
    if suffix == ".webp":
        return len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP"
    return any(data.startswith(signature) for signature in signatures)


# ============================================================
# UPLOAD VALIDATION
# ============================================================

def validate_upload(
    path: Union[str, Path],
    max_mb: int = 10,
    size_bytes: int | None = None,
) -> str:
    """
    Validate an uploaded file.

    Returns a sanitized filename.

    Compatible with:
        validate_upload(filename, max_mb)
        validate_upload(filename, max_mb, size_bytes=...)
    """

    filename = Path(path).name
    suffix = Path(filename).suffix.lower()

    if suffix not in ALLOWED_TYPES:
        raise ValueError(
            f"Unsupported file type: {suffix or 'unknown'}"
        )


    if size_bytes is None:
        candidate = Path(path)

        if candidate.exists() and candidate.is_file():
            size_bytes = candidate.stat().st_size

    if data is not None:
        size_bytes = len(data)

    if size_bytes is not None:
        max_bytes = max(1, int(max_mb)) * 1024 * 1024

        if int(size_bytes) > max_bytes:
            raise ValueError(
                f"File is too large. Maximum allowed size is "
                f"{max_mb} MB."
            )

    if data is not None and not _magic_matches(suffix, data):
        raise ValueError("File content does not match its declared type.")

    # --------------------------------------------------------
    # Sanitize filename
    # --------------------------------------------------------

    safe_name = re.sub(
        r"[^A-Za-z0-9._-]+",
        "_",
        filename,
    )

    safe_name = safe_name.strip("._")

    if not safe_name:
        raise ValueError(
            "Invalid filename."
        )

    # Make sure extension remains supported.
    final_suffix = Path(
        safe_name
    ).suffix.lower()

    if final_suffix not in ALLOWED_TYPES:
        raise ValueError(
            f"Unsupported file type: {final_suffix or 'unknown'}"
        )

    return safe_name


# ============================================================
# TEXT EXTRACTION
# ============================================================

def extract_upload_text(
    filename: Union[str, Path],
    data: bytes,
) -> str:
    """
    Extract text from PDF, DOCX, TXT, or Markdown uploads.
    """

    if not data:
        return ""

    suffix = Path(
        filename
    ).suffix.lower()

    # --------------------------------------------------------
    # TXT / Markdown
    # --------------------------------------------------------

    if suffix in {".txt", ".md"}:
        return data.decode(
            "utf-8",
            errors="ignore",
        ).strip()

    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    if suffix == ".pdf":
        return _extract_pdf(
            data
        ).strip()

    # --------------------------------------------------------
    # DOCX
    # --------------------------------------------------------

    if suffix == ".docx":
        return _extract_docx(
            data
        ).strip()

    raise ValueError(
        f"Cannot extract text from {suffix or 'unknown'} files."
    )


# ============================================================
# PDF EXTRACTION
# ============================================================

def _extract_pdf(
    data: bytes,
) -> str:

    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError(
            "PDF support requires pypdf."
        ) from exc

    try:
        reader = PdfReader(
            io.BytesIO(data)
        )

        pages: list[str] = []

        for page_number, page in enumerate(
            reader.pages,
            start=1,
        ):
            text = (
                page.extract_text()
                or ""
            ).strip()

            if text:
                pages.append(
                    f"[Page {page_number}]\n{text}"
                )

        return "\n\n".join(
            pages
        )

    except Exception as exc:
        raise ValueError("The PDF could not be read. It may be malformed or unsupported.") from exc


# ============================================================
# DOCX EXTRACTION
# ============================================================

def _extract_docx(
    data: bytes,
) -> str:

    try:
        from docx import Document
    except ImportError as exc:
        raise RuntimeError(
            "DOCX support requires python-docx."
        ) from exc

    try:
        document = Document(
            io.BytesIO(data)
        )

        paragraphs: list[str] = []

        for paragraph in document.paragraphs:
            text = paragraph.text.strip()

            if text:
                paragraphs.append(text)

        return "\n\n".join(
            paragraphs
        )

    except Exception as exc:
        raise ValueError("The DOCX could not be read. It may be malformed or unsupported.") from exc


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def is_supported_file(
    filename: Union[str, Path],
) -> bool:
    return (
        Path(filename)
        .suffix
        .lower()
        in ALLOWED_TYPES
    )


def is_image_file(
    filename: Union[str, Path],
) -> bool:
    return (
        Path(filename)
        .suffix
        .lower()
        in IMAGE_TYPES
    )


def is_text_file(
    filename: Union[str, Path],
) -> bool:
    return (
        Path(filename)
        .suffix
        .lower()
        in TEXT_TYPES
    )


def get_image_mime(
    filename: Union[str, Path],
) -> str:

    suffix = (
        Path(filename)
        .suffix
        .lower()
    )

    mime = IMAGE_MIME.get(
        suffix
    )

    if not mime:
        raise ValueError(
            f"Unsupported image type: {suffix}"
        )

    return mime
