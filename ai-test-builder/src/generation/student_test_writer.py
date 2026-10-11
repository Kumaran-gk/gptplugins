from __future__ import annotations

from pathlib import Path
from typing import Any


def _first_non_empty(*values: Any, default: Any = "") -> Any:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        return value
    return default


def _normalize_question_type(value: str) -> str:
    raw = (value or "").strip().lower()

    if raw in {"mc", "mcq", "multiple_choice", "multiple-choice"}:
        return "multiple_choice"
    if raw in {"short", "short_answer", "short-answer"}:
        return "short_answer"
    if raw in {"long", "long_answer", "long-answer", "written_response"}:
        return "long_answer"
    if raw in {"calculation", "numeric", "problem_solving", "problem-solving"}:
        return "calculation"

    return raw or "question"


def _format_marks(value: Any) -> str:
    if value in (None, "", 0):
        return ""
    return f" [{value} mark{'s' if value != 1 else ''}]"


def _topic_pool_from_blueprint(blueprint: dict[str, Any]) -> list[str]:
    topic_distribution = blueprint.get("topic_distribution") or blueprint.get("topics") or {}

    if isinstance(topic_distribution, dict):
        return [
            str(topic)
            for topic, _ in sorted(
                topic_distribution.items(),
                key=lambda item: item[1] if isinstance(item[1], (int, float)) else 0,
                reverse=True,
            )
        ]

    if isinstance(topic_distribution, list):
        topics: list[str] = []
        for item in topic_distribution:
            if isinstance(item, str):
                topics.append(item)
            elif isinstance(item, dict):
                name = item.get("topic") or item.get("name")
                if name:
                    topics.append(str(name))
        return topics

    return []


def _default_output_path(blueprint_path: str | Path) -> Path:
    blueprint_path = Path(blueprint_path)
    stem = blueprint_path.stem.replace("_blueprint", "")
    subject_folder = blueprint_path.parent.name
    return Path("data/generated") / subject_folder / f"{stem}_student_test.txt"


def _build_placeholder_prompt(
    *,
    q_number: int,
    q_type: str,
    topic: str,
    difficulty: str,
    marks: Any,
) -> str:
    mark_text = _format_marks(marks)
    difficulty_text = f" ({difficulty})" if difficulty else ""

    if q_type == "multiple_choice":
        return f"{q_number}. {topic}{difficulty_text}: Choose the best answer.{mark_text}"

    if q_type == "short_answer":
        return f"{q_number}. {topic}{difficulty_text}: Answer briefly and clearly.{mark_text}"

    if q_type == "calculation":
        return f"{q_number}. {topic}{difficulty_text}: Solve the problem. Show all necessary work.{mark_text}"

    if q_type == "long_answer":
        return f"{q_number}. {topic}{difficulty_text}: Answer fully and justify your reasoning.{mark_text}"

    return f"{q_number}. {topic}{difficulty_text}: Complete the question.{mark_text}"


def _default_mc_choices(topic: str) -> list[str]:
    return [
        f"A. Correct answer for {topic}",
        f"B. Common misconception about {topic}",
        f"C. Distractor based on partial understanding of {topic}",
        f"D. Distractor based on a typical error in {topic}",
    ]


def _render_answer_lines(count: int) -> list[str]:
    return ["_" * 80 for _ in range(max(1, count))]


def _render_question(
    question: dict[str, Any],
    *,
    q_number: int,
    fallback_topic: str,
    fallback_type: str,
    fallback_difficulty: str,
) -> list[str]:
    lines: list[str] = []

    q_type = _normalize_question_type(
        str(_first_non_empty(question.get("type"), fallback_type, default="question"))
    )
    topic = str(_first_non_empty(question.get("topic"), fallback_topic, default="General"))
    difficulty = str(_first_non_empty(question.get("difficulty"), fallback_difficulty, default=""))
    marks = _first_non_empty(question.get("marks"), question.get("mark"), default="")

    prompt = _first_non_empty(
        question.get("prompt"),
        question.get("question_text"),
        question.get("text"),
        default="",
    )

    if prompt:
        prompt_line = f"{q_number}. {prompt}{_format_marks(marks)}"
    else:
        prompt_line = _build_placeholder_prompt(
            q_number=q_number,
            q_type=q_type,
            topic=topic,
            difficulty=difficulty,
            marks=marks,
        )

    lines.append(prompt_line)

    if q_type == "multiple_choice":
        choices = question.get("choices") or question.get("options") or _default_mc_choices(topic)
        for choice in choices:
            lines.append(f"   {choice}")
    elif q_type == "short_answer":
        answer_lines = int(question.get("answer_lines", 3) or 3)
        lines.extend(_render_answer_lines(answer_lines))
    elif q_type in {"calculation", "long_answer"}:
        answer_lines = int(question.get("answer_lines", 6) or 6)
        lines.extend(_render_answer_lines(answer_lines))

    lines.append("")
    return lines


def _build_placeholder_questions_for_section(
    section: dict[str, Any],
    *,
    starting_number: int,
    topic_pool: list[str],
) -> tuple[list[dict[str, Any]], int]:
    questions: list[dict[str, Any]] = []

    count = _first_non_empty(
        section.get("question_count"),
        section.get("count"),
        section.get("num_questions"),
        default=0,
    )
    try:
        count = int(count)
    except (TypeError, ValueError):
        count = 0

    section_type = _normalize_question_type(str(section.get("question_type", "")))
    difficulty = str(section.get("difficulty", "")).strip()

    for i in range(count):
        topic = topic_pool[i % len(topic_pool)] if topic_pool else "General course content"
        questions.append(
            {
                "number": starting_number + i,
                "type": section_type,
                "topic": topic,
                "difficulty": difficulty,
                "marks": section.get("marks_per_question") or section.get("marks") or "",
            }
        )

    return questions, starting_number + count


def render_student_test_text(
    generation_plan: dict[str, Any],
    blueprint: dict[str, Any],
) -> str:
    metadata = generation_plan.get("metadata") or {}
    blueprint_meta = blueprint.get("metadata") or {}

    title = str(
        _first_non_empty(
            metadata.get("title"),
            blueprint.get("title"),
            blueprint_meta.get("title"),
            default="Generated Student Test",
        )
    )
    subject = str(
        _first_non_empty(
            metadata.get("subject"),
            blueprint.get("subject"),
            blueprint_meta.get("subject"),
            default="",
        )
    )
    course_code = str(
        _first_non_empty(
            metadata.get("course_code"),
            blueprint.get("course_code"),
            blueprint_meta.get("course_code"),
            default="",
        )
    )
    unit_name = str(
        _first_non_empty(
            metadata.get("unit_name"),
            blueprint.get("unit_name"),
            blueprint_meta.get("unit_name"),
            default="",
        )
    )
    total_marks = _first_non_empty(
        metadata.get("total_marks"),
        generation_plan.get("total_marks"),
        blueprint.get("total_marks"),
        default="",
    )
    time_limit = _first_non_empty(
        metadata.get("time_limit"),
        blueprint.get("time_limit"),
        default="",
    )

    instructions = (
        generation_plan.get("instructions")
        or blueprint.get("instructions")
        or [
            "Answer all questions.",
            "Show all necessary work.",
            "Read each question carefully before answering.",
        ]
    )

    if isinstance(instructions, str):
        instructions = [instructions]

    sections = (
        generation_plan.get("sections")
        or generation_plan.get("question_plan")
        or generation_plan.get("test_sections")
        or []
    )

    topic_pool = _topic_pool_from_blueprint(blueprint)

    lines: list[str] = []
    lines.append(title)
    lines.append("=" * len(title))
    lines.append("")

    if subject:
        lines.append(f"Subject: {subject}")
    if course_code:
        lines.append(f"Course: {course_code}")
    if unit_name:
        lines.append(f"Unit: {unit_name}")
    if total_marks not in ("", None):
        lines.append(f"Total Marks: {total_marks}")
    if time_limit not in ("", None):
        lines.append(f"Time: {time_limit}")

    lines.append("")
    lines.append("Name: ________________________________")
    lines.append("Date: _________________________________")
    lines.append("Teacher: ______________________________")
    lines.append("")

    lines.append("Instructions")
    lines.append("------------")
    for item in instructions:
        lines.append(f"- {item}")
    lines.append("")

    question_number = 1

    for section_index, section in enumerate(sections, start=1):
        section_title = str(
            _first_non_empty(
                section.get("title"),
                section.get("name"),
                default=f"Section {section_index}",
            )
        )
        section_instructions = section.get("instructions") or ""

        lines.append(section_title)
        lines.append("-" * len(section_title))

        if section_instructions:
            if isinstance(section_instructions, list):
                for item in section_instructions:
                    lines.append(f"* {item}")
            else:
                lines.append(str(section_instructions))
            lines.append("")

        questions = section.get("questions") or section.get("items") or []

        if not questions:
            questions, question_number = _build_placeholder_questions_for_section(
                section,
                starting_number=question_number,
                topic_pool=topic_pool,
            )
            for q in questions:
                lines.extend(
                    _render_question(
                        q,
                        q_number=int(q["number"]),
                        fallback_topic=str(q.get("topic", "General")),
                        fallback_type=str(q.get("type", "question")),
                        fallback_difficulty=str(q.get("difficulty", "")),
                    )
                )
            continue

        fallback_type = _normalize_question_type(str(section.get("question_type", "")))
        fallback_difficulty = str(section.get("difficulty", "")).strip()

        for i, question in enumerate(questions):
            fallback_topic = (
                topic_pool[i % len(topic_pool)] if topic_pool else "General course content"
            )
            lines.extend(
                _render_question(
                    question,
                    q_number=question_number,
                    fallback_topic=fallback_topic,
                    fallback_type=fallback_type,
                    fallback_difficulty=fallback_difficulty,
                )
            )
            question_number += 1

    lines.append("End of Test")
    lines.append("-----------")
    lines.append("")

    return "\n".join(lines)


def save_student_test_text(
    *,
    generation_plan: dict[str, Any],
    blueprint: dict[str, Any],
    blueprint_path: str | Path,
    output_path: str | Path | None = None,
) -> Path:
    output_file = Path(output_path) if output_path else _default_output_path(blueprint_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    content = render_student_test_text(generation_plan=generation_plan, blueprint=blueprint)
    output_file.write_text(content, encoding="utf-8")

    return output_file