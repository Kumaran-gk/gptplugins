from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.memory.retrieval import retrieve_ranked_blueprint_summaries
from src.utils.json_utils import load_json_file


def _is_candidate_blueprint_file(path: Path) -> bool:
    if path.suffix.lower() != ".json":
        return False

    name = path.name.lower()
    if name.endswith("_debug.json"):
        return False
    if name.endswith("_validation_debug.json"):
        return False

    return "_blueprint.json" in name or name.endswith(".json")


def load_blueprint_from_path(path: str | Path) -> Dict[str, Any]:
    blueprint_path = Path(path)

    if not blueprint_path.exists():
        raise FileNotFoundError(f"Blueprint file not found: {blueprint_path}")

    return load_json_file(blueprint_path)


def list_blueprint_paths(subject_blueprint_dir: str | Path) -> List[Path]:
    directory = Path(subject_blueprint_dir)

    if not directory.exists():
        return []

    candidates = [
        path
        for path in directory.glob("*.json")
        if _is_candidate_blueprint_file(path)
    ]

    return sorted(candidates, key=lambda p: p.stat().st_mtime, reverse=True)


def _safe_text_list(values: List[Any]) -> List[str]:
    return [str(v).lower() for v in values if v is not None]


def _build_search_haystack(blueprint: Dict[str, Any]) -> str:
    title = str(blueprint.get("title") or "")
    subject = str(blueprint.get("subject") or "")
    course_code = str(blueprint.get("course_code") or "")
    unit_name = str((blueprint.get("unit") or {}).get("unit_name") or "")

    topic_names = _safe_text_list(
        [item.get("topic") for item in (blueprint.get("topic_distribution") or [])]
    )
    subtopics = _safe_text_list(
        [
            sub
            for item in (blueprint.get("topic_distribution") or [])
            for sub in (item.get("subtopics") or [])
        ]
    )
    tags = _safe_text_list((blueprint.get("memory_metadata") or {}).get("tags") or [])
    signature = _safe_text_list(
        (blueprint.get("memory_metadata") or {}).get("teacher_style_signature") or []
    )

    parts = [
        title.lower(),
        subject.lower(),
        course_code.lower(),
        unit_name.lower(),
        " ".join(topic_names),
        " ".join(subtopics),
        " ".join(tags),
        " ".join(signature),
    ]

    return " ".join(parts)


def _score_blueprint(blueprint: Dict[str, Any], query: Optional[str]) -> int:
    if not query:
        return 0

    query_terms = [term.strip().lower() for term in query.split() if term.strip()]
    if not query_terms:
        return 0

    haystack = _build_search_haystack(blueprint)
    title = str(blueprint.get("title") or "").lower()
    unit_name = str((blueprint.get("unit") or {}).get("unit_name") or "").lower()

    score = 0
    for term in query_terms:
        if term in haystack:
            score += 2
        if term in title:
            score += 3
        if term in unit_name:
            score += 3

    return score


def _memory_summary_map(
    *,
    memory_dir: str | Path,
    subject_slug: str,
    query: Optional[str],
    limit: int = 25,
) -> Dict[str, Dict[str, Any]]:
    ranked = retrieve_ranked_blueprint_summaries(
        memory_dir=str(memory_dir),
        subject_slug=subject_slug,
        query=query,
        limit=limit,
    )

    result: Dict[str, Dict[str, Any]] = {}
    for item in ranked:
        record = item["record"]
        blueprint_id = record.get("blueprint_id")
        if blueprint_id:
            result[str(blueprint_id)] = {
                "record": record,
                "score": item["score"],
            }

    return result


def discover_blueprints(
    subject_blueprint_dir: str | Path,
    *,
    query: Optional[str] = None,
    limit: int = 5,
    memory_dir: Optional[str | Path] = None,
    subject_slug: Optional[str] = None,
) -> List[Dict[str, Any]]:
    paths = list_blueprint_paths(subject_blueprint_dir)
    discovered: List[Dict[str, Any]] = []

    memory_matches: Dict[str, Dict[str, Any]] = {}
    if memory_dir and subject_slug:
        memory_matches = _memory_summary_map(
            memory_dir=memory_dir,
            subject_slug=subject_slug,
            query=query,
            limit=max(10, limit * 3),
        )

    for path in paths:
        try:
            blueprint = load_blueprint_from_path(path)
        except Exception:
            continue

        if "blueprint_id" not in blueprint or "schema_version" not in blueprint:
            continue

        blueprint_id = str(blueprint.get("blueprint_id"))
        file_score = _score_blueprint(blueprint, query)

        memory_match = memory_matches.get(blueprint_id)
        memory_score = memory_match["score"] if memory_match else 0

        combined_score = (file_score * 2) + (memory_score * 3)

        discovered.append(
            {
                "path": str(path),
                "score": combined_score,
                "file_score": file_score,
                "memory_score": memory_score,
                "title": blueprint.get("title"),
                "subject": blueprint.get("subject"),
                "unit_name": (blueprint.get("unit") or {}).get("unit_name"),
                "blueprint_id": blueprint.get("blueprint_id"),
                "modified_time": path.stat().st_mtime,
                "memory_match": memory_match["record"] if memory_match else None,
            }
        )

    if query:
        discovered.sort(
            key=lambda item: (item["score"], item["modified_time"]),
            reverse=True,
        )
    else:
        discovered.sort(key=lambda item: item["modified_time"], reverse=True)

    return discovered[: max(1, limit)]


def resolve_blueprint_paths(
    *,
    explicit_paths: List[str],
    subject_blueprint_dir: str | Path,
    query: Optional[str] = None,
    limit: int = 1,
    memory_dir: Optional[str | Path] = None,
    subject_slug: Optional[str] = None,
) -> Dict[str, Any]:
    if explicit_paths:
        return {
            "resolved_paths": explicit_paths,
            "discovery_results": [],
            "resolution_mode": "explicit_paths",
        }

    discovered = discover_blueprints(
        subject_blueprint_dir,
        query=query,
        limit=limit,
        memory_dir=memory_dir,
        subject_slug=subject_slug,
    )

    resolved_paths = [item["path"] for item in discovered]

    return {
        "resolved_paths": resolved_paths,
        "discovery_results": discovered,
        "resolution_mode": "query" if query else "latest",
    }
