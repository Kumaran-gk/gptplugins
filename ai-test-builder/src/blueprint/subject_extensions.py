from __future__ import annotations

import re
from typing import Any, Dict


def _contains_any(text: str, *phrases: str) -> bool:
    return any(phrase in text for phrase in phrases)


def _add_unique(target: list[str], value: str) -> None:
    if value not in target:
        target.append(value)


def _build_chemistry_extensions(text: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "notation_rules": [],
        "topic_specific_constraints": [],
        "lab_skills": [],
    }

    if _contains_any(text, "include states", "(aq)", "(s)", "(l)", "(g)"):
        _add_unique(
            result["notation_rules"],
            "Chemical state symbols should be included where expected.",
        )
    if _contains_any(text, "balance", "balanced equation"):
        _add_unique(
            result["topic_specific_constraints"],
            "Chemical equations may require balancing.",
        )
    if _contains_any(text, "type of reaction", "reaction type", "classify the reaction"):
        _add_unique(
            result["topic_specific_constraints"],
            "Reaction classification should remain represented.",
        )
    if _contains_any(text, "lab", "experiment", "procedure", "observation"):
        _add_unique(
            result["lab_skills"],
            "Observation, procedure interpretation, and lab-style reasoning may be required.",
        )

    return result


def _build_physics_extensions(text: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "formulas_expected": [],
        "units_and_constants": [],
        "graph_types": [],
        "diagram_types": [],
        "calculation_modes": [],
        "topic_specific_constraints": [],
    }

    if _contains_any(text, "calculate", "determine", "solve"):
        _add_unique(
            result["calculation_modes"],
            "Multi-step calculation questions may require showing work and substitutions.",
        )
    if _contains_any(text, "free-body", "fbd"):
        _add_unique(result["diagram_types"], "free_body_diagram")
    if _contains_any(text, "circuit", "series circuit", "parallel circuit"):
        _add_unique(result["diagram_types"], "circuit_diagram")
    if _contains_any(text, "graph", "position-time", "velocity-time", "acceleration-time"):
        _add_unique(result["graph_types"], "motion_graph")
    if _contains_any(text, "ray diagram", "reflection", "refraction"):
        _add_unique(result["diagram_types"], "ray_diagram")

    formula_signals = {
        "newton": "Newton's laws and force equations may be expected.",
        "kinetic": "Energy equations may be expected.",
        "potential": "Energy equations may be expected.",
        "voltage": "Electrical relationship equations may be expected.",
        "resistance": "Electrical relationship equations may be expected.",
        "power": "Power equations may be expected.",
    }
    for signal, note in formula_signals.items():
        if signal in text:
            _add_unique(result["formulas_expected"], note)

    unit_patterns = [
        ("\\bkg\\b", "kilogram"),
        ("\\bm/s\\b", "metres_per_second"),
        ("\\bn\\b", "newton"),
        ("\\bj\\b", "joule"),
        ("\\bv\\b", "volt"),
        ("\\ba\\b", "ampere"),
        ("\\bw\\b", "watt"),
    ]
    for pattern, unit_name in unit_patterns:
        if re.search(pattern, text):
            result["units_and_constants"].append({"name": unit_name})

    if _contains_any(text, "show your work", "include units"):
        _add_unique(
            result["topic_specific_constraints"],
            "Units and clearly shown steps may be part of the marking expectations.",
        )

    return result


def _build_math_extensions(text: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "notation_rules": [],
        "graph_types": [],
        "proof_requirements": [],
        "calculation_modes": [],
        "topic_specific_constraints": [],
    }

    if _contains_any(text, "prove", "show that", "justify"):
        _add_unique(
            result["proof_requirements"],
            "Questions may require justified reasoning or proof-style structure.",
        )
    if _contains_any(text, "exact value", "simplify fully", "in simplest form"):
        _add_unique(
            result["notation_rules"],
            "Exact-value and simplified-form notation may matter.",
        )
    if _contains_any(text, "function notation", "f(x)", "g(x)"):
        _add_unique(
            result["notation_rules"],
            "Function notation should remain consistent and explicit.",
        )
    if _contains_any(text, "graph", "vertex", "intercept", "slope"):
        _add_unique(result["graph_types"], "cartesian_function_graph")
    if _contains_any(text, "triangle", "sin", "cos", "tan", "radian", "degree"):
        _add_unique(
            result["topic_specific_constraints"],
            "Trigonometric notation and angle mode expectations may matter.",
        )
    if _contains_any(text, "solve", "determine", "calculate"):
        _add_unique(
            result["calculation_modes"],
            "Algebraic or numeric work may require intermediate steps to receive full credit.",
        )

    return result


def _build_biology_extensions(text: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "diagram_types": [],
        "lab_skills": [],
        "topic_specific_constraints": [],
    }

    if _contains_any(text, "label", "diagram", "cell", "organ", "microscope"):
        _add_unique(result["diagram_types"], "biological_labeling_diagram")
    if _contains_any(text, "lab", "experiment", "observe", "microscope", "procedure"):
        _add_unique(
            result["lab_skills"],
            "Observation, experimental interpretation, and lab reasoning may be required.",
        )
    if _contains_any(text, "explain the process", "describe the process", "cycle", "system"):
        _add_unique(
            result["topic_specific_constraints"],
            "Process explanations and terminology precision may be important.",
        )

    return result


def build_subject_extensions(
    extraction: Dict[str, Any],
    *,
    subject: str,
) -> Dict[str, Any]:
    """
    Build subject-specific blueprint enrichments from the extracted source text.

    The base schema allows flexible keys here. This helper keeps subject-specific
    heuristics out of the general blueprint builder.
    """
    text = (extraction.get("text", "") or "").lower()
    subject_key = subject.strip().lower()

    if subject_key == "chemistry":
        return _build_chemistry_extensions(text)
    if subject_key == "physics":
        return _build_physics_extensions(text)
    if subject_key == "math":
        return _build_math_extensions(text)
    if subject_key == "biology":
        return _build_biology_extensions(text)

    return {
        "notation_rules": [],
        "topic_specific_constraints": [],
    }
