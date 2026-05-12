import os
import subprocess
import sys
from pathlib import Path

from pptx import Presentation


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _console_script() -> str:
    return str(Path(sys.executable).with_name("consultdeck"))


def _env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    return env


def test_console_script_help_uses_console_command_name() -> None:
    result = subprocess.run(
        [_console_script(), "--help"],
        cwd=PROJECT_ROOT,
        env=_env(),
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout.startswith("usage: consultdeck ")
    assert "usage: python -m consultdeck" not in result.stdout


def test_module_help_uses_module_command_name() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "consultdeck", "--help"],
        cwd=PROJECT_ROOT,
        env=_env(),
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout.startswith("usage: python -m consultdeck ")


def test_cli_generates_pptx(tmp_path) -> None:
    output_dir = tmp_path / "output"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "consultdeck",
            "--topic",
            "生成AIの業務活用",
            "--purpose",
            "proposal",
            "--audience",
            "経営層",
            "--slides",
            "5",
            "--output",
            str(output_dir),
            "--deck-id",
            "deck-cli-test",
        ],
        cwd=PROJECT_ROOT,
        env=_env(),
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    output_path = output_dir / "deck-cli-test.pptx"
    assert str(output_path) in result.stdout
    assert output_path.exists()
    assert len(Presentation(output_path).slides) == 5


def test_cli_uses_default_templates_outside_project_root(tmp_path) -> None:
    cwd = tmp_path / "outside"
    cwd.mkdir()
    output_dir = tmp_path / "output"

    result = subprocess.run(
        [
            _console_script(),
            "--topic",
            "生成AIの業務活用",
            "--purpose",
            "proposal",
            "--audience",
            "経営層",
            "--slides",
            "3",
            "--output",
            str(output_dir),
            "--deck-id",
            "deck-default-template",
        ],
        cwd=cwd,
        env=_env(),
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert (output_dir / "deck-default-template.pptx").exists()


def test_cli_prefers_explicit_templates_over_default(tmp_path) -> None:
    cwd = tmp_path / "outside"
    cwd.mkdir()
    output_dir = tmp_path / "output"
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "custom.yaml").write_text(
        """
template_id: custom_proposal
name: Custom Proposal
doc_type: proposal
use_case: 提案書
audience: 現場
phase: proposal
slide_structure:
  - 表紙
  - 課題
layout_rules:
  default: content
style_rules:
  font: Arial
output_targets:
  - pptx
""".lstrip(),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            _console_script(),
            "--topic",
            "生成AIの業務活用",
            "--purpose",
            "proposal",
            "--audience",
            "現場",
            "--slides",
            "2",
            "--output",
            str(output_dir),
            "--templates",
            str(template_dir),
            "--deck-id",
            "deck-explicit-template",
        ],
        cwd=cwd,
        env=_env(),
        text=True,
        capture_output=True,
        check=False,
    )

    output_path = output_dir / "deck-explicit-template.pptx"
    assert result.returncode == 0
    assert output_path.exists()
    assert len(Presentation(output_path).slides) == 2


def test_cli_fails_when_required_arguments_are_missing(tmp_path) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "consultdeck", "--output", str(tmp_path)],
        cwd=PROJECT_ROOT,
        env=_env(),
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "error:" in result.stderr


def test_cli_fails_when_template_does_not_match(tmp_path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "consultdeck",
            "--topic",
            "生成AIの業務活用",
            "--purpose",
            "proposal",
            "--audience",
            "現場",
            "--slides",
            "5",
            "--output",
            str(tmp_path),
        ],
        cwd=PROJECT_ROOT,
        env=_env(),
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "No matching template" in result.stderr
