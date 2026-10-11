from __future__ import annotations

from pathlib import Path


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}


def detect_file_kind(file_path: str | Path) -> str:
    """
    Return one of:
    - pdf
    - docx
    - image

    Raise ValueError for unsupported types.
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return "pdf"
    if suffix == ".docx":
        return "docx"
    if suffix in IMAGE_EXTENSIONS:
        return "image"

    raise ValueError(f"Unsupported file type: {path.name}")