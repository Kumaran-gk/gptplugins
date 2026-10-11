from __future__ import annotations

from src.blueprint.subject_extensions import build_subject_extensions
from src.utils.json_utils import load_json_text, pretty_dump_json
from src.utils.logging_utils import LOGGER_ROOT_NAME, configure_logging, get_logger


def test_build_subject_extensions_for_chemistry():
    extraction = {
        "text": (
            "Predict the products. Include states and balance the equation. "
            "State the type of reaction and describe the lab observation."
        )
    }

    result = build_subject_extensions(extraction, subject="chemistry")

    assert "Chemical state symbols should be included where expected." in result["notation_rules"]
    assert "Chemical equations may require balancing." in result["topic_specific_constraints"]
    assert "Reaction classification should remain represented." in result["topic_specific_constraints"]
    assert result["lab_skills"]


def test_build_subject_extensions_for_other_supported_subjects():
    physics = build_subject_extensions(
        {
            "text": (
                "Use a free-body diagram. Calculate the force in N and graph the motion."
            )
        },
        subject="physics",
    )
    math = build_subject_extensions(
        {
            "text": (
                "Prove the identity, use function notation, and graph the parabola."
            )
        },
        subject="math",
    )
    biology = build_subject_extensions(
        {
            "text": (
                "Label the cell diagram and explain the process observed in the lab."
            )
        },
        subject="biology",
    )

    assert "free_body_diagram" in physics["diagram_types"]
    assert physics["calculation_modes"]
    assert math["proof_requirements"]
    assert "cartesian_function_graph" in math["graph_types"]
    assert "biological_labeling_diagram" in biology["diagram_types"]
    assert biology["lab_skills"]


def test_logging_utils_and_json_utils_are_usable():
    root_logger = configure_logging("DEBUG")
    child_logger = get_logger("tests.phase1")

    assert root_logger.name == LOGGER_ROOT_NAME
    assert child_logger.name == f"{LOGGER_ROOT_NAME}.tests.phase1"

    payload = {"subject": "chemistry", "count": 2}
    dumped = pretty_dump_json(payload, sort_keys=True)

    assert '"count": 2' in dumped
    assert load_json_text(dumped) == payload
