from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Dict, List

from src.blueprint.subject_extensions import build_subject_extensions


def _slugify(value: str) -> str:
    return (
        value.strip()
        .lower()
        .replace("&", "and")
        .replace("/", "-")
        .replace("\\", "-")
        .replace(" ", "-")
    )


def _iso_utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _confidence_label_to_score(label: str | None) -> float:
    mapping = {
        "low": 0.45,
        "medium": 0.7,
        "high": 0.9,
    }
    return mapping.get((label or "").lower(), 0.6)


def _map_file_type_for_schema(file_type: str | None) -> str:
    value = (file_type or "").lower()
    if value in {"pdf", "docx", "txt"}:
        return value
    return "other"


def _clean_none_values(obj: Any) -> Any:
    if isinstance(obj, dict):
        cleaned = {}
        for key, value in obj.items():
            if value is None:
                continue
            cleaned_value = _clean_none_values(value)
            if cleaned_value is None:
                continue
            cleaned[key] = cleaned_value
        return cleaned

    if isinstance(obj, list):
        cleaned_list = []
        for item in obj:
            if item is None:
                continue
            cleaned_item = _clean_none_values(item)
            if cleaned_item is None:
                continue
            cleaned_list.append(cleaned_item)
        return cleaned_list

    return obj


def _build_source_files(extraction: Dict[str, Any]) -> List[Dict[str, Any]]:
    segments = extraction.get("segments", []) or []
    page_numbers = [
        segment["page_number"]
        for segment in segments
        if isinstance(segment, dict) and "page_number" in segment
    ]

    source_file = {
        "file_name": extraction.get("file_name", "unknown"),
        "file_type": _map_file_type_for_schema(extraction.get("file_type")),
        "path": extraction.get("file_path"),
    }

    if page_numbers:
        source_file["pages_used"] = sorted(set(page_numbers))

    return [_clean_none_values(source_file)]


def _infer_test_type(patterns: Dict[str, Any]) -> str:
    if patterns.get("multiple_choice_signals", {}).get("likely_multiple_choice_present"):
        return "mixed_assessment"

    section_titles = " ".join(
        section.get("title", "").lower()
        for section in patterns.get("section_candidates", []) or []
    )

    if "multiple choice" in section_titles and "application" in section_titles:
        return "mixed_assessment"
    if "multiple choice" in section_titles:
        return "multiple_choice_test"
    if "written" in section_titles or "application" in section_titles:
        return "written_test"

    return "unit_test"


def _infer_question_types_from_title(title: str) -> List[str]:
    lowered = title.lower()
    types: List[str] = []

    if "multiple choice" in lowered:
        types.append("multiple_choice")
    if "short answer" in lowered:
        types.append("short_answer")
    if "long answer" in lowered or "written" in lowered:
        types.append("written_response")
    if "application" in lowered:
        types.append("application")
    if "true/false" in lowered or "true false" in lowered:
        types.append("true_false")

    return types


SECTION_INSTRUCTION_RE = re.compile(r"\(([^()]{8,140})\)")


def _extract_section_instruction(title: str) -> str | None:
    matches = SECTION_INSTRUCTION_RE.findall(title or "")

    for match in matches:
        candidate = match.strip(" -|")
        lowered = candidate.lower()
        if any(
            keyword in lowered
            for keyword in [
                "use ",
                "show ",
                "answer ",
                "write ",
                "full sentences",
                "justify",
                "explain",
                "achieve full marks",
            ]
        ):
            return candidate

    return None


def _count_questions_for_section(
    section: Dict[str, Any],
    question_candidates: List[Dict[str, Any]],
) -> int | None:
    line_index = section.get("line_index")
    end_line = section.get("end_line")
    if not isinstance(line_index, int):
        return None

    count = 0
    for question in question_candidates:
        qline = question.get("line_index")
        if not isinstance(qline, int):
            continue
        if qline < line_index:
            continue
        if isinstance(end_line, int) and qline > end_line:
            continue
        count += 1

    return count or None


def _infer_sparse_section_question_count(
    *,
    section: Dict[str, Any],
    built_section: Dict[str, Any],
    detected_count: int | None,
) -> int | None:
    question_types = built_section.get("question_types", []) or []
    mark_hint = built_section.get("marks")
    score_total = section.get("score_total")
    title = str(built_section.get("title") or "").lower()

    if "multiple_choice" in question_types:
        inferred_total = None
        if isinstance(score_total, int) and score_total > 0:
            inferred_total = score_total
        elif isinstance(mark_hint, int) and mark_hint > 0 and detected_count in {None, 0}:
            inferred_total = mark_hint

        if inferred_total is not None and (detected_count is None or detected_count < max(5, inferred_total // 3)):
            return inferred_total

    if (
        "predicting products" in title
        and isinstance(mark_hint, int)
        and "instructions" not in title
    ):
        if detected_count is not None and detected_count >= 4:
            return max(detected_count, mark_hint // 4)
        return max(4, mark_hint // 4)

    return detected_count


def _build_sections(patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
    section_candidates = patterns.get("section_candidates", []) or []
    question_candidates = patterns.get("question_candidates", []) or []
    sections: List[Dict[str, Any]] = []

    if not section_candidates:
        main_section: Dict[str, Any] = {
            "section_id": "section_1",
            "title": "Main Section",
            "order": 1,
        }
        if question_candidates:
            main_section["num_questions"] = len(question_candidates)
        return [
            main_section
        ]

    for index, section in enumerate(section_candidates, start=1):
        built = {
            "section_id": f"section_{index}",
            "title": section.get("title") or f"Section {index}",
            "order": index,
        }

        mark_hint = section.get("mark_hint")
        if isinstance(mark_hint, int):
            built["marks"] = mark_hint

        section_instruction = _extract_section_instruction(built["title"])
        if section_instruction:
            built["instructions"] = section_instruction

        question_types = _infer_question_types_from_title(built["title"])
        if question_types:
            built["question_types"] = question_types

        section_question_count = _count_questions_for_section(section, question_candidates)
        inferred_section_question_count = _infer_sparse_section_question_count(
            section=section,
            built_section=built,
            detected_count=section_question_count,
        )
        if inferred_section_question_count is not None:
            built["num_questions"] = inferred_section_question_count
        elif section_question_count is not None:
            built["num_questions"] = section_question_count

        sections.append(built)

    return sections


def _build_topic_distribution(topics: Dict[str, Any]) -> List[Dict[str, Any]]:
    distribution: List[Dict[str, Any]] = []

    for item in topics.get("topic_distribution", []) or []:
        distribution.append(
            {
                "topic": item.get("topic", "unknown_topic"),
                "weight_pct": item.get("weight_pct", 0.0),
                "subtopics": item.get("matched_keywords", [])[:5],
            }
        )

    if not distribution:
        distribution.append(
            {
                "topic": "general_content",
                "weight_pct": 100.0,
                "subtopics": [],
            }
        )

    return distribution


def _extract_common_verbs(extraction: Dict[str, Any]) -> List[str]:
    text = (extraction.get("text", "") or "").lower()
    verb_pool = [
        "identify",
        "state",
        "name",
        "list",
        "calculate",
        "determine",
        "predict",
        "balance",
        "classify",
        "compare",
        "solve",
        "explain",
        "justify",
        "analyze",
        "evaluate",
    ]

    found = [verb for verb in verb_pool if verb in text]
    return found[:8]


def _build_question_style(
    extraction: Dict[str, Any],
    patterns: Dict[str, Any],
) -> Dict[str, Any]:
    stem_styles: List[str] = []
    response_formats: List[str] = []
    diagram_expectations: List[str] = []
    answer_style_expectations: List[str] = []

    if patterns.get("question_candidates"):
        stem_styles.append("numbered_questions")
    if _extract_common_verbs(extraction):
        stem_styles.append("command_verb_led")

    if patterns.get("multiple_choice_signals", {}).get("likely_multiple_choice_present"):
        response_formats.append("multiple_choice")

    section_titles = " ".join(
        section.get("title", "").lower()
        for section in patterns.get("section_candidates", []) or []
    )

    if "written" in section_titles or "application" in section_titles:
        response_formats.append("written_response")

    text = (extraction.get("text", "") or "").lower()

    if not response_formats:
        response_formats.append("constructed_response")

    if "full sentences" in text:
        answer_style_expectations.append("full_sentence_explanations")
    if "include states" in text:
        answer_style_expectations.append("notation_precision_required")

    if "diagram" in text or "graph" in text:
        diagram_expectations.append("diagram_or_visual_interpretation_possible")

    return {
        "stem_styles": list(dict.fromkeys(stem_styles)) or ["numbered_questions"],
        "response_formats": list(dict.fromkeys(response_formats)),
        "common_verbs": _extract_common_verbs(extraction),
        "wording_tone": "instructional_assessment",
        "diagram_expectations": diagram_expectations,
        "answer_style_expectations": answer_style_expectations,
    }


def _build_generation_rules(
    extraction: Dict[str, Any],
    topics: Dict[str, Any],
) -> Dict[str, Any]:
    text = (extraction.get("text", "") or "").lower()
    constraints: List[str] = []

    if "balance" in text:
        constraints.append("Preserve balancing-style chemistry questions.")
    if "type of reaction" in text or "reaction type" in text:
        constraints.append("Preserve reaction-classification tasks.")
    if "include states" in text:
        constraints.append("Preserve notation/state-symbol expectations.")
    if "application" in text:
        constraints.append("Include at least some application-oriented items.")

    top_topics = [item.get("topic", "") for item in topics.get("topic_distribution", [])[:3]]

    return {
        "preserve_structure": True,
        "reuse_prohibited": True,
        "variation_policy": "Preserve structure, topic weighting, and difficulty intent while generating fresh questions and contexts.",
        "freshness_requirements": [
            "Do not copy source questions verbatim.",
            "Use new surface contexts, values, or examples where appropriate.",
        ],
        "constraints": constraints + [f"Top detected topics: {', '.join([t for t in top_topics if t])}"],
    }


def _build_inferred_patterns(
    topics: Dict[str, Any],
    difficulty: Dict[str, Any],
    traps: Dict[str, Any],
) -> List[str]:
    inferred: List[str] = []

    topic_distribution = topics.get("topic_distribution", []) or []
    if topic_distribution:
        top_topic = topic_distribution[0]["topic"]
        inferred.append(f"The assessment likely emphasizes {top_topic}.")

    easy_pct = difficulty.get("easy_pct", 0.0)
    medium_pct = difficulty.get("medium_pct", 0.0)
    hard_pct = difficulty.get("hard_pct", 0.0)

    inferred.append(
        f"Estimated difficulty profile is easy={easy_pct}%, medium={medium_pct}%, hard={hard_pct}%."
    )

    if traps.get("trap_patterns"):
        inferred.append("The assessment likely uses precision and setup traps as part of its design.")

    return inferred


def build_blueprint_draft(
    *,
    subject: str,
    extraction: Dict[str, Any],
    patterns: Dict[str, Any],
    topics: Dict[str, Any],
    difficulty: Dict[str, Any],
    traps: Dict[str, Any],
) -> Dict[str, Any]:
    unit_name = topics.get("unit_name") or "Unknown Unit"
    course_code = topics.get("course_code")
    subject_slug = _slugify(subject)
    unit_slug = _slugify(unit_name)

    blueprint_id = f"{subject_slug}-{unit_slug}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

    observed_patterns = []
    observed_patterns.extend(patterns.get("observed_patterns", []))
    observed_patterns.extend(topics.get("observed_topic_signals", []))
    observed_patterns.extend(traps.get("observed_trap_signals", []))

    top_topic = "unknown"
    topic_distribution = topics.get("topic_distribution", []) or []
    if topic_distribution:
        top_topic = topic_distribution[0].get("topic", "unknown")

    teacher_style_signature = [
        f"test_type:{_infer_test_type(patterns)}",
        f"sections:{len(patterns.get('section_candidates', []))}",
        f"question_candidates:{len(patterns.get('question_candidates', []))}",
        f"top_topic:{top_topic}",
    ]

    blueprint: Dict[str, Any] = {
        "schema_version": "1.0",
        "blueprint_id": blueprint_id,
        "created_at": _iso_utc_now(),
        "title": unit_name if unit_name != "Unknown Unit" else extraction.get("file_name", "Untitled Blueprint"),
        "subject": subject,
        "unit": {
            "unit_name": unit_name,
            "chapter_refs": [],
            "learning_goals": [],
        },
        "source_files": _build_source_files(extraction),
        "analysis_summary": {
            "confidence": _confidence_label_to_score(difficulty.get("analysis_confidence")),
            "observed_patterns": list(dict.fromkeys(observed_patterns)),
            "inferred_patterns": _build_inferred_patterns(topics, difficulty, traps),
            "notes": "This blueprint was generated from heuristic extraction and analysis. Review recommended before production use.",
        },
        "structure": {
            "test_type": _infer_test_type(patterns),
            "sections": _build_sections(patterns),
            "ordering_rules": [
                "Preserve approximate section flow unless explicitly changed."
            ],
        },
        "topic_distribution": _build_topic_distribution(topics),
        "difficulty_profile": {
            "easy_pct": difficulty.get("easy_pct", 0.0),
            "medium_pct": difficulty.get("medium_pct", 0.0),
            "hard_pct": difficulty.get("hard_pct", 0.0),
            "progression_notes": difficulty.get("progression_notes", []),
            "cognitive_skills": difficulty.get("cognitive_skills", []),
        },
        "question_style": _build_question_style(extraction, patterns),
        "trap_patterns": traps.get("trap_patterns", []),
        "generation_rules": _build_generation_rules(extraction, topics),
        "memory_metadata": {
            "tags": [
                subject_slug,
                _slugify(course_code) if course_code else None,
                unit_slug,
            ],
            "summary_for_retrieval": f"{subject} blueprint for {unit_name} with emphasis on detected topic weighting and teacher-style structure.",
            "teacher_style_signature": [item for item in teacher_style_signature if item],
        },
        "cumulative_metadata": {
            "eligible_for_cumulative": True,
            "prerequisite_topics": [item["topic"] for item in _build_topic_distribution(topics)[:3]],
            "recommended_merge_tags": [
                subject_slug,
                unit_slug,
            ],
        },
        "subject_extensions": build_subject_extensions(extraction, subject=subject),
    }

    if course_code:
        blueprint["course_code"] = course_code

    return _clean_none_values(blueprint)
