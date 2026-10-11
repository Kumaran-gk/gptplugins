from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


SECTION_HEADER_RE = re.compile(
    r"^\s*(section|part)\s+([A-Za-z0-9]+)\s*[:\-]?\s*(.*)$",
    re.IGNORECASE,
)
SCORED_SECTION_HEADER_RE = re.compile(
    r"^\s*(multiple choice|short answer|written response|application questions?|essay)\s+(\d{1,3})\s*/\s*(\d{1,3})\s*$",
    re.IGNORECASE,
)

QUESTION_HEADER_PATTERNS = [
    re.compile(r"^\s*question\s+(\d{1,3})\s*[:.\-)]\s*(.*)$", re.IGNORECASE),
    re.compile(r"^\s*\d{1,3}[^\d]{1,6}(\d{1,3})\s*[:.\-,)]\s*(.*)$", re.IGNORECASE),
    re.compile(r"^\s*[^\d]{0,12}(\d{1,3})\s*[:.\-,)]\s*(.*)$", re.IGNORECASE),
    re.compile(r"^\s*[^\d]{0,12}(\d{1,3})\.(.*)$", re.IGNORECASE),
]

MC_OPTION_INLINE_RE = re.compile(r"(?:\(|\b)([A-D])(?:\)|[.)])")
MC_OPTION_LINE_RE = re.compile(r"^\s*([A-D])[\).]\s+")
MARK_PATTERNS = [
    re.compile(r"\((\d+)\s*marks?\)", re.IGNORECASE),
    re.compile(r"\((\d+)\s*m\)", re.IGNORECASE),
    re.compile(r"\b(\d+)\s*marks?\b", re.IGNORECASE),
]

SECTION_KEYWORDS = [
    "multiple choice",
    "short answer",
    "long answer",
    "application question",
    "application questions",
    "free response",
    "true/false",
    "matching",
    "written response",
    "essay",
]

TITLE_SKIP_PATTERNS = [
    re.compile(r"^\s*\d+\s*[:.\-)]"),
    re.compile(r"^\s*question\s+\d+", re.IGNORECASE),
    re.compile(r"^\s*(section|part)\s+", re.IGNORECASE),
]
TITLE_LABEL_PATTERNS = [
    re.compile(r"^\s*name\s*:", re.IGNORECASE),
    re.compile(r"^\s*date\s*:", re.IGNORECASE),
    re.compile(r"^\s*teacher\s*:", re.IGNORECASE),
]
COURSE_OR_TEST_RE = re.compile(
    r"\b([A-Z]{3}\d[A-Z]\b|unit\b|chapter\b|test\b|exam\b|quiz\b)",
    re.IGNORECASE,
)
MARKED_SECTION_LINE_RE = re.compile(r"\((\d+)\s*marks?\)", re.IGNORECASE)
QUESTION_LIKE_SECTION_SKIP_RE = re.compile(
    r"\b(include|balance|predict|explain|describe|compare|determine|calculate|solve)\b",
    re.IGNORECASE,
)


def _clean_display_text(line: str) -> str:
    text = line.strip()
    text = re.sub(r"^[^A-Za-z0-9(]+", "", text)
    text = re.sub(r"[^A-Za-z0-9)\]]+$", "", text)
    text = re.sub(r"\s+", " ", text)
    text = text.strip(" -|/")
    return text.strip()


def _looks_like_noise_line(line: str) -> bool:
    if not line:
        return True

    alnum_count = sum(1 for char in line if char.isalnum())
    alpha_count = sum(1 for char in line if char.isalpha())
    non_space_count = sum(1 for char in line if not char.isspace())

    if non_space_count == 0:
        return True
    if alpha_count == 0 and alnum_count < 3:
        return True

    symbol_count = non_space_count - alnum_count
    return symbol_count > max(6, alnum_count * 1.2)


def _split_lines(text: str) -> List[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _extract_mark_value(text: str) -> Optional[int]:
    for pattern in MARK_PATTERNS:
        match = pattern.search(text)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return None
    return None


def _guess_title(lines: List[str]) -> Optional[str]:
    strong_candidates: List[str] = []

    for line in lines[:12]:
        cleaned = _clean_display_text(line)
        if len(cleaned) < 3 or len(cleaned) > 140:
            continue
        if any(pattern.search(cleaned) for pattern in TITLE_SKIP_PATTERNS):
            continue
        if any(pattern.search(cleaned) for pattern in TITLE_LABEL_PATTERNS):
            continue
        if _looks_like_noise_line(cleaned):
            continue
        if COURSE_OR_TEST_RE.search(cleaned):
            strong_candidates.append(cleaned)
            continue
        if not strong_candidates:
            strong_candidates.append(cleaned)

    return strong_candidates[0] if strong_candidates else None


def _detect_section_candidates(lines: List[str]) -> List[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []

    for idx, line in enumerate(lines, start=1):
        scored_section_match = SCORED_SECTION_HEADER_RE.match(line)
        if scored_section_match:
            title = scored_section_match.group(1).strip().title()
            score_observed = int(scored_section_match.group(2))
            score_total = int(scored_section_match.group(3))
            candidates.append(
                {
                    "title": title,
                    "line_index": idx,
                    "mark_hint": score_total,
                    "score_observed": score_observed,
                    "score_total": score_total,
                    "evidence": line,
                    "detection_type": "scored_section_header",
                }
            )
            continue

        section_match = SECTION_HEADER_RE.match(line)
        if section_match:
            section_type = section_match.group(1).strip()
            section_id = section_match.group(2).strip()
            remainder = _clean_display_text(section_match.group(3).strip())
            title = f"{section_type.title()} {section_id}".strip()
            if remainder:
                title = f"{title} - {remainder}"

            candidates.append(
                {
                    "title": title,
                    "line_index": idx,
                    "mark_hint": _extract_mark_value(line),
                    "evidence": line,
                    "detection_type": "explicit_section_header",
                }
            )
            continue

        lowered = line.lower()
        if any(keyword in lowered for keyword in SECTION_KEYWORDS):
            cleaned_line = _clean_display_text(line)
            candidates.append(
                {
                    "title": cleaned_line or line,
                    "line_index": idx,
                    "mark_hint": _extract_mark_value(line),
                    "evidence": line,
                    "detection_type": "keyword_section_header",
                }
            )
            continue

        cleaned_line = _clean_display_text(line)
        alpha_tokens = re.findall(r"[A-Za-z]+", cleaned_line)
        if (
            cleaned_line
            and len(cleaned_line) <= 100
            and len(alpha_tokens) >= 4
            and MARKED_SECTION_LINE_RE.search(cleaned_line)
            and not QUESTION_LIKE_SECTION_SKIP_RE.search(cleaned_line)
            and not any(pattern.match(cleaned_line) for pattern in QUESTION_HEADER_PATTERNS)
            and not cleaned_line.lower().startswith(("total:", "bonus:"))
        ):
            candidates.append(
                {
                    "title": cleaned_line,
                    "line_index": idx,
                    "mark_hint": _extract_mark_value(cleaned_line),
                    "evidence": line,
                    "detection_type": "mark_based_section_header",
                }
            )

    # Deduplicate by line index
    deduped: List[Dict[str, Any]] = []
    seen = set()
    for item in candidates:
        key = (item["line_index"], item["title"])
        if key not in seen:
            seen.add(key)
            deduped.append(item)

    # Add end_line based on next section
    for i, section in enumerate(deduped):
        if i + 1 < len(deduped):
            next_line = deduped[i + 1]["line_index"]
            section["end_line"] = (
                next_line - 1 if next_line > section["line_index"] else section["line_index"]
            )
        else:
            section["end_line"] = len(lines)

    return deduped


def _guess_question_type(line: str) -> str:
    lowered = line.lower()

    if "multiple choice" in lowered:
        return "multiple_choice"
    if "true or false" in lowered or "true/false" in lowered:
        return "true_false"
    if "match" in lowered:
        return "matching"
    if "explain" in lowered or "describe" in lowered:
        return "written_response"
    if "calculate" in lowered or "determine" in lowered or "solve" in lowered:
        return "calculation_or_solution"
    return "unknown"


def _is_plausible_question_candidate(line: str, remainder: str, *, mark_hint: Optional[int]) -> bool:
    cleaned_remainder = _clean_display_text(remainder)
    if mark_hint is not None:
        return True
    if len(cleaned_remainder) < 6:
        return False
    if re.search(r"(->|=|>|<|\([a-z]{1,3}\)|[A-Za-z]{1,3}\d[A-Za-z0-9]*)", line):
        return True
    alpha_tokens = re.findall(r"[A-Za-z]+", cleaned_remainder)
    if len(alpha_tokens) >= 4:
        return True
    if QUESTION_LIKE_SECTION_SKIP_RE.search(cleaned_remainder):
        return True
    return False


def _detect_question_candidates(lines: List[str]) -> List[Dict[str, Any]]:
    questions: List[Dict[str, Any]] = []

    for idx, line in enumerate(lines, start=1):
        if len(line) > 220:
            continue

        matched = None
        for pattern in QUESTION_HEADER_PATTERNS:
            matched = pattern.match(line)
            if matched:
                break

        if not matched:
            continue

        try:
            question_number = int(matched.group(1))
        except ValueError:
            continue

        remainder = matched.group(2).strip() if matched.lastindex and matched.lastindex >= 2 else ""
        mark_hint = _extract_mark_value(line)
        if not _is_plausible_question_candidate(line, remainder, mark_hint=mark_hint):
            continue
        questions.append(
            {
                "question_number": question_number,
                "line_index": idx,
                "raw_header": line,
                "mark_hint": mark_hint,
                "question_type_guess": _guess_question_type(line),
                "preview": remainder[:120],
            }
        )

    # Deduplicate repeated OCR hits
    deduped: List[Dict[str, Any]] = []
    seen_numbers_at_lines = set()
    for item in questions:
        key = (item["question_number"], item["line_index"])
        if key not in seen_numbers_at_lines:
            seen_numbers_at_lines.add(key)
            deduped.append(item)

    return deduped


def _build_numbering_summary(questions: List[Dict[str, Any]]) -> Dict[str, Any]:
    numbers = [item["question_number"] for item in questions]
    unique_numbers = sorted(set(numbers))

    if not unique_numbers:
        return {
            "question_count_estimate": 0,
            "unique_question_numbers": [],
            "is_strictly_increasing": False,
            "gaps": [],
            "min_question_number": None,
            "max_question_number": None,
        }

    gaps: List[int] = []
    for i in range(len(unique_numbers) - 1):
        current_num = unique_numbers[i]
        next_num = unique_numbers[i + 1]
        if next_num != current_num + 1:
            gaps.extend(list(range(current_num + 1, next_num)))

    is_strictly_increasing = numbers == sorted(numbers)

    return {
        "question_count_estimate": len(unique_numbers),
        "unique_question_numbers": unique_numbers,
        "is_strictly_increasing": is_strictly_increasing,
        "gaps": gaps,
        "min_question_number": unique_numbers[0],
        "max_question_number": unique_numbers[-1],
    }


def _detect_multiple_choice_signals(lines: List[str]) -> Dict[str, Any]:
    option_line_count = 0
    inline_option_line_count = 0
    example_lines: List[str] = []

    for line in lines:
        if MC_OPTION_LINE_RE.search(line):
            option_line_count += 1
            if len(example_lines) < 5:
                example_lines.append(line)
            continue

        inline_matches = MC_OPTION_INLINE_RE.findall(line)
        if len(inline_matches) >= 2:
            inline_option_line_count += 1
            if len(example_lines) < 5:
                example_lines.append(line)

    likely_multiple_choice_present = (option_line_count + inline_option_line_count) > 0

    return {
        "likely_multiple_choice_present": likely_multiple_choice_present,
        "option_line_count": option_line_count,
        "inline_option_line_count": inline_option_line_count,
        "example_lines": example_lines,
    }


def _build_layout_signals(lines: List[str]) -> Dict[str, Any]:
    first_lines = lines[:20]
    title_candidate = _guess_title(lines)

    has_total_marks = any("total:" in line.lower() or "total marks" in line.lower() for line in first_lines)
    has_written_test_phrase = any("written test" in line.lower() for line in first_lines)
    mark_mentions_count = sum(1 for line in lines if _extract_mark_value(line) is not None)

    return {
        "title_candidate": title_candidate,
        "has_total_marks_signal": has_total_marks,
        "has_written_test_signal": has_written_test_phrase,
        "mark_mentions_count": mark_mentions_count,
        "line_count": len(lines),
    }


def _build_observed_patterns(
    sections: List[Dict[str, Any]],
    questions: List[Dict[str, Any]],
    numbering: Dict[str, Any],
    mc_signals: Dict[str, Any],
    layout: Dict[str, Any],
) -> List[str]:
    observed: List[str] = []

    if layout.get("title_candidate"):
        observed.append(f"Possible title detected: {layout['title_candidate']}")

    if sections:
        observed.append(f"Detected approximately {len(sections)} section candidate(s).")

    if numbering["question_count_estimate"] > 0:
        observed.append(
            f"Detected question numbering up to about {numbering['max_question_number']}."
        )

    if numbering["gaps"]:
        observed.append(f"Question numbering gaps detected: {numbering['gaps']}")

    if mc_signals["likely_multiple_choice_present"]:
        observed.append("Multiple-choice option patterns detected.")

    if layout["has_total_marks_signal"]:
        observed.append("A total marks signal appears near the start of the test.")

    if layout["has_written_test_signal"]:
        observed.append("A written test phrase appears near the start of the test.")

    if not observed:
        observed.append("Only weak structural signals were detected.")

    return observed


def extract_patterns_from_extraction(extraction: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract reusable structural patterns from normalized extraction output.
    """
    text = extraction.get("text", "") or ""
    lines = _split_lines(text)

    sections = _detect_section_candidates(lines)
    questions = _detect_question_candidates(lines)
    numbering = _build_numbering_summary(questions)
    mc_signals = _detect_multiple_choice_signals(lines)
    layout = _build_layout_signals(lines)
    observed_patterns = _build_observed_patterns(
        sections=sections,
        questions=questions,
        numbering=numbering,
        mc_signals=mc_signals,
        layout=layout,
    )

    return {
        "file_name": extraction.get("file_name"),
        "file_type": extraction.get("file_type"),
        "source_kind": extraction.get("source_kind"),
        "section_candidates": sections,
        "question_candidates": questions,
        "numbering_patterns": numbering,
        "multiple_choice_signals": mc_signals,
        "layout_signals": layout,
        "observed_patterns": observed_patterns,
    }
