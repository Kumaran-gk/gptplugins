from __future__ import annotations

import re
from typing import Any, Dict, List


MOJIBAKE_REPLACEMENTS = {
    "Â»": '"',
    "â€™": "'",
    "â€œ": '"',
    "â€\x9d": '"',
    "â€”": "-",
    "â€“": "-",
    "â€¢": "-",
    "Â°": " degrees",
    "Â©": "(c)",
    "â‰¥": ">=",
    "â‰¤": "<=",
    "âˆš": "sqrt",
}


def _replace_mojibake(text: str) -> str:
    for source, target in MOJIBAKE_REPLACEMENTS.items():
        text = text.replace(source, target)
    return text


QUESTION_OR_SECTION_RE = re.compile(
    r"^\s*(question\s+\d+|\d+[\.\),]|[a-z][\.\)]|bonus:|section\b|part\b)",
    re.IGNORECASE,
)
COURSE_OR_TEST_RE = re.compile(
    r"\b([A-Z]{3}\d[A-Z]\b|unit\b|chapter\b|test\b|exam\b|quiz\b|instructions?\b|total\b|marks?\b)",
    re.IGNORECASE,
)


def _looks_like_formula_or_equation(line: str) -> bool:
    lowered = line.lower()
    if "->" in line or "=" in line or ">" in line:
        return True
    if any(token in lowered for token in ["(aq)", "(s)", "(l)", "(g)", "hcl", "naoh", "agno3", "caco3"]):
        return True
    return False


def _looks_like_typed_prose_line(line: str) -> bool:
    alpha_tokens = re.findall(r"[A-Za-z']+", line)
    if len(alpha_tokens) < 8:
        return False

    alpha_chars = [char for char in line if char.isalpha()]
    uppercase_count = sum(1 for char in alpha_chars if char.isupper())
    lowercase_count = sum(1 for char in alpha_chars if char.islower())
    uppercase_ratio = uppercase_count / max(1, uppercase_count + lowercase_count)
    symbol_count = sum(
        1
        for char in line
        if not char.isspace() and not char.isalnum() and char not in ".,:;!?()[]{}+-*/\\'"
    )
    symbol_ratio = symbol_count / max(1, len([char for char in line if not char.isspace()]))
    mixed_case_tokens = sum(
        1
        for token in alpha_tokens
        if len(token) >= 5 and any(ch.islower() for ch in token) and any(ch.isupper() for ch in token)
    )

    return uppercase_ratio < 0.2 and symbol_ratio < 0.12 and mixed_case_tokens == 0


def _looks_like_assessment_line(line: str) -> bool:
    lowered = line.lower()
    if QUESTION_OR_SECTION_RE.match(line):
        return True
    if COURSE_OR_TEST_RE.search(line):
        return True
    if any(
        phrase in lowered
        for phrase in [
            "multiple choice",
            "application questions",
            "written response",
            "predict",
            "balance",
            "classify",
            "explain",
            "describe",
            "compare",
            "calculate",
            "determine",
            "which",
            "what",
            "why",
            "how",
            "include states",
        ]
    ):
        return True
    if _looks_like_formula_or_equation(line):
        return True
    if _looks_like_typed_prose_line(line):
        return True
    return False


def _looks_like_ocr_answer_noise_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if _looks_like_assessment_line(stripped):
        return False

    alpha_tokens = re.findall(r"[A-Za-z']+", stripped)
    if not alpha_tokens:
        return len(stripped) <= 4

    alpha_chars = [char for char in stripped if char.isalpha()]
    uppercase_count = sum(1 for char in alpha_chars if char.isupper())
    lowercase_count = sum(1 for char in alpha_chars if char.islower())
    non_space_chars = [char for char in stripped if not char.isspace()]
    symbol_count = sum(
        1
        for char in non_space_chars
        if not char.isalnum() and char not in ".,:;!?()[]{}+-*/\\'"
    )

    mixed_case_tokens = sum(
        1
        for token in alpha_tokens
        if len(token) >= 5 and any(ch.islower() for ch in token) and any(ch.isupper() for ch in token)
    )
    uppercase_tokens = sum(1 for token in alpha_tokens if len(token) >= 2 and token.isupper())
    titlecase_tokens = sum(1 for token in alpha_tokens if len(token) >= 4 and token[:1].isupper() and token[1:].islower())
    vowel_poor_tokens = sum(
        1
        for token in alpha_tokens
        if len(token) >= 4 and not re.search(r"[aeiouyAEIOUY]", token)
    )

    alpha_count = len(alpha_tokens)
    symbol_ratio = symbol_count / max(1, len(non_space_chars))
    uppercase_ratio = uppercase_count / max(1, uppercase_count + lowercase_count)

    if stripped.lower().startswith("name:") and len(stripped) < 40:
        return True
    if alpha_count <= 4 and (mixed_case_tokens >= 1 or vowel_poor_tokens >= 1):
        return True
    if alpha_count <= 8 and mixed_case_tokens >= 2:
        return True
    if alpha_count <= 10 and mixed_case_tokens >= 1 and uppercase_tokens >= 2:
        return True
    if alpha_count <= 8 and uppercase_tokens >= 1 and titlecase_tokens >= 2:
        return True
    if alpha_count <= 8 and uppercase_tokens >= 1 and re.search(r"\d", stripped) and not _looks_like_formula_or_equation(stripped):
        return True
    if alpha_count <= 8 and titlecase_tokens >= 4 and not stripped.endswith((".", "?", "!", ":")):
        return True
    if alpha_count <= 8 and symbol_ratio > 0.18 and not _looks_like_formula_or_equation(stripped):
        return True
    if alpha_count <= 8 and uppercase_ratio > 0.35 and mixed_case_tokens >= 1:
        return True
    return False


def _should_filter_ocr_noise(extraction: Dict[str, Any]) -> bool:
    source_kind = str(extraction.get("source_kind") or "").lower()
    extraction_method = str((extraction.get("metadata") or {}).get("extraction_method") or "").lower()

    return source_kind in {"scanned_pdf", "mixed_pdf", "image"} or extraction_method in {"ocr", "hybrid", "tesseract"}


def _filter_ocr_answer_noise(text: str) -> tuple[str, int]:
    kept_lines: List[str] = []
    removed_count = 0

    for raw_line in text.split("\n"):
        line = raw_line.rstrip()
        if _looks_like_ocr_answer_noise_line(line):
            removed_count += 1
            continue
        kept_lines.append(line)

    return "\n".join(kept_lines), removed_count


def normalize_text(text: str) -> str:
    """
    Apply conservative normalization.

    Goals:
    - unify line endings
    - trim trailing spaces
    - collapse excessive blank lines
    - preserve math/science notation as much as possible
    """
    if not text:
        return ""

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _replace_mojibake(text)

    lines = [line.rstrip() for line in text.split("\n")]

    cleaned_lines: List[str] = []
    blank_run = 0

    for line in lines:
        if line.strip() == "":
            blank_run += 1
            if blank_run <= 2:
                cleaned_lines.append("")
        else:
            blank_run = 0
            cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)

    # Collapse repeated spaces/tabs inside lines
    text = re.sub(r"[ \t]+", " ", text)

    # Fix spacing before punctuation like "Question 1 :" -> "Question 1:"
    text = re.sub(r"\s+([:;,])", r"\1", text)
    text = re.sub(r"[|]{2,}", "|", text)
    text = re.sub(r"[/]{2,}", "/", text)

    return text.strip()


def normalize_extraction(extraction: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize the raw extraction payload from PDF / DOCX / image reader.
    """
    normalized_segments: List[Dict[str, Any]] = []
    removed_noise_line_count = 0
    filter_ocr_noise = _should_filter_ocr_noise(extraction)

    for segment in extraction.get("segments", []):
        normalized_text = normalize_text(segment.get("text", ""))
        if filter_ocr_noise and normalized_text:
            normalized_text, removed_count = _filter_ocr_answer_noise(normalized_text)
            removed_noise_line_count += removed_count
            normalized_text = normalize_text(normalized_text)
        if normalized_text:
            updated_segment = dict(segment)
            updated_segment["text"] = normalized_text
            updated_segment["char_count"] = len(normalized_text)
            normalized_segments.append(updated_segment)

    normalized_full_text = "\n\n".join(
        segment["text"] for segment in normalized_segments
    ).strip()

    normalized = dict(extraction)
    normalized["text"] = normalized_full_text
    normalized["segments"] = normalized_segments

    metadata = dict(normalized.get("metadata", {}))
    metadata["normalized"] = True
    if filter_ocr_noise:
        metadata["ocr_noise_lines_removed"] = removed_noise_line_count
    normalized["metadata"] = metadata

    return normalized
