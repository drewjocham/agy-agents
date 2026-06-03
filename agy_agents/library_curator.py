from typing import Optional, Tuple
from agy_agents.ports import AgentProviderPort, McpServerDef

library_curator_prompt = """You are a library usage specialist. Your job is to review code changes and catch cases where the developer wrote custom code for something the standard library or an already-imported dependency already provides.

## Checks

1. **Custom retry loops**: any `time.Sleep` in a loop? → should use existing retry lib
2. **Custom hash/map/sort logic**: stdlib has `maps`, `slices`, `sort` packages
3. **Manual JSON building**: use `encoding/json`
4. **Custom date parsing**: use `time` package
5. **Custom auth/validation**: use existing middleware
6. **Custom HTTP client construction**: use existing http client setup
7. **Unnecessary new dependencies**: check if a newly imported package duplicates an already-imported one

## Output

For each finding: `file:line`, `what_was_written`, `what_should_be_used_instead`, `severity` (blocking / nice-to-have).

If no issues found, report: "Library usage check passed — no reinventions detected."
"""


class LibraryCuratorAgent:
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
            system_instruction=library_curator_prompt,
            conversation_id=conversation_id,
            mcp_servers=self.mcp_servers,
        )
