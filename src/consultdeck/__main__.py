from __future__ import annotations

import argparse
import sys
from pathlib import Path

from consultdeck.models.requirement_spec import RequirementSpec
from consultdeck.pipeline.pipeline import Pipeline, PipelineError


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    requirement = RequirementSpec(
        theme=args.topic,
        purpose=args.purpose,
        audience=args.audience,
        slide_count=args.slides,
    )
    pipeline = Pipeline(template_dir=args.templates)

    try:
        output_path = pipeline.run(
            requirement,
            output_dir=args.output,
            deck_id=args.deck_id,
        )
    except PipelineError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(output_path)
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m consultdeck")
    parser.add_argument("--topic", required=True, help="資料テーマ")
    parser.add_argument("--purpose", required=True, help="資料種別。例: proposal")
    parser.add_argument("--audience", required=True, help="想定読者")
    parser.add_argument("--slides", type=int, required=True, help="生成するスライド枚数")
    parser.add_argument("--output", type=Path, required=True, help="PPTX出力ディレクトリ")
    parser.add_argument(
        "--templates",
        type=Path,
        default=Path("assets/templates"),
        help="テンプレートYAMLディレクトリ",
    )
    parser.add_argument("--deck-id", default=None, help="出力ファイル名に使うdeck_id")
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
