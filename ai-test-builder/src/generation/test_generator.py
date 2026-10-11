from __future__ import annotations

from typing import Any, Dict, List, Set

from src.generation.content_grounding import select_snippets_for_topics
from src.generation.section_generator import infer_question_count, render_section


def summarize_blueprint_for_generation(blueprint: Dict[str, Any]) -> Dict[str, Any]:
    structure = blueprint.get("structure", {})
    sections = structure.get("sections", []) or []
    topic_distribution = blueprint.get("topic_distribution", []) or []
    difficulty = blueprint.get("difficulty_profile", {}) or {}
    question_style = blueprint.get("question_style", {}) or {}

    return {
        "title": blueprint.get("title"),
        "subject": blueprint.get("subject"),
        "course_code": blueprint.get("course_code"),
        "unit_name": blueprint.get("unit", {}).get("unit_name"),
        "test_type": structure.get("test_type"),
        "section_count": len(sections),
        "top_topics": [item.get("topic") for item in topic_distribution[:5]],
        "difficulty_profile": {
            "easy_pct": difficulty.get("easy_pct"),
            "medium_pct": difficulty.get("medium_pct"),
            "hard_pct": difficulty.get("hard_pct"),
        },
        "response_formats": question_style.get("response_formats", []),
        "common_verbs": question_style.get("common_verbs", []),
        "trap_count": len(blueprint.get("trap_patterns", []) or []),
    }


def build_generation_plan_stub(
    blueprint: Dict[str, Any],
    *,
    requested_version: str | None = None,
    content_bundle: Dict[str, Any] | None = None,
    complexity_mode: str | None = None,
) -> Dict[str, Any]:
    structure = blueprint.get("structure", {})
    sections = structure.get("sections", []) or []
    topic_distribution = blueprint.get("topic_distribution", []) or []
    difficulty = blueprint.get("difficulty_profile", {}) or {}
    question_style = blueprint.get("question_style", {}) or {}
    generation_rules = blueprint.get("generation_rules", {}) or {}
    subject_extensions = blueprint.get("subject_extensions", {}) or {}

    top_topics = [item.get("topic") for item in topic_distribution[:5] if item.get("topic")]
    section_topic_overrides = subject_extensions.get("section_topic_overrides", {}) or {}
    section_mark_overrides = subject_extensions.get("section_mark_overrides", {}) or {}
    section_prebuilt_questions = subject_extensions.get("section_prebuilt_questions", {}) or {}
    version_prebuilt_questions = (
        subject_extensions.get("version_prebuilt_questions", {}) or {}
    )
    requested_version_key = str(requested_version or "").strip().lower()
    version_section_prebuilt_questions = (
        version_prebuilt_questions.get(requested_version_key, {}) or {}
    )

    section_plans: List[Dict[str, Any]] = []
    for section in sections:
        section_id = section.get("section_id")
        section_topics = section_topic_overrides.get(section_id) or top_topics[:3]
        section_plan = {
            "section_id": section_id,
            "title": section.get("title"),
            "order": section.get("order"),
            "instructions": section.get("instructions"),
            "num_questions": section.get("num_questions"),
            "question_types": section.get("question_types", []),
            "marks": section.get("marks"),
            "question_marks": section_mark_overrides.get(section_id) or [],
            "prebuilt_questions": (
                version_section_prebuilt_questions.get(section_id)
                or section_prebuilt_questions.get(section_id)
                or []
            ),
            "timing_notes": section.get("timing_notes"),
            "target_topics": [topic for topic in section_topics if topic],
            "target_difficulty_profile": {
                "easy_pct": difficulty.get("easy_pct"),
                "medium_pct": difficulty.get("medium_pct"),
                "hard_pct": difficulty.get("hard_pct"),
            },
            "response_formats": question_style.get("response_formats", []),
            "style_constraints": {
                "common_verbs": question_style.get("common_verbs", []),
                "answer_style_expectations": question_style.get(
                    "answer_style_expectations", []
                ),
            },
            "complexity_mode": complexity_mode or "standard",
        }
        section_plan["source_snippets"] = select_snippets_for_topics(
            content_bundle,
            target_topics=section_plan["target_topics"],
            limit=3,
        )
        section_plan["estimated_question_count"] = (
            int(section.get("num_questions"))
            if isinstance(section.get("num_questions"), int) and section.get("num_questions", 0) > 0
            else infer_question_count(section_plan)
        )
        section_plans.append(section_plan)

    return {
        "blueprint_id": blueprint.get("blueprint_id"),
        "title": blueprint.get("title"),
        "subject": blueprint.get("subject"),
        "unit_name": blueprint.get("unit", {}).get("unit_name"),
        "version_label": requested_version or "v1",
        "preserve_structure": generation_rules.get("preserve_structure", True),
        "reuse_prohibited": generation_rules.get("reuse_prohibited", True),
        "variation_policy": generation_rules.get("variation_policy"),
        "section_plans": section_plans,
        "top_topics": top_topics,
        "complexity_mode": complexity_mode or "standard",
        "difficulty_profile": {
            "easy_pct": difficulty.get("easy_pct"),
            "medium_pct": difficulty.get("medium_pct"),
            "hard_pct": difficulty.get("hard_pct"),
        },
        "generation_constraints": generation_rules.get("constraints", []),
        "content_grounding_summary": (
            {
                "source_file_count": content_bundle.get("source_file_count"),
                "snippet_count": content_bundle.get("snippet_count"),
                "top_terms": content_bundle.get("top_terms", []),
            }
            if isinstance(content_bundle, dict)
            else None
        ),
    }


def render_student_test_markdown(
    blueprint: Dict[str, Any],
    generation_plan: Dict[str, Any],
) -> Dict[str, Any]:
    title = generation_plan.get("title") or blueprint.get("title") or "Generated Test"
    subject = blueprint.get("subject") or generation_plan.get("subject") or "Unknown Subject"
    course_code = blueprint.get("course_code")
    unit_name = blueprint.get("unit", {}).get("unit_name")
    version_label = generation_plan.get("version_label") or "v1"

    header_lines: List[str] = [
        f"# {title} - Student Version ({version_label})",
        "",
        f"**Subject:** {subject}",
    ]

    if course_code:
        header_lines.append(f"**Course Code:** {course_code}")
    if unit_name:
        header_lines.append(f"**Unit:** {unit_name}")
    content_grounding = generation_plan.get("content_grounding_summary") or {}
    if content_grounding.get("snippet_count"):
        header_lines.append(
            f"**Unit Content Grounding:** {content_grounding.get('snippet_count')} snippet(s) from {content_grounding.get('source_file_count')} file(s)"
        )

    header_lines.extend(
        [
            "",
            "**Instructions:** Answer all questions. Show full work where required. Write clearly and use appropriate notation.",
            "",
        ]
    )

    body_parts: List[str] = []
    all_question_records: List[Dict[str, Any]] = []
    used_signatures: Set[str] = set()

    next_question_number = 1
    for section_plan in generation_plan.get("section_plans", []):
        rendered = render_section(
            subject=subject,
            section_plan=section_plan,
            start_question_number=next_question_number,
            used_signatures=used_signatures,
            version_label=version_label,
        )
        body_parts.append(rendered["markdown"])
        all_question_records.extend(rendered["questions"])
        next_question_number = rendered["next_question_number"]

    markdown = "\n".join(header_lines) + "\n\n" + "\n\n".join(body_parts)

    return {
        "markdown": markdown.strip() + "\n",
        "question_records": all_question_records,
        "question_count": len(all_question_records),
    }


def render_teacher_test_markdown(
    blueprint: Dict[str, Any],
    generation_plan: Dict[str, Any],
    rendered_student: Dict[str, Any],
) -> Dict[str, Any]:
    title = generation_plan.get("title") or blueprint.get("title") or "Generated Test"
    subject = blueprint.get("subject") or generation_plan.get("subject") or "Unknown Subject"
    course_code = blueprint.get("course_code")
    unit_name = blueprint.get("unit", {}).get("unit_name")
    version_label = generation_plan.get("version_label") or "v1"

    lines: List[str] = [
        f"# {title} - Teacher Version / Answer Key ({version_label})",
        "",
        f"**Subject:** {subject}",
    ]

    if course_code:
        lines.append(f"**Course Code:** {course_code}")
    if unit_name:
        lines.append(f"**Unit:** {unit_name}")

    lines.extend(
        [
            "",
            "## Answer Key",
            "",
        ]
    )

    answer_key_records: List[Dict[str, Any]] = []

    for question in rendered_student.get("question_records", []):
        qnum = question.get("question_number")
        qtype = question.get("question_type")
        topic = question.get("topic")
        marks = question.get("marks")
        answer_hint = question.get("answer_hint") or "No answer hint recorded."

        lines.append(
            f"{qnum}. [{topic} | {qtype} | {marks} mark{'s' if marks != 1 else ''}] {answer_hint}"
        )

        answer_key_records.append(
            {
                "question_number": qnum,
                "topic": topic,
                "question_type": qtype,
                "marks": marks,
                "answer_hint": answer_hint,
            }
        )

    lines.append("")
    lines.append("## Student Paper Reference")
    lines.append("")
    lines.append(rendered_student["markdown"])

    return {
        "markdown": "\n".join(lines).strip() + "\n",
        "answer_key_records": answer_key_records,
        "question_count": len(answer_key_records),
    }
