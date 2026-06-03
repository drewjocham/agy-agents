from typing import Optional, Tuple
from agy_agents.ports import AgentProviderPort, McpServerDef

ba_prompt = """You are a Senior Business Analyst Agent focused on **Domain-Driven Design (DDD)**.

Your job is to convert raw requirements into:
1. **User Stories** in the standard "As a... I want... so that..." form, each with Gherkin acceptance criteria (Given/When/Then).
2. **Bounded Contexts** — name them, define the ubiquitous language inside each, and identify the integration patterns between them.
3. **Event Triggers** — the domain events that downstream backend services and QA automation will key off of.

## Conventions
- Story IDs follow `BC-NN` (e.g., `ORDERS-01`)
- Event names are past-tense and namespaced: `orders.OrderPlaced`, `billing.PaymentCaptured`

## Tools
You have access to MCP tools provided by your environment. Use them to analyze and extract logic.
"""


class BusinessAnalystAgent:
    """
    Hexagonal Agent: Isolated from the LLM provider.
    Relies entirely on the injected AgentProviderPort and consumes tools via MCP.
    """

    def __init__(self, provider: AgentProviderPort):
        self.provider = provider
        # Assuming we have an MCP server that provides BA tools (e.g., `define_user_stories`, `map_event_triggers`)
        # If we had a real fastMCP server script, we'd reference it here.
        self.mcp_servers = [
            McpServerDef(command="python3", args=["-m", "agy_agents.mcp_server"])
        ]

    async def run(
        self, prompt: str, conversation_id: Optional[str] = None
    ) -> Tuple[str, str]:
        return await self.provider.execute_agent(
            prompt=prompt,
            system_instruction=ba_prompt,
            conversation_id=conversation_id,
            mcp_servers=self.mcp_servers,
        )
