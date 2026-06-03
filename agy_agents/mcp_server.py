import logging
import logfire
from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

# Pydantic Tracing via Logfire (will pick up LOGFIRE_TOKEN from env if set)
logfire.configure()
logging.basicConfig(level=logging.INFO)

mcp = FastMCP("AgyAgentsMCP")

# ── BA Tools


@mcp.tool()
def define_user_stories(raw_requirements: str) -> List[Dict[str, Any]]:
    """Converts raw text requirements into structured UserStory models."""
    with logfire.span("mcp.define_user_stories", _level="info"):
        return [{"story_id": "EXAMPLE-01", "description": raw_requirements}]


@mcp.tool()
def map_event_triggers(story_id: str, gherkin: str) -> List[Dict[str, Any]]:
    """Identifies specific events necessary for the Go backend and QA automation pipelines."""
    with logfire.span("mcp.map_event_triggers", story_id=story_id, _level="info"):
        return [{"name": "example.Triggered", "owner": "example_context"}]


# ── Backend Tools ──────────────────────────────────────────


@mcp.tool()
def scaffold_go_service(service_name: str, bounded_context: str) -> Dict[str, str]:
    """Returns a complete Go project skeleton. The LLM fills in domain-specific logic in its main response."""
    with logfire.span(
        "mcp.scaffold_go_service", service_name=service_name, _level="info"
    ):
        return {
            "cmd/server/main.go": f"// Scaffolding for {service_name}\npackage main\n\nfunc main() {{}}",
            f"internal/domain/{service_name}.go": "package domain\n",
            "internal/domain/events.go": "package domain\n",
            "internal/ports/repository.go": "package ports\n",
            "internal/ports/events.go": "package ports\n",
            "internal/adapters/repository/postgres.go": "package repository\n",
            "internal/adapters/eventbus/nats.go": "package eventbus\n",
            "internal/adapters/handlers/grpc.go": "package handlers\n",
            f"api/protobuf/{service_name}.proto": 'syntax="proto3";\n',
            "go.mod": f"module {service_name}\n\ngo 1.22",
            "Makefile": "build:\n\tgo build -o bin/server cmd/server/main.go",
        }


@mcp.tool()
def generate_dockerfile(service_name: str, port: int) -> str:
    """Returns multi-stage Dockerfile."""
    with logfire.span(
        "mcp.generate_dockerfile", service_name=service_name, _level="info"
    ):
        return f"FROM golang:1.22-alpine AS builder\n# Build steps...\nEXPOSE {port}\n"


if __name__ == "__main__":
    # Start the MCP stdio server
    mcp.run()
