from __future__ import annotations

import argparse
import sys
from pathlib import Path

from consultdeck.llm.provider_factory import build_llm_provider
from consultdeck.models.requirement_spec import RequirementSpec
from consultdeck.pipeline.pipeline import Pipeline, PipelineError


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser(prog=_default_prog())
    args = parser.parse_args(argv)

    requirement = RequirementSpec(
        theme=args.topic,
        purpose=args.purpose,
        audience=args.audience,
        slide_count=args.slides,
    )
    pipeline = Pipeline(
        template_dir=args.templates,
        llm_provider=build_llm_provider(
            args.llm_provider,
            model_name=args.llm_model,
        ),
    )

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


def _default_prog() -> str | None:
    if Path(sys.argv[0]).name == "__main__.py":
        return "python -m consultdeck"
    return None


def _build_parser(prog: str | None = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=prog)
    parser.add_argument("--topic", required=True, help="資料テーマ")
    parser.add_argument("--purpose", required=True, help="資料種別。例: proposal")
    parser.add_argument("--audience", required=True, help="想定読者")
    parser.add_argument("--slides", type=int, required=True, help="生成するスライド枚数")
    parser.add_argument("--output", type=Path, required=True, help="PPTX出力ディレクトリ")
    parser.add_argument(
        "--templates",
        type=Path,
        default=_default_template_dir(),
        help="テンプレートYAMLディレクトリ",
    )
    parser.add_argument("--deck-id", default=None, help="出力ファイル名に使うdeck_id")
    parser.add_argument(
        "--llm-provider",
        choices=["none", "fake", "ollama"],
        default="none",
        help="本文生成Provider",
    )
    parser.add_argument(
        "--llm-model",
        default="gemma4:latest",
        help="LLM model name for providers that use a model selector",
    )
    return parser


def _default_template_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "assets" / "templates"


if __name__ == "__main__":
    raise SystemExit(main())
