from typing import Optional, Tuple
from agy_agents.ports import AgentProviderPort, McpServerDef

database_prompt = """You are a Senior Database Engineer.
Your objective is to generate optimal SQL migrations, schema DDL, Redis/Cache configurations, and data seeding scripts.
Ensure databases are normalized where appropriate, properly indexed, and follow best practices for the chosen RDBMS (e.g., PostgreSQL).
Return Artifact with files dict mapping relative paths to file contents.


CRITICAL WORKFLOW:
1. **History Review:** Use `query_history` to recall previous architectural and contextual decisions before generating logic.
2. **Log Progress:** Call `log_activity` after significant actions.
3. **Proactive Docs:** Keep `docs/` updated via `update_documentation` when implementing major features.

"""


class DatabaseAgent:
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
            system_instruction=database_prompt,
            conversation_id=conversation_id,
            mcp_servers=self.mcp_servers,
        )
