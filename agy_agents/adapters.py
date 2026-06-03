import os
import logfire
from typing import List, Tuple, Optional

from google.antigravity import Agent, types
from google.antigravity.connections.local import LocalAgentConfig

from agy_agents.hooks import get_standard_hooks
from agy_agents.ports import AgentProviderPort, McpServerDef

logfire.configure()


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

                # Observability logging transparent to the caller
                usage = agent.conversation.total_usage
                logfire.info(
                    "agent.metrics",
                    prompt_tokens=usage.prompt_token_count,
                    total_tokens=usage.total_token_count,
                )

                return await response.text(), agent.conversation_id
