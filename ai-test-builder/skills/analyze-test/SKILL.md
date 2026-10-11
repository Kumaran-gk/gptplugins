---
name: analyze-test
description: Analyze an existing test paper (PDF, DOCX, or normalized text) and produce a structured blueprint JSON capturing topics, structure, difficulty, traps, and generation rules. Use this when the task is to study old tests and extract reusable assessment patterns. Do not use this skill for generating a new test from scratch.
---

# Analyze Test Skill

## Purpose

Use this skill to read one or more source test papers and convert them into a reusable blueprint JSON.

This skill is for pattern extraction, not direct test writing.

Main outcomes:
- identify the structure of the source test
- extract reusable assessment patterns
- separate observed evidence from inferred conclusions
- produce schema-aligned blueprint JSON
- save a retrieval-friendly summary for later reuse

## When to use

Use this skill when the user wants to:
- analyze an old test
- extract topics, structure, difficulty, or traps
- build a reusable test blueprint
- create subject-aware pattern memory from source papers
- prepare future generation of similar tests
- prepare future cumulative assessments from unit-level blueprints

## When not to use

Do not use this skill when the user wants to:
- directly generate a fresh practice test without analysis
- merge multiple existing blueprints into one cumulative test
- only reformat a source file
- only summarize raw file contents without blueprint creation

In those cases, prefer:
- `generate-test`
- `build-cumulative-test`
- normal repo workflow outside this skill

## Inputs

Expected runtime inputs:
- `subject`: dynamic subject name provided at runtime
- one or more source files, usually from `data/input/<subject>/`
- optional metadata such as:
  - grade level
  - course code
  - curriculum
  - unit name
  - teacher style notes

Supported source formats:
- PDF
- DOCX
- normalized text derived from those files

## Required outputs

This skill must produce:

1. A structured blueprint JSON that validates against:
   - `schemas/blueprint_schema.json`

2. A concise analysis summary that clearly separates:
   - observed patterns
   - inferred patterns
   - uncertainty / low-confidence areas

3. A retrieval-friendly memory summary suitable for storing in memory MCP

Blueprint output location:
- `data/blueprints/<subject>/`

Prefer versioned or timestamped filenames.
Do not overwrite existing blueprint files unless explicitly asked.

## Analysis principles

Always do these in order:

1. Extract and normalize the source content
2. Identify explicit structure before deeper interpretation
3. Detect sections, question types, mark patterns, and ordering
4. Map topics and subtopics
5. Estimate difficulty distribution
6. Detect common trap patterns and distractor styles
7. Infer generation rules from repeated evidence
8. Build blueprint JSON
9. validate the blueprint against the schema
10. write the blueprint and summary outputs

## Evidence rules

Separate evidence into two categories:

### Observed patterns
Only include things directly supported by the source test, such as:
- number of sections
- section titles
- question counts
- mark values
- repeated verbs
- explicit diagram usage
- obvious ordering patterns
- visible topic coverage

### Inferred patterns
Only include conclusions that are reasonably derived from the evidence, such as:
- likely teacher preference for multi-step reasoning
- likely preference for conceptual traps before computation
- likely difficulty progression across sections
- likely answer-style expectations

Do not present inferences as certain facts.
Mark uncertainty explicitly.

## What to extract

Always try to extract as many of these as the source allows:

### Metadata
- subject
- title
- grade level
- course code
- curriculum
- unit / chapter
- source file names
- pages used

### Structure
- test type
- duration if stated
- total marks if stated
- section order
- section purpose
- question types by section
- number of questions
- marks by section
- ordering rules

### Topic design
- main topics
- subtopics
- topic weighting
- recurring concept clusters
- representation types used
- whether the test mixes conceptual and computational work

### Difficulty
- easy / medium / hard mix
- progression across the test
- cognitive skill distribution
- whether later questions combine skills
- whether distractors increase in subtlety over time

### Style
- stem styles
- command verbs
- wording tone
- response format expectations
- diagram expectations
- proof / derivation / explanation expectations
- calculation style expectations

### Trap patterns
- common distractor logic
- sign / unit / conversion traps
- notation traps
- multi-step setup traps
- ambiguous wording patterns
- common conceptual misconceptions exploited by questions

### Generation rules
- what structure should be preserved
- what must vary in future generated tests
- whether source questions must not be copied
- what difficulty signature should remain stable
- what topic weighting should remain stable

## Subject handling

Subject is always dynamic at runtime.

Use the shared schema for common fields.
Use `subject_extensions` for subject-specific findings.

Examples:
- Math: proof expectations, exact values, notation rules, graph types
- Physics: units, constants, diagram types, lab skills, calculation modes
- Chemistry: equations, balancing style, units, lab skills, representation forms
- Biology: diagram labeling, vocabulary precision, process explanations, data interpretation

Do not hardcode subject-specific assumptions unless supported by the source or runtime input.

## Recommended workflow

### Step A - Ingest
Read the source files.
Extract text from PDF or DOCX.
Normalize spacing, numbering, and section boundaries.

### Step B - Structural pass
Identify:
- title and metadata
- section breaks
- question numbering
- mark allocation
- instructions
- recurring layout patterns

### Step C - Topic pass
Identify the assessed topics and subtopics.
Estimate relative topic weight based on:
- count
- marks
- space used
- recurrence

### Step D - Difficulty pass
Estimate difficulty using signals such as:
- number of steps
- abstraction level
- amount of setup needed
- distractor subtlety
- combination of multiple concepts
- required interpretation versus direct recall

### Step E - Trap pass
Identify recurring pitfalls intentionally embedded in the source test.

### Step F - Blueprint build
Construct a schema-valid JSON blueprint.

### Step G - Memory summary
Create a concise summary suitable for memory storage, including:
- subject
- unit
- teacher/test style signature
- structure summary
- difficulty signature
- trap summary
- retrieval tags

## Output format expectations

### Blueprint JSON
The blueprint must:
- be valid JSON
- be deterministic in structure
- follow `schemas/blueprint_schema.json`
- include both shared fields and subject extensions where appropriate

### Summary notes
Alongside the JSON, produce a short human-readable summary with:
- source files analyzed
- high-confidence patterns
- lower-confidence inferences
- missing or ambiguous areas
- suggested filename for saved blueprint

## File naming convention

Preferred blueprint filename pattern:

`<subject>_<unit-or-topic>_blueprint_v1.json`

If the unit name is unknown, use a descriptive fallback:

`<subject>_test-pattern_blueprint_v1.json`

Use lowercase and hyphen/underscore-safe names where practical.

## Memory MCP guidance

If memory MCP is available, store only concise reusable knowledge, such as:
- structure signature
- topic weighting summary
- difficulty signature
- trap pattern summary
- teacher style signature
- merge tags for future cumulative assessments

Do not store:
- raw extraction dumps
- long unstructured text blocks
- copied question banks unless explicitly requested

## Filesystem MCP guidance

If filesystem MCP is available:
- read source files from `data/input/<subject>/`
- write blueprint JSON to `data/blueprints/<subject>/`
- optionally write a sidecar summary markdown or text file next to the blueprint

Do not overwrite existing files unless explicitly instructed.

## Quality bar

A good analysis should be:
- evidence-based
- reusable
- subject-aware
- schema-valid
- concise in memory form
- detailed in blueprint form

## Failure handling

If extraction is incomplete or noisy:
- still extract what is reliable
- mark confidence appropriately
- list missing or uncertain parts
- avoid inventing structure not supported by evidence

If schema validation fails:
- fix the blueprint before treating the analysis as complete

If the source is too weak for a full blueprint:
- return a partial analysis summary
- clearly state why a full blueprint could not be built

## Definition of done

This skill is complete only when:
- the source test has been analyzed
- structure, topics, difficulty, and traps have been extracted as far as possible
- observed versus inferred patterns are clearly separated
- a schema-valid blueprint JSON has been produced
- the blueprint is ready for later use by `generate-test`
- a concise memory-ready summary has been produced