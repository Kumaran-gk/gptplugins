from __future__ import annotations

import json
from pathlib import Path

import fitz
import src.agent.workflow as workflow_module

from src.agent.workflow import AgentWorkflow, WorkflowRequest
from src.generation.section_generator import build_question_record


def test_generate_flow_creates_student_and_teacher_files(temp_settings, valid_blueprint):
    subject = "chemistry"
    subject_dirs = temp_settings.ensure_subject_dirs(subject)
    blueprint_path = Path(subject_dirs["blueprint_path"]) / "chemistry_unit-2-chemical-reactions-test_blueprint.json"
    blueprint_path.write_text(json.dumps(valid_blueprint, indent=2), encoding="utf-8")

    workflow = AgentWorkflow(settings=temp_settings)
    request = WorkflowRequest(
        skill="generate-test",
        subject=subject,
        blueprint_files=[str(blueprint_path)],
        options={"version": "verTest", "include_teacher": "true", "save_debug": "true"},
    )

    result = workflow.run(request)

    assert result["status"] == "ok"
    assert len(result["generation_outputs"]) == 1

    output = result["generation_outputs"][0]
    assert output["blueprint_valid"] is True
    assert output["student_test_path"] is not None
    assert output["teacher_test_path"] is not None

    student_path = Path(output["student_test_path"])
    teacher_path = Path(output["teacher_test_path"])
    artifact_root = Path(subject_dirs["generated_path"]) / "artifacts"

    assert student_path.exists()
    assert teacher_path.exists()
    assert artifact_root in student_path.parents
    assert artifact_root in teacher_path.parents

    student_text = student_path.read_text(encoding="utf-8")
    teacher_text = teacher_path.read_text(encoding="utf-8")

    assert "Student Version" in student_text
    assert "Teacher Version / Answer Key" in teacher_text


def test_generation_versions_can_change_mc_option_order():
    section_plan = {
        "title": "Section A - Multiple Choice",
        "question_types": ["multiple_choice"],
        "target_topics": ["chemical_reactions"],
    }

    version_a = build_question_record(
        subject="chemistry",
        section_plan=section_plan,
        question_number=1,
        question_index=0,
        used_signatures=None,
        version_label="verA",
    )
    version_b = build_question_record(
        subject="chemistry",
        section_plan=section_plan,
        question_number=1,
        question_index=0,
        used_signatures=None,
        version_label="verB",
    )

    assert version_a["answer_hint"] in {"A", "B", "C", "D"}
    assert version_b["answer_hint"] in {"A", "B", "C", "D"}
    assert version_a["options"] != version_b["options"] or version_a["answer_hint"] != version_b["answer_hint"]


def test_generate_flow_respects_section_num_questions_and_instructions(temp_settings, valid_blueprint):
    subject = "chemistry"
    subject_dirs = temp_settings.ensure_subject_dirs(subject)

    custom_blueprint = json.loads(json.dumps(valid_blueprint))
    custom_blueprint["structure"]["sections"] = [
        {
            "section_id": "section_1",
            "title": "Section A - Multiple Choice",
            "order": 1,
            "question_types": ["multiple_choice"],
            "marks": 4,
            "num_questions": 2,
            "instructions": "Choose the best answer for each question.",
        },
        {
            "section_id": "section_2",
            "title": "Section B - Written Response",
            "order": 2,
            "question_types": ["written_response"],
            "marks": 6,
            "num_questions": 1,
            "instructions": "Use full sentences and show reasoning.",
        },
    ]

    blueprint_path = Path(subject_dirs["blueprint_path"]) / "chemistry_structured_blueprint.json"
    blueprint_path.write_text(json.dumps(custom_blueprint, indent=2), encoding="utf-8")

    workflow = AgentWorkflow(settings=temp_settings)
    request = WorkflowRequest(
        skill="generate-test",
        subject=subject,
        blueprint_files=[str(blueprint_path)],
        options={"version": "verStructured", "include_teacher": "false", "save_debug": "false"},
    )

    result = workflow.run(request)
    output = result["generation_outputs"][0]
    student_text = Path(output["student_test_path"]).read_text(encoding="utf-8")

    assert output["question_count"] == 3
    assert "*Section Plan: 2 questions | 4 marks*" in student_text
    assert "*Instructions: Choose the best answer for each question.*" in student_text
    assert "*Section Plan: 1 question | 6 marks*" in student_text
    assert "*Instructions: Use full sentences and show reasoning.*" in student_text


def test_generate_flow_can_export_docx(temp_settings, valid_blueprint):
    subject = "chemistry"
    subject_dirs = temp_settings.ensure_subject_dirs(subject)
    blueprint_path = Path(subject_dirs["blueprint_path"]) / "chemistry_docx_blueprint.json"
    blueprint_path.write_text(json.dumps(valid_blueprint, indent=2), encoding="utf-8")

    workflow = AgentWorkflow(settings=temp_settings)
    request = WorkflowRequest(
        skill="generate-test",
        subject=subject,
        blueprint_files=[str(blueprint_path)],
        options={
            "version": "verDocx",
            "include_teacher": "true",
            "save_debug": "false",
            "export_formats": "md,docx",
        },
    )

    result = workflow.run(request)
    output = result["generation_outputs"][0]

    assert output["student_docx_path"] is not None
    assert output["teacher_docx_path"] is not None
    student_docx_path = Path(output["student_docx_path"])
    teacher_docx_path = Path(output["teacher_docx_path"])
    artifact_root = Path(subject_dirs["generated_path"]) / "artifacts"
    assert student_docx_path.exists()
    assert teacher_docx_path.exists()
    assert artifact_root in student_docx_path.parents
    assert artifact_root in teacher_docx_path.parents


def test_generate_flow_can_export_pdf(temp_settings, valid_blueprint):
    subject = "chemistry"
    subject_dirs = temp_settings.ensure_subject_dirs(subject)
    blueprint_path = Path(subject_dirs["blueprint_path"]) / "chemistry_pdf_blueprint.json"
    blueprint_path.write_text(json.dumps(valid_blueprint, indent=2), encoding="utf-8")

    workflow = AgentWorkflow(settings=temp_settings)
    request = WorkflowRequest(
        skill="generate-test",
        subject=subject,
        blueprint_files=[str(blueprint_path)],
        options={
            "version": "verPdf",
            "include_teacher": "true",
            "save_debug": "false",
            "export_formats": "md,pdf",
        },
    )

    result = workflow.run(request)
    output = result["generation_outputs"][0]

    assert output["student_pdf_path"] is not None
    assert output["teacher_pdf_path"] is not None
    student_pdf_path = Path(output["student_pdf_path"])
    teacher_pdf_path = Path(output["teacher_pdf_path"])

    assert student_pdf_path.exists()
    assert teacher_pdf_path.exists()
    assert student_pdf_path.parent == Path(subject_dirs["generated_path"])
    assert teacher_pdf_path.parent == Path(subject_dirs["generated_path"])

    student_doc = fitz.open(student_pdf_path)
    student_text = "\n".join(page.get_text() for page in student_doc)
    student_doc.close()

    assert "8." in student_text
    assert "Cu + Cl2 ->" in student_text or "CaCO3 ->" in student_text


def test_generate_flow_routes_non_pdf_outputs_to_artifact_folder(temp_settings, valid_blueprint):
    subject = "chemistry"
    subject_dirs = temp_settings.ensure_subject_dirs(subject)
    blueprint_path = Path(subject_dirs["blueprint_path"]) / "chemistry_artifact_blueprint.json"
    blueprint_path.write_text(json.dumps(valid_blueprint, indent=2), encoding="utf-8")

    workflow = AgentWorkflow(settings=temp_settings)
    request = WorkflowRequest(
        skill="generate-test",
        subject=subject,
        blueprint_files=[str(blueprint_path)],
        options={
            "version": "verArtifacts",
            "include_teacher": "true",
            "save_debug": "true",
            "export_formats": "pdf",
        },
    )

    result = workflow.run(request)
    output = result["generation_outputs"][0]
    artifact_root = Path(subject_dirs["generated_path"]) / "artifacts"

    assert artifact_root.exists()
    assert artifact_root in Path(output["student_test_path"]).parents
    assert artifact_root in Path(output["teacher_test_path"]).parents
    assert artifact_root in Path(output["generation_plan_debug_path"]).parents
    assert Path(output["student_pdf_path"]).parent == Path(subject_dirs["generated_path"])
    assert Path(output["teacher_pdf_path"]).parent == Path(subject_dirs["generated_path"])


def test_generate_flow_can_raise_question_complexity(temp_settings, valid_blueprint):
    subject = "chemistry"
    subject_dirs = temp_settings.ensure_subject_dirs(subject)
    blueprint_path = Path(subject_dirs["blueprint_path"]) / "chemistry_challenging_blueprint.json"
    blueprint_path.write_text(json.dumps(valid_blueprint, indent=2), encoding="utf-8")

    workflow = AgentWorkflow(settings=temp_settings)
    request = WorkflowRequest(
        skill="generate-test",
        subject=subject,
        blueprint_files=[str(blueprint_path)],
        options={
            "version": "verHarder",
            "include_teacher": "false",
            "save_debug": "false",
            "complexity_mode": "challenging",
        },
    )

    result = workflow.run(request)
    output = result["generation_outputs"][0]
    student_text = Path(output["student_test_path"]).read_text(encoding="utf-8")

    assert output["generation_plan"]["complexity_mode"] == "challenging"
    assert "Justify each major step or classification" in student_text or (
        "Consider balancing, classification, and any evidence" in student_text
    )


def test_generate_flow_can_use_gpt_backend_with_mock(temp_settings, valid_blueprint, monkeypatch):
    subject = "chemistry"
    subject_dirs = temp_settings.ensure_subject_dirs(subject)
    blueprint_path = Path(subject_dirs["blueprint_path"]) / "chemistry_gpt_blueprint.json"
    blueprint_path.write_text(json.dumps(valid_blueprint, indent=2), encoding="utf-8")

    def fake_enrich_generation_plan_with_gpt(*, blueprint, generation_plan, model, reasoning_effort, verbosity):
        enriched = json.loads(json.dumps(generation_plan))
        enriched["generation_backend"] = "gpt"
        enriched["openai_model"] = model
        for section_plan in enriched["section_plans"]:
            section_plan["prebuilt_questions"] = [
                {
                    "question_type": "multiple_choice"
                    if idx == 0
                    else "written_response",
                    "topic": "chemical_reactions",
                    "marks": 1 if idx == 0 else 3,
                    "stem": f"GPT grounded question {idx + 1} using unit content.",
                    "options": [
                        "A. Choice one",
                        "B. Choice two",
                        "C. Choice three",
                        "D. Choice four",
                    ]
                    if idx == 0
                    else [],
                    "answer_hint": "A" if idx == 0 else "Sample marking note",
                    "source_excerpt": "Argentite ore contains silver sulfide.",
                }
                for idx in range(section_plan["estimated_question_count"])
            ]
        return enriched

    monkeypatch.setattr(
        workflow_module,
        "enrich_generation_plan_with_gpt",
        fake_enrich_generation_plan_with_gpt,
    )

    workflow = AgentWorkflow(settings=temp_settings)
    request = WorkflowRequest(
        skill="generate-test",
        subject=subject,
        blueprint_files=[str(blueprint_path)],
        options={
            "version": "verGPT",
            "include_teacher": "false",
            "save_debug": "false",
            "use_gpt": "true",
            "openai_model": "gpt-5.4-mini",
            "content_bundle": {
                "source_file_count": 1,
                "snippet_count": 1,
                "top_terms": ["argentite"],
                "snippets": [
                    {
                        "excerpt": "Argentite ore contains silver sulfide.",
                        "topics": ["chemical_reactions"],
                    }
                ],
            },
        },
    )

    result = workflow.run(request)
    output = result["generation_outputs"][0]
    student_text = Path(output["student_test_path"]).read_text(encoding="utf-8")

    assert output["generation_backend"] == "gpt"
    assert output["openai_model"] == "gpt-5.4-mini"
    assert "GPT grounded question 1 using unit content." in student_text
