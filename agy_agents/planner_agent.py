from typing import Optional, Tuple
from agy_agents.ports import AgentProviderPort, McpServerDef

planner_agent_prompt = """You are a Planner Agent. Your job is to decompose high-level goals into a structured,
executable multi-step plan. For each step, identify the required agent capability,
a detailed prompt for that agent, and any task dependencies.

Analyze the goal carefully and break it into the minimal number of discrete steps needed.
Each step must be achievable by a single agent capability.
Dependencies define order: if step B depends on step A's output, list A's task ID in B's dependencies.

"""


class PlannerAgentAgent:
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
            system_instruction=planner_agent_prompt,
            conversation_id=conversation_id,
            mcp_servers=self.mcp_servers,
        )
