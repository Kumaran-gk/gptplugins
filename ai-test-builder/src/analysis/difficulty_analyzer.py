from __future__ import annotations

from typing import Any, Dict, List


EASY_VERBS = {
    "identify",
    "state",
    "name",
    "list",
    "define",
}
MEDIUM_VERBS = {
    "calculate",
    "determine",
    "predict",
    "balance",
    "classify",
    "compare",
    "solve",
}
HARD_VERBS = {
    "explain",
    "justify",
    "prove",
    "derive",
    "analyze",
    "evaluate",
    "design",
}


def _score_question_difficulty(question: Dict[str, Any]) -> str:
    raw_header = (question.get("raw_header") or "").lower()
    preview = (question.get("preview") or "").lower()
    text = f"{raw_header} {preview}"

    mark_hint = question.get("mark_hint")
    score = 0

    for verb in EASY_VERBS:
        if verb in text:
            score += 1

    for verb in MEDIUM_VERBS:
        if verb in text:
            score += 2

    for verb in HARD_VERBS:
        if verb in text:
            score += 3

    if mark_hint is not None:
        if mark_hint >= 4:
            score += 2
        elif mark_hint >= 2:
            score += 1

    if len(text) > 120:
        score += 1

    if " and " in text:
        score += 1

    if "explain" in text and "calculate" in text:
        score += 2

    if score <= 2:
        return "easy"
    if score <= 5:
        return "medium"
    return "hard"


def _build_pct(count: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round((count / total) * 100, 2)


def analyze_difficulty_from_patterns(
    extraction: Dict[str, Any],
    patterns: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build a rough difficulty profile from detected question candidates and text signals.
    """
    questions = patterns.get("question_candidates", []) or []

    if not questions:
        full_text = extraction.get("text", "") or ""
        char_count = len(full_text)

        if char_count < 800:
            easy_pct, medium_pct, hard_pct = 50.0, 40.0, 10.0
        elif char_count < 2500:
            easy_pct, medium_pct, hard_pct = 35.0, 45.0, 20.0
        else:
            easy_pct, medium_pct, hard_pct = 25.0, 50.0, 25.0

        return {
            "easy_pct": easy_pct,
            "medium_pct": medium_pct,
            "hard_pct": hard_pct,
            "difficulty_by_question": [],
            "progression_notes": [
                "Difficulty estimated from document-level text size because question detection was weak."
            ],
            "cognitive_skills": [
                "mixed_recall_and_procedure"
            ],
            "analysis_confidence": "low",
        }

    difficulty_by_question: List[Dict[str, Any]] = []
    buckets = {"easy": 0, "medium": 0, "hard": 0}

    for question in questions:
        label = _score_question_difficulty(question)
        buckets[label] += 1
        difficulty_by_question.append(
            {
                "question_number": question.get("question_number"),
                "difficulty": label,
                "mark_hint": question.get("mark_hint"),
                "preview": question.get("preview"),
            }
        )

    total = len(difficulty_by_question)

    progression_notes: List[str] = []
    if total >= 2:
        first_half = difficulty_by_question[: max(1, total // 2)]
        second_half = difficulty_by_question[max(1, total // 2):]

        first_half_hard = sum(1 for item in first_half if item["difficulty"] == "hard")
        second_half_hard = sum(1 for item in second_half if item["difficulty"] == "hard")

        if second_half_hard > first_half_hard:
            progression_notes.append("Later detected questions appear harder than earlier ones.")
        elif second_half_hard == first_half_hard:
            progression_notes.append("Detected question difficulty appears relatively mixed across the test.")
        else:
            progression_notes.append("Earlier detected questions appear unusually difficult relative to later ones.")

    cognitive_skills: List[str] = []
    previews_joined = " ".join(
        (item.get("preview") or "").lower() for item in difficulty_by_question
    )

    if any(word in previews_joined for word in ["calculate", "determine", "solve", "balance"]):
        cognitive_skills.append("procedural_problem_solving")
    if any(word in previews_joined for word in ["predict", "classify", "compare"]):
        cognitive_skills.append("concept_application")
    if any(word in previews_joined for word in ["explain", "justify", "analyze"]):
        cognitive_skills.append("extended_reasoning")

    if not cognitive_skills:
        cognitive_skills.append("mixed_recall_and_procedure")

    return {
        "easy_pct": _build_pct(buckets["easy"], total),
        "medium_pct": _build_pct(buckets["medium"], total),
        "hard_pct": _build_pct(buckets["hard"], total),
        "difficulty_by_question": difficulty_by_question,
        "progression_notes": progression_notes,
        "cognitive_skills": cognitive_skills,
        "analysis_confidence": "medium" if total >= 4 else "low",
    }