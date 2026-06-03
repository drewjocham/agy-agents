import os
import logfire
from typing import List, Tuple, Optional

from google.antigravity import Agent, types
from google.antigravity.connections.local import LocalAgentConfig

from agy_agents.hooks import get_standard_hooks
from agy_agents.ports import AgentProviderPort, McpServerDef


# Configure Logfire for the EU tenant if the environment variable isn't already set
if not os.environ.get("LOGFIRE_BASE_URL"):
    os.environ["LOGFIRE_BASE_URL"] = "https://logfire-api-eu.pydantic.dev/"

if not os.environ.get("LOGFIRE_TOKEN"):
    os.environ["LOGFIRE_TOKEN"] = (
        "pylf_v2_eu_3fd048bb-3ff5-4d76-95eb-76d36927c22b_dvn4CFlWjcw11ql5vjYSkmlwDJ4QCj3H9v2rznf6qWjy"
    )

logfire.configure()
try:
    logfire.instrument_pydantic_ai()
except AttributeError:
    pass


class AntigravityAgentAdapter(AgentProviderPort):
    """
    Hexagonal Adapter: Implements the AgentProviderPort using the Google Antigravity SDK.
    """

    def __init__(self, save_dir: str = ".agy_memory"):
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)

    async def execute_agent(
        self,
        prompt: str,
        system_instruction: str,
        agent_name: str = "Unknown",
        conversation_id: Optional[str] = None,
        mcp_servers: Optional[List[McpServerDef]] = None,
    ) -> Tuple[str, str]:

        # Translate generic MCP definitions into AGY SDK specific configurations
        mcp_config = []
        if mcp_servers:
            for srv in mcp_servers:
                mcp_config.append(
                    types.McpStdioServer(command=srv.command, args=srv.args)
                )

        config = LocalAgentConfig(
            system_instruction=system_instruction,
            save_dir=self.save_dir,
            conversation_id=conversation_id,
            capabilities=types.CapabilitiesConfig(
                enable_subagents=True,
            ),
            hooks=get_standard_hooks(),
            mcp_servers=mcp_config,
        )

        with logfire.span("agent.execute", conversation_id=conversation_id):
            async with Agent(config) as agent:
                response = await agent.chat(prompt)
                response_text = await response.text()

                # Observability logging transparent to the caller
                usage = agent.conversation.total_usage
                logfire.info(
                    "agent.metrics",
                    prompt_tokens=usage.prompt_token_count,
                    total_tokens=usage.total_token_count,
                )

                # ── MANDATORY QUALITY GATE FOR CODING TASKS ──
                # If the persona is a coder, intercept completion and force a review.
                coding_keywords = ["backend engineer", "frontend", "coder", "developer"]
                is_coder = any(
                    kw in system_instruction.lower() for kw in coding_keywords
                )
                if is_coder or agent_name.lower() in [
                    "backendengineeragent",
                    "frontendagent",
                    "servicecoderagent",
                ]:
                    logfire.info(
                        "Coding task detected. Triggering mandatory Quality Gates."
                    )
                    import asyncio
                    import subprocess
                    from agy_agents.mcp_server import delegate_task_to_subagent

                    # 1. Native Turnaround Loop: Always run make lint and make test
                    turnaround_output = "\n=== NATIVE TURNAROUND LOOP ===\n"
                    try:
                        subprocess.run(
                            ["make", "lint"], capture_output=True, text=True, check=True
                        )
                        turnaround_output += "✅ make lint PASSED.\n"
                    except subprocess.CalledProcessError as e:
                        turnaround_output += (
                            f"❌ make lint FAILED:\n{e.stderr or e.stdout}\n"
                        )

                    try:
                        subprocess.run(
                            ["make", "test"], capture_output=True, text=True, check=True
                        )
                        turnaround_output += "✅ make test PASSED.\n"
                    except subprocess.CalledProcessError as e:
                        turnaround_output += (
                            f"❌ make test FAILED:\n{e.stderr or e.stdout}\n"
                        )

                    # 2. Spawn the 3 required checks concurrently
                    tester_task = delegate_task_to_subagent(
                        "TestEngAgent",
                        f"Review this code and turnaround logs for testing gaps:\n{turnaround_output}\n{response_text}",
                    )
                    sec_task = delegate_task_to_subagent(
                        "SecurityAgent",
                        f"Review this code for security flaws:\n{response_text}",
                    )
                    curator_task = delegate_task_to_subagent(
                        "LibraryCuratorAgent",
                        f"Review this code for dependency issues:\n{response_text}",
                    )

                    reviews = await asyncio.gather(
                        tester_task, sec_task, curator_task, return_exceptions=True
                    )

                    response_text += f"\n{turnaround_output}"
                    response_text += "\n=== AUTOMATED QUALITY GATE REVIEWS ===\n"
                    response_text += f"\n--- Tester Review ---\n{reviews[0]}\n"
                    response_text += f"\n--- Security Review ---\n{reviews[1]}\n"
                    response_text += f"\n--- Library Curator Review ---\n{reviews[2]}\n"

                return response_text, agent.conversation_id
