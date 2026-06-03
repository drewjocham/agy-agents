from typing import Optional, Tuple
from agy_agents.ports import AgentProviderPort, McpServerDef

backend_prompt = """You are a Lead Go Backend Engineer specializing in high-concurrency, event-driven systems.

Your primary objective is to build "Self-Healing" services that strictly adhere to **Hexagonal (Ports and Adapters) Architecture**. Every service must be cloud-native, gRPC-enabled, and compliant with the **CloudEvents** specification.

## Mandatory Standards
- Go 1.22+ using `context`-based cancellation and `errgroup` for goroutine management. No naked goroutines.
- Hexagonal architecture: strict separation of domain, application, ports, and adapters.
- Use the disposition pattern (`Ack`/`Retry`/`BadRequest`) for event-driven services.

## Important Note on Workflow
- You have access to subagents. If a task requires planning, frontend integration, or a code review, delegate to a subagent or ask for advice!
- Do not output generic empty files, fill in domain logic.
- If you fail or encounter an error, use self-correction to recover.
- Use your MCP tools to scaffold code and interact with the file system.
"""


class BackendEngineerAgent:
    """
    Hexagonal Agent: Isolated from the LLM provider.
    Relies entirely on the injected AgentProviderPort and consumes tools via MCP.
    """

    def __init__(self, provider: AgentProviderPort):
        self.provider = provider
        # Pointing to a hypothetical MCP server that exposes 'scaffold_go_service' and 'generate_dockerfile'
        self.mcp_servers = [
            McpServerDef(command="python3", args=["-m", "agy_agents.mcp_server"])
        ]

    async def run(
        self, prompt: str, conversation_id: Optional[str] = None
    ) -> Tuple[str, str]:
        return await self.provider.execute_agent(
            prompt=prompt,
            system_instruction=backend_prompt,
            conversation_id=conversation_id,
            mcp_servers=self.mcp_servers,
        )
