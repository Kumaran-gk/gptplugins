from __future__ import annotations

import re
from collections import Counter
from typing import Any, Dict, List

from src.analysis.topic_mapper import map_topics_from_extraction


WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9\-\+()]{2,}")
NON_ALPHA_RE = re.compile(r"[^A-Za-z0-9]+")
STOPWORDS = {
    "about",
    "after",
    "again",
    "because",
    "being",
    "between",
    "could",
    "every",
    "explain",
    "following",
    "include",
    "marks",
    "reaction",
    "reactions",
    "should",
    "their",
    "there",
    "these",
    "those",
    "using",
    "which",
    "write",
    "your",
}


def _clean_fragment(text: str) -> str:
    return " ".join(text.replace("\u00a0", " ").split()).strip()


def _is_useful_fragment(text: str) -> bool:
    if len(text) < 45:
        return False

    alnum_count = sum(1 for char in text if char.isalnum())
    if alnum_count < max(20, len(text) * 0.45):
        return False

    return True


def _candidate_fragments(text: str) -> List[str]:
    raw_parts = re.split(r"\n\s*\n", text)
    fragments: List[str] = []

    for part in raw_parts:
        cleaned = _clean_fragment(part)
        if _is_useful_fragment(cleaned):
            fragments.append(cleaned)
            continue

        for line in part.splitlines():
            cleaned_line = _clean_fragment(line)
            if _is_useful_fragment(cleaned_line):
                fragments.append(cleaned_line)

    return fragments


def _snippet_topics(snippet: str, *, subject: str) -> List[str]:
    extraction = {
        "text": snippet,
        "segments": [{"text": snippet}],
        "file_name": "unit-content",
        "source_kind": "unit_content",
    }
    topic_map = map_topics_from_extraction(extraction, subject=subject)
    return [
        item.get("topic")
        for item in (topic_map.get("topic_distribution") or [])
        if item.get("topic")
    ]


def _top_terms(snippets: List[Dict[str, Any]], *, limit: int = 10) -> List[str]:
    counts: Counter[str] = Counter()
    for snippet in snippets:
        for token in WORD_RE.findall(snippet.get("excerpt", "").lower()):
            normalized = NON_ALPHA_RE.sub("", token)
            if len(normalized) < 4 or normalized in STOPWORDS:
                continue
            counts[normalized] += 1
    return [term for term, _ in counts.most_common(limit)]


def build_unit_content_bundle(
    extractions: List[Dict[str, Any]],
    *,
    subject: str,
    max_snippets: int = 24,
) -> Dict[str, Any]:
    snippets: List[Dict[str, Any]] = []
    seen_excerpts: set[str] = set()

    for extraction in extractions:
        for fragment in _candidate_fragments(extraction.get("text", "")):
            excerpt = fragment[:260].strip()
            excerpt_key = excerpt.lower()
            if excerpt_key in seen_excerpts:
                continue
            seen_excerpts.add(excerpt_key)

            snippets.append(
                {
                    "source_file": extraction.get("file_name"),
                    "source_kind": extraction.get("source_kind"),
                    "excerpt": excerpt,
                    "topics": _snippet_topics(excerpt, subject=subject)[:3],
                }
            )
            if len(snippets) >= max_snippets:
                break
        if len(snippets) >= max_snippets:
            break

    source_files = [
        extraction.get("file_name")
        for extraction in extractions
        if extraction.get("file_name")
    ]

    return {
        "subject": subject,
        "source_file_count": len(source_files),
        "source_files": list(dict.fromkeys(source_files)),
        "snippet_count": len(snippets),
        "top_terms": _top_terms(snippets),
        "snippets": snippets,
    }


def select_snippets_for_topics(
    content_bundle: Dict[str, Any] | None,
    *,
    target_topics: List[str],
    limit: int = 3,
) -> List[Dict[str, Any]]:
    if not content_bundle:
        return []

    snippets = content_bundle.get("snippets", []) or []
    if not snippets:
        return []

    normalized_topics = {topic for topic in target_topics if topic}
    matched = [
        snippet
        for snippet in snippets
        if normalized_topics.intersection(set(snippet.get("topics", [])))
    ]
    ordered = matched + [snippet for snippet in snippets if snippet not in matched]
    return ordered[:limit]
