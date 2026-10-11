---
name: build-test-pack
description: Run the end-to-end pipeline from one or more source tests to blueprint creation, multi-version generation, optional cumulative generation, and packaged outputs such as markdown, DOCX, and PDF. Use this when the user wants one entrypoint instead of separate analyze/generate/build-cumulative steps.
---

# Build Test Pack Skill

This is the main test-creator skill for the repository.
Use it as the user-facing orchestrator and treat the following repo skills as specialized sub-skills that inform the workflow:
- `analyze-test`
- `generate-test`
- `build-cumulative-test`

## Purpose

Use this skill when the user wants a single workflow that:
- accepts one or more source test files
- analyzes them into blueprint JSON
- generates multiple fresh versions
- optionally builds a cumulative paper across units
- writes packaged outputs in one run

This skill is the single-entry orchestration layer for the repository.

## When to use

Use this skill when the user wants to:
- give one source PDF and get similar test versions back
- avoid running multiple separate commands
- create student and teacher versions in one run
- produce markdown, DOCX, or PDF outputs in one run
- build a final cumulative paper after unit-level inputs have been processed

## When not to use

Do not use this skill when the task is only one narrow stage, such as:
- analyzing a source test only
- generating from one already-chosen blueprint only
- building a cumulative test only

In those cases, prefer:
- `analyze-test`
- `generate-test`
- `build-cumulative-test`

## Inputs

Expected runtime inputs:
- `subject`
- one or more source files, usually from `data/input/<subject>/`
- or one or more blueprint files from `data/blueprints/<subject>/`
- runtime options such as:
  - `versions=verA,verB,verC`
  - `include_teacher=true`
  - `export_formats=md,docx,pdf`
  - `pdf_mode=text|ocr|auto`
  - `build_cumulative=true`
  - `cumulative_version=final-review`
  - `unit_weights=Unit 1:20,Unit 2:30,Unit 3:50`

## Required outputs

This skill should produce a consolidated run result containing:
- blueprint paths created or used
- generated student outputs
- generated teacher outputs
- optional cumulative outputs
- one manifest JSON summarizing the whole run

Generated files should be written under:
- `data/blueprints/<subject>/`
- `data/generated_tests/<subject>/`

## Workflow

1. If source tests are provided, run the analyze phase first.
2. Collect valid blueprint paths from analysis or explicit input.
3. For each requested version, generate student and optional teacher outputs.
4. If cumulative generation is requested and at least two blueprints exist, build the cumulative paper.
5. Package requested export formats.
6. Save a manifest describing the entire run.

When operating as the main test creator, use these internal workflow responsibilities:
- `analyze-test` for structure/style extraction from teacher source tests
- `generate-test` for versioned fresh paper generation
- `build-cumulative-test` for final weighted or merged assessments

The user should not need to invoke those sub-skills directly when this main skill is appropriate.

## MCP / Agent Role

When this repo is exposed through MCP, prefer `build-test-pack` as the main tool/agent entrypoint.

Recommended behavior:
- ask for the source test file(s)
- optionally ask for unit-content file(s)
- run the full pipeline
- return a concise manifest of created outputs
- keep lower-level tools available for debugging, repair, or advanced workflows

## Export behavior

Supported export formats:
- `md`
- `docx`
- `pdf`

Use the manifest to surface the final file paths to the user.

## Quality bar

A good build-test-pack run should:
- require one command only
- keep outputs grouped by subject
- preserve version labels clearly
- avoid hiding failures in nested steps
- expose exactly which files were created

## Definition of done

This skill is complete only when:
- the end-to-end pipeline has run from the supplied entrypoint
- all requested versions were generated
- any requested cumulative paper was produced
- requested export formats were written
- the manifest file is present and usable
