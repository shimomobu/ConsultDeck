import os
import subprocess
import sys
from pathlib import Path

from pptx import Presentation


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    return env


def test_console_script_help_uses_console_command_name() -> None:
    result = subprocess.run(
        [str(Path(sys.executable).with_name("consultdeck")), "--help"],
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
