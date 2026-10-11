# AI Test Builder - Repository Instructions

## Purpose

This repository builds an AI-powered Test Builder system using Codex + MCP.

Main goals:
- Read old test papers from PDF and DOCX
- Analyze them for reusable assessment patterns
- Store those patterns as structured blueprint JSON
- Generate similar practice tests
- Support multiple subjects dynamically at runtime
- Later combine unit blueprints into cumulative tests

## Core workflow

Use one main agent workflow for this repository:
1. Ingest source test files
2. Normalize extracted content
3. Analyze pattern, structure, difficulty, and traps
4. Build a validated blueprint JSON
5. Store and index the blueprint
6. Generate a new test from the blueprint
7. Later support cumulative test generation from multiple blueprints

## Skill entry point

Use the packaged `ai-test-builder` skill under `skills/ai-test-builder/` as the single user-facing workflow. It routes preference-based questions, source analysis, blueprint generation, and cumulative tests through the appropriate MCP tools. Keep stage-specific detail in the skill's references rather than adding more top-level skills.

## Runtime behavior

Subject is always dynamic at runtime.
Do not hardcode a single subject.

Supported examples include:
- Chemistry
- Physics
- Math
- Biology

Always use:
- a generalized blueprint schema for shared structure
- subject-specific extensions for subject-only fields

## Blueprint rules

Blueprints must capture reusable test-design patterns, not just raw question text.

Always try to extract:
- subject
- grade / course / level if available
- unit or chapter
- topic distribution
- section structure
- question types
- mark distribution
- difficulty profile
- common traps / distractor styles
- wording style
- diagram / calculation / proof expectations
- answer style expectations
- source metadata

Output blueprints as JSON and validate them against:
- `schemas/blueprint_schema.json`

Store generated blueprint files under:
- `data/blueprints/<subject>/`

## File handling

Read source files from:
- `data/input/<subject>/`

Write generated tests to:
- `data/generated_tests/<subject>/`

Do not overwrite existing outputs unless explicitly asked.
Prefer creating timestamped or versioned output files.

## MCP usage

Use MCP tools for:
- filesystem: read source tests, write blueprints, write generated tests
- memory: store reusable blueprint summaries, pattern notes, and retrieval-friendly metadata

When storing to memory, save concise reusable knowledge such as:
- recurring structure patterns
- teacher style preferences
- difficulty signatures
- common distractor patterns
- unit-level blueprint summaries

Do not store noisy raw extraction dumps in memory unless explicitly needed.

## Implementation expectations

Keep implementation modular.

Use:
- `src/ingestion/` for file reading and normalization
- `src/analysis/` for pattern extraction and analysis
- `src/blueprint/` for schema building and validation
- `src/generation/` for test creation
- `src/memory/` for memory indexing and retrieval
- `src/agent/` for main workflow orchestration

## Coding rules

Prefer clear Python modules over large monolithic files.
Prefer pure functions for analysis and transformation steps where practical.
Keep JSON output deterministic and schema-valid.
Add logging around file ingestion, blueprint creation, validation, and generation.
Fail with clear error messages when input extraction is incomplete or invalid.

## Agent behavior

When analyzing a test:
- identify structure before generating conclusions
- separate observed facts from inferred patterns
- mark uncertainty explicitly
- preserve evidence snippets where useful

When generating a test:
- follow blueprint constraints closely
- preserve structure and difficulty intent
- do not copy source questions verbatim unless explicitly requested
- create fresh questions consistent with the blueprint
- maintain subject alignment and unit alignment

When building cumulative tests later:
- merge multiple blueprints carefully
- preserve topic weighting intentionally
- avoid overrepresenting one unit unless asked

## Validation rule

Any produced blueprint JSON must be checked against the repository schema before it is treated as complete.

## Output preference

Prefer outputs that are:
- reusable
- structured
- easy to diff
- easy to extend to new subjects
- easy to combine later into cumulative test workflows
