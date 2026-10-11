from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, List

import pymupdf as fitz


HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
ITALIC_RE = re.compile(r"\*(.+?)\*")

PAGE_WIDTH = 612
PAGE_HEIGHT = 792
LEFT_MARGIN = 54
RIGHT_MARGIN = 54
TOP_MARGIN = 54
BOTTOM_MARGIN = 54
LINE_SPACING = 6


def _clean_inline_markdown(text: str) -> str:
    cleaned = BOLD_RE.sub(r"\1", text)
    cleaned = ITALIC_RE.sub(r"\1", cleaned)
    return cleaned.strip()


def _iter_lines(markdown_text: str) -> Iterable[str]:
    for line in markdown_text.splitlines():
        yield line.rstrip()


def _font_size_for_line(line: str) -> tuple[float, bool]:
    heading_match = HEADING_RE.match(line.strip())
    if heading_match:
        level = len(heading_match.group(1))
        if level == 1:
            return 18.0, True
        if level == 2:
            return 14.0, True
        return 12.0, True
    return 11.0, False


def _renderable_text(line: str) -> str:
    stripped = line.strip()
    heading_match = HEADING_RE.match(stripped)
    if heading_match:
        return _clean_inline_markdown(heading_match.group(2))
    return _clean_inline_markdown(stripped)


def _line_layout(line: str) -> tuple[str, float, bool, float]:
    stripped = line.rstrip()
    font_size, is_bold = _font_size_for_line(stripped)

    if HEADING_RE.match(stripped.strip()):
        return _renderable_text(stripped), font_size, is_bold, LEFT_MARGIN

    if re.match(r"^\s+[A-Z]\.\s+", stripped):
        return _renderable_text(stripped), font_size, is_bold, LEFT_MARGIN + 24

    if re.match(r"^\d+\.\s+", stripped.strip()):
        return _renderable_text(stripped), font_size, is_bold, LEFT_MARGIN

    if stripped.strip().startswith("- "):
        return _renderable_text(stripped), font_size, is_bold, LEFT_MARGIN + 12

    return _renderable_text(stripped), font_size, is_bold, LEFT_MARGIN


def _wrap_text(
    text: str,
    *,
    fontname: str,
    fontsize: float,
    max_width: float,
) -> List[str]:
    if not text:
        return [""]

    words = text.split()
    if not words:
        return [""]

    wrapped: List[str] = []
    current = words[0]

    for word in words[1:]:
        candidate = f"{current} {word}"
        if fitz.get_text_length(candidate, fontname=fontname, fontsize=fontsize) <= max_width:
            current = candidate
            continue
        wrapped.append(current)
        current = word

    wrapped.append(current)
    return wrapped


def export_markdown_to_pdf(
    markdown_text: str,
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    document = fitz.open()
    page = document.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
    cursor_y = TOP_MARGIN
    content_width = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN

    for raw_line in _iter_lines(markdown_text):
        line = raw_line.rstrip()
        if not line.strip():
            cursor_y += 10
            if cursor_y > PAGE_HEIGHT - BOTTOM_MARGIN:
                page = document.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
                cursor_y = TOP_MARGIN
            continue

        text, font_size, is_bold, indent_x = _line_layout(line)
        fontname = "hebo" if is_bold else "helv"
        wrapped_lines = _wrap_text(
            text,
            fontname=fontname,
            fontsize=font_size,
            max_width=PAGE_WIDTH - indent_x - RIGHT_MARGIN,
        )

        for wrapped_line in wrapped_lines:
            needed_height = font_size + LINE_SPACING
            if cursor_y + needed_height > PAGE_HEIGHT - BOTTOM_MARGIN:
                page = document.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
                cursor_y = TOP_MARGIN

            page.insert_text(
                fitz.Point(indent_x, cursor_y + font_size),
                wrapped_line,
                fontsize=font_size,
                fontname=fontname,
            )
            cursor_y += needed_height

    document.save(str(path))
    document.close()
    return path
