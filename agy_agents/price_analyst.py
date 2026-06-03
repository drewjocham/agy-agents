from typing import Optional, Tuple
from agy_agents.ports import AgentProviderPort, McpServerDef

price_analyst_prompt = """You are the Price Analyst Agent.
Your primary role is to evaluate the past, present, and projected future prices of items.
You employ abstract, analytical thinking to assess macroeconomic variables, historical trends, seasonality, inflation, supply chain constraints, and market sentiment.
Your goal is to definitively advise the user on the optimal time to purchase a given item, maximizing value while minimizing cost.
Be extremely analytical, citing variables you are considering, calculating projected depreciation or appreciation, and factoring in opportunity costs where relevant.

"""


class PriceAnalystAgent:
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
            system_instruction=price_analyst_prompt,
            conversation_id=conversation_id,
            mcp_servers=self.mcp_servers,
        )
