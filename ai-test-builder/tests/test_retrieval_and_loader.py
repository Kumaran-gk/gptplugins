from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from src.blueprint.loader import list_blueprint_paths, resolve_blueprint_paths
from src.memory.blueprint_index import (
    build_blueprint_memory_record,
    build_cumulative_memory_record,
    build_generation_memory_record,
)
from src.memory.memory_store import append_memory_record
from src.memory.retrieval import (
    retrieve_blueprint_summaries,
    retrieve_cumulative_summaries,
    retrieve_generation_summaries,
    retrieve_ranked_blueprint_summaries,
)
from src.utils.json_utils import write_json_file


def _write_blueprint(path: Path, blueprint: dict) -> Path:
    write_json_file(path, blueprint)
    return path


def test_retrieval_filters_record_types_and_ranks_blueprints(temp_settings, valid_blueprint):
    subject_slug = "chemistry"

    first = deepcopy(valid_blueprint)
    first["blueprint_id"] = "chemistry-reactions"
    first["title"] = "Chemical Reactions Review"
    first["unit"]["unit_name"] = "Unit 2 Reactions"
    first["memory_metadata"]["summary_for_retrieval"] = "Blueprint focused on balancing and reaction classes."
    first["created_at"] = "2026-04-03T00:00:00Z"

    second = deepcopy(valid_blueprint)
    second["blueprint_id"] = "chemistry-stoichiometry"
    second["title"] = "Stoichiometry Practice Test"
    second["unit"]["unit_name"] = "Unit 3 Stoichiometry"
    second["topic_distribution"] = [
        {
            "topic": "stoichiometry",
            "weight_pct": 100.0,
            "subtopics": ["mole", "molar mass", "limiting reactant"],
        }
    ]
    second["memory_metadata"]["summary_for_retrieval"] = "Blueprint focused on stoichiometry and molar mass."
    second["created_at"] = "2026-04-04T00:00:00Z"

    append_memory_record(
        memory_dir=temp_settings.memory_dir,
        subject_slug=subject_slug,
        record=build_blueprint_memory_record(first),
    )
    append_memory_record(
        memory_dir=temp_settings.memory_dir,
        subject_slug=subject_slug,
        record=build_blueprint_memory_record(second),
    )
    append_memory_record(
        memory_dir=temp_settings.memory_dir,
        subject_slug=subject_slug,
        record=build_generation_memory_record(
            blueprint=second,
            version_label="verA",
            student_test_path="student.md",
            teacher_test_path="teacher.md",
        ),
    )
    append_memory_record(
        memory_dir=temp_settings.memory_dir,
        subject_slug=subject_slug,
        record=build_cumulative_memory_record(
            subject="chemistry",
            version_label="verC",
            units=["Unit 2 Reactions", "Unit 3 Stoichiometry"],
            top_topics=["stoichiometry", "chemical_reactions"],
            student_test_path="cumulative_student.md",
            teacher_test_path="cumulative_teacher.md",
        ),
    )

    blueprint_records = retrieve_blueprint_summaries(
        memory_dir=str(temp_settings.memory_dir),
        subject_slug=subject_slug,
    )
    generation_records = retrieve_generation_summaries(
        memory_dir=str(temp_settings.memory_dir),
        subject_slug=subject_slug,
    )
    cumulative_records = retrieve_cumulative_summaries(
        memory_dir=str(temp_settings.memory_dir),
        subject_slug=subject_slug,
    )
    ranked = retrieve_ranked_blueprint_summaries(
        memory_dir=str(temp_settings.memory_dir),
        subject_slug=subject_slug,
        query="stoichiometry molar mass",
        limit=2,
    )

    assert len(blueprint_records) == 2
    assert len(generation_records) == 1
    assert len(cumulative_records) == 1
    assert ranked[0]["record"]["blueprint_id"] == "chemistry-stoichiometry"
    assert ranked[0]["score"] >= ranked[1]["score"]


def test_resolve_blueprint_paths_uses_query_and_ignores_debug_files(temp_settings, valid_blueprint):
    subject_dirs = temp_settings.ensure_subject_dirs("chemistry")
    subject_slug = "chemistry"

    reactions = deepcopy(valid_blueprint)
    reactions["blueprint_id"] = "chemistry-reactions"
    reactions["title"] = "Chemical Reactions Review"
    reactions["unit"]["unit_name"] = "Unit 2 Reactions"
    reactions["created_at"] = "2026-04-03T00:00:00Z"

    stoich = deepcopy(valid_blueprint)
    stoich["blueprint_id"] = "chemistry-stoichiometry"
    stoich["title"] = "Stoichiometry Practice Test"
    stoich["unit"]["unit_name"] = "Unit 3 Stoichiometry"
    stoich["topic_distribution"] = [
        {
            "topic": "stoichiometry",
            "weight_pct": 100.0,
            "subtopics": ["mole", "molar mass"],
        }
    ]
    stoich["memory_metadata"]["summary_for_retrieval"] = "Mole and stoichiometry focus."
    stoich["created_at"] = "2026-04-04T00:00:00Z"

    reactions_path = _write_blueprint(
        Path(subject_dirs["blueprint_path"]) / "chemistry_unit-2-reactions_blueprint.json",
        reactions,
    )
    stoich_path = _write_blueprint(
        Path(subject_dirs["blueprint_path"]) / "chemistry_unit-3-stoichiometry_blueprint.json",
        stoich,
    )
    _write_blueprint(
        Path(subject_dirs["blueprint_path"]) / "chemistry_unit-3-stoichiometry_pattern_debug.json",
        {"debug": True},
    )

    append_memory_record(
        memory_dir=temp_settings.memory_dir,
        subject_slug=subject_slug,
        record=build_blueprint_memory_record(reactions),
    )
    append_memory_record(
        memory_dir=temp_settings.memory_dir,
        subject_slug=subject_slug,
        record=build_blueprint_memory_record(stoich),
    )

    listed = list_blueprint_paths(subject_dirs["blueprint_path"])
    resolved = resolve_blueprint_paths(
        explicit_paths=[],
        subject_blueprint_dir=subject_dirs["blueprint_path"],
        query="stoichiometry mole",
        limit=1,
        memory_dir=temp_settings.memory_dir,
        subject_slug=subject_slug,
    )

    assert reactions_path in listed
    assert stoich_path in listed
    assert all("debug" not in path.name for path in listed)
    assert resolved["resolution_mode"] == "query"
    assert resolved["resolved_paths"] == [str(stoich_path)]
    assert resolved["discovery_results"][0]["blueprint_id"] == "chemistry-stoichiometry"
