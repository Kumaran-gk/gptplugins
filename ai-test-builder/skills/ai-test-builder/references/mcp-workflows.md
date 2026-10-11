# MCP workflows and file handling

Use this reference only when the AI Test Builder route needs a tool call or a
file-format decision. The plugin's MCP server name is `ai_test_builder`.

## Inputs

- `subject` is required for every tool and determines the subject output folder.
- Source tests and optional unit-content files: `.pdf`, `.docx`, `.png`,
  `.jpg`, `.jpeg`, `.tif`, `.tiff`, `.bmp`, `.webp`. The analyzer handles one
  source file as one blueprint. Combine images into a PDF if multiple pages
  should produce one blueprint.
- PDF `pdf_mode`: `auto` (default), `text`, or `ocr`. `auto` OCRs pages with
  weak embedded text. Scanned PDFs and images require Tesseract. Options
  include `tesseract_cmd` and `ocr_lang` (default `eng`). DOCX extraction reads
  paragraph and table text, not embedded images.
- Existing blueprint files must be JSON valid against
  `schemas/blueprint_schema.json`. Do not pass plain text or PDF as a blueprint.
- Use readable absolute paths when the source is outside the plugin directory.
  Input files under `data/input/<subject>/` are ignored by Git; newly created
  blueprints and generated outputs are not.

## Tool routing

| Goal | Tool and important arguments |
| --- | --- |
| Save questions written from user preferences | `save_custom_test(subject, title, student_markdown, teacher_markdown?, version?, export_formats?)`. Supported formats: `md`, `docx`, `pdf`. |
| Analyze only | `analyze_test(subject, input_files, options?)`. Include `pdf_mode`, `ocr_lang`, or `tesseract_cmd` when needed. Inspect each `blueprint_valid` flag and uncertainty. |
| Full source-to-paper run | `build_test_pack(subject, input_files?, blueprint_files?, unit_content_files?, options?)`. At least one source test or blueprint is required. Useful options: `versions`, `include_teacher`, `export_formats`, `pdf_mode`, `build_cumulative`, `cumulative_version`, `unit_weights`. Defaults are two versions, teacher copies, and Markdown. |
| New paper from blueprint | `generate_test(subject, blueprint_files?, unit_content_files?, options?)`. Useful options: `version`, `include_teacher`, `export_formats`, `blueprint_query`, `max_blueprints`. |
| Cumulative paper | `build_cumulative_test(subject, blueprint_files?, options?)`. Supply at least two blueprints. Useful options: `version`, `unit_weights`, `include_teacher`, `export_formats`. |

Options are a dictionary; `versions` and `export_formats` accept comma-separated
values or lists where supported. `unit_weights` uses `Unit Name:weight` entries,
for example `Motion:40,Forces:60`. Match names recorded in the blueprints.

## Outputs and quality checks

- Valid blueprints: `data/blueprints/<subject>/`; concise retrieval records:
  `data/memory/`.
- Generated student and teacher files: `data/generated_tests/<subject>/`.
  Test packs also create an artifacts folder and a JSON run manifest. PDF files
  may be saved directly in the subject's generated-tests folder.
- Paths are relative to the plugin copy executing the server. Installed plugins
  run from Codex's plugin cache; keep an external copy of wanted outputs before
  removing or updating the plugin.
- The blueprint-backed generator defaults to a template backend. Use GPT-backed
  generation only when explicitly selected and an `OPENAI_API_KEY` is
  configured. Preference-based Codex-authored questions do not need that key.
- Before reporting success, confirm schema validation, requested version and
  format counts, answer keys, and all returned file paths. Review OCR and
  generated mathematics or science content before classroom use.
