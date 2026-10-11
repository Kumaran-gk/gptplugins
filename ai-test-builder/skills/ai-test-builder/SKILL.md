---
name: ai-test-builder
description: Create a complete practice question paper from a user's preferences, old tests, or saved blueprints. Gather the needed inputs, analyze and validate sources when appropriate, generate fresh student and teacher outputs, and report the files created.
---

# AI Test Builder

Use this as the single entry point for building a paper. The user may start with
a topic, one or more old tests, or existing blueprint JSON. Choose the route
that fits the supplied input and carry it through to the requested result.

## Intake

- Identify the subject and the goal. Ask only for missing details required for
  that route: a topic for a preference-based paper, a readable source path for
  source analysis, or valid blueprint paths for blueprint generation.
- Accept optional grade/course, unit, curriculum, topics to include or exclude,
  question count and types, marks, difficulty, version count, answer style,
  student/teacher copies, and `md`, `docx`, or `pdf` exports. Use reasonable
  defaults for omitted choices and state important assumptions.
- Use absolute file paths when available. Source-test and optional unit-content
  files may be PDF, DOCX, or supported images. OCR requires Tesseract for scans;
  see [MCP workflows](references/mcp-workflows.md) for file types and options.
- Treat a direct request for a blueprint, a single new version, or a cumulative
  paper as that specific goal. Do not generate unrelated artifacts.

## Route the work

1. **Preferences only:** Write original, subject-aligned questions in Codex.
   Check the requested count, types, marks, difficulty, answers, calculations,
   and units. Return the paper in chat. When files are requested, call
   `ai_test_builder.save_custom_test` with complete student Markdown and an
   optional separate teacher Markdown, then report returned paths. No source
   paper, blueprint, or separate API key is required.
2. **Old source test(s):** Use `ai_test_builder.build_test_pack` for the full
   route: ingest, normalize, analyze, validate blueprint JSON, generate the
   requested fresh version(s), export files, and return its manifest. Pass
   optional unit-content files separately from test-pattern files. If the user
   requests analysis only, call `ai_test_builder.analyze_test` and stop after
   showing the blueprint path and confidence/uncertainty summary.
3. **Existing blueprint(s):** Validate each blueprint against
   `schemas/blueprint_schema.json`. For a new unit paper, call
   `ai_test_builder.generate_test`. For a cumulative paper, use at least two
   blueprints with `ai_test_builder.build_cumulative_test` and pass requested
   unit weights. `build_test_pack` can also create multiple versions from
   existing blueprint files in one run.

Use [MCP workflows](references/mcp-workflows.md) for the exact tool inputs,
file formats, option names, and output layout when calling a tool.

## Finish the paper

- Keep structure, topic weighting, difficulty intent, and answer style from a
  blueprint unless the user requests a change. Make questions fresh; do not
  copy source questions verbatim unless explicitly asked.
- Keep observed source facts separate from inferred patterns. Mark weak OCR,
  missing diagrams, and uncertain topic or mark estimates. Do not invent
  unreadable content.
- Check the tool result and all requested artifacts. A `partial` result or
  missing export is not complete: explain the issue and repair it when possible.
- Give the user the blueprint path when one was made, the student and teacher
  paper paths, requested formats, version labels, and the test-pack manifest
  path when applicable. Mention assumptions that changed the paper.
