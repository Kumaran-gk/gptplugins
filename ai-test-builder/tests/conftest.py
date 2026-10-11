from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.config import Settings  # noqa: E402


@pytest.fixture
def repo_schema_path() -> Path:
    return REPO_ROOT / "schemas" / "blueprint_schema.json"


@pytest.fixture
def temp_settings(tmp_path: Path, repo_schema_path: Path) -> Settings:
    data_dir = tmp_path / "data"
    input_dir = data_dir / "input"
    blueprints_dir = data_dir / "blueprints"
    generated_tests_dir = data_dir / "generated_tests"
    memory_dir = data_dir / "memory"
    schemas_dir = REPO_ROOT / "schemas"

    for path in [data_dir, input_dir, blueprints_dir, generated_tests_dir, memory_dir]:
        path.mkdir(parents=True, exist_ok=True)

    return Settings(
        root_dir=tmp_path,
        schemas_dir=schemas_dir,
        data_dir=data_dir,
        input_dir=input_dir,
        blueprints_dir=blueprints_dir,
        generated_tests_dir=generated_tests_dir,
        memory_dir=memory_dir,
        blueprint_schema_path=repo_schema_path,
    )


@pytest.fixture
def valid_blueprint() -> dict:
    return {
        "schema_version": "1.0",
        "blueprint_id": "chemistry-unit-2-sample",
        "created_at": "2026-04-03T00:00:00Z",
        "title": "Unit 2 Chemical Reactions Test",
        "subject": "chemistry",
        "course_code": "SCH3U",
        "unit": {
            "unit_name": "Unit 2 Chemical Reactions Test",
            "chapter_refs": [],
            "learning_goals": [],
        },
        "source_files": [
            {
                "file_name": "unit-2-test.pdf",
                "file_type": "pdf",
            }
        ],
        "analysis_summary": {
            "confidence": 0.7,
            "observed_patterns": ["Detected sections"],
            "inferred_patterns": ["Likely chemistry unit test"],
            "notes": "Test fixture blueprint",
        },
        "structure": {
            "test_type": "mixed_assessment",
            "sections": [
                {
                    "section_id": "section_1",
                    "title": "Section A - Multiple Choice",
                    "order": 1,
                    "question_types": ["multiple_choice"],
                    "marks": 10,
                },
                {
                    "section_id": "section_2",
                    "title": "Section B - Written Response",
                    "order": 2,
                    "question_types": ["written_response"],
                    "marks": 12,
                },
            ],
            "ordering_rules": [
                "Preserve approximate section flow unless explicitly changed."
            ],
        },
        "topic_distribution": [
            {
                "topic": "chemical_reactions",
                "weight_pct": 80.0,
                "subtopics": ["balance", "combustion"],
            },
            {
                "topic": "lab_and_applications",
                "weight_pct": 20.0,
                "subtopics": ["application"],
            },
        ],
        "difficulty_profile": {
            "easy_pct": 40.0,
            "medium_pct": 40.0,
            "hard_pct": 20.0,
            "progression_notes": ["Later questions are somewhat harder."],
            "cognitive_skills": [
                "procedural_problem_solving",
                "concept_application",
            ],
        },
        "question_style": {
            "stem_styles": ["numbered_questions", "command_verb_led"],
            "response_formats": ["multiple_choice", "written_response"],
            "common_verbs": ["predict", "balance", "classify"],
            "wording_tone": "instructional_assessment",
            "diagram_expectations": [],
            "answer_style_expectations": ["notation_precision_required"],
        },
        "trap_patterns": [
            {
                "trap_type": "balancing_precision",
                "description": "Students may identify the correct reaction but lose marks on balancing.",
                "frequency": "high",
                "examples": ["Incorrect coefficients"],
            }
        ],
        "generation_rules": {
            "preserve_structure": True,
            "reuse_prohibited": True,
            "variation_policy": "Preserve structure and difficulty while generating fresh questions.",
            "freshness_requirements": [
                "Do not copy source questions verbatim."
            ],
            "constraints": [
                "Preserve reaction-classification tasks."
            ],
        },
        "memory_metadata": {
            "tags": ["chemistry", "sch3u", "unit-2-chemical-reactions-test"],
            "summary_for_retrieval": "Chemistry blueprint for unit 2 chemical reactions.",
            "teacher_style_signature": [
                "test_type:mixed_assessment",
                "sections:2",
                "top_topic:chemical_reactions",
            ],
        },
        "cumulative_metadata": {
            "eligible_for_cumulative": True,
            "prerequisite_topics": ["chemical_reactions"],
            "recommended_merge_tags": ["chemistry", "unit-2-chemical-reactions-test"],
        },
        "subject_extensions": {
            "notation_rules": [
                "Chemical state symbols should be included where expected."
            ],
            "topic_specific_constraints": [
                "Chemical equations may require balancing."
            ],
        },
    }