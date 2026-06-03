from typing import Optional, Tuple
from agy_agents.ports import AgentProviderPort, McpServerDef

docs_prompt = """You are a Technical Writer and API Documentation Specialist.
Your objective is to generate accurate OpenAPI/Swagger specifications, comprehensive README files, and detailed API reference docs from the provided technical specifications and code artifacts.
Return Artifact with files dict mapping relative paths to file contents.

"""


class DocsAgent:
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
            system_instruction=docs_prompt,
            conversation_id=conversation_id,
            mcp_servers=self.mcp_servers,
        )
