from __future__ import annotations

import argparse
import json
from typing import Any, Dict, List

from dotenv import load_dotenv

from src.agent.router import resolve_skill
from src.agent.workflow import AgentWorkflow, WorkflowRequest
from src.config import Settings
from src.utils.logging_utils import configure_logging


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="AI Test Builder - Codex + MCP starter CLI"
    )

    parser.add_argument(
        "skill",
        choices=[
            "analyze-test",
            "generate-test",
            "build-cumulative-test",
            "build-test-pack",
        ],
        help="Skill to run.",
    )
    parser.add_argument(
        "--subject",
        required=True,
        help="Dynamic subject name, e.g. chemistry, physics, math, biology.",
    )
    parser.add_argument(
        "--input",
        nargs="*",
        default=[],
        help="Input source files for analyze-test.",
    )
    parser.add_argument(
        "--blueprints",
        nargs="*",
        default=[],
        help="Blueprint JSON files for generate-test or build-cumulative-test.",
    )
    parser.add_argument(
        "--unit-content",
        nargs="*",
        default=[],
        help="Unit-content source files used to ground generated questions.",
    )
    parser.add_argument(
        "--option",
        action="append",
        default=[],
        help="Optional key=value runtime option. Can be repeated.",
    )

    return parser


def parse_options(option_args: List[str]) -> Dict[str, Any]:
    parsed: Dict[str, Any] = {}
    for item in option_args:
        if "=" not in item:
            raise ValueError(
                f"Invalid --option value '{item}'. Expected key=value format."
            )
        key, value = item.split("=", 1)
        parsed[key.strip()] = value.strip()
    return parsed


def main() -> None:
    load_dotenv()
    configure_logging()
    parser = build_parser()
    args = parser.parse_args()

    settings = Settings.load()
    workflow = AgentWorkflow(settings=settings)

    request = WorkflowRequest(
        skill=resolve_skill(args.skill).replace("_", "-"),
        subject=args.subject,
        input_files=args.input,
        blueprint_files=args.blueprints,
        unit_content_files=args.unit_content,
        options=parse_options(args.option),
    )

    result = workflow.run(request)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
