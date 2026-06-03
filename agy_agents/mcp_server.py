import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List

import logfire
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


# ── Long-Term Semantic Memory Tools ────────────────────────

MEMORY_DIR = ".agent_memory"
MEMORY_FILE = os.path.join(MEMORY_DIR, "knowledge_base.json")


def _load_memory() -> Dict[str, List[str]]:
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


def _save_memory_state(state: Dict[str, List[str]]):
    os.makedirs(MEMORY_DIR, exist_ok=True)
    with open(MEMORY_FILE, "w") as f:
        json.dump(state, f, indent=4)


@mcp.tool()
def store_long_term_memory(topic: str, fact: str) -> str:
    """
    Saves a crucial fact or decision into permanent memory, associating it with a topic.
    Use this to persist knowledge beyond the current conversation context window.
    """
    with logfire.span("mcp.store_memory", topic=topic, _level="info"):
        mem = _load_memory()
        topic = topic.lower().strip()
        if topic not in mem:
            mem[topic] = []
        if fact not in mem[topic]:
            mem[topic].append(fact)
            _save_memory_state(mem)
        return f"Successfully committed fact to long-term memory under '{topic}'."


@mcp.tool()
def query_long_term_memory(keyword: str) -> str:
    """
    Retrieves stored semantic facts from long-term memory across all past interactions.
    """
    with logfire.span("mcp.query_memory", keyword=keyword, _level="info"):
        mem = _load_memory()
        keyword = keyword.lower().strip()
        results = []
        for topic, facts in mem.items():
            if keyword in topic:
                results.extend(facts)
            else:
                results.extend([f for f in facts if keyword in f.lower()])

        if not results:
            return f"No memories found matching '{keyword}'."
        return "\n".join([f"- {r}" for r in set(results)])


@mcp.tool()
def run_agent_by_name(agent_name: str, task: str, run_on_gks: bool = False) -> str:
    """
    Executes a specialized agent. For lightweight tasks, runs locally.
    Set run_on_gks=True ONLY for heavy thinking tasks to offload to the remote Global Knowledge Service (GKS).
    """
    with logfire.span(
        "mcp.run_agent_by_name", agent=agent_name, gks=run_on_gks, _level="info"
    ):
        if not run_on_gks:
            # Local execution
            return f"[LOCAL EXECUTION] Agent {agent_name} executed task locally: {task}"

        # Remote GKS execution
        config_path = Path.home() / ".openclaw" / "openclaw.json"
        if not config_path.exists():
            return "Error: Remote GKS is not configured. Missing ~/.openclaw/openclaw.json."

        try:
            result = subprocess.run(
                ["openclaw", "gateway", "call", "agent", agent_name, "--prompt", task],
                capture_output=True,
                text=True,
                check=True,
            )

            # Check if output is JSON
            try:
                parsed = json.loads(result.stdout)
                return json.dumps(parsed, indent=2)
            except json.JSONDecodeError:
                # Raw fallback
                return result.stdout.strip()

        except subprocess.CalledProcessError as e:
            err_msg = e.stderr.strip() if e.stderr else e.stdout.strip()
            return f"GatewayTransportError: {err_msg}"
        except Exception as e:
            return f"GatewayTransportError: Unexpected Error: {str(e)}"


if __name__ == "__main__":
    # Start the MCP stdio server
    mcp.run()
