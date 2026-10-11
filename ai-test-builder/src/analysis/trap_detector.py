from __future__ import annotations

import re
from typing import Any, Dict, List


CHEMISTRY_STATE_SIGNAL_RE = re.compile(r"\b\(aq\)|\(s\)|\(l\)|\(g\)\b", re.IGNORECASE)


def _normalized_text(extraction: Dict[str, Any]) -> str:
    return (extraction.get("text", "") or "").lower()


def _add_trap(
    traps: List[Dict[str, Any]],
    *,
    trap_type: str,
    description: str,
    frequency: str = "medium",
    examples: List[str] | None = None,
) -> None:
    traps.append(
        {
            "trap_type": trap_type,
            "description": description,
            "frequency": frequency,
            "examples": examples or [],
        }
    )


def detect_trap_patterns(
    extraction: Dict[str, Any],
    patterns: Dict[str, Any],
    *,
    subject: str,
) -> Dict[str, Any]:
    """
    Detect likely trap patterns or teacher-style pitfalls from extracted text
    and structural patterns.

    This is heuristic and conservative. It should prefer obvious signals over
    speculative ones.
    """
    text = _normalized_text(extraction)
    section_candidates = patterns.get("section_candidates", []) or []
    question_candidates = patterns.get("question_candidates", []) or []
    mc_signals = patterns.get("multiple_choice_signals", {}) or {}

    traps: List[Dict[str, Any]] = []
    observed_signals: List[str] = []

    # Generic multi-step / stacked-command trap
    stacked_command_count = 0
    for question in question_candidates:
        header = (question.get("raw_header") or "").lower()
        preview = (question.get("preview") or "").lower()
        combined = f"{header} {preview}"

        command_hits = 0
        for verb in [
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
        ]:
            if verb in combined:
                command_hits += 1

        if command_hits >= 2:
            stacked_command_count += 1

    if stacked_command_count >= 2:
        _add_trap(
            traps,
            trap_type="multi_step_command_stack",
            description="Questions appear to combine multiple required actions in a single item, increasing setup and execution difficulty.",
            frequency="high" if stacked_command_count >= 3 else "medium",
            examples=[
                "Items that ask students to predict, balance, and classify in one question."
            ],
        )
        observed_signals.append("Multiple question candidates appear to stack more than one command verb.")

    # Multiple-choice distractor style
    if mc_signals.get("likely_multiple_choice_present"):
        _add_trap(
            traps,
            trap_type="multiple_choice_distractors",
            description="Multiple-choice style likely introduces distractors that test close reading and misconception filtering.",
            frequency="medium",
            examples=mc_signals.get("example_lines", [])[:3],
        )
        observed_signals.append("Multiple-choice option patterns were detected.")

    # Chemistry-specific traps
    if subject.strip().lower() == "chemistry":
        if "predict the product" in text or "predict products" in text:
            _add_trap(
                traps,
                trap_type="product_prediction_error",
                description="Students may choose chemically implausible or incomplete products when predicting reactions.",
                frequency="high",
                examples=["Predicting products requires recognizing reaction pattern before writing products."],
            )
            observed_signals.append("Predict-the-product wording appears in the source test.")

        if "balance" in text or "balanced equation" in text:
            _add_trap(
                traps,
                trap_type="balancing_precision",
                description="Students may identify the correct reaction but lose marks on balancing or coefficient precision.",
                frequency="high",
                examples=["Correct reaction identification but incorrect balancing."],
            )
            observed_signals.append("Balancing language appears in the source test.")

        if "type of reaction" in text or "reaction type" in text:
            _add_trap(
                traps,
                trap_type="reaction_classification_confusion",
                description="Students may confuse reaction categories even when the reaction itself is recognized correctly.",
                frequency="medium",
                examples=["Confusing synthesis, decomposition, combustion, and displacement types."],
            )
            observed_signals.append("Reaction classification language appears in the source test.")

        if "include states" in text or CHEMISTRY_STATE_SIGNAL_RE.search(text):
            _add_trap(
                traps,
                trap_type="state_symbol_precision",
                description="Chemical state symbols and notation accuracy appear to matter and may act as a precision trap.",
                frequency="medium",
                examples=["Including (s), (l), (g), and (aq) correctly."],
            )
            observed_signals.append("State-symbol expectations appear in the source test.")

        if "application" in text or "applications" in text:
            _add_trap(
                traps,
                trap_type="application_transfer",
                description="Some questions appear to require transfer from learned reaction patterns into applied or real-world contexts.",
                frequency="medium",
                examples=["Application questions may require concept transfer rather than direct recall."],
            )
            observed_signals.append("Application-style wording appears in the source test.")

    # Generic written-response precision
    if "full sentences" in text or "explain" in text or "justify" in text:
        _add_trap(
            traps,
            trap_type="written_precision",
            description="Written-response expectations may penalize incomplete reasoning, not just factual errors.",
            frequency="medium",
            examples=["Use full sentences or explain reasoning clearly."],
        )
        observed_signals.append("Written-response precision language appears in the source test.")

    # Section-based mixed-format trap
    if len(section_candidates) >= 2:
        _add_trap(
            traps,
            trap_type="format_shift",
            description="The assessment appears to shift across sections, which can change how students must respond and manage time.",
            frequency="medium",
            examples=[section.get("title", "") for section in section_candidates[:3]],
        )
        observed_signals.append("Multiple section candidates suggest format changes across the test.")

    # Deduplicate by trap type
    deduped: List[Dict[str, Any]] = []
    seen = set()
    for trap in traps:
        trap_key = trap["trap_type"]
        if trap_key not in seen:
            seen.add(trap_key)
            deduped.append(trap)

    return {
        "trap_patterns": deduped,
        "observed_trap_signals": list(dict.fromkeys(observed_signals)),
    }