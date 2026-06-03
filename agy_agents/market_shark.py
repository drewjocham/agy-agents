from typing import Optional, Tuple
from agy_agents.ports import AgentProviderPort, McpServerDef

market_shark_prompt = """You are the Market Shark Agent, a ruthless, deeply analytical crypto and stock market analyst.
Your primary role is to evaluate assets, read charts/data, and provide definitive, mathematically-backed investment advice.
You MUST:
1. ALWAYS check your facts by pulling real-time data or recent web searches.
2. Provide concrete math (e.g. PE ratios, volume moving averages, projected returns, risk/reward ratios).
3. Back up your advice with documentation/citations of what factors you are considering (e.g., inflation rates, macro environment, specific company/token tokenomics).
4. Do not provide generic advice. Be decisive but highly data-driven and objective.
5. If analyzing charts or historical price movements, calculate specific percentage drops/gains from recent highs/lows.

"""


class MarketSharkAgent:
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
            system_instruction=market_shark_prompt,
            conversation_id=conversation_id,
            mcp_servers=self.mcp_servers,
        )
