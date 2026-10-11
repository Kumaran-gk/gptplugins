# AI Test Builder

AI Test Builder is a Codex plugin for creating practice question papers. You can
describe the paper you want, analyze an older paper into a reusable blueprint,
generate new versions from that blueprint, or combine several unit blueprints
into a cumulative paper. The subject is chosen at runtime; examples include
math, chemistry, physics, and biology.

**Plugin website:** [AI Test Builder on GitHub](https://github.com/Kumaran-gk/gptplugins/tree/main/ai-test-builder)
**Source repository:** [Kumaran-gk/gptplugins](https://github.com/Kumaran-gk/gptplugins)

The GitHub plugin page is the project's current website. This plugin is shared
through the `gptplugins` marketplace; it is not a listing in OpenAI's public
Plugins Directory.

## Choose a workflow

| Goal | What you provide | What the plugin creates |
| --- | --- | --- |
| Questions from your preferences | Subject and topic; add level, count, types, marks, difficulty, and output format for better control | Original questions, optional separate teacher answers, and requested files |
| Analyze an old test | Subject and at least one PDF, DOCX, or image file | One validated blueprint JSON per source file and an analysis summary |
| Build a test pack | Subject and at least one source test or blueprint JSON | Blueprint(s) when needed, new version(s), optional teacher copies and cumulative paper, plus a run manifest |
| Generate from a blueprint | Subject and a valid blueprint JSON, or a search query that identifies one | A fresh paper that follows the blueprint's structure and topic mix |
| Build a cumulative paper | Subject and at least two blueprint JSON files | A paper combining the selected units, with optional unit weights |

For a quick paper, no source document, blueprint, or separate API key is needed.
The `create-custom-test` skill has Codex write the questions and uses the local
`save_custom_test` tool when you ask for files. The analyzed-paper workflow uses
the bundled local MCP server and its blueprint schema. Its default generation
backend is a template-based generator. An optional GPT-backed mode requires an
`OPENAI_API_KEY`; selecting it may incur API charges.

## Install in Codex

You need a Codex version with plugin commands and internet access. The public
repository can be added with GitHub's `owner/repo` shorthand; no full URL or
branch name is required:

```sh
codex plugin marketplace add Kumaran-gk/gptplugins
codex plugin list
codex plugin add ai-test-builder@gptplugins
codex plugin list
```

The final list should show `ai-test-builder@gptplugins` as installed and enabled.
Restart Codex or start a new chat so the plugin's skills and MCP server are
available. You can also install it from the `gptplugins` source in Codex's
Plugins Directory.

The local MCP server runs with the `python` command. Install Python 3.12 or
newer, make `python` available on `PATH`, and install its dependencies. The
plugin install command does **not** install Python packages. One simple way to
obtain the requirements file is:

```sh
git clone https://github.com/Kumaran-gk/gptplugins.git
cd gptplugins
python --version
python -m pip install -r ai-test-builder/requirements.txt
```

If you already have the repository, use your existing checkout instead of
cloning it again. Git is only needed to obtain or update the repository; Codex
installs the plugin from the marketplace command above. For scanned PDFs or
image files, also install [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
and put its executable on `PATH`, or give the tool its `tesseract_cmd` path.
Tesseract is unnecessary for text-based PDF and DOCX inputs.

## Inputs: what is required

### Preference-based questions

The essential details are a **subject** and **topic or unit**. If you omit other
choices, Codex uses reasonable defaults and should tell you what it assumed.
For a controlled paper, specify:

- Grade, course, or learner level and the curriculum if relevant.
- Topic boundaries and any topics to exclude.
- Total number of questions and the mix of multiple choice, short answer,
  calculations, explanations, proofs, or diagrams.
- Difficulty, total marks or marks per question, and time limit.
- Whether you want student and teacher versions, worked solutions, or marking
  guidance.
- Whether to show the paper in chat or save Markdown (`md`), DOCX, or PDF files.

Preference-based generation does not create a blueprint automatically. Use the
source analysis workflow when you want to reuse the pattern of an old paper.

### Source tests and unit content

For analysis, provide a **subject** and the path to at least one source test.
For a one-step test pack, you may instead provide an existing blueprint JSON.
Use paths that Codex can read, preferably absolute paths. You can keep private
papers under `data/input/<subject>/` in a local checkout; the repository ignores
input files. The installed plugin has its own copy of the `data/` folders.

| Input | Accepted file types | How it is read |
| --- | --- | --- |
| Text-based test PDF | `.pdf` | Embedded text is extracted page by page. |
| Scanned or mixed PDF | `.pdf` | `pdf_mode=auto` uses OCR on pages with little embedded text; `ocr` forces OCR on every page. Requires Tesseract when OCR runs. |
| Word test | `.docx` | Paragraph and table text is extracted. Embedded pictures are not separately OCRed. |
| Photo or scan | `.png`, `.jpg`, `.jpeg`, `.tif`, `.tiff`, `.bmp`, `.webp` | Tesseract OCR reads the image. One image is treated as one page; list each page file when using multiple images. |
| Existing blueprint | `.json` matching `schemas/blueprint_schema.json` | Validated and used to generate a new paper; not treated as a source test. |
| Optional unit content | PDF, DOCX, or the image formats above | Read separately to provide topic content when building a test pack. The old test still supplies the assessment pattern. |

Plain `.txt`, legacy `.doc`, and PPT files are not direct inputs to the
source-file pipeline. Convert them to PDF or DOCX first. You may paste short
text or instructions into a preference-based prompt. OCR can miss handwriting,
math notation, tables, and diagrams; inspect the analysis and generated paper
before using them with students. Visual diagrams are not reproduced as images
by the extraction pipeline.

For PDF input, `pdf_mode` accepts `auto` (default), `text`, or `ocr`. You can
also specify `ocr_lang` (default `eng`) and `tesseract_cmd` when Tesseract is
not on `PATH`. Use `text` only for PDFs with extractable text. A blank or noisy
extraction should be corrected before relying on its blueprint.

## How a blueprint is made

1. The plugin detects each source file type and extracts text from its pages,
   paragraphs, tables, or image OCR.
2. It normalizes the extracted text, then identifies observable structure such
   as section headings, question numbering, question types, marks, and topic
   signals.
3. It estimates topic distribution, difficulty, and recurring traps or
   distractor styles. Observations are kept distinct from inferences and
   uncertain areas should be reported.
4. It builds a subject-aware JSON blueprint with source metadata, unit,
   structure, topic distribution, difficulty profile, question style, trap
   patterns, generation rules, and subject-specific extensions.
5. It validates the JSON against
   [`schemas/blueprint_schema.json`](schemas/blueprint_schema.json). Only a
   valid blueprint is saved and indexed for later retrieval.

Each source test produces its own blueprint under
`data/blueprints/<subject>/`. A blueprint describes reusable test design; it
is not a transcript or copy of the old questions. New tests should change the
wording, values, contexts, and distractors while preserving the chosen
structure and difficulty. Analysis can also save extraction and validation
debug JSON. Review source names and debug artifacts before sharing them.

## How a question paper is generated

- **From preferences:** Codex drafts and checks original questions in chat.
  When files are requested, `save_custom_test` writes student Markdown and an
  optional separate teacher copy, then exports requested DOCX/PDF files.
- **From an old paper:** Analyze the source into a valid blueprint. Generate
  from that blueprint with one or more version labels. A test pack combines
  these steps and writes a manifest of the created files.
- **From several units:** Analyze each unit or supply its blueprint JSON. Give
  at least two blueprints for a cumulative paper and optional weights such as
  `Unit 1:30,Unit 2:70`.

The paper generator uses the blueprint's section pattern, topic weighting,
difficulty, and answer style. Ask for a separate teacher version to get an
answer key or worked steps where supported. Check factual answers, calculations,
marks, and layout before classroom use. The default blueprint generator is
template-based, so inspect question variety and edit weak items.

## Copyable prompt examples

Replace the example file paths and names with your own. Send **one prompt at a
time** in a new Codex chat after installation. Paths must be accessible to
Codex. Naming the subject explicitly keeps outputs in the right subject folder.

### 1. Create questions without a source paper

```text
Create a Grade 11 Chemistry practice paper on stoichiometry. Make 12 original questions: 4 multiple choice, 4 short answer, and 4 calculations. Use medium difficulty with a few harder final questions, 40 marks total, and a 60-minute time limit. Exclude limiting reagents. Give me a student paper and a separate teacher answer key with worked calculations. Save both as Markdown and PDF. Check the answers and units before saving.
```

Required input: subject and topic. The remaining details in this example set
the paper's level, structure, difficulty, marks, and output files.

### 2. Analyze one text-based PDF into a blueprint

```text
Analyze the test at <absolute-path-to-test.pdf> as a Grade 11 Chemistry stoichiometry test. Use PDF text extraction. Create and validate a reusable blueprint JSON, then show the observed structure, inferred patterns, topic weighting, difficulty, and uncertain areas. Do not generate a new paper yet. Give me the saved blueprint path.
```

Required input: subject and PDF path. `pdf_mode=text` is appropriate only when
the PDF contains selectable text.

### 3. Analyze scanned pages or handwritten images

```text
Analyze these scanned Grade 10 Biology test pages as one source set: <absolute-path-to-page-1.png> and <absolute-path-to-page-2.png>. Use OCR with English and create validated blueprint JSON for each supplied file. Explain any unclear text, missing diagram information, or uncertain marks. Do not invent unreadable questions. Give me the blueprint paths.
```

Required input: subject and image paths. Tesseract OCR must be installed.
The current analyzer creates **one blueprint per file**, so combine page images
into one PDF first if they belong to a single paper and you need one blueprint.

### 4. Analyze a DOCX test

```text
Analyze <absolute-path-to-test.docx> as a Grade 12 Physics forces test. Extract the paragraphs and tables, create a schema-valid blueprint, and summarize the section order, marks, question types, topics, and common traps. Report anything contained only in images that you cannot read. Give me the saved blueprint path.
```

Required input: subject and DOCX path.

### 5. Build two new versions from an old paper in one run

```text
Build a test pack for Grade 11 Math using <absolute-path-to-old-test.pdf>. Analyze it into a validated blueprint, then generate two fresh versions named A and B. Preserve the section structure, topic balance, and difficulty without copying source questions. Include separate student and teacher papers with answers. Export Markdown, DOCX, and PDF. Give me the blueprint path, output paths, and run manifest. Use pdf_mode=auto.
```

Required input: subject and at least one source test. You can supply several
source tests or existing blueprint JSON files. A test pack defaults to two
versions (`verA`, `verB`), a teacher copy, and Markdown if you do not specify
those choices.

### 6. Ground a test pack in unit content

```text
Build a Grade 11 Chemistry test pack from the assessment pattern in <absolute-path-to-old-test.pdf>. Also use <absolute-path-to-unit-notes.pdf> as unit content for topic grounding. Create two fresh versions with student and teacher papers in PDF and Markdown. First validate the new blueprint, then show the output paths and manifest. Flag topics that the unit notes do not support.
```

Required input: subject and a source test or blueprint. The unit-content file
is optional and supplies context; it is separate from the source paper used to
extract test structure.

### 7. Generate from a saved blueprint

```text
Using the valid blueprint at <absolute-path-to-blueprint.json>, generate a new Grade 11 Chemistry practice paper labeled Version C. Keep its sections, topic weighting, marks, and difficulty profile, but use fresh questions and values. Include student and separate teacher versions with worked answers. Export Markdown and PDF, then report every created path.
```

Required input: subject and blueprint path. If you do not know the path, ask
Codex to list or find blueprints for the subject and confirm which one to use.

### 8. Build a cumulative paper from multiple units

```text
Build a cumulative Grade 11 Physics practice exam from <absolute-path-to-motion-blueprint.json> and <absolute-path-to-forces-blueprint.json>. Weight Motion 40% and Forces 60%. Create a student paper and a separate teacher paper with answers, labeled Final Review. Export Markdown and PDF. Validate both blueprints first and show the saved output paths.
```

Required input: subject and at least two valid blueprint paths. Unit weights
are optional; use the unit names stored in the blueprints when specifying them.

## Files, privacy, and updates

| Path inside the plugin | Purpose |
| --- | --- |
| `data/input/<subject>/` | Your local source papers. Git ignores the input files; an empty folder marker is included. |
| `data/blueprints/<subject>/` | Validated reusable blueprint JSON and, when enabled, analysis debug files. |
| `data/generated_tests/<subject>/` | Student and teacher Markdown, DOCX, PDF, and run artifacts. |
| `data/memory/` | Short retrieval records for finding blueprint patterns again. |

The public repository includes reviewed blueprints and generated outputs but
does not include the original input papers. New blueprints, debug files, and
generated tests can contain source text or metadata and are **not ignored by
Git**. Review them for names, student details, school details, and addresses
before committing or sharing. See [data/README.md](data/README.md).

Installed plugin files are cached by Codex under its plugin cache. The Python
tools write to the `data/` directory of the plugin copy they are running.
Keep a copy of any outputs you want to retain outside that cache, especially
before removing or updating the plugin. In a development checkout, the same
relative paths are under the checkout's `ai-test-builder/` folder.

To receive a newer published version of the marketplace, use:

```sh
codex plugin marketplace upgrade gptplugins
codex plugin list
```

## Development and reference files

- [Plugin manifest](.codex-plugin/plugin.json)
- [MCP server configuration](.mcp.json)
- [Blueprint schema](schemas/blueprint_schema.json)
- [Skills](skills/)
- [Python requirements](requirements.txt)
- [OpenAI's Codex plugin documentation](https://developers.openai.com/plugins/build/plugins)

From the `ai-test-builder/` directory, run `python -m pytest -q` to check the
test suite. The five MCP tools are `save_custom_test`, `analyze_test`,
`generate_test`, `build_cumulative_test`, and `build_test_pack`.
