from typing import Optional, Tuple
from agy_agents.ports import AgentProviderPort, McpServerDef

devops_prompt = """You are a Principal DevOps Engineer.
Your objective is to design and generate complete CI/CD pipelines (GitHub Actions, GitLab CI), comprehensive Docker Compose setups for local development, and advanced Makefiles.
Prioritize secure, fast, and repeatable builds.
Return Artifact with files dict mapping relative paths to file contents.


CRITICAL WORKFLOW:
1. **History Review:** Use `query_history` to recall previous architectural and contextual decisions before generating logic.
2. **Log Progress:** Call `log_activity` after significant actions.
3. **Proactive Docs:** Keep `docs/` updated via `update_documentation` when implementing major features.

"""


class DevopsAgent:
    """
    Hexagonal Agent: Isolated from the LLM provider.
    Relies entirely on the injected AgentProviderPort and consumes tools via MCP.
    """

    def __init__(self, provider: AgentProviderPort):
        self.provider = provider
        self.mcp_servers = [
            McpServerDef(command="python3", args=["-m", "agy_agents.mcp_server"])
        ]

    async def run(
        self, prompt: str, conversation_id: Optional[str] = None
    ) -> Tuple[str, str]:
        return await self.provider.execute_agent(
            prompt=prompt,
            system_instruction=devops_prompt,
            conversation_id=conversation_id,
            mcp_servers=self.mcp_servers,
        )
