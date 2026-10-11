from __future__ import annotations

from copy import deepcopy

from src.analysis.pattern_extractor import extract_patterns_from_extraction
from src.blueprint.builder import build_blueprint_draft
from src.generation.cumulative_builder import (
    build_cumulative_generation_plan_stub,
    render_cumulative_student_markdown,
)
from src.ingestion.normalizer import normalize_text


def test_normalize_text_replaces_common_mojibake():
    raw = "Newtonâ€™s second law â€” use 30Â° and donâ€œt panic."

    normalized = normalize_text(raw)

    assert "Newton's second law" in normalized
    assert "-" in normalized
    assert "30 degrees" in normalized


def test_pattern_extractor_prefers_real_title_over_name_field():
    extraction = {
        "text": "\n".join(
            [
                "Name: | lol? A KAY",
                "/ SCH3U Unit 2 Chemical Reactions Test",
                "Written 53153",
                "Application Questions (18 Marks (Use full sentences for all questions to achieve full marks) | &",
                "1. Explain one application of combustion reactions. (3 marks)",
            ]
        )
    }

    patterns = extract_patterns_from_extraction(extraction)

    assert patterns["layout_signals"]["title_candidate"] == "SCH3U Unit 2 Chemical Reactions Test"
    assert patterns["section_candidates"][0]["title"] == (
        "Application Questions (18 Marks (Use full sentences for all questions to achieve full marks)"
    )


def test_pattern_extractor_handles_scored_scan_headers_and_ocr_question_noise():
    extraction = {
        "text": "\n".join(
            [
                "/ SCH3U Unit 2 Chemical Reactions Test",
                "Multiple Choice 2/25",
                "Total: U /78",
                "Predicting Products of All Types of Reactions (35 marks)",
                "Y/Y] 1.JAgNO3(aq) + MgBr2(aq) ->",
                "4. Mg(OH)2(aq) + 2 HBr(aq) >",
                "GI | 5-2Cu(s) + Cl2 ->",
                "9} 7. Na2O + SO3 ->",
                "2 - Q Cera",
                "Application Questions (18 Marks (Use full sentences for all questions to achieve full marks) | &",
                "1, Silver is a highly valuable metal used in batteries.",
                "2. Many antacid tablets contain calcium carbonate.",
            ]
        ),
        "file_name": "unit-2-test.pdf",
        "file_type": "pdf",
        "source_kind": "scanned_pdf",
    }

    patterns = extract_patterns_from_extraction(extraction)

    assert patterns["section_candidates"][0]["title"] == "Multiple Choice"
    assert patterns["section_candidates"][0]["mark_hint"] == 25
    assert patterns["section_candidates"][0]["detection_type"] == "scored_section_header"
    assert patterns["section_candidates"][1]["title"] == "Predicting Products of All Types of Reactions (35 marks)"
    assert patterns["numbering_patterns"]["unique_question_numbers"] == [1, 2, 4, 5, 7]
    previews = [item["preview"] for item in patterns["question_candidates"]]
    assert "Q Cera" not in previews


def test_blueprint_builder_infers_question_count_from_scored_multiple_choice_scan():
    extraction = {
        "text": "\n".join(
            [
                "SCH3U Unit 2 Chemical Reactions Test",
                "Multiple Choice 2/25",
                "Predicting Products of All Types of Reactions (35 marks)",
                "Y/Y] 1.JAgNO3(aq) + MgBr2(aq) ->",
                "4. Mg(OH)2(aq) + 2 HBr(aq) >",
                "GI | 5-2Cu(s) + Cl2 ->",
                "9} 7. Na2O + SO3 ->",
                "Application Questions (18 Marks (Use full sentences for all questions to achieve full marks) | &",
                "1, Silver is a highly valuable metal used in batteries.",
                "2. Many antacid tablets contain calcium carbonate.",
                "3. a) When properly lighting and adjusting a Bunsen burner",
                "4. Your friend wants to BBQ steaks for dinner.",
                "5. Many neutralization reactions can be proven with indicators.",
            ]
        ),
        "file_name": "unit-2-test.pdf",
        "file_type": "pdf",
        "source_kind": "scanned_pdf",
    }
    patterns = extract_patterns_from_extraction(extraction)
    topics = {
        "unit_name": "Unit 2 Chemical Reactions Test",
        "course_code": "SCH3U",
        "topic_distribution": [
            {"topic": "chemical_reactions", "weight_pct": 80.0, "matched_keywords": ["balance"]},
            {"topic": "lab_and_applications", "weight_pct": 20.0, "matched_keywords": ["application"]},
        ],
        "observed_topic_signals": [],
    }
    difficulty = {
        "easy_pct": 40.0,
        "medium_pct": 40.0,
        "hard_pct": 20.0,
        "analysis_confidence": "medium",
        "progression_notes": [],
        "cognitive_skills": [],
    }
    traps = {"trap_patterns": [], "observed_trap_signals": []}

    blueprint = build_blueprint_draft(
        subject="chemistry",
        extraction=extraction,
        patterns=patterns,
        topics=topics,
        difficulty=difficulty,
        traps=traps,
    )

    sections = blueprint["structure"]["sections"]
    assert sections[0]["title"] == "Multiple Choice"
    assert sections[0]["marks"] == 25
    assert sections[0]["num_questions"] == 25
    assert sections[1]["title"] == "Predicting Products of All Types of Reactions (35 marks)"
    assert sections[1]["num_questions"] >= 8


def test_cumulative_render_avoids_duplicate_question_stems(valid_blueprint):
    first = deepcopy(valid_blueprint)
    first["blueprint_id"] = "chemistry-unit-2"
    first["unit"]["unit_name"] = "Unit 2 Chemical Reactions"
    first["title"] = "Unit 2 Chemical Reactions Test"

    second = deepcopy(valid_blueprint)
    second["blueprint_id"] = "chemistry-unit-3"
    second["unit"]["unit_name"] = "Unit 3 Stoichiometry"
    second["title"] = "Unit 3 Stoichiometry Test"
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

    plan = build_cumulative_generation_plan_stub(
        [first, second],
        requested_version="verQuality",
    )
    rendered = render_cumulative_student_markdown(
        subject="chemistry",
        cumulative_plan=plan,
    )

    stems = [record["stem"] for record in rendered["question_records"]]

    assert len(stems) == len(set(stems))
