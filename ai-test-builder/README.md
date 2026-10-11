# AI Test Builder

AI Test Builder is a Codex plugin for making practice questions from your
preferences or from the structure of existing tests. It supports dynamic
subjects, including math, chemistry, physics, and biology.

## What it can do

- Create original questions from a subject, topic, level, difficulty, question
  count, and format, without a source paper or separate API key.
- Analyze PDF, DOCX, and image tests into schema-validated blueprint JSON.
- Generate student and teacher versions from a blueprint.
- Combine unit blueprints into a cumulative test.
- Save Markdown, DOCX, and PDF outputs.

## Install

Install Python 3.12 or newer and make `python` available on your PATH. Install
the plugin's dependencies:

```sh
git clone https://github.com/Kumaran-gk/gptplugins.git
cd gptplugins
python -m pip install -r ai-test-builder/requirements.txt
codex plugin marketplace add Kumaran-gk/gptplugins
```

Restart Codex, choose the `gptplugins` marketplace in the Plugins Directory,
and install **AI Test Builder**. Start a new chat after installation.

Example prompts:

> Create 12 Grade 11 chemistry questions about stoichiometry, medium
> difficulty, with four multiple-choice questions and a separate answer key.

> Analyze my test in `data/input/chemistry/` and make two new versions with
> student and teacher PDFs.

The first prompt uses the `create-custom-test` skill and does not need an API
key. The source-test workflow uses the local MCP server. Tesseract OCR is
optional for scanned documents. `OPENAI_API_KEY` is required only if you
explicitly select the separate GPT-backed generation mode.

## Data folders

- `data/input/<subject>/`: add your own source papers locally. Git ignores
  these files and retains the empty input folder with `.gitkeep`.
- `data/blueprints/<subject>/`: reusable blueprint JSON.
- `data/generated_tests/<subject>/`: generated student and teacher files.
- `data/memory/`: local retrieval records.

The included blueprints and generated outputs have been scrubbed for detected
personal identifiers and local paths. New blueprints and outputs are visible
to Git, so review them before committing changes. See [data/README.md](data/README.md).

## Development

Run the test suite with `python -m pytest -q`. The plugin manifest is
[`.codex-plugin/plugin.json`](.codex-plugin/plugin.json), and the MCP server
is configured in [`.mcp.json`](.mcp.json).
