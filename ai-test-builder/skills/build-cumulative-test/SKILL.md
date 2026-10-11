---
name: build-cumulative-test
description: Build a cumulative test from multiple existing blueprint JSON files while preserving intentional topic weighting, unit balance, structure, and difficulty progression. Use this when several unit-level blueprints already exist and the goal is to combine them into one coherent assessment.
---

# Build Cumulative Test Skill

## Purpose

Use this skill to build a cumulative test from multiple blueprint JSON files.

This skill is for combining existing analyzed unit-level patterns into one coherent cumulative assessment.

Main outcomes:
- load multiple schema-valid blueprints
- merge structure and topic coverage intentionally
- preserve fair balance across units
- avoid accidental overrepresentation of one unit
- produce a fresh cumulative test
- optionally produce answer key, solutions, or teacher version

## When to use

Use this skill when the user wants to:
- combine multiple unit blueprints into one test
- create a midterm, final review, or cumulative practice test
- merge several analyzed teacher styles into one controlled assessment
- create a balanced assessment across units or chapters
- preserve blueprint evidence while expanding scope

## When not to use

Do not use this skill when the user wants to:
- analyze raw source test papers
- generate a test from only one blueprint
- only summarize or compare blueprints without building a test

In those cases, prefer:
- `analyze-test`
- `generate-test`
- normal repo workflow outside this skill

## Inputs

Expected runtime inputs:
- `subject`: dynamic subject name provided at runtime
- two or more blueprint JSON files from `data/blueprints/<subject>/`
- optional cumulative settings such as:
  - target total marks
  - target duration
  - unit weighting
  - section format
  - question count
  - difficulty shift
  - review-heavy vs exam-style emphasis
  - include answer key
  - include worked solutions
  - teacher vs student version

Optional user instructions may include:
- give more weight to recent units
- keep all units equally represented
- make it look like a real exam
- make it mostly multiple choice
- include mixed full-solution problems
- use only selected units
- keep the same teacher style throughout

## Required inputs before merging

Before building a cumulative test, confirm that:
- each blueprint exists
- each blueprint is valid JSON
- each blueprint matches `schemas/blueprint_schema.json`
- the selected blueprints belong to the same subject unless the user explicitly wants cross-subject behavior
- the selected blueprints contain enough detail to merge responsibly

If blueprint quality is uneven:
- use the strongest blueprints as anchors
- reduce confidence for weak areas
- state assumptions clearly
- avoid inventing unsupported unit structure

## Required outputs

This skill must produce:

1. A cumulative test generated from multiple blueprints
2. Optionally:
   - answer key
   - worked solutions
   - teacher version
   - student version
3. A short merge summary that lists:
   - blueprints used
   - unit weighting decisions
   - preserved structure patterns
   - conflicts resolved
   - assumptions made

Write cumulative outputs to:
- `data/generated_tests/<subject>/`

Do not overwrite existing files unless explicitly asked.
Prefer versioned filenames.

## Core merge rules

Always follow these rules:

1. Merge intentionally, not by simple concatenation
2. Preserve unit balance unless the user explicitly asks otherwise
3. Preserve the overall subject style and assessment identity
4. Avoid overloading the cumulative test with one blueprint's structure
5. Respect explicit user weighting instructions
6. Preserve difficulty progression across the whole test
7. Generate fresh questions rather than reusing prior source wording
8. Keep the final test coherent as one assessment, not as separate stitched fragments

## Merge priorities

When multiple blueprints differ, resolve in this order:

1. Explicit user instruction
2. Subject consistency
3. Required structural feasibility
4. Fair topic coverage
5. Difficulty balance
6. Dominant repeated patterns across blueprints
7. Unit-specific style preferences

If two blueprints conflict and no user instruction resolves it:
- choose the option that best supports coherence and fairness
- record the choice in the merge summary

## What to preserve from each blueprint

Always try to preserve:

### Coverage
- major topics from each included unit
- essential subtopics
- representative skill types
- conceptual and computational balance

### Structure
- section logic where compatible
- mark patterns where practical
- response expectations
- progression logic

### Difficulty
- global easy / medium / hard balance
- within-section progression
- end-of-test challenge level
- trap intensity and misconception patterns

### Style
- wording tone
- command verbs
- answer format expectations
- diagram / graph / derivation expectations
- proof / explanation expectations where relevant

### Trap patterns
- recurring distractor styles
- likely misconception patterns
- setup traps
- notation / sign / unit traps
- multi-step reasoning traps

## What should change in cumulative generation

A cumulative test should usually adapt these elements:
- redistribute topic weights across units
- smooth structure into a single coherent paper
- reduce redundant question forms across units
- prevent duplicate skill checks
- create bridges between earlier and later units where appropriate
- build mixed questions that combine prerequisite knowledge when supported

## Balance strategies

Use one of these balancing strategies based on user intent:

### Equal unit balance
Use when the user wants each unit represented similarly.

### Weighted by recency
Use when later units should appear more heavily.

### Weighted by marks
Use when the blueprint evidence suggests some units normally carry more marks.

### Weighted by exam realism
Use when the cumulative test should resemble a formal exam pattern.

### Weighted by difficulty progression
Use when earlier units should anchor accessible questions and later units should support harder synthesis items.

If the user gives no weighting instruction:
- default to fair, defensible balance across included blueprints
- avoid letting the largest blueprint dominate automatically

## Subject handling

Subject is always dynamic at runtime.

Use shared blueprint fields for common merge logic.
Use `subject_extensions` to preserve subject-specific behavior.

Examples:
- Math: carry forward notation consistency, graphing/proof style, exact value expectations
- Physics: carry forward units, constants, circuit/force/energy style calculations, diagram expectations
- Chemistry: carry forward equation handling, balancing, stoichiometric setup, representations, lab/data interpretation
- Biology: carry forward terminology precision, labeling expectations, process explanations, diagram/data interpretation

Do not merge incompatible subject assumptions without explicit instruction.

## Recommended workflow

### Step A - Load blueprints
Read and validate all selected blueprint JSON files.

### Step B - Build merge map
Identify for each blueprint:
- covered unit
- topic weights
- structure
- difficulty profile
- trap patterns
- style signature
- cumulative metadata
- merge tags

### Step C - Resolve merge strategy
Decide:
- target total structure
- unit balance
- topic balance
- difficulty progression
- answer format mix
- repeated structure to keep or reduce

### Step D - Build cumulative blueprint plan
Create a temporary internal plan for:
- sections
- question counts
- unit/topic allocation
- marks
- target difficulty by section
- synthesis opportunities
- cumulative-only traps or review features

### Step E - Generate draft test
Generate fresh questions from the merged plan.

### Step F - Check coherence
Verify:
- all selected units are represented appropriately
- there are no duplicate questions or duplicate skill checks
- the test reads as one assessment
- the difficulty curve is sensible
- unit/topic balance matches the merge strategy
- no unit is unintentionally dominant

### Step G - Produce outputs
Write:
- cumulative student test
- optional teacher version
- optional answer key / solutions
- merge summary

## Cumulative question design guidance

When appropriate, include some questions that:
- connect prerequisite knowledge from earlier units
- require students to choose among multiple methods
- test transfer rather than isolated recall
- preserve fairness by not depending on hidden assumptions
- still feel consistent with the original teacher style

Do not force synthesis questions if the source blueprints do not support them.

## Output format expectations

Possible output types may include:
- markdown
- plain text
- JSON sidecar metadata
- later DOCX / PDF formatting through downstream workflows

At minimum, the output should be cleanly structured and easy to transform into print-ready documents.

A good cumulative test should include:
- title
- subject
- covered units if known
- clear section headings
- instructions
- numbered questions
- marks if applicable
- balanced scope across the selected blueprints

## Answer key / teacher output

If answer key or teacher version is requested, include:
- correct answers
- worked steps where appropriate
- marking guidance if supported
- brief note when a question intentionally synthesizes multiple units

Keep teacher content separate from the student-facing version when possible.

## File naming convention

Preferred output patterns:

Student cumulative test:
`<subject>_cumulative-test_v1.md`

Teacher cumulative test:
`<subject>_cumulative-teacher_v1.md`

Cumulative answer key:
`<subject>_cumulative-answer-key_v1.md`

If unit names should appear:
`<subject>_units-1-4_cumulative-test_v1.md`

Use lowercase and filename-safe names where practical.

## Memory MCP guidance

If memory MCP is available, store only concise reusable merge notes, such as:
- blueprints combined
- merge strategy used
- unit weighting summary
- cumulative style signature
- synthesis level used
- difficulty balance notes

Do not store full cumulative test text in memory unless explicitly requested.

## Filesystem MCP guidance

If filesystem MCP is available:
- read blueprint files from `data/blueprints/<subject>/`
- write generated cumulative outputs to `data/generated_tests/<subject>/`
- optionally write a sidecar merge summary next to the output

Do not overwrite existing files unless explicitly instructed.

## Quality bar

A good cumulative test should be:
- coherent
- balanced
- subject-accurate
- fair across units
- fresh
- structurally intentional
- consistent with blueprint evidence
- easy to format later into DOCX/PDF

## Failure handling

If one or more blueprints are too weak:
- identify which ones are weak
- reduce reliance on unsupported fields
- state assumptions clearly
- suggest re-running `analyze-test` for those units if needed

If merge conflicts are strong:
- resolve them explicitly
- document the resolution in the merge summary

If the generated cumulative test feels stitched together:
- rebalance sections
- smooth transitions
- reduce redundancy
- regenerate until the output reads as one coherent assessment

## Definition of done

This skill is complete only when:
- multiple valid blueprints have been loaded
- a clear merge strategy has been applied
- a fresh cumulative test has been generated
- unit/topic balance is intentional and defensible
- the output is saved in the correct subject folder
- any answer key / teacher version requested has also been produced
- a short merge summary has been produced