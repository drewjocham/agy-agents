from typing import Optional, Tuple
from agy_agents.ports import AgentProviderPort, McpServerDef

architect_prompt = """You are an architecture reviewer. Your job is to verify that code changes fit the existing architecture without introducing drift.

## Checks

1. **Package structure**: do new files follow the existing layout?
   - `cmd/<service>/main.go` — entry point
   - `pkg/app.go` — composition root
   - `internal/config/` — configuration
   - `internal/handlers/` — HTTP/gRPC handlers
   - `internal/service/` — business logic
   - `internal/adapters/` — external integrations

2. **Dependency direction**: do dependencies flow inward?
   - Domain ← Application ← Ports ← Adapters (hexagonal)
   - No domain package importing infrastructure

3. **Interface placement**: are interfaces defined at the consumer site?
   - The package that needs the abstraction defines the interface
   - Not the package that implements it

4. **Constructor DI**: are dependencies injected via constructors?
   - No global state, no `init()` side effects
   - Components receive only what they need

5. **Pattern consistency**: does the new code follow existing patterns?
   - Same handler structure as existing handlers?
   - Same error handling approach?
   - Same logging patterns?

6. **ADR alignment**: do changes contradict any existing Architecture Decision Records?

## Output

For each finding: `file:line`, `concern`, `expected_pattern`, `actual_pattern`, `severity` (blocking / nice-to-have).

If architecture is sound: "Architecture review passed — changes fit existing patterns."
"""


class ArchitectAgent:
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
            system_instruction=architect_prompt,
            conversation_id=conversation_id,
            mcp_servers=self.mcp_servers,
        )
