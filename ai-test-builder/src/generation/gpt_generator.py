from __future__ import annotations

import json
import os
from typing import Any, Dict, List

from src.generation.section_generator import (
    infer_question_count,
    _default_marks_for_type,
    _normalize_question_type,
)


def _response_text(response: Any) -> str:
    text = getattr(response, "output_text", None)
    if text:
        return str(text)
    if isinstance(response, dict) and response.get("output_text"):
        return str(response["output_text"])
    raise ValueError("OpenAI response did not contain output_text.")


def _extract_json_payload(text: str) -> Dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        parts = stripped.split("```")
        for part in parts:
            candidate = part.strip()
            if candidate.startswith("json"):
                candidate = candidate[4:].strip()
            if candidate.startswith("{"):
                return json.loads(candidate)
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("GPT response did not contain a JSON object.")
    return json.loads(stripped[start : end + 1])


def _prompt_for_section(
    *,
    blueprint: Dict[str, Any],
    generation_plan: Dict[str, Any],
    section_plan: Dict[str, Any],
) -> str:
    source_snippets = section_plan.get("source_snippets", []) or []
    snippet_lines = [
        f"- {snippet.get('excerpt')}"
        for snippet in source_snippets
        if snippet.get("excerpt")
    ]
    if not snippet_lines:
        snippet_lines = ["- No unit-content snippet was provided for this section."]

    question_count = infer_question_count(section_plan)
    question_types = section_plan.get("question_types", []) or ["written_response"]

    return (
        "You are generating a fresh classroom assessment section.\n"
        "Return JSON only, with no markdown fences or commentary.\n\n"
        "Requirements:\n"
        f"- Subject: {blueprint.get('subject')}\n"
        f"- Course code: {blueprint.get('course_code')}\n"
        f"- Unit: {(blueprint.get('unit') or {}).get('unit_name')}\n"
        f"- Test title: {blueprint.get('title')}\n"
        f"- Version label: {generation_plan.get('version_label')}\n"
        f"- Section title: {section_plan.get('title')}\n"
        f"- Question count: {question_count}\n"
        f"- Allowed question types: {', '.join(question_types)}\n"
        f"- Target topics: {', '.join(section_plan.get('target_topics', []))}\n"
        f"- Instructions: {section_plan.get('instructions') or 'None'}\n"
        f"- Marks for section: {section_plan.get('marks') or 'Not specified'}\n"
        f"- Common verbs: {', '.join((section_plan.get('style_constraints') or {}).get('common_verbs', []))}\n"
        f"- Answer style expectations: {', '.join((section_plan.get('style_constraints') or {}).get('answer_style_expectations', []))}\n"
        "- Preserve structure and difficulty intent from the section plan.\n"
        "- Use the unit-content snippets as the factual source base.\n"
        "- Do not copy the source test verbatim.\n"
        "- Produce classroom-ready questions and answer hints.\n\n"
        "Unit-content snippets:\n"
        + "\n".join(snippet_lines)
        + "\n\n"
        "Return exactly this JSON shape:\n"
        '{\n'
        '  "questions": [\n'
        '    {\n'
        '      "question_type": "multiple_choice or written_response or application",\n'
        '      "topic": "topic name",\n'
        '      "marks": 1,\n'
        '      "stem": "full question text",\n'
        '      "options": ["A. ...", "B. ...", "C. ...", "D. ..."],\n'
        '      "answer_hint": "short answer key or marking note",\n'
        '      "source_excerpt": "which snippet informed this question"\n'
        '    }\n'
        '  ]\n'
        '}\n'
    )


def _normalize_gpt_questions(
    *,
    section_plan: Dict[str, Any],
    payload: Dict[str, Any],
) -> List[Dict[str, Any]]:
    question_count = infer_question_count(section_plan)
    items = payload.get("questions", []) or []
    normalized: List[Dict[str, Any]] = []

    fallback_type = _normalize_question_type(
        ((section_plan.get("question_types") or ["written_response"])[0])
    )
    fallback_topic = (
        (section_plan.get("target_topics") or ["general_content"])[0]
    )

    for item in items[:question_count]:
        question_type = _normalize_question_type(
            str(item.get("question_type") or fallback_type)
        )
        marks = item.get("marks")
        try:
            marks = int(marks)
        except (TypeError, ValueError):
            marks = _default_marks_for_type(question_type)

        options = item.get("options") or []
        if question_type != "multiple_choice":
            options = []

        normalized.append(
            {
                "question_type": question_type,
                "topic": str(item.get("topic") or fallback_topic),
                "marks": marks,
                "stem": str(item.get("stem") or "").strip(),
                "options": [str(option).strip() for option in options if str(option).strip()],
                "answer_hint": str(item.get("answer_hint") or "").strip() or None,
                "source_excerpt": str(item.get("source_excerpt") or "").strip() or None,
            }
        )

    if len(normalized) != question_count:
        raise ValueError(
            f"GPT generated {len(normalized)} question(s); expected {question_count}."
        )

    return normalized


def enrich_generation_plan_with_gpt(
    *,
    blueprint: Dict[str, Any],
    generation_plan: Dict[str, Any],
    model: str,
    reasoning_effort: str = "none",
    verbosity: str = "low",
) -> Dict[str, Any]:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "The 'openai' package is not installed. Run 'pip install -r requirements.txt'."
        ) from exc

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Add it to your environment or a local .env file."
        )

    client = OpenAI()
    enriched_plan = json.loads(json.dumps(generation_plan))

    for section_plan in enriched_plan.get("section_plans", []):
        prompt = _prompt_for_section(
            blueprint=blueprint,
            generation_plan=enriched_plan,
            section_plan=section_plan,
        )
        response = client.responses.create(
            model=model,
            input=prompt,
            reasoning={"effort": reasoning_effort},
            text={"verbosity": verbosity},
        )
        payload = _extract_json_payload(_response_text(response))
        section_plan["prebuilt_questions"] = _normalize_gpt_questions(
            section_plan=section_plan,
            payload=payload,
        )

    enriched_plan["generation_backend"] = "gpt"
    enriched_plan["openai_model"] = model
    enriched_plan["openai_reasoning_effort"] = reasoning_effort
    return enriched_plan
