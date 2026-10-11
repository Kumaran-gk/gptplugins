from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Dict, Optional

import pytesseract
from PIL import Image


def is_tesseract_available(tesseract_cmd: Optional[str] = None) -> bool:
    """
    Check whether Tesseract OCR is available.
    """
    if tesseract_cmd:
        return Path(tesseract_cmd).exists()
    return shutil.which("tesseract") is not None


def configure_tesseract(tesseract_cmd: Optional[str] = None) -> None:
    """
    Configure pytesseract to use a specific executable path if provided.
    """
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd


def ensure_tesseract_available(tesseract_cmd: Optional[str] = None) -> None:
    configure_tesseract(tesseract_cmd)

    if not is_tesseract_available(tesseract_cmd):
        raise RuntimeError(
            "Tesseract OCR is not available. Install Tesseract on the machine "
            "or provide a valid tesseract_cmd path."
        )


def extract_text_from_pil_image(
    image: Image.Image,
    *,
    tesseract_cmd: Optional[str] = None,
    lang: str = "eng",
) -> str:
    """
    OCR text from a PIL image.
    """
    ensure_tesseract_available(tesseract_cmd)
    text = pytesseract.image_to_string(image, lang=lang)
    return text.strip()


def extract_text_from_image_path(
    image_path: str | Path,
    *,
    tesseract_cmd: Optional[str] = None,
    lang: str = "eng",
) -> Dict[str, Any]:
    """
    OCR text from an image file path and return a normalized extraction-like payload.
    """
    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {path}")

    with Image.open(path) as img:
        text = extract_text_from_pil_image(
            img,
            tesseract_cmd=tesseract_cmd,
            lang=lang,
        )

    return {
        "file_name": path.name,
        "file_path": str(path.resolve()),
        "file_type": path.suffix.lower().lstrip("."),
        "source_kind": "image",
        "page_count": 1,
        "text": text,
        "segments": [
            {
                "segment_type": "image",
                "index": 1,
                "text": text,
                "char_count": len(text),
            }
        ],
        "metadata": {
            "extraction_method": "tesseract",
            "ocr_lang": lang,
        },
    }