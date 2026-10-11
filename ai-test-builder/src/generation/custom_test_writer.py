"""Save a test authored in the Codex conversation from user preferences."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from src.config import Settings, slugify
from src.generation.docx_exporter import export_markdown_to_docx
from src.generation.pdf_exporter import export_markdown_to_pdf
from src.utils.file_io import write_text


def _safe_name(value: str) -> str:
    name = re.sub(r"[^a-z0-9-]+", "-", slugify(value)).strip("-")
    return name[:64].rstrip("-") or "custom-test"


def _unique_path(directory: Path, filename: str) -> Path:
    candidate = directory / filename
    count = 2
    while candidate.exists():
        candidate = directory / f"{Path(filename).stem}_{count}{Path(filename).suffix}"
        count += 1
    return candidate


def save_custom_test(
    *,
    settings: Settings,
    subject: str,
    title: str,
    student_markdown: str,
    teacher_markdown: str | None = None,
    version: str = "v1",
    export_formats: list[str] | None = None,
) -> dict[str, Any]:
    if not subject.strip() or not title.strip() or not student_markdown.strip():
        raise ValueError("subject, title, and student_markdown must be nonempty")
    formats = {value.lower() for value in (export_formats or ["md"])}
    if not formats or formats - {"md", "docx", "pdf"}:
        raise ValueError("export_formats must contain only md, docx, or pdf")

    directory = settings.ensure_subject_dirs(subject)["generated_path"]
    stem = f"{_safe_name(title)}_{_safe_name(version)}"
    outputs: dict[str, str] = {}
    for kind, content in (("student", student_markdown), ("teacher", teacher_markdown)):
        if not content:
            continue
        md_path = _unique_path(directory, f"{stem}_{kind}.md")
        write_text(md_path, content.rstrip() + "\n")
        outputs[f"{kind}_md"] = str(md_path)
        if "docx" in formats:
            docx_path = _unique_path(directory, f"{stem}_{kind}.docx")
            export_markdown_to_docx(content, docx_path)
            outputs[f"{kind}_docx"] = str(docx_path)
        if "pdf" in formats:
            pdf_path = _unique_path(directory, f"{stem}_{kind}.pdf")
            export_markdown_to_pdf(content, pdf_path)
            outputs[f"{kind}_pdf"] = str(pdf_path)
    return {"subject": subject, "title": title, "version": version, "outputs": outputs}
