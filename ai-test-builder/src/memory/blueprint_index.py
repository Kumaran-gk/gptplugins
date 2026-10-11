from __future__ import annotations

from typing import Any, Dict, List


def build_blueprint_memory_record(blueprint: Dict[str, Any]) -> Dict[str, Any]:
    topic_distribution = blueprint.get("topic_distribution", []) or []
    top_topics = [item.get("topic") for item in topic_distribution[:5] if item.get("topic")]

    structure = blueprint.get("structure", {}) or {}
    sections = structure.get("sections", []) or []

    difficulty = blueprint.get("difficulty_profile", {}) or {}
    memory_metadata = blueprint.get("memory_metadata", {}) or {}
    cumulative_metadata = blueprint.get("cumulative_metadata", {}) or {}

    return {
        "record_type": "blueprint_summary",
        "blueprint_id": blueprint.get("blueprint_id"),
        "title": blueprint.get("title"),
        "subject": blueprint.get("subject"),
        "course_code": blueprint.get("course_code"),
        "unit_name": blueprint.get("unit", {}).get("unit_name"),
        "top_topics": top_topics,
        "section_titles": [section.get("title") for section in sections if section.get("title")],
        "test_type": structure.get("test_type"),
        "difficulty_profile": {
            "easy_pct": difficulty.get("easy_pct"),
            "medium_pct": difficulty.get("medium_pct"),
            "hard_pct": difficulty.get("hard_pct"),
        },
        "trap_types": [
            trap.get("trap_type")
            for trap in (blueprint.get("trap_patterns", []) or [])
            if trap.get("trap_type")
        ],
        "memory_tags": memory_metadata.get("tags", []),
        "teacher_style_signature": memory_metadata.get("teacher_style_signature", []),
        "summary_for_retrieval": memory_metadata.get("summary_for_retrieval"),
        "eligible_for_cumulative": cumulative_metadata.get("eligible_for_cumulative", False),
        "recommended_merge_tags": cumulative_metadata.get("recommended_merge_tags", []),
        "created_at": blueprint.get("created_at"),
    }


def build_generation_memory_record(
    *,
    blueprint: Dict[str, Any],
    version_label: str,
    student_test_path: str | None,
    teacher_test_path: str | None,
) -> Dict[str, Any]:
    return {
        "record_type": "generated_test_summary",
        "blueprint_id": blueprint.get("blueprint_id"),
        "title": blueprint.get("title"),
        "subject": blueprint.get("subject"),
        "unit_name": blueprint.get("unit", {}).get("unit_name"),
        "version_label": version_label,
        "student_test_path": student_test_path,
        "teacher_test_path": teacher_test_path,
        "top_topics": [
            item.get("topic")
            for item in (blueprint.get("topic_distribution", []) or [])[:5]
            if item.get("topic")
        ],
        "teacher_style_signature": (
            blueprint.get("memory_metadata", {}) or {}
        ).get("teacher_style_signature", []),
        "created_at": blueprint.get("created_at"),
    }


def build_cumulative_memory_record(
    *,
    subject: str,
    version_label: str,
    units: List[str],
    top_topics: List[str],
    student_test_path: str | None,
    teacher_test_path: str | None,
) -> Dict[str, Any]:
    return {
        "record_type": "cumulative_test_summary",
        "subject": subject,
        "version_label": version_label,
        "units": units,
        "top_topics": top_topics,
        "student_test_path": student_test_path,
        "teacher_test_path": teacher_test_path,
    }