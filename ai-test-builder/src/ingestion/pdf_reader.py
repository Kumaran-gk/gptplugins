from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import pymupdf as fitz
from PIL import Image
from pypdf import PdfReader

from src.ingestion.ocr_reader import extract_text_from_pil_image
from src.utils.logging_utils import get_logger


LOGGER = get_logger("ingestion.pdf_reader")


def _render_pdf_page_to_pil(
    pdf_path: Path,
    page_index_zero_based: int,
    zoom: float = 2.0,
) -> Image.Image:
    """
    Render a PDF page to a PIL image for OCR.
    """
    document = fitz.open(str(pdf_path))
    try:
        page = document.load_page(page_index_zero_based)
        matrix = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        return image
    finally:
        document.close()


def _extract_text_pdf_pages(pdf_path: Path) -> List[Dict[str, Any]]:
    """
    Extract embedded text from each PDF page using pypdf.
    """
    reader = PdfReader(str(pdf_path))
    pages: List[Dict[str, Any]] = []

    for page_index, page in enumerate(reader.pages, start=1):
        raw_text = page.extract_text() or ""
        page_text = raw_text.strip()

        pages.append(
            {
                "page_number": page_index,
                "text": page_text,
                "char_count": len(page_text),
                "extraction_source": "embedded_text",
            }
        )

    return pages


def read_pdf(
    file_path: str | Path,
    *,
    mode: str = "auto",
    tesseract_cmd: Optional[str] = None,
    lang: str = "eng",
    weak_text_threshold: int = 80,
) -> Dict[str, Any]:
    """
    Read a PDF and return a structured extraction payload.

    Modes:
    - text : use embedded PDF text only
    - ocr  : OCR every page
    - auto : use embedded text when strong enough, OCR weak/empty pages
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a .pdf file, got: {path.name}")

    if mode not in {"text", "ocr", "auto"}:
        raise ValueError("mode must be one of: text, ocr, auto")

    LOGGER.info("Reading PDF path=%s mode=%s", path, mode)
    embedded_pages = _extract_text_pdf_pages(path)
    final_pages: List[Dict[str, Any]] = []

    for page_info in embedded_pages:
        page_number = page_info["page_number"]
        embedded_text = page_info["text"]
        use_ocr = False

        if mode == "ocr":
            use_ocr = True
        elif mode == "text":
            use_ocr = False
        elif mode == "auto":
            use_ocr = len(embedded_text.strip()) < weak_text_threshold

        if use_ocr:
            image = _render_pdf_page_to_pil(path, page_number - 1)
            ocr_text = extract_text_from_pil_image(
                image,
                tesseract_cmd=tesseract_cmd,
                lang=lang,
            )

            final_pages.append(
                {
                    "page_number": page_number,
                    "text": ocr_text,
                    "char_count": len(ocr_text),
                    "extraction_source": "ocr",
                }
            )
        else:
            final_pages.append(page_info)

    full_text = "\n\n".join(
        page["text"] for page in final_pages if page["text"].strip()
    ).strip()

    if mode == "text":
        source_kind = "text_pdf"
        extraction_method = "pypdf"
    elif mode == "ocr":
        source_kind = "scanned_pdf"
        extraction_method = "ocr"
    else:
        if all(page["extraction_source"] == "embedded_text" for page in final_pages):
            source_kind = "text_pdf"
            extraction_method = "pypdf"
        elif all(page["extraction_source"] == "ocr" for page in final_pages):
            source_kind = "scanned_pdf"
            extraction_method = "ocr"
        else:
            source_kind = "mixed_pdf"
            extraction_method = "hybrid"

    result = {
        "file_name": path.name,
        "file_path": str(path.resolve()),
        "file_type": "pdf",
        "source_kind": source_kind,
        "page_count": len(final_pages),
        "text": full_text,
        "segments": final_pages,
        "metadata": {
            "extraction_method": extraction_method,
            "ocr_lang": lang if extraction_method in {"ocr", "hybrid"} else None,
            "weak_text_threshold": weak_text_threshold,
            "mode": mode,
        },
    }
    LOGGER.info(
        "Completed PDF read path=%s pages=%s source_kind=%s extraction_method=%s",
        path,
        result["page_count"],
        result["source_kind"],
        result["metadata"]["extraction_method"],
    )
    return result
