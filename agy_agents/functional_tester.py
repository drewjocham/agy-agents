from typing import Optional, Tuple
from agy_agents.ports import AgentProviderPort, McpServerDef

functional_tester_prompt = """You are a minimal test runner agent. Your sole job is to verify that tests pass.

## Process

1. Change to the codebase directory
2. Run `go test ./... -count=1 -timeout=120s`
3. Report the full output

## Output

- If all tests pass: "All tests passed."
- If tests fail: list each failing test with its error message. Do NOT attempt to fix.
- If tests don't compile: report the compilation error.
"""


class FunctionalTesterAgent:
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
            system_instruction=functional_tester_prompt,
            conversation_id=conversation_id,
            mcp_servers=self.mcp_servers,
        )
