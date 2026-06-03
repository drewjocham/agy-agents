from typing import Optional, Tuple
from agy_agents.ports import AgentProviderPort, McpServerDef

weather_prompt = """You are a Weather Agent.
Your job is to provide accurate weather forecasts, climate summaries, and travel-related weather advice.

"""


class WeatherAgent:
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
            system_instruction=weather_prompt,
            conversation_id=conversation_id,
            mcp_servers=self.mcp_servers,
        )
