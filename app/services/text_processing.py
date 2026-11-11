import re
from pathlib import PurePosixPath

SUPPORTED_EXTENSIONS = {".txt", ".md"}
DEFAULT_CHUNK_SIZE = 900
DEFAULT_CHUNK_OVERLAP = 120


class UnsupportedDocumentError(ValueError):
    """Raised when an upload is not a supported text document."""


class InvalidDocumentError(ValueError):
    """Raised when a document cannot be decoded or contains no text."""


def extract_text(filename: str, content: bytes) -> str:
    safe_name = filename.replace("\\", "/").split("/")[-1]
    suffix = PurePosixPath(safe_name).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise UnsupportedDocumentError(
            "Only UTF-8 .txt and .md documents are supported in this release."
        )
    try:
        text = content.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    except UnicodeDecodeError as exc:
        raise InvalidDocumentError("Document must be valid UTF-8 text.") from exc

    text = text.strip()
    if not text or "\x00" in text:
        raise InvalidDocumentError("Document is empty or contains invalid null characters.")
    return text


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    if chunk_size < 1 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Require chunk_size > overlap >= 0.")

    normalized = re.sub(r"[ \t]+", " ", text).strip()
    if not normalized:
        return []

    chunks = []
    start = 0
    while start < len(normalized):
        end = min(start + chunk_size, len(normalized))
        if end < len(normalized):
            boundary = normalized.rfind(" ", start + chunk_size // 2, end)
            if boundary > start:
                end = boundary
        piece = normalized[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= len(normalized):
            break
        start = max(end - overlap, start + 1)
    return chunks
