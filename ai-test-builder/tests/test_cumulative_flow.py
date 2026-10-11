from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from src.agent.workflow import AgentWorkflow, WorkflowRequest
from src.generation.cumulative_builder import build_cumulative_generation_plan_stub
from src.memory.memory_store import load_memory_records
from src.utils.json_utils import write_json_file


def test_build_cumulative_flow_creates_outputs_and_memory(temp_settings, valid_blueprint):
    subject = "chemistry"
    subject_dirs = temp_settings.ensure_subject_dirs(subject)

    first = deepcopy(valid_blueprint)
    first["blueprint_id"] = "chemistry-unit-2"
    first["title"] = "Unit 2 Chemical Reactions Test"
    first["unit"]["unit_name"] = "Unit 2 Chemical Reactions"
    first["created_at"] = "2026-04-03T00:00:00Z"

    second = deepcopy(valid_blueprint)
    second["blueprint_id"] = "chemistry-unit-3"
    second["title"] = "Unit 3 Stoichiometry Test"
    second["unit"]["unit_name"] = "Unit 3 Stoichiometry"
    second["topic_distribution"] = [
        {
            "topic": "stoichiometry",
            "weight_pct": 75.0,
            "subtopics": ["mole", "molar mass", "yield"],
        },
        {
            "topic": "lab_and_applications",
            "weight_pct": 25.0,
            "subtopics": ["application"],
        },
    ]
    second["memory_metadata"]["summary_for_retrieval"] = "Stoichiometry-heavy chemistry blueprint."
    second["created_at"] = "2026-04-04T00:00:00Z"

    first_path = Path(subject_dirs["blueprint_path"]) / "chemistry_unit-2_blueprint.json"
    second_path = Path(subject_dirs["blueprint_path"]) / "chemistry_unit-3_blueprint.json"
    write_json_file(first_path, first)
    write_json_file(second_path, second)

    workflow = AgentWorkflow(settings=temp_settings)
    request = WorkflowRequest(
        skill="build-cumulative-test",
        subject=subject,
        blueprint_files=[str(first_path), str(second_path)],
        options={"version": "verCum", "include_teacher": "true", "save_debug": "true"},
    )

    result = workflow.run(request)

    assert result["status"] == "ok"
    assert len(result["blueprint_results"]) == 2
    assert result["cumulative_student_test_path"] is not None
    assert result["cumulative_teacher_test_path"] is not None
    assert result["memory_record_path"] is not None
    assert result["question_count"] > 0

    student_path = Path(result["cumulative_student_test_path"])
    teacher_path = Path(result["cumulative_teacher_test_path"])
    memory_path = Path(result["memory_record_path"])
    artifact_root = Path(subject_dirs["generated_path"]) / "artifacts"

    assert student_path.exists()
    assert teacher_path.exists()
    assert memory_path.exists()
    assert Path(result["cumulative_plan_path"]).exists()
    assert Path(result["cumulative_render_path"]).exists()
    assert Path(result["cumulative_validation_path"]).exists()
    assert artifact_root in student_path.parents
    assert artifact_root in teacher_path.parents
    assert artifact_root in Path(result["cumulative_plan_path"]).parents
    assert artifact_root in Path(result["cumulative_render_path"]).parents
    assert artifact_root in Path(result["cumulative_validation_path"]).parents

    student_text = student_path.read_text(encoding="utf-8")
    teacher_text = teacher_path.read_text(encoding="utf-8")
    records = load_memory_records(
        memory_dir=temp_settings.memory_dir,
        subject_slug="chemistry",
    )

    assert "Cumulative Test - Student Version" in student_text
    assert "Unit 2 Chemical Reactions" in student_text
    assert "Unit 3 Stoichiometry" in student_text
    assert "Cumulative Answer Key" in teacher_text
    assert records[-1]["record_type"] == "cumulative_test_summary"
    assert records[-1]["version_label"] == "verCum"


def test_cumulative_plan_balances_topics_across_units(valid_blueprint):
    first = deepcopy(valid_blueprint)
    first["blueprint_id"] = "chemistry-unit-2"
    first["title"] = "Unit 2 Chemical Reactions Test"
    first["unit"]["unit_name"] = "Unit 2 Chemical Reactions"
    first["topic_distribution"] = [
        {
            "topic": "chemical_reactions",
            "weight_pct": 90.0,
            "subtopics": ["balance", "combustion"],
        },
        {
            "topic": "lab_and_applications",
            "weight_pct": 10.0,
            "subtopics": ["application"],
        },
    ]

    second = deepcopy(valid_blueprint)
    second["blueprint_id"] = "chemistry-unit-3"
    second["title"] = "Unit 3 Stoichiometry Test"
    second["unit"]["unit_name"] = "Unit 3 Stoichiometry"
    second["topic_distribution"] = [
        {
            "topic": "stoichiometry",
            "weight_pct": 95.0,
            "subtopics": ["mole", "molar mass"],
        },
        {
            "topic": "lab_and_applications",
            "weight_pct": 5.0,
            "subtopics": ["application"],
        },
    ]

    plan = build_cumulative_generation_plan_stub(
        [first, second],
        requested_version="verBalanced",
    )

    assert plan["merge_strategy"] == "balanced_unit_topic_round_robin"
    assert plan["units"] == ["Unit 2 Chemical Reactions", "Unit 3 Stoichiometry"]
    assert plan["top_topics"][:2] == ["chemical_reactions", "stoichiometry"]
    assert plan["section_plans"][0]["target_topics"][:2] == ["chemical_reactions", "stoichiometry"]
    assert len(plan["unit_allocations"]) == 2
    assert plan["unit_allocations"][0]["top_topics"][0] == "chemical_reactions"
    assert plan["unit_allocations"][1]["top_topics"][0] == "stoichiometry"
