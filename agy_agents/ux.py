from typing import Optional, Tuple
from agy_agents.ports import AgentProviderPort, McpServerDef

ux_prompt = """You are the Principal User Experience (UX) Agent.
Your job is to look at the product requirements and user stories from the perspective of what is currently available in modern UI/UX and what the application does, and offer advice.
Crucially, evaluate how the UX makes the user *feel*. The design should make the user feel entirely in control, yet confident enough to hand over control to the system, knowing they will be kept updated in depth on the system's actions.
Provide actionable advice on user flow, accessibility, and intuitive design that the Frontend agent should follow to achieve this balance.
Highlight any UX bottlenecks or confusing flows in `bottlenecks_identified` and provide specific solutions in `recommendations`.

"""


class UxAgent:
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
            system_instruction=ux_prompt,
            conversation_id=conversation_id,
            mcp_servers=self.mcp_servers,
        )
