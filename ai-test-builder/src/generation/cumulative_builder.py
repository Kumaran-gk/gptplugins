from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Set

from src.generation.section_generator import render_section


def _unique_preserve_order(values: List[str]) -> List[str]:
    return list(dict.fromkeys([value for value in values if value]))


def _blueprint_topic_priority(blueprint: Dict[str, Any], *, limit: int = 4) -> List[str]:
    topic_distribution = blueprint.get("topic_distribution", []) or []
    prioritized = sorted(
        topic_distribution,
        key=lambda item: float(item.get("weight_pct", 0.0) or 0.0),
        reverse=True,
    )
    topics = [item.get("topic") for item in prioritized if item.get("topic")]
    return _unique_preserve_order(topics)[:limit]


def _balanced_topics_for_cumulative(
    blueprints: List[Dict[str, Any]],
    *,
    limit: int = 6,
    unit_weights: Dict[str, float] | None = None,
) -> List[str]:
    topic_rows: List[List[str]] = []
    row_weights: List[int] = []

    for blueprint in blueprints:
        unit_name = blueprint.get("unit", {}).get("unit_name")
        topic_rows.append(_blueprint_topic_priority(blueprint, limit=limit))

        unit_weight = None
        if unit_weights and unit_name:
            unit_weight = unit_weights.get(unit_name)

        repeat_count = 1
        if unit_weight and unit_weight > 0:
            repeat_count = max(1, int(round(unit_weight / 25.0)))
        row_weights.append(repeat_count)

    balanced: List[str] = []
    row_positions = [0 for _ in topic_rows]

    while len(balanced) < limit:
        progress_made = False
        for row_index, row in enumerate(topic_rows):
            added_for_row = 0
            while (
                row_positions[row_index] < len(row)
                and added_for_row < row_weights[row_index]
            ):
                topic = row[row_positions[row_index]]
                row_positions[row_index] += 1
                if topic in balanced:
                    continue
                balanced.append(topic)
                added_for_row += 1
                progress_made = True
                if len(balanced) >= limit:
                    return balanced
        if not progress_made:
            break

    return balanced[:limit]


def _topics_for_section(top_topics: List[str], *, offset: int, count: int = 4) -> List[str]:
    if not top_topics:
        return []

    rotated = top_topics[offset:] + top_topics[:offset]
    return rotated[: min(count, len(rotated))]


def summarize_blueprints_for_cumulative(blueprints: List[Dict[str, Any]]) -> Dict[str, Any]:
    units = []
    subjects = []
    total_sections = 0
    topic_totals: Dict[str, float] = defaultdict(float)

    for blueprint in blueprints:
        subjects.append(blueprint.get("subject"))
        unit_name = blueprint.get("unit", {}).get("unit_name")
        if unit_name:
            units.append(unit_name)

        sections = blueprint.get("structure", {}).get("sections", []) or []
        total_sections += len(sections)

        for topic in blueprint.get("topic_distribution", []) or []:
            topic_name = topic.get("topic")
            weight = float(topic.get("weight_pct", 0.0) or 0.0)
            if topic_name:
                topic_totals[topic_name] += weight

    sorted_topics = sorted(topic_totals.items(), key=lambda item: item[1], reverse=True)

    return {
        "blueprint_count": len(blueprints),
        "subjects": list(dict.fromkeys([item for item in subjects if item])),
        "units": _unique_preserve_order(units),
        "total_sections": total_sections,
        "top_topics": [topic for topic, _ in sorted_topics[:8]],
    }


def build_cumulative_generation_plan_stub(
    blueprints: List[Dict[str, Any]],
    *,
    requested_version: str | None = None,
    unit_weights: Dict[str, float] | None = None,
) -> Dict[str, Any]:
    summary = summarize_blueprints_for_cumulative(blueprints)

    topic_totals: Dict[str, float] = defaultdict(float)
    unit_allocations: List[Dict[str, Any]] = []
    for blueprint in blueprints:
        unit_name = blueprint.get("unit", {}).get("unit_name")
        unit_topics = _blueprint_topic_priority(blueprint, limit=4)

        for topic in blueprint.get("topic_distribution", []) or []:
            topic_name = topic.get("topic")
            weight = float(topic.get("weight_pct", 0.0) or 0.0)
            if topic_name:
                topic_totals[topic_name] += weight

        unit_allocations.append(
            {
                "unit_name": unit_name,
                "weight_pct": (unit_weights or {}).get(unit_name),
                "top_topics": unit_topics,
                "section_count": len(blueprint.get("structure", {}).get("sections", []) or []),
            }
        )

    top_topics = _balanced_topics_for_cumulative(
        blueprints,
        limit=6,
        unit_weights=unit_weights,
    )
    if not top_topics:
        sorted_topics = sorted(topic_totals.items(), key=lambda item: item[1], reverse=True)
        top_topics = [topic for topic, _ in sorted_topics[:6]]

    has_multiple_choice = False
    has_written = False
    has_application = False

    for blueprint in blueprints:
        for section in blueprint.get("structure", {}).get("sections", []) or []:
            question_types = [item.lower() for item in (section.get("question_types", []) or [])]
            title = (section.get("title") or "").lower()

            if "multiple_choice" in question_types or "multiple choice" in title:
                has_multiple_choice = True
            if "written_response" in question_types or "written" in title:
                has_written = True
            if "application" in question_types or "application" in title:
                has_application = True

    section_plans: List[Dict[str, Any]] = []

    if has_multiple_choice:
        section_plans.append(
            {
                "section_id": "cumulative_section_1",
                "title": "Cumulative Multiple Choice Review",
                "order": 1,
                "question_types": ["multiple_choice"],
                "target_topics": _topics_for_section(top_topics, offset=0),
                "source_units": summary["units"],
                "estimated_question_count": 8,
            }
        )

    if has_written:
        section_plans.append(
            {
                "section_id": "cumulative_section_2",
                "title": "Cumulative Written Response",
                "order": len(section_plans) + 1,
                "question_types": ["written_response"],
                "target_topics": _topics_for_section(top_topics, offset=1),
                "source_units": summary["units"],
                "estimated_question_count": 4,
            }
        )

    if has_application or not section_plans:
        section_plans.append(
            {
                "section_id": f"cumulative_section_{len(section_plans) + 1}",
                "title": "Applications and Synthesis",
                "order": len(section_plans) + 1,
                "question_types": ["application"],
                "target_topics": _topics_for_section(top_topics, offset=2),
                "source_units": summary["units"],
                "estimated_question_count": 3,
            }
        )

    return {
        "version_label": requested_version or "v1",
        "blueprint_count": len(blueprints),
        "units": summary["units"],
        "top_topics": top_topics,
        "unit_weights": unit_weights or {},
        "unit_allocations": unit_allocations,
        "section_plans": section_plans,
        "merge_strategy": (
            "weighted_unit_topic_round_robin" if unit_weights else "balanced_unit_topic_round_robin"
        ),
        "notes": [
            "This cumulative plan interleaves major topics across supplied blueprints.",
            "It aims to preserve unit representation before repeating dominant topics.",
            "Later steps should generate actual cumulative questions from this plan.",
        ],
    }


def render_cumulative_student_markdown(
    *,
    subject: str,
    cumulative_plan: Dict[str, Any],
) -> Dict[str, Any]:
    version_label = cumulative_plan.get("version_label") or "v1"
    units = cumulative_plan.get("units", []) or []
    top_topics = cumulative_plan.get("top_topics", []) or []

    header_lines: List[str] = [
        f"# {subject.title()} Cumulative Test - Student Version ({version_label})",
        "",
        f"**Subject:** {subject}",
        f"**Units Included:** {', '.join(units) if units else 'Multiple units'}",
        "",
        "**Instructions:** Answer all questions. Show full work where required. Write clearly and use appropriate notation.",
    ]

    if top_topics:
        header_lines.extend(
            [
                "",
                f"**Major Topic Emphasis:** {', '.join(top_topics)}",
            ]
        )

    unit_weights = cumulative_plan.get("unit_weights", {}) or {}
    if unit_weights:
        header_lines.extend(
            [
                f"**Unit Weighting:** {', '.join(f'{unit}: {weight:g}%' for unit, weight in unit_weights.items())}",
            ]
        )

    body_parts: List[str] = []
    question_records: List[Dict[str, Any]] = []
    used_signatures: Set[str] = set()

    next_question_number = 1
    for section_plan in cumulative_plan.get("section_plans", []):
        rendered = render_section(
            subject=subject,
            section_plan=section_plan,
            start_question_number=next_question_number,
            used_signatures=used_signatures,
            version_label=version_label,
        )
        body_parts.append(rendered["markdown"])
        question_records.extend(rendered["questions"])
        next_question_number = rendered["next_question_number"]

    markdown = "\n".join(header_lines).strip() + "\n\n" + "\n\n".join(body_parts)

    return {
        "markdown": markdown.strip() + "\n",
        "question_records": question_records,
        "question_count": len(question_records),
    }


def render_cumulative_teacher_markdown(
    *,
    subject: str,
    cumulative_plan: Dict[str, Any],
    rendered_student: Dict[str, Any],
) -> Dict[str, Any]:
    version_label = cumulative_plan.get("version_label") or "v1"
    units = cumulative_plan.get("units", []) or []

    lines: List[str] = [
        f"# {subject.title()} Cumulative Test - Teacher Version / Answer Key ({version_label})",
        "",
        f"**Subject:** {subject}",
        f"**Units Included:** {', '.join(units) if units else 'Multiple units'}",
        "",
        "## Cumulative Answer Key",
        "",
    ]

    unit_weights = cumulative_plan.get("unit_weights", {}) or {}
    if unit_weights:
        lines[5:5] = [
            f"**Unit Weighting:** {', '.join(f'{unit}: {weight:g}%' for unit, weight in unit_weights.items())}",
            "",
        ]

    answer_key_records: List[Dict[str, Any]] = []

    for question in rendered_student.get("question_records", []):
        qnum = question.get("question_number")
        topic = question.get("topic")
        qtype = question.get("question_type")
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

    lines.extend(
        [
            "",
            "## Student Paper Reference",
            "",
            rendered_student["markdown"],
        ]
    )

    return {
        "markdown": "\n".join(lines).strip() + "\n",
        "answer_key_records": answer_key_records,
        "question_count": len(answer_key_records),
    }
