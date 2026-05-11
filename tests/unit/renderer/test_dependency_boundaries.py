from pathlib import Path


def test_pptx_dependency_is_limited_to_renderer_source() -> None:
    source_root = Path("src/consultdeck")
    offenders: list[Path] = []

    for path in source_root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "pptx" not in text:
            continue
        if "src/consultdeck/renderer" not in path.as_posix():
            offenders.append(path)

    assert offenders == []
