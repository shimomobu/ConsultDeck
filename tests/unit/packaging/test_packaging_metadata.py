import tomllib
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_pyproject_declares_consultdeck_console_script() -> None:
    pyproject = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text())

    assert pyproject["project"]["scripts"]["consultdeck"] == "consultdeck.__main__:main"


def test_readme_documents_current_cli_commands_and_constraints() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    assert "pip install -e ." in readme
    assert "consultdeck --topic" in readme
    assert "python -m consultdeck" in readme
    assert "LLM本文生成なし" in readme
    assert "MCP Rendererなし" in readme
    assert "Stable Diffusion画像差し込みなし" in readme
    assert "PPTX見た目は最小限" in readme
