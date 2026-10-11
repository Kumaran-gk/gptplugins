from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from src.ingestion.ocr_reader import extract_text_from_image_path


def read_image(
    file_path: str | Path,
    *,
    tesseract_cmd: Optional[str] = None,
    lang: str = "eng",
) -> Dict[str, Any]:
    """
    Read an image file and OCR it into the common extraction structure.
    """
    return extract_text_from_image_path(
        file_path,
        tesseract_cmd=tesseract_cmd,
        lang=lang,
    )