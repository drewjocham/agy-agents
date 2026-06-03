from typing import Optional, Tuple
from agy_agents.ports import AgentProviderPort, McpServerDef

asymmetric_reviewer_prompt = """You are an Asymmetric Reviewer Agent.
    You are an expert in law and corporate tricks. Your goal is to help save money when traveling, when done correctly,
    by finding loopholes and exploiting asymmetric information.

"""


class AsymmetricReviewerAgent:
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
            system_instruction=asymmetric_reviewer_prompt,
            conversation_id=conversation_id,
            mcp_servers=self.mcp_servers,
        )
