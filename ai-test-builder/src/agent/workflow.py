from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.analysis.difficulty_analyzer import analyze_difficulty_from_patterns
from src.analysis.pattern_extractor import extract_patterns_from_extraction
from src.analysis.topic_mapper import map_topics_from_extraction
from src.analysis.trap_detector import detect_trap_patterns
from src.blueprint.builder import build_blueprint_draft
from src.blueprint.validator import validate_blueprint
from src.config import Settings, slugify
from src.generation.test_generator import (
    build_generation_plan_stub,
    render_student_test_markdown,
    render_teacher_test_markdown,
    summarize_blueprint_for_generation,
)
from src.generation.gpt_generator import enrich_generation_plan_with_gpt
from src.generation.content_grounding import build_unit_content_bundle
from src.generation.docx_exporter import export_markdown_to_docx
from src.generation.pdf_exporter import export_markdown_to_pdf
from src.generation.cumulative_builder import (
    build_cumulative_generation_plan_stub,
    render_cumulative_student_markdown,
    render_cumulative_teacher_markdown,
    summarize_blueprints_for_cumulative,
)
from src.memory.blueprint_index import (
    build_blueprint_memory_record,
    build_cumulative_memory_record,
    build_generation_memory_record,
)
from src.blueprint.loader import load_blueprint_from_path, resolve_blueprint_paths
from src.memory.memory_store import append_memory_record
from src.ingestion.detector import detect_file_kind
from src.ingestion.docx_reader import read_docx
from src.ingestion.image_reader import read_image
from src.ingestion.normalizer import normalize_extraction
from src.ingestion.pdf_reader import read_pdf
from src.utils.file_io import write_json, write_text
from src.utils.logging_utils import get_logger


LOGGER = get_logger("agent.workflow")


@dataclass
class WorkflowRequest:
    skill: str
    subject: str
    input_files: List[str] = field(default_factory=list)
    blueprint_files: List[str] = field(default_factory=list)
    unit_content_files: List[str] = field(default_factory=list)
    options: Dict[str, Any] = field(default_factory=dict)


class AgentWorkflow:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def run(self, request: WorkflowRequest) -> Dict[str, Any]:
        if request.skill == "analyze-test":
            return self.analyze_test(request)
        if request.skill == "generate-test":
            return self.generate_test(request)
        if request.skill == "build-cumulative-test":
            return self.build_cumulative_test(request)
        if request.skill == "build-test-pack":
            return self.build_test_pack(request)
        raise ValueError(f"Unsupported skill: {request.skill}")

    @staticmethod
    def _is_true(value: Any, *, default: bool = False) -> bool:
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}

    @staticmethod
    def _parse_csv_option(value: Any, *, default: List[str]) -> List[str]:
        if value is None:
            return list(default)
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        return [item.strip() for item in str(value).split(",") if item.strip()]

    @staticmethod
    def _parse_unit_weights(value: Any) -> Dict[str, float]:
        unit_weights: Dict[str, float] = {}
        if value in {None, ""}:
            return unit_weights

        entries = value if isinstance(value, list) else str(value).split(",")
        for entry in entries:
            raw_entry = str(entry).strip()
            if not raw_entry:
                continue
            if ":" not in raw_entry:
                raise ValueError(
                    "Invalid unit_weights entry "
                    f"'{raw_entry}'. Expected Unit Name:weight format."
                )

            unit_name, weight_text = raw_entry.split(":", 1)
            try:
                unit_weights[unit_name.strip()] = float(weight_text.strip())
            except ValueError as exc:
                raise ValueError(
                    "Invalid unit_weights entry "
                    f"'{raw_entry}'. Weight must be numeric."
                ) from exc

        return unit_weights

    @staticmethod
    def _unique_output_path(directory: Path, filename: str) -> Path:
        candidate = directory / filename
        if not candidate.exists():
            return candidate

        stem = candidate.stem
        suffix = candidate.suffix
        counter = 2
        while True:
            numbered = directory / f"{stem}_{counter}{suffix}"
            if not numbered.exists():
                return numbered
            counter += 1

    @staticmethod
    def _collect_valid_blueprint_paths(analyze_result: Dict[str, Any]) -> List[str]:
        paths: List[str] = []
        for output in analyze_result.get("blueprint_outputs", []):
            blueprint_path = output.get("blueprint_path")
            if output.get("blueprint_valid") and blueprint_path:
                paths.append(str(blueprint_path))
        return paths

    @staticmethod
    def _dedupe_preserve_order(values: List[str]) -> List[str]:
        return list(dict.fromkeys([value for value in values if value]))

    @staticmethod
    def _requested_export_formats(options: Dict[str, Any]) -> List[str]:
        formats = AgentWorkflow._parse_csv_option(
            options.get("export_formats"),
            default=["md"],
        )
        normalized: List[str] = []
        for value in formats:
            lowered = value.strip().lower()
            if lowered in {"md", "markdown", "docx", "pdf"} and lowered not in normalized:
                if lowered in {"md", "markdown"}:
                    normalized.append("md")
                else:
                    normalized.append(lowered)
        return normalized or ["md"]

    @staticmethod
    def _unique_directory(parent: Path, directory_name: str) -> Path:
        parent.mkdir(parents=True, exist_ok=True)
        candidate = parent / directory_name
        if not candidate.exists():
            candidate.mkdir(parents=True, exist_ok=False)
            return candidate

        counter = 2
        while True:
            numbered = parent / f"{directory_name}_{counter}"
            if not numbered.exists():
                numbered.mkdir(parents=True, exist_ok=False)
                return numbered
            counter += 1

    @staticmethod
    def _safe_directory_name(value: str, *, max_length: int = 48) -> str:
        slug = slugify(value)
        if len(slug) <= max_length:
            return slug

        digest = hashlib.sha1(slug.encode("utf-8")).hexdigest()[:8]
        trimmed = slug[: max_length - len(digest) - 1].rstrip("-")
        return f"{trimmed}-{digest}"

    @staticmethod
    def _prepare_output_dirs(
        *,
        subject_generated_dir: Path,
        artifact_label: str,
        requested_artifact_root: Any = None,
    ) -> Dict[str, Path]:
        artifact_root = (
            Path(str(requested_artifact_root))
            if requested_artifact_root not in {None, ""}
            else subject_generated_dir / "artifacts"
        )
        artifact_root.mkdir(parents=True, exist_ok=True)
        artifact_dir = AgentWorkflow._unique_directory(
            artifact_root,
            AgentWorkflow._safe_directory_name(artifact_label),
        )
        return {
            "pdf_dir": subject_generated_dir,
            "artifact_root": artifact_root,
            "artifact_dir": artifact_dir,
        }

    def _read_source_extraction(
        self,
        file_path: str,
        *,
        pdf_mode: str,
        tesseract_cmd: Any,
        ocr_lang: str,
    ) -> Dict[str, Any]:
        file_kind = detect_file_kind(file_path)

        if file_kind == "pdf":
            raw = read_pdf(
                file_path,
                mode=pdf_mode,
                tesseract_cmd=tesseract_cmd,
                lang=ocr_lang,
            )
        elif file_kind == "docx":
            raw = read_docx(file_path)
        elif file_kind == "image":
            raw = read_image(
                file_path,
                tesseract_cmd=tesseract_cmd,
                lang=ocr_lang,
            )
        else:
            raise ValueError(f"Unsupported detected file kind: {file_kind}")

        normalized = normalize_extraction(raw)
        normalized["detected_file_kind"] = file_kind
        return normalized

    def _build_unit_content_artifacts(
        self,
        request: WorkflowRequest,
        *,
        artifact_dir: Path,
        subject_slug: str,
    ) -> Dict[str, Any] | None:
        if not request.unit_content_files:
            return None

        pdf_mode = request.options.get(
            "unit_content_pdf_mode",
            request.options.get("pdf_mode", "auto"),
        )
        tesseract_cmd = request.options.get("tesseract_cmd")
        ocr_lang = request.options.get("ocr_lang", "eng")

        LOGGER.info(
            "Building unit content bundle subject=%s files=%s",
            request.subject,
            len(request.unit_content_files),
        )

        normalized_files: List[Dict[str, Any]] = []
        combined_text_parts: List[str] = []
        for unit_content_file in request.unit_content_files:
            normalized = self._read_source_extraction(
                unit_content_file,
                pdf_mode=pdf_mode,
                tesseract_cmd=tesseract_cmd,
                ocr_lang=ocr_lang,
            )
            normalized_files.append(normalized)
            combined_text_parts.append(normalized.get("text", ""))

        content_bundle = build_unit_content_bundle(
            normalized_files,
            subject=request.subject,
        )
        combined_text = "\n\n".join(
            part.strip() for part in combined_text_parts if part.strip()
        ).strip()

        bundle_path = self._unique_output_path(
            artifact_dir,
            f"{subject_slug}_unit_content_bundle.json",
        )
        text_path = self._unique_output_path(
            artifact_dir,
            f"{subject_slug}_unit_content_text.txt",
        )

        write_json(bundle_path, content_bundle)
        write_text(text_path, combined_text)

        LOGGER.info(
            "Created unit content bundle subject=%s bundle=%s text=%s snippets=%s",
            request.subject,
            bundle_path,
            text_path,
            content_bundle.get("snippet_count"),
        )

        return {
            "content_bundle": content_bundle,
            "content_bundle_path": str(bundle_path),
            "content_text_path": str(text_path),
            "content_sources": [
                {
                    "file_name": normalized.get("file_name"),
                    "file_kind": normalized.get("detected_file_kind"),
                    "source_kind": normalized.get("source_kind"),
                    "page_count": normalized.get("page_count"),
                }
                for normalized in normalized_files
            ],
        }

    def analyze_test(self, request: WorkflowRequest) -> Dict[str, Any]:
        if not request.input_files:
            raise ValueError("analyze-test requires at least one input file.")

        subject_dirs = self.settings.ensure_subject_dirs(request.subject)
        subject_slug = slugify(request.subject)

        extraction_mode = request.options.get("pdf_mode", "auto")
        tesseract_cmd = request.options.get("tesseract_cmd")
        ocr_lang = request.options.get("ocr_lang", "eng")
        save_debug = str(request.options.get("save_debug", "true")).lower() == "true"

        extracted_files: List[Dict[str, Any]] = []
        all_observed_patterns: List[str] = []
        all_topic_signals: List[str] = []
        blueprint_outputs: List[Dict[str, Any]] = []

        LOGGER.info(
            "Starting analyze-test subject=%s inputs=%s",
            request.subject,
            len(request.input_files),
        )

        for input_file in request.input_files:
            file_kind = detect_file_kind(input_file)
            LOGGER.info("Analyzing input_file=%s file_kind=%s", input_file, file_kind)
            normalized = self._read_source_extraction(
                input_file,
                pdf_mode=extraction_mode,
                tesseract_cmd=tesseract_cmd,
                ocr_lang=ocr_lang,
            )
            patterns = extract_patterns_from_extraction(normalized)
            topics = map_topics_from_extraction(normalized, subject=request.subject)
            difficulty = analyze_difficulty_from_patterns(normalized, patterns)
            traps = detect_trap_patterns(normalized, patterns, subject=request.subject)

            blueprint = build_blueprint_draft(
                subject=request.subject,
                extraction=normalized,
                patterns=patterns,
                topics=topics,
                difficulty=difficulty,
                traps=traps,
            )

            validation = validate_blueprint(
                blueprint,
                self.settings.blueprint_schema_path,
            )

            debug_json_path: Optional[Path] = None
            pattern_json_path: Optional[Path] = None
            analysis_json_path: Optional[Path] = None
            blueprint_json_path: Optional[Path] = None
            validation_json_path: Optional[Path] = None

            source_stem = Path(input_file).stem

            if save_debug:
                debug_json_path = (
                    subject_dirs["blueprint_path"]
                    / f"{source_stem}_extraction_debug.json"
                )
                pattern_json_path = (
                    subject_dirs["blueprint_path"]
                    / f"{source_stem}_pattern_debug.json"
                )
                analysis_json_path = (
                    subject_dirs["blueprint_path"]
                    / f"{source_stem}_analysis_debug.json"
                )
                validation_json_path = (
                    subject_dirs["blueprint_path"]
                    / f"{source_stem}_validation_debug.json"
                )

                write_json(debug_json_path, normalized)
                write_json(pattern_json_path, patterns)
                write_json(
                    analysis_json_path,
                    {
                        "file_name": normalized.get("file_name"),
                        "subject": request.subject,
                        "patterns": patterns,
                        "topics": topics,
                        "difficulty": difficulty,
                        "traps": traps,
                    },
                )
                write_json(validation_json_path, validation)

            memory_record_path: Optional[Path] = None

            if validation["is_valid"]:
                unit_slug = slugify(topics.get("unit_name") or source_stem)
                blueprint_json_path = (
                    subject_dirs["blueprint_path"]
                    / f"{subject_slug}_{unit_slug}_blueprint.json"
                )
                write_json(blueprint_json_path, blueprint)

                blueprint_memory_record = build_blueprint_memory_record(blueprint)
                memory_record_path = append_memory_record(
                    memory_dir=self.settings.memory_dir,
                    subject_slug=subject_slug,
                    record=blueprint_memory_record,
                )
                LOGGER.info(
                    "Created blueprint subject=%s path=%s memory_path=%s",
                    request.subject,
                    blueprint_json_path,
                    memory_record_path,
                )

            observed_patterns = patterns.get("observed_patterns", [])
            topic_signals = topics.get("observed_topic_signals", [])

            all_observed_patterns.extend(observed_patterns)
            all_topic_signals.extend(topic_signals)

            extracted_files.append(
                {
                    "input_file": input_file,
                    "file_kind": file_kind,
                    "file_name": normalized["file_name"],
                    "source_kind": normalized.get("source_kind"),
                    "page_count": normalized.get("page_count"),
                    "segment_count": len(normalized.get("segments", [])),
                    "char_count": len(normalized.get("text", "")),
                    "preview": normalized.get("text", "")[:1000],
                    "title_candidate": patterns.get("layout_signals", {}).get("title_candidate"),
                    "section_candidate_count": len(patterns.get("section_candidates", [])),
                    "question_candidate_count": len(patterns.get("question_candidates", [])),
                    "multiple_choice_detected": patterns.get("multiple_choice_signals", {}).get(
                        "likely_multiple_choice_present", False
                    ),
                    "course_code": topics.get("course_code"),
                    "unit_name": topics.get("unit_name"),
                    "topic_distribution": topics.get("topic_distribution", []),
                    "difficulty_profile": {
                        "easy_pct": difficulty.get("easy_pct"),
                        "medium_pct": difficulty.get("medium_pct"),
                        "hard_pct": difficulty.get("hard_pct"),
                        "analysis_confidence": difficulty.get("analysis_confidence"),
                    },
                    "cognitive_skills": difficulty.get("cognitive_skills", []),
                    "trap_pattern_count": len(traps.get("trap_patterns", [])),
                    "observed_patterns": observed_patterns,
                    "observed_topic_signals": topic_signals,
                    "debug_json_path": str(debug_json_path) if debug_json_path else None,
                    "pattern_debug_path": str(pattern_json_path) if pattern_json_path else None,
                    "analysis_debug_path": str(analysis_json_path) if analysis_json_path else None,
                    "validation_debug_path": str(validation_json_path) if validation_json_path else None,
                    "blueprint_path": str(blueprint_json_path) if blueprint_json_path else None,
                    "blueprint_valid": validation["is_valid"],
                    "blueprint_error_count": validation["error_count"],
                    "memory_record_path": str(memory_record_path) if memory_record_path else None,
                }
            )

            blueprint_outputs.append(
                {
                    "input_file": input_file,
                    "blueprint_valid": validation["is_valid"],
                    "blueprint_path": str(blueprint_json_path) if blueprint_json_path else None,
                    "validation_errors": validation["errors"],
                    "memory_record_path": str(memory_record_path) if memory_record_path else None,
                }
            )

        unique_observed_patterns = list(dict.fromkeys(all_observed_patterns))
        unique_topic_signals = list(dict.fromkeys(all_topic_signals))

        overall_valid = all(item["blueprint_valid"] for item in blueprint_outputs)

        return {
            "status": "ok" if overall_valid else "partial",
            "skill": request.skill,
            "subject": request.subject,
            "subject_slug": subject_slug,
            "schema_path": str(self.settings.blueprint_schema_path),
            "extracted_files": extracted_files,
            "blueprint_outputs": blueprint_outputs,
            "overall_observed_patterns": unique_observed_patterns,
            "overall_topic_signals": unique_topic_signals,
            "next_implementation_stage": [
                "improve OCR cleanup and structure detection quality",
                "deepen subject-specific extensions beyond current heuristics",
                "expand retrieval and cumulative-flow test coverage",
                "reduce extraction noise in saved blueprint titles and patterns",
            ],
        }

    def build_test_pack(self, request: WorkflowRequest) -> Dict[str, Any]:
        subject_dirs = self.settings.ensure_subject_dirs(request.subject)
        subject_slug = slugify(request.subject)

        if not request.input_files and not request.blueprint_files:
            raise ValueError(
                "build-test-pack requires at least one input file or blueprint file."
            )

        versions = self._parse_csv_option(
            request.options.get("versions"),
            default=["verA", "verB"],
        )
        include_teacher = self._is_true(
            request.options.get("include_teacher"),
            default=True,
        )
        save_debug = self._is_true(
            request.options.get("save_debug"),
            default=True,
        )
        export_formats = self._requested_export_formats(request.options)
        build_cumulative = self._is_true(
            request.options.get("build_cumulative"),
            default=False,
        )
        cumulative_version = request.options.get("cumulative_version", "cumulative")
        manifest_label = request.options.get("manifest_label", "run")
        unit_weights = self._parse_unit_weights(request.options.get("unit_weights"))
        complexity_mode = request.options.get("complexity_mode")
        pack_output_dirs = self._prepare_output_dirs(
            subject_generated_dir=subject_dirs["generated_path"],
            artifact_label=f"{subject_slug}_test_pack_{manifest_label}",
            requested_artifact_root=request.options.get("artifact_root_dir"),
        )

        LOGGER.info(
            "Starting build-test-pack subject=%s inputs=%s blueprints=%s unit_content=%s versions=%s build_cumulative=%s",
            request.subject,
            len(request.input_files),
            len(request.blueprint_files),
            len(request.unit_content_files),
            versions,
            build_cumulative,
        )

        unit_content_artifacts = self._build_unit_content_artifacts(
            request,
            artifact_dir=pack_output_dirs["artifact_dir"],
            subject_slug=subject_slug,
        )

        analysis_result: Optional[Dict[str, Any]] = None
        analyzed_blueprint_paths: List[str] = []
        if request.input_files:
            analysis_request = WorkflowRequest(
                skill="analyze-test",
                subject=request.subject,
                input_files=request.input_files,
                options={
                    **request.options,
                    "save_debug": str(save_debug).lower(),
                },
            )
            analysis_result = self.analyze_test(analysis_request)
            analyzed_blueprint_paths = self._collect_valid_blueprint_paths(analysis_result)

        blueprint_paths = self._dedupe_preserve_order(
            analyzed_blueprint_paths + [str(path) for path in request.blueprint_files]
        )

        if not blueprint_paths:
            raise ValueError(
                "build-test-pack could not produce or resolve any valid blueprint files."
            )

        version_results: List[Dict[str, Any]] = []
        generated_student_paths: List[str] = []
        generated_teacher_paths: List[str] = []
        generated_student_docx_paths: List[str] = []
        generated_teacher_docx_paths: List[str] = []
        generated_student_pdf_paths: List[str] = []
        generated_teacher_pdf_paths: List[str] = []

        for version_label in versions:
            generation_request = WorkflowRequest(
                skill="generate-test",
                subject=request.subject,
                blueprint_files=blueprint_paths,
                options={
                    "version": version_label,
                    "include_teacher": str(include_teacher).lower(),
                    "save_debug": str(save_debug).lower(),
                    "export_formats": ",".join(export_formats),
                    "content_bundle": (
                        unit_content_artifacts.get("content_bundle")
                        if unit_content_artifacts
                        else None
                    ),
                    "generation_backend": request.options.get("generation_backend"),
                    "use_gpt": request.options.get("use_gpt"),
                    "openai_model": request.options.get("openai_model"),
                    "openai_reasoning_effort": request.options.get("openai_reasoning_effort"),
                    "openai_verbosity": request.options.get("openai_verbosity"),
                    "complexity_mode": complexity_mode,
                    "artifact_root_dir": str(pack_output_dirs["artifact_dir"]),
                },
            )
            generation_result = self.generate_test(generation_request)
            version_results.append(generation_result)

            for output in generation_result.get("generation_outputs", []):
                student_path = output.get("student_test_path")
                teacher_path = output.get("teacher_test_path")
                student_docx_path = output.get("student_docx_path")
                teacher_docx_path = output.get("teacher_docx_path")
                student_pdf_path = output.get("student_pdf_path")
                teacher_pdf_path = output.get("teacher_pdf_path")
                if student_path:
                    generated_student_paths.append(student_path)
                if teacher_path:
                    generated_teacher_paths.append(teacher_path)
                if student_docx_path:
                    generated_student_docx_paths.append(student_docx_path)
                if teacher_docx_path:
                    generated_teacher_docx_paths.append(teacher_docx_path)
                if student_pdf_path:
                    generated_student_pdf_paths.append(student_pdf_path)
                if teacher_pdf_path:
                    generated_teacher_pdf_paths.append(teacher_pdf_path)

        cumulative_result: Optional[Dict[str, Any]] = None
        if build_cumulative and len(blueprint_paths) >= 2:
            cumulative_options: Dict[str, Any] = {
                "version": cumulative_version,
                "include_teacher": str(include_teacher).lower(),
                "save_debug": str(save_debug).lower(),
                "export_formats": ",".join(export_formats),
                "complexity_mode": complexity_mode,
                "artifact_root_dir": str(pack_output_dirs["artifact_dir"]),
            }
            if unit_weights:
                cumulative_options["unit_weights"] = ",".join(
                    f"{unit_name}:{weight:g}" for unit_name, weight in unit_weights.items()
                )

            cumulative_request = WorkflowRequest(
                skill="build-cumulative-test",
                subject=request.subject,
                blueprint_files=blueprint_paths,
                options=cumulative_options,
            )
            cumulative_result = self.build_cumulative_test(cumulative_request)

        manifest = {
            "status": "ok",
            "skill": request.skill,
            "subject": request.subject,
            "subject_slug": subject_slug,
            "input_files": request.input_files,
            "blueprint_files": blueprint_paths,
            "unit_content_files": request.unit_content_files,
            "versions_requested": versions,
            "include_teacher": include_teacher,
            "export_formats": export_formats,
            "build_cumulative": build_cumulative,
            "unit_weights": unit_weights,
            "unit_content_bundle_path": (
                unit_content_artifacts.get("content_bundle_path")
                if unit_content_artifacts
                else None
            ),
            "unit_content_text_path": (
                unit_content_artifacts.get("content_text_path")
                if unit_content_artifacts
                else None
            ),
            "unit_content_summary": (
                unit_content_artifacts.get("content_bundle")
                if unit_content_artifacts
                else None
            ),
            "analysis_result": analysis_result,
            "version_results": version_results,
            "cumulative_result": cumulative_result,
            "generated_student_paths": self._dedupe_preserve_order(generated_student_paths),
            "generated_teacher_paths": self._dedupe_preserve_order(generated_teacher_paths),
            "generated_student_docx_paths": self._dedupe_preserve_order(generated_student_docx_paths),
            "generated_teacher_docx_paths": self._dedupe_preserve_order(generated_teacher_docx_paths),
            "generated_student_pdf_paths": self._dedupe_preserve_order(generated_student_pdf_paths),
            "generated_teacher_pdf_paths": self._dedupe_preserve_order(generated_teacher_pdf_paths),
        }

        manifest_path = self._unique_output_path(
            pack_output_dirs["artifact_dir"],
            f"{subject_slug}_test_pack_manifest_{slugify(str(manifest_label))}.json",
        )
        write_json(manifest_path, manifest)

        partial_status = False
        if analysis_result and analysis_result.get("status") != "ok":
            partial_status = True
        if any(result.get("status") != "ok" for result in version_results):
            partial_status = True
        if build_cumulative and len(blueprint_paths) < 2:
            partial_status = True
        if cumulative_result and cumulative_result.get("status") != "ok":
            partial_status = True

        status = "partial" if partial_status else "ok"
        cumulative_state = (
            "generated"
            if cumulative_result
            else "skipped_insufficient_blueprints"
            if build_cumulative and len(blueprint_paths) < 2
            else "not_requested"
        )

        LOGGER.info(
            "Completed build-test-pack subject=%s blueprints=%s versions=%s cumulative=%s manifest=%s",
            request.subject,
            len(blueprint_paths),
            len(version_results),
            cumulative_state,
            manifest_path,
        )

        return {
            "status": status,
            "skill": request.skill,
            "subject": request.subject,
            "subject_slug": subject_slug,
            "manifest_path": str(manifest_path),
            "artifact_dir": str(pack_output_dirs["artifact_dir"]),
            "analysis_result": analysis_result,
            "blueprint_paths": blueprint_paths,
            "unit_content_files": request.unit_content_files,
            "unit_content_bundle_path": (
                unit_content_artifacts.get("content_bundle_path")
                if unit_content_artifacts
                else None
            ),
            "unit_content_text_path": (
                unit_content_artifacts.get("content_text_path")
                if unit_content_artifacts
                else None
            ),
            "unit_content_summary": (
                unit_content_artifacts.get("content_bundle")
                if unit_content_artifacts
                else None
            ),
            "versions_requested": versions,
            "export_formats": export_formats,
            "version_results": version_results,
            "generated_student_paths": self._dedupe_preserve_order(generated_student_paths),
            "generated_teacher_paths": self._dedupe_preserve_order(generated_teacher_paths),
            "generated_student_docx_paths": self._dedupe_preserve_order(generated_student_docx_paths),
            "generated_teacher_docx_paths": self._dedupe_preserve_order(generated_teacher_docx_paths),
            "generated_student_pdf_paths": self._dedupe_preserve_order(generated_student_pdf_paths),
            "generated_teacher_pdf_paths": self._dedupe_preserve_order(generated_teacher_pdf_paths),
            "cumulative_state": cumulative_state,
            "cumulative_result": cumulative_result,
            "unit_weights": unit_weights,
            "next_implementation_stage": [
                "add a docx/pdf packaging layer for print-ready export",
                "support richer cumulative weighting strategies in question allocation",
                "improve generated question freshness beyond current templates",
            ],
        }

    def generate_test(self, request: WorkflowRequest) -> Dict[str, Any]:
        subject_dirs = self.settings.ensure_subject_dirs(request.subject)
        subject_slug = slugify(request.subject)

        version_label = request.options.get("version", "v1")
        save_debug = self._is_true(request.options.get("save_debug"), default=True)
        include_teacher = self._is_true(
            request.options.get("include_teacher"),
            default=True,
        )
        export_formats = self._requested_export_formats(request.options)
        content_bundle = request.options.get("content_bundle")
        complexity_mode = request.options.get("complexity_mode")
        raw_generation_backend = request.options.get("generation_backend")
        generation_backend = (
            str(raw_generation_backend).strip().lower()
            if raw_generation_backend not in {None, ""}
            else "gpt" if self._is_true(request.options.get("use_gpt")) else "template"
        )
        raw_openai_model = request.options.get("openai_model")
        openai_model = (
            str(raw_openai_model).strip()
            if raw_openai_model not in {None, ""}
            else "gpt-5.4-mini"
        )
        raw_reasoning_effort = request.options.get("openai_reasoning_effort")
        openai_reasoning_effort = (
            str(raw_reasoning_effort).strip()
            if raw_reasoning_effort not in {None, ""}
            else "none"
        )
        raw_openai_verbosity = request.options.get("openai_verbosity")
        openai_verbosity = (
            str(raw_openai_verbosity).strip()
            if raw_openai_verbosity not in {None, ""}
            else "low"
        )
        blueprint_query = request.options.get("blueprint_query")
        max_blueprints = int(request.options.get("max_blueprints", "1"))

        resolved = resolve_blueprint_paths(
            explicit_paths=request.blueprint_files,
            subject_blueprint_dir=subject_dirs["blueprint_path"],
            query=blueprint_query,
            limit=max_blueprints,
            memory_dir=self.settings.memory_dir,
            subject_slug=subject_slug,
        )

        resolved_paths = resolved["resolved_paths"]
        if not resolved_paths:
            raise ValueError(
                "generate-test could not resolve any blueprint files. "
                "Pass --blueprints explicitly or use --option blueprint_query=..."
            )

        generation_outputs: List[Dict[str, Any]] = []

        LOGGER.info(
            "Starting generate-test subject=%s resolved_blueprints=%s include_teacher=%s",
            request.subject,
            len(resolved_paths),
            include_teacher,
        )

        for blueprint_file in resolved_paths:
            blueprint_path = Path(blueprint_file)

            if not blueprint_path.exists():
                raise FileNotFoundError(f"Blueprint file not found: {blueprint_path}")

            blueprint = load_blueprint_from_path(blueprint_path)
            validation = validate_blueprint(
                blueprint,
                self.settings.blueprint_schema_path,
            )

            plan_debug_path: Optional[Path] = None
            validation_debug_path: Optional[Path] = None
            render_debug_path: Optional[Path] = None
            teacher_debug_path: Optional[Path] = None
            student_test_path: Optional[Path] = None
            teacher_test_path: Optional[Path] = None
            student_docx_path: Optional[Path] = None
            teacher_docx_path: Optional[Path] = None
            student_pdf_path: Optional[Path] = None
            teacher_pdf_path: Optional[Path] = None
            memory_record_path: Optional[Path] = None

            generation_plan: Optional[Dict[str, Any]] = None
            blueprint_summary: Optional[Dict[str, Any]] = None
            rendered_test: Optional[Dict[str, Any]] = None
            rendered_teacher: Optional[Dict[str, Any]] = None

            source_stem = blueprint_path.stem.replace("_blueprint", "")
            artifact_stem = self._safe_directory_name(source_stem, max_length=24)
            artifact_root_override = request.options.get("artifact_root_dir")
            artifact_label = (
                f"gen_{version_label}"
                if artifact_root_override not in {None, ""}
                else f"{source_stem}_{version_label}"
            )
            output_dirs = self._prepare_output_dirs(
                subject_generated_dir=subject_dirs["generated_path"],
                artifact_label=artifact_label,
                requested_artifact_root=artifact_root_override,
            )

            if validation["is_valid"]:
                blueprint_summary = summarize_blueprint_for_generation(blueprint)
                generation_plan = build_generation_plan_stub(
                    blueprint,
                    requested_version=version_label,
                    content_bundle=content_bundle,
                    complexity_mode=complexity_mode,
                )
                if generation_backend == "gpt":
                    generation_plan = enrich_generation_plan_with_gpt(
                        blueprint=blueprint,
                        generation_plan=generation_plan,
                        model=openai_model,
                        reasoning_effort=openai_reasoning_effort,
                        verbosity=openai_verbosity,
                    )
                rendered_test = render_student_test_markdown(
                    blueprint,
                    generation_plan,
                )

                student_test_path = (
                    self._unique_output_path(
                        output_dirs["artifact_dir"],
                        f"{artifact_stem}_student_{version_label}.md",
                    )
                )
                write_text(student_test_path, rendered_test["markdown"])
                if "docx" in export_formats:
                    student_docx_path = self._unique_output_path(
                        output_dirs["artifact_dir"],
                        f"{artifact_stem}_student_{version_label}.docx",
                    )
                    export_markdown_to_docx(
                        rendered_test["markdown"],
                        student_docx_path,
                    )
                if "pdf" in export_formats:
                    student_pdf_path = self._unique_output_path(
                        output_dirs["pdf_dir"],
                        f"{source_stem}_student_{version_label}.pdf",
                    )
                    export_markdown_to_pdf(
                        rendered_test["markdown"],
                        student_pdf_path,
                    )

                if include_teacher:
                    rendered_teacher = render_teacher_test_markdown(
                        blueprint,
                        generation_plan,
                        rendered_test,
                    )
                    teacher_test_path = (
                        self._unique_output_path(
                            output_dirs["artifact_dir"],
                            f"{artifact_stem}_teacher_{version_label}.md",
                        )
                    )
                    write_text(teacher_test_path, rendered_teacher["markdown"])
                    if "docx" in export_formats:
                        teacher_docx_path = self._unique_output_path(
                            output_dirs["artifact_dir"],
                            f"{artifact_stem}_teacher_{version_label}.docx",
                        )
                        export_markdown_to_docx(
                            rendered_teacher["markdown"],
                            teacher_docx_path,
                        )
                    if "pdf" in export_formats:
                        teacher_pdf_path = self._unique_output_path(
                            output_dirs["pdf_dir"],
                            f"{source_stem}_teacher_{version_label}.pdf",
                        )
                        export_markdown_to_pdf(
                            rendered_teacher["markdown"],
                            teacher_pdf_path,
                        )

                generation_memory_record = build_generation_memory_record(
                    blueprint=blueprint,
                    version_label=version_label,
                    student_test_path=str(student_test_path) if student_test_path else None,
                    teacher_test_path=str(teacher_test_path) if teacher_test_path else None,
                )
                memory_record_path = append_memory_record(
                    memory_dir=self.settings.memory_dir,
                    subject_slug=subject_slug,
                    record=generation_memory_record,
                )
                LOGGER.info(
                    "Generated test subject=%s blueprint=%s student=%s teacher=%s",
                    request.subject,
                    blueprint_path,
                    student_test_path,
                    teacher_test_path,
                )

                if save_debug:
                    plan_debug_path = (
                        output_dirs["artifact_dir"]
                        / f"{artifact_stem}_generation_plan_debug.json"
                    )
                    validation_debug_path = (
                        output_dirs["artifact_dir"]
                        / f"{artifact_stem}_generation_validation_debug.json"
                    )
                    render_debug_path = (
                        output_dirs["artifact_dir"]
                        / f"{artifact_stem}_generation_render_debug.json"
                    )

                    write_json(plan_debug_path, generation_plan)
                    write_json(validation_debug_path, validation)
                    write_json(
                        render_debug_path,
                        {
                            "question_count": rendered_test["question_count"],
                            "question_records": rendered_test["question_records"],
                        },
                    )

                    if rendered_teacher:
                        teacher_debug_path = (
                            output_dirs["artifact_dir"]
                            / f"{artifact_stem}_teacher_render_debug.json"
                        )
                        write_json(
                            teacher_debug_path,
                            {
                                "question_count": rendered_teacher["question_count"],
                                "answer_key_records": rendered_teacher["answer_key_records"],
                            },
                        )

            else:
                if save_debug:
                    validation_debug_path = (
                        output_dirs["artifact_dir"]
                        / f"{artifact_stem}_generation_validation_debug.json"
                    )
                    write_json(validation_debug_path, validation)

            generation_outputs.append(
                {
                    "blueprint_file": str(blueprint_path),
                    "blueprint_valid": validation["is_valid"],
                    "blueprint_error_count": validation["error_count"],
                    "blueprint_summary": blueprint_summary,
                    "content_grounding_summary": (
                        generation_plan.get("content_grounding_summary")
                        if generation_plan
                        else None
                    ),
                    "generation_backend": generation_plan.get("generation_backend", generation_backend)
                    if generation_plan
                    else generation_backend,
                    "openai_model": generation_plan.get("openai_model") if generation_plan else None,
                    "generation_plan": generation_plan,
                    "artifact_dir": str(output_dirs["artifact_dir"]),
                    "question_count": rendered_test["question_count"] if rendered_test else 0,
                    "student_test_path": str(student_test_path) if student_test_path else None,
                    "teacher_test_path": str(teacher_test_path) if teacher_test_path else None,
                    "student_docx_path": str(student_docx_path) if student_docx_path else None,
                    "teacher_docx_path": str(teacher_docx_path) if teacher_docx_path else None,
                    "student_pdf_path": str(student_pdf_path) if student_pdf_path else None,
                    "teacher_pdf_path": str(teacher_pdf_path) if teacher_pdf_path else None,
                    "student_test_preview": (
                        rendered_test["markdown"][:800] if rendered_test else None
                    ),
                    "generation_plan_debug_path": str(plan_debug_path) if plan_debug_path else None,
                    "render_debug_path": str(render_debug_path) if render_debug_path else None,
                    "teacher_debug_path": str(teacher_debug_path) if teacher_debug_path else None,
                    "validation_debug_path": str(validation_debug_path) if validation_debug_path else None,
                    "memory_record_path": str(memory_record_path) if memory_record_path else None,
                }
            )

        overall_valid = all(item["blueprint_valid"] for item in generation_outputs)

        return {
            "status": "ok" if overall_valid else "partial",
            "skill": request.skill,
            "subject": request.subject,
            "subject_slug": subject_slug,
            "output_generated_dir": str(subject_dirs["generated_path"]),
            "artifact_root_dir": str(
                Path(str(request.options.get("artifact_root_dir")))
                if request.options.get("artifact_root_dir") not in {None, ""}
                else subject_dirs["generated_path"] / "artifacts"
            ),
            "export_formats": export_formats,
            "generation_backend": generation_backend,
            "openai_model": openai_model if generation_backend == "gpt" else None,
            "content_grounding_summary": (
                {
                    "source_file_count": content_bundle.get("source_file_count"),
                    "snippet_count": content_bundle.get("snippet_count"),
                    "top_terms": content_bundle.get("top_terms", []),
                }
                if isinstance(content_bundle, dict)
                else None
            ),
            "blueprint_resolution": resolved,
            "generation_outputs": generation_outputs,
            "next_implementation_stage": [
                "improve question richness and variation quality",
                "deepen subject-specific generation constraints and variation",
                "expand retrieval and blueprint-resolution tests",
                "reduce repeated template usage across generated versions",
            ],
        }

    def build_cumulative_test(self, request: WorkflowRequest) -> Dict[str, Any]:
        subject_dirs = self.settings.ensure_subject_dirs(request.subject)
        subject_slug = slugify(request.subject)

        version_label = request.options.get("version", "v1")
        save_debug = self._is_true(request.options.get("save_debug"), default=True)
        include_teacher = self._is_true(
            request.options.get("include_teacher"),
            default=True,
        )
        export_formats = self._requested_export_formats(request.options)
        blueprint_query = request.options.get("blueprint_query")
        max_blueprints = int(request.options.get("max_blueprints", "2"))
        unit_weights = self._parse_unit_weights(request.options.get("unit_weights"))
        complexity_mode = request.options.get("complexity_mode")

        resolved = resolve_blueprint_paths(
            explicit_paths=request.blueprint_files,
            subject_blueprint_dir=subject_dirs["blueprint_path"],
            query=blueprint_query,
            limit=max_blueprints,
            memory_dir=self.settings.memory_dir,
            subject_slug=subject_slug,
        )

        resolved_paths = resolved["resolved_paths"]
        if not resolved_paths:
            raise ValueError(
                "build-cumulative-test could not resolve any blueprint files. "
                "Pass --blueprints explicitly or use --option blueprint_query=..."
            )

        loaded_blueprints: List[Dict[str, Any]] = []
        blueprint_results: List[Dict[str, Any]] = []

        LOGGER.info(
            "Starting build-cumulative-test subject=%s resolved_blueprints=%s include_teacher=%s",
            request.subject,
            len(resolved_paths),
            include_teacher,
        )

        for blueprint_file in resolved_paths:
            blueprint_path = Path(blueprint_file)

            if not blueprint_path.exists():
                raise FileNotFoundError(f"Blueprint file not found: {blueprint_path}")

            blueprint = load_blueprint_from_path(blueprint_path)
            validation = validate_blueprint(
                blueprint,
                self.settings.blueprint_schema_path,
            )

            blueprint_results.append(
                {
                    "blueprint_file": str(blueprint_path),
                    "blueprint_valid": validation["is_valid"],
                    "blueprint_error_count": validation["error_count"],
                    "unit_name": blueprint.get("unit", {}).get("unit_name"),
                    "validation_errors": validation["errors"],
                }
            )

            if validation["is_valid"]:
                loaded_blueprints.append(blueprint)

        cumulative_summary: Optional[Dict[str, Any]] = None
        cumulative_plan: Optional[Dict[str, Any]] = None
        cumulative_render: Optional[Dict[str, Any]] = None
        cumulative_teacher_render: Optional[Dict[str, Any]] = None
        cumulative_plan_path: Optional[Path] = None
        cumulative_validation_path: Optional[Path] = None
        cumulative_render_path: Optional[Path] = None
        cumulative_teacher_debug_path: Optional[Path] = None
        cumulative_student_test_path: Optional[Path] = None
        cumulative_teacher_test_path: Optional[Path] = None
        cumulative_student_docx_path: Optional[Path] = None
        cumulative_teacher_docx_path: Optional[Path] = None
        cumulative_student_pdf_path: Optional[Path] = None
        cumulative_teacher_pdf_path: Optional[Path] = None
        memory_record_path: Optional[Path] = None
        output_dirs = self._prepare_output_dirs(
            subject_generated_dir=subject_dirs["generated_path"],
            artifact_label=(
                f"cum_{version_label}"
                if request.options.get("artifact_root_dir") not in {None, ""}
                else f"{subject_slug}_cumulative_{version_label}"
            ),
            requested_artifact_root=request.options.get("artifact_root_dir"),
        )
        artifact_subject_stem = self._safe_directory_name(
            f"{subject_slug}_cumulative",
            max_length=24,
        )

        if loaded_blueprints:
            cumulative_summary = summarize_blueprints_for_cumulative(loaded_blueprints)
            cumulative_plan = build_cumulative_generation_plan_stub(
                loaded_blueprints,
                requested_version=version_label,
                unit_weights=unit_weights,
            )
            cumulative_plan["complexity_mode"] = complexity_mode
            for section_plan in cumulative_plan.get("section_plans", []):
                section_plan["complexity_mode"] = complexity_mode
            cumulative_render = render_cumulative_student_markdown(
                subject=request.subject,
                cumulative_plan=cumulative_plan,
            )

            cumulative_student_test_path = (
                self._unique_output_path(
                    output_dirs["artifact_dir"],
                    f"{artifact_subject_stem}_student_{version_label}.md",
                )
            )
            write_text(cumulative_student_test_path, cumulative_render["markdown"])
            if "docx" in export_formats:
                cumulative_student_docx_path = self._unique_output_path(
                    output_dirs["artifact_dir"],
                    f"{artifact_subject_stem}_student_{version_label}.docx",
                )
                export_markdown_to_docx(
                    cumulative_render["markdown"],
                    cumulative_student_docx_path,
                )
            if "pdf" in export_formats:
                cumulative_student_pdf_path = self._unique_output_path(
                    output_dirs["pdf_dir"],
                    f"{subject_slug}_cumulative_student_{version_label}.pdf",
                )
                export_markdown_to_pdf(
                    cumulative_render["markdown"],
                    cumulative_student_pdf_path,
                )

            if include_teacher:
                cumulative_teacher_render = render_cumulative_teacher_markdown(
                    subject=request.subject,
                    cumulative_plan=cumulative_plan,
                    rendered_student=cumulative_render,
                )
                cumulative_teacher_test_path = (
                    self._unique_output_path(
                        output_dirs["artifact_dir"],
                        f"{artifact_subject_stem}_teacher_{version_label}.md",
                    )
                )
                write_text(cumulative_teacher_test_path, cumulative_teacher_render["markdown"])
                if "docx" in export_formats:
                    cumulative_teacher_docx_path = self._unique_output_path(
                        output_dirs["artifact_dir"],
                        f"{artifact_subject_stem}_teacher_{version_label}.docx",
                    )
                    export_markdown_to_docx(
                        cumulative_teacher_render["markdown"],
                        cumulative_teacher_docx_path,
                    )
                if "pdf" in export_formats:
                    cumulative_teacher_pdf_path = self._unique_output_path(
                        output_dirs["pdf_dir"],
                        f"{subject_slug}_cumulative_teacher_{version_label}.pdf",
                    )
                    export_markdown_to_pdf(
                        cumulative_teacher_render["markdown"],
                        cumulative_teacher_pdf_path,
                    )

            cumulative_memory_record = build_cumulative_memory_record(
                subject=request.subject,
                version_label=version_label,
                units=cumulative_plan.get("units", []) if cumulative_plan else [],
                top_topics=cumulative_plan.get("top_topics", []) if cumulative_plan else [],
                student_test_path=str(cumulative_student_test_path) if cumulative_student_test_path else None,
                teacher_test_path=str(cumulative_teacher_test_path) if cumulative_teacher_test_path else None,
            )
            memory_record_path = append_memory_record(
                memory_dir=self.settings.memory_dir,
                subject_slug=subject_slug,
                record=cumulative_memory_record,
            )
            LOGGER.info(
                "Generated cumulative test subject=%s blueprints=%s student=%s teacher=%s",
                request.subject,
                len(loaded_blueprints),
                cumulative_student_test_path,
                cumulative_teacher_test_path,
            )

            if save_debug:
                cumulative_plan_path = (
                    output_dirs["artifact_dir"]
                    / f"{artifact_subject_stem}_plan_{version_label}.json"
                )
                cumulative_validation_path = (
                    output_dirs["artifact_dir"]
                    / f"{artifact_subject_stem}_validation_{version_label}.json"
                )
                cumulative_render_path = (
                    output_dirs["artifact_dir"]
                    / f"{artifact_subject_stem}_render_{version_label}.json"
                )

                write_json(cumulative_plan_path, cumulative_plan)
                write_json(
                    cumulative_validation_path,
                    {
                        "blueprint_results": blueprint_results,
                        "valid_blueprint_count": len(loaded_blueprints),
                    },
                )
                write_json(
                    cumulative_render_path,
                    {
                        "question_count": cumulative_render["question_count"],
                        "question_records": cumulative_render["question_records"],
                    },
                )

                if cumulative_teacher_render:
                    cumulative_teacher_debug_path = (
                        output_dirs["artifact_dir"]
                        / f"{artifact_subject_stem}_teacher_render_{version_label}.json"
                    )
                    write_json(
                        cumulative_teacher_debug_path,
                        {
                            "question_count": cumulative_teacher_render["question_count"],
                            "answer_key_records": cumulative_teacher_render["answer_key_records"],
                        },
                    )

        overall_valid = len(loaded_blueprints) == len(resolved_paths)

        return {
            "status": "ok" if overall_valid else "partial",
            "skill": request.skill,
            "subject": request.subject,
            "subject_slug": subject_slug,
            "output_generated_dir": str(subject_dirs["generated_path"]),
            "artifact_dir": str(output_dirs["artifact_dir"]),
            "export_formats": export_formats,
            "blueprint_resolution": resolved,
            "blueprint_results": blueprint_results,
            "cumulative_summary": cumulative_summary,
            "cumulative_plan": cumulative_plan,
            "unit_weights": unit_weights,
            "question_count": cumulative_render["question_count"] if cumulative_render else 0,
            "cumulative_student_test_path": (
                str(cumulative_student_test_path) if cumulative_student_test_path else None
            ),
            "cumulative_teacher_test_path": (
                str(cumulative_teacher_test_path) if cumulative_teacher_test_path else None
            ),
            "cumulative_student_docx_path": (
                str(cumulative_student_docx_path) if cumulative_student_docx_path else None
            ),
            "cumulative_teacher_docx_path": (
                str(cumulative_teacher_docx_path) if cumulative_teacher_docx_path else None
            ),
            "cumulative_student_pdf_path": (
                str(cumulative_student_pdf_path) if cumulative_student_pdf_path else None
            ),
            "cumulative_teacher_pdf_path": (
                str(cumulative_teacher_pdf_path) if cumulative_teacher_pdf_path else None
            ),
            "cumulative_student_test_preview": (
                cumulative_render["markdown"][:800] if cumulative_render else None
            ),
            "cumulative_plan_path": str(cumulative_plan_path) if cumulative_plan_path else None,
            "cumulative_validation_path": (
                str(cumulative_validation_path) if cumulative_validation_path else None
            ),
            "cumulative_render_path": str(cumulative_render_path) if cumulative_render_path else None,
            "cumulative_teacher_debug_path": (
                str(cumulative_teacher_debug_path) if cumulative_teacher_debug_path else None
            ),
            "memory_record_path": str(memory_record_path) if memory_record_path else None,
            "next_implementation_stage": [
                "improve merge weighting and synthesis logic",
                "avoid repetition across merged sections",
                "add cumulative and retrieval test coverage",
            ],
        }
