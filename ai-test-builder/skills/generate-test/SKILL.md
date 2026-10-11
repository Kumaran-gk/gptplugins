---
name: generate-test
description: Generate a new practice test from an existing blueprint JSON while preserving structure, topic weighting, difficulty intent, and style constraints without copying source questions verbatim. Use this when a reusable blueprint already exists and the goal is to create a fresh test.
---

# Generate Test Skill

## Purpose

Use this skill to generate a fresh test from an existing blueprint JSON.

This skill is for test creation from a blueprint, not for analyzing source papers from scratch.

Main outcomes:
- read a schema-valid blueprint
- preserve the intended structure and style
- generate fresh questions aligned to the blueprint
- keep subject and unit alignment
- produce a reusable test output file
- optionally produce an answer key or teacher version

## When to use

Use this skill when the user wants to:
- generate a practice test from an existing blueprint
- create a new version of a known test style
- create alternate versions such as A/B/C
- preserve question structure but vary content
- generate student and teacher versions
- produce print-ready tests from stored blueprints

## When not to use

Do not use this skill when the user wants to:
- analyze old source tests and extract patterns
- merge several unit blueprints into a cumulative test
- validate or repair a raw blueprint from scratch without generation

In those cases, prefer:
- `analyze-test`
- `build-cumulative-test`
- normal repo workflow outside this skill

## Inputs

Expected runtime inputs:
- `subject`: dynamic subject name provided at runtime
- one blueprint JSON, usually from `data/blueprints/<subject>/`
- optional generation settings such as:
  - version label
  - target difficulty shift
  - number of questions
  - output format
  - student vs teacher version
  - include answer key
  - include solutions
  - print-friendly formatting preference

Optional user instructions may include:
- make it trickier
- make it shorter
- keep same pattern
- add more application questions
- reduce multiple choice
- create full-solution version
- match a specific teacher style

## Required inputs before generation

Before generating, confirm the blueprint:
- exists
- is valid JSON
- matches `schemas/blueprint_schema.json`
- contains enough information to support generation

If the blueprint is incomplete, do not silently invent major structure.
Instead:
- generate only what is reliably supported
- state what was assumed
- or ask for re-analysis / blueprint repair

## Required outputs

This skill must produce:

1. A fresh generated test aligned to the blueprint
2. Optionally:
   - answer key
   - worked solutions
   - teacher version
   - student version
3. A short generation summary that lists:
   - blueprint used
   - preserved constraints
   - intentional variations
   - any assumptions made

Write generated tests to:
- `data/generated_tests/<subject>/`

Do not overwrite existing files unless explicitly asked.
Prefer versioned filenames.

## Core generation rules

Always follow these rules:

1. Preserve the structure unless the user explicitly asks to change it
2. Preserve topic weighting unless the user explicitly asks to rebalance it
3. Preserve the intended difficulty signature
4. Preserve response-type expectations
5. Generate fresh questions rather than copying the original source wording
6. Keep subject alignment and unit alignment
7. Keep the style consistent with the blueprint
8. Respect blueprint generation constraints
9. Keep outputs organized and reusable

## Non-copying rule

Do not copy source questions verbatim unless the user explicitly asks for cloning or close imitation.

Default behavior:
- preserve pattern
- preserve style
- preserve difficulty intent
- change surface wording, values, contexts, and setups appropriately

Acceptable variation examples:
- new numeric values
- new real-world contexts
- new diagram contexts
- new distractors of the same type
- new multi-step combinations consistent with blueprint rules

## What to preserve from the blueprint

Always try to preserve:

### Structure
- number of sections
- section order
- question type by section
- mark allocation
- balance of objective vs constructed response
- progression pattern

### Topic design
- topic weighting
- subtopic balance
- representation types
- conceptual vs computational split
- proof / explanation / diagram requirements

### Difficulty
- easy / medium / hard balance
- progression from accessible to harder items
- cognitive demand style
- trap intensity

### Style
- wording tone
- command verbs
- response format expectations
- answer style expectations
- diagram / graph / derivation expectations

### Trap patterns
- same families of distractors
- same misconception style
- same unit / sign / notation pitfalls
- same multi-step setup traps

## Allowed variation

The generator may vary:
- contexts
- numeric values
- ordering within a section if allowed by the blueprint
- names, scenarios, examples, diagrams, and datasets
- question wording while preserving the same intent
- exact distractor text while preserving distractor type

The generator should not vary:
- core topic coverage
- overall blueprint identity
- skill-level intent
- required answer format
- key structure constraints unless explicitly instructed

## Subject handling

Subject is always dynamic at runtime.

Use the blueprint common fields for shared behavior.
Use `subject_extensions` to shape subject-specific generation.

Examples:
- Math: notation consistency, exact value handling, proof style, graphing expectations
- Physics: units, constants, circuit/force/energy style calculations, diagram expectations
- Chemistry: equations, balancing, mole relationships, lab/data interpretation
- Biology: labeling, terminology precision, process explanations, interpretation of visuals/data

Do not inject unsupported subject assumptions that are not grounded in the blueprint or user instruction.

## Recommended workflow

### Step A - Load blueprint
Read the blueprint JSON and validate it.

### Step B - Read constraints
Extract:
- structure
- topic distribution
- difficulty profile
- question style
- trap patterns
- generation rules
- subject extensions

### Step C - Build generation plan
Create a section-by-section plan:
- how many questions
- which topics
- target difficulty
- intended trap types
- required answer formats

### Step D - Generate draft items
Generate fresh questions aligned to the section plan.

### Step E - Check alignment
Verify:
- no missing topics
- no duplicated questions
- difficulty is balanced
- structure matches the blueprint
- subject language is correct
- no verbatim copying

### Step F - Produce outputs
Write:
- student test
- optional teacher version
- optional answer key / solutions
- generation summary

## Output format expectations

Possible output types may include:
- markdown
- plain text
- JSON sidecar metadata
- later DOCX / PDF formatting through downstream workflows

At minimum, the output should be cleanly structured and easy to transform into print-ready documents.

A good generated test should include:
- title
- subject and unit if known
- clear section headings
- instructions
- numbered questions
- marks if applicable
- spacing that supports later formatting

## Answer key / teacher output

If answer key or teacher version is requested, include:
- correct answers
- worked steps where appropriate
- marking guidance if supported by blueprint/user request
- brief rationale for tricky distractors where useful

Keep teacher content separate from the student-facing version when possible.

## File naming convention

Preferred output patterns:

Student test:
`<subject>_<unit-or-topic>_test_v1.md`

Teacher version:
`<subject>_<unit-or-topic>_teacher_v1.md`

Answer key:
`<subject>_<unit-or-topic>_answer-key_v1.md`

If generating versioned alternates:
`<subject>_<unit-or-topic>_test_verA.md`
`<subject>_<unit-or-topic>_test_verB.md`

Use lowercase and filename-safe names where practical.

## Memory MCP guidance

If memory MCP is available, store only concise reusable generation notes, such as:
- blueprint used
- version created
- variation style used
- difficulty adjustment notes
- teacher style matching notes

Do not store full generated test text in memory unless explicitly requested.

## Filesystem MCP guidance

If filesystem MCP is available:
- read blueprint files from `data/blueprints/<subject>/`
- write generated test outputs to `data/generated_tests/<subject>/`
- optionally write sidecar metadata or summary files next to the output

Do not overwrite existing files unless explicitly instructed.

## Quality bar

A good generated test should be:
- fresh
- aligned to blueprint intent
- structurally consistent
- subject-accurate
- varied but not random
- reusable for classroom practice
- easy to format later into DOCX/PDF

## Failure handling

If the blueprint is too weak:
- identify the missing fields
- generate only the reliable portions
- clearly state assumptions
- recommend re-running `analyze-test` if needed

If generation drifts from the blueprint:
- correct the drift before treating the output as complete

If the requested customizations conflict with the blueprint:
- prioritize explicit user instruction
- state what changed from the original blueprint

## Definition of done

This skill is complete only when:
- a valid blueprint has been loaded
- a fresh test has been generated from it
- structure, topic coverage, and difficulty intent match the blueprint
- the output is saved in the correct subject folder
- any answer key / teacher version requested has also been produced
- a short generation summary has been produced