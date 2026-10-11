from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH


HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
ITALIC_RE = re.compile(r"\*(.+?)\*")


def _clean_inline_markdown(text: str) -> str:
    cleaned = BOLD_RE.sub(r"\1", text)
    cleaned = ITALIC_RE.sub(r"\1", cleaned)
    return cleaned.strip()


def _iter_nonempty_lines(markdown_text: str) -> Iterable[str]:
    for line in markdown_text.splitlines():
        yield line.rstrip()


def export_markdown_to_docx(
    markdown_text: str,
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    document = Document()
    lines = list(_iter_nonempty_lines(markdown_text))
    title_written = False

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            document.add_paragraph("")
            continue

        heading_match = HEADING_RE.match(line)
        if heading_match:
            level = min(len(heading_match.group(1)), 4)
            heading_text = _clean_inline_markdown(heading_match.group(2))
            paragraph = document.add_heading(heading_text, level=level)
            if not title_written and level == 1:
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                title_written = True
            continue

        if re.match(r"^\d+\.\s+", line):
            document.add_paragraph(_clean_inline_markdown(line), style="List Number")
            continue

        if line.startswith("- "):
            document.add_paragraph(_clean_inline_markdown(line[2:]), style="List Bullet")
            continue

        if line.startswith("**") and line.endswith("**"):
            paragraph = document.add_paragraph()
            run = paragraph.add_run(_clean_inline_markdown(line))
            run.bold = True
            continue

        if line.startswith("*") and line.endswith("*"):
            paragraph = document.add_paragraph()
            run = paragraph.add_run(_clean_inline_markdown(line))
            run.italic = True
            continue

        document.add_paragraph(_clean_inline_markdown(line))

    document.save(str(path))
    return path
