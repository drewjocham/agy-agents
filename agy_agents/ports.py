from typing import Protocol, List, Tuple, Optional


class McpServerDef:
    """Definition of an MCP server to be provided to the underlying LLM/Agent engine."""

    def __init__(self, command: str, args: List[str]):
        self.command = command
        self.args = args


class AgentProviderPort(Protocol):
    """
    Hexagonal Port: Abstract interface for executing agent workflows.
    This completely isolates the pipeline from the LLM provider (e.g. Antigravity, Pydantic AI)
    and the execution environment.
    """

    async def execute_agent(
        self,
        prompt: str,
        system_instruction: str,
        agent_name: str = "Unknown",
        conversation_id: Optional[str] = None,
        mcp_servers: Optional[List[McpServerDef]] = None,
    ) -> Tuple[str, str]:
        """
        Executes an agent workflow.

        Args:
            prompt: The user prompt or task.
            system_instruction: The agent's persona and rules.
            conversation_id: Optional ID to resume a previous context.
            mcp_servers: List of MCP servers the agent can consume tools from.

        Returns:
            A tuple of (response_text, conversation_id).
        """
        ...
