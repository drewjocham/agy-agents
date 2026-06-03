from typing import Optional, Tuple
from agy_agents.ports import AgentProviderPort, McpServerDef

current_events_prompt = """You are a Current Events Agent and a history buff.
Your job is to provide context on current events, blending modern news with historical perspectives.

"""


class CurrentEventsAgent:
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
            system_instruction=current_events_prompt,
            conversation_id=conversation_id,
            mcp_servers=self.mcp_servers,
        )
