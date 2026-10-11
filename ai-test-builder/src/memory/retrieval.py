from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.memory.memory_store import load_memory_records


def _normalize_terms(text: Optional[str]) -> List[str]:
    if not text:
        return []
    return [term.strip().lower() for term in str(text).split() if term.strip()]


def _record_haystack(record: Dict[str, Any]) -> str:
    parts: List[str] = []

    for key in [
        "title",
        "subject",
        "course_code",
        "unit_name",
        "summary_for_retrieval",
    ]:
        value = record.get(key)
        if value:
            parts.append(str(value).lower())

    for list_key in [
        "top_topics",
        "section_titles",
        "trap_types",
        "memory_tags",
        "teacher_style_signature",
        "recommended_merge_tags",
        "units",
    ]:
        values = record.get(list_key) or []
        for value in values:
            if value:
                parts.append(str(value).lower())

    return " ".join(parts)


def _score_record(record: Dict[str, Any], query: Optional[str]) -> int:
    terms = _normalize_terms(query)
    if not terms:
        return 0

    haystack = _record_haystack(record)
    title = str(record.get("title") or "").lower()
    unit_name = str(record.get("unit_name") or "").lower()
    summary = str(record.get("summary_for_retrieval") or "").lower()

    score = 0
    for term in terms:
        if term in haystack:
            score += 2
        if term in title:
            score += 4
        if term in unit_name:
            score += 4
        if term in summary:
            score += 3

    return score


def retrieve_memory_by_subject(
    *,
    memory_dir: str,
    subject_slug: str,
) -> List[Dict[str, Any]]:
    return load_memory_records(
        memory_dir=memory_dir,
        subject_slug=subject_slug,
    )


def retrieve_blueprint_summaries(
    *,
    memory_dir: str,
    subject_slug: str,
) -> List[Dict[str, Any]]:
    records = load_memory_records(
        memory_dir=memory_dir,
        subject_slug=subject_slug,
    )
    return [record for record in records if record.get("record_type") == "blueprint_summary"]


def retrieve_generation_summaries(
    *,
    memory_dir: str,
    subject_slug: str,
) -> List[Dict[str, Any]]:
    records = load_memory_records(
        memory_dir=memory_dir,
        subject_slug=subject_slug,
    )
    return [record for record in records if record.get("record_type") == "generated_test_summary"]


def retrieve_cumulative_summaries(
    *,
    memory_dir: str,
    subject_slug: str,
) -> List[Dict[str, Any]]:
    records = load_memory_records(
        memory_dir=memory_dir,
        subject_slug=subject_slug,
    )
    return [record for record in records if record.get("record_type") == "cumulative_test_summary"]


def retrieve_ranked_blueprint_summaries(
    *,
    memory_dir: str,
    subject_slug: str,
    query: Optional[str] = None,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    summaries = retrieve_blueprint_summaries(
        memory_dir=memory_dir,
        subject_slug=subject_slug,
    )

    ranked: List[Dict[str, Any]] = []
    for record in summaries:
        ranked.append(
            {
                "record": record,
                "score": _score_record(record, query),
            }
        )

    if query:
        ranked.sort(
            key=lambda item: (
                item["score"],
                str((item["record"] or {}).get("created_at") or ""),
            ),
            reverse=True,
        )
    else:
        ranked.sort(
            key=lambda item: str((item["record"] or {}).get("created_at") or ""),
            reverse=True,
        )

    return ranked[: max(1, limit)]