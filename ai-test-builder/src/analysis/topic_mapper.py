from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple


SUBJECT_TOPIC_KEYWORDS: Dict[str, Dict[str, List[str]]] = {
    "chemistry": {
        "chemical_reactions": [
            "chemical reaction",
            "chemical reactions",
            "reaction type",
            "type of reaction",
            "predict the product",
            "predict products",
            "balance",
            "balanced equation",
            "synthesis",
            "decomposition",
            "single displacement",
            "double displacement",
            "combustion",
        ],
        "stoichiometry": [
            "stoichiometry",
            "mole",
            "moles",
            "molar mass",
            "mass-mass",
            "limiting reactant",
            "limiting reagent",
            "yield",
            "percent yield",
        ],
        "solutions_and_concentration": [
            "solution",
            "solutions",
            "solute",
            "solvent",
            "concentration",
            "dilution",
            "molar concentration",
            "mol/l",
            "molarity",
        ],
        "atomic_structure": [
            "atom",
            "atomic",
            "electron",
            "proton",
            "neutron",
            "isotope",
            "bohr",
            "electron configuration",
        ],
        "lab_and_applications": [
            "lab",
            "experiment",
            "procedure",
            "observation",
            "application",
            "applications",
            "real-world",
        ],
    },
    "physics": {
        "forces_and_motion": [
            "force",
            "forces",
            "motion",
            "acceleration",
            "velocity",
            "newton",
            "free-body",
            "fbd",
            "friction",
        ],
        "energy": [
            "energy",
            "work",
            "power",
            "kinetic",
            "potential",
            "efficiency",
            "thermal",
            "heat",
        ],
        "electricity": [
            "electric",
            "current",
            "voltage",
            "potential difference",
            "resistance",
            "circuit",
            "charge",
            "power consumption",
        ],
        "waves_and_light": [
            "wave",
            "frequency",
            "wavelength",
            "light",
            "reflection",
            "refraction",
        ],
    },
    "math": {
        "algebra": [
            "simplify",
            "factor",
            "expand",
            "solve",
            "equation",
            "expression",
            "polynomial",
        ],
        "functions": [
            "function",
            "domain",
            "range",
            "graph",
            "transformation",
            "vertex",
            "intercept",
        ],
        "trigonometry": [
            "sin",
            "cos",
            "tan",
            "trigonometry",
            "identity",
            "radian",
            "degree",
            "triangle",
            "sine law",
            "cosine law",
        ],
        "exponentials_and_finance": [
            "exponential",
            "interest",
            "compound",
            "simple interest",
            "growth",
            "decay",
            "present value",
            "future value",
        ],
        "sequences": [
            "sequence",
            "series",
            "arithmetic",
            "geometric",
            "recursive",
            "term",
            "common difference",
            "common ratio",
        ],
    },
    "biology": {
        "cells_and_systems": [
            "cell",
            "cells",
            "organelle",
            "membrane",
            "diffusion",
            "osmosis",
            "system",
            "organ",
        ],
        "genetics": [
            "gene",
            "genetics",
            "dna",
            "rna",
            "inheritance",
            "allele",
            "chromosome",
        ],
        "evolution": [
            "evolution",
            "natural selection",
            "adaptation",
            "species",
            "variation",
        ],
        "ecology": [
            "ecosystem",
            "population",
            "community",
            "food chain",
            "habitat",
            "biodiversity",
        ],
    },
}


COURSE_CODE_RE = re.compile(r"\b([A-Z]{3}\d[A-Z])\b")
UNIT_HINT_RE = re.compile(
    r"\b(unit\s+\d+\s*[A-Za-z0-9 \-]*)\b",
    re.IGNORECASE,
)
CHAPTER_HINT_RE = re.compile(
    r"\b(chapter\s+\d+\s*[A-Za-z0-9 \-]*)\b",
    re.IGNORECASE,
)


def _normalize_text_for_matching(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s\-/]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _count_keyword_hits(text: str, keyword: str) -> int:
    pattern = r"\b" + re.escape(keyword.lower()) + r"\b"
    return len(re.findall(pattern, text))


def _detect_course_code(text: str) -> str | None:
    match = COURSE_CODE_RE.search(text)
    return match.group(1) if match else None


def _detect_unit_name(text: str) -> str | None:
    unit_match = UNIT_HINT_RE.search(text)
    if unit_match:
        return unit_match.group(1).strip()

    chapter_match = CHAPTER_HINT_RE.search(text)
    if chapter_match:
        return chapter_match.group(1).strip()

    return None


def _topic_hits_for_subject(subject: str, text: str) -> List[Tuple[str, int, List[str]]]:
    subject_key = subject.strip().lower()
    topic_map = SUBJECT_TOPIC_KEYWORDS.get(subject_key, {})

    hits: List[Tuple[str, int, List[str]]] = []

    for topic_name, keywords in topic_map.items():
        matched_keywords: List[str] = []
        score = 0

        for keyword in keywords:
            count = _count_keyword_hits(text, keyword)
            if count > 0:
                matched_keywords.append(keyword)
                score += count

        if score > 0:
            hits.append((topic_name, score, matched_keywords))

    hits.sort(key=lambda item: item[1], reverse=True)
    return hits


def _build_topic_distribution(topic_hits: List[Tuple[str, int, List[str]]]) -> List[Dict[str, Any]]:
    total_score = sum(score for _, score, _ in topic_hits)

    if total_score <= 0:
        return []

    distribution: List[Dict[str, Any]] = []
    for topic_name, score, matched_keywords in topic_hits:
        weight_pct = round((score / total_score) * 100, 2)
        distribution.append(
            {
                "topic": topic_name,
                "weight_pct": weight_pct,
                "matched_keywords": matched_keywords,
            }
        )

    return distribution


def map_topics_from_extraction(
    extraction: Dict[str, Any],
    *,
    subject: str,
) -> Dict[str, Any]:
    """
    Infer likely topics and rough topic weighting from normalized extraction text.
    """
    raw_text = extraction.get("text", "") or ""
    normalized_text = _normalize_text_for_matching(raw_text)

    course_code = _detect_course_code(raw_text)
    unit_name = _detect_unit_name(raw_text)

    topic_hits = _topic_hits_for_subject(subject, normalized_text)
    topic_distribution = _build_topic_distribution(topic_hits)

    observed_topic_signals: List[str] = []
    for topic in topic_distribution[:5]:
        observed_topic_signals.append(
            f"Topic signal detected for {topic['topic']} via keywords: {', '.join(topic['matched_keywords'][:5])}"
        )

    if course_code:
        observed_topic_signals.insert(0, f"Possible course code detected: {course_code}")

    if unit_name:
        observed_topic_signals.insert(0, f"Possible unit/chapter detected: {unit_name}")

    return {
        "subject": subject,
        "course_code": course_code,
        "unit_name": unit_name,
        "topic_distribution": topic_distribution,
        "observed_topic_signals": observed_topic_signals,
        "raw_topic_hit_count": len(topic_hits),
    }