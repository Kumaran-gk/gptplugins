from __future__ import annotations

import argparse
import json
import os
from typing import Any, Dict, List

from dotenv import load_dotenv

from src.agent.workflow import AgentWorkflow, WorkflowRequest
from src.config import Settings
from src.generation.custom_test_writer import save_custom_test as write_custom_test


try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover - import guard for local setup
    raise RuntimeError(
        "The MCP server requires the 'mcp' package. Install it with 'pip install -r requirements.txt'."
    ) from exc


load_dotenv()


def _build_request(
    *,
    skill: str,
    subject: str,
    input_files: List[str] | None = None,
    blueprint_files: List[str] | None = None,
    unit_content_files: List[str] | None = None,
    options: Dict[str, Any] | None = None,
) -> WorkflowRequest:
    return WorkflowRequest(
        skill=skill,
        subject=subject,
        input_files=input_files or [],
        blueprint_files=blueprint_files or [],
        unit_content_files=unit_content_files or [],
        options=options or {},
    )


def create_mcp_server(*, host: str, port: int) -> FastMCP:
    settings = Settings.load()
    workflow = AgentWorkflow(settings=settings)
    server = FastMCP(
        "ai-test-builder",
        host=host,
        port=port,
    )

    @server.tool()
    def save_custom_test(
        subject: str,
        title: str,
        student_markdown: str,
        teacher_markdown: str | None = None,
        version: str = "v1",
        export_formats: List[str] | None = None,
    ) -> str:
        """Save preference-based questions authored by Codex as student and teacher files.

        Use when the user asks for questions by subject, topic, grade, difficulty,
        or style without providing a source test or blueprint. Codex writes the
        questions and answers; this tool saves markdown and optional DOCX/PDF.
        """
        result = write_custom_test(
            settings=settings,
            subject=subject,
            title=title,
            student_markdown=student_markdown,
            teacher_markdown=teacher_markdown,
            version=version,
            export_formats=export_formats,
        )
        return json.dumps(result, indent=2)

    @server.tool()
    def build_test_pack(
        subject: str,
        input_files: List[str] | None = None,
        blueprint_files: List[str] | None = None,
        unit_content_files: List[str] | None = None,
        options: Dict[str, Any] | None = None,
    ) -> str:
        """
        Main test-creator entrypoint.

        Use this tool when the goal is to analyze a source test, generate one or more fresh versions,
        optionally use unit-content grounding, and optionally build a cumulative paper in one workflow.
        """
        request = _build_request(
            skill="build-test-pack",
            subject=subject,
            input_files=input_files,
            blueprint_files=blueprint_files,
            unit_content_files=unit_content_files,
            options=options,
        )
        result = workflow.run(request)
        return json.dumps(result, indent=2)

    @server.tool()
    def analyze_test(
        subject: str,
        input_files: List[str],
        options: Dict[str, Any] | None = None,
    ) -> str:
        """
        Analyze teacher source tests and create a reusable blueprint.
        """
        request = _build_request(
            skill="analyze-test",
            subject=subject,
            input_files=input_files,
            options=options,
        )
        result = workflow.run(request)
        return json.dumps(result, indent=2)

    @server.tool()
    def generate_test(
        subject: str,
        blueprint_files: List[str] | None = None,
        unit_content_files: List[str] | None = None,
        options: Dict[str, Any] | None = None,
    ) -> str:
        """
        Generate a fresh test from an existing blueprint.
        """
        request = _build_request(
            skill="generate-test",
            subject=subject,
            blueprint_files=blueprint_files,
            unit_content_files=unit_content_files,
            options=options,
        )
        result = workflow.run(request)
        return json.dumps(result, indent=2)

    @server.tool()
    def build_cumulative_test(
        subject: str,
        blueprint_files: List[str] | None = None,
        options: Dict[str, Any] | None = None,
    ) -> str:
        """
        Build a cumulative paper from multiple blueprints.
        """
        request = _build_request(
            skill="build-cumulative-test",
            subject=subject,
            blueprint_files=blueprint_files,
            options=options,
        )
        result = workflow.run(request)
        return json.dumps(result, indent=2)

    return server


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI Test Builder MCP server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default=os.getenv("AI_TEST_BUILDER_MCP_TRANSPORT", "stdio"),
        help="MCP transport to use. For Codex localhost URL integration, prefer streamable-http.",
    )
    parser.add_argument(
        "--host",
        default=os.getenv("AI_TEST_BUILDER_MCP_HOST", "127.0.0.1"),
        help="Host for HTTP-based MCP transports.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("AI_TEST_BUILDER_MCP_PORT", "8000")),
        help="Port for HTTP-based MCP transports.",
    )
    return parser


def main() -> None:  # pragma: no cover - runtime entrypoint
    parser = _build_parser()
    args = parser.parse_args()

    server = create_mcp_server(host=args.host, port=args.port)
    server.run(transport=args.transport)


if __name__ == "__main__":  # pragma: no cover - runtime entrypoint
    main()
