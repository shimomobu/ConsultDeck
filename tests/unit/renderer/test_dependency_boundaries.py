from pathlib import Path


def test_pptx_dependency_is_limited_to_renderer_source() -> None:
    project_root = Path(__file__).resolve().parents[3]
    source_root = project_root / "src" / "consultdeck"
    offenders: list[Path] = []

    for path in source_root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "from pptx" not in text and "import pptx" not in text:
            continue
        if "src/consultdeck/renderer" not in path.relative_to(project_root).as_posix():
            offenders.append(path)

    assert offenders == []
