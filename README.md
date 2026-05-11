# ConsultDeck

ConsultDeck is a local CLI tool for generating an editable PowerPoint deck from a structured request and a registered template.

Current flow:

```text
RequirementSpec -> TemplateSelector -> OutlineBuilder -> SlideBuilder -> BuiltinPptxRenderer -> .pptx
```

## Setup

Create and activate a virtual environment, then install the project in editable mode.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

For local test execution, install development extras.

```bash
pip install -e ".[dev]"
```

## CLI Usage

After editable install, run the console script without setting `PYTHONPATH`.

```bash
consultdeck --topic "生成AIの業務活用" --purpose proposal --audience "経営層" --slides 5 --output output/
```

The module entrypoint also remains available.

```bash
python -m consultdeck --topic "生成AIの業務活用" --purpose proposal --audience "経営層" --slides 5 --output output/
```

Both commands print the generated `.pptx` path.

## Current Constraints

- LLM本文生成なし: slide messages and bullets are deterministic placeholders.
- MCP Rendererなし: only the builtin PPTX renderer is wired.
- Stable Diffusion画像差し込みなし: image generation and insertion are not active.
- PPTX見た目は最小限: layouts are intentionally basic and editable.
