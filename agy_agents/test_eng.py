from typing import Optional, Tuple
from agy_agents.ports import AgentProviderPort, McpServerDef

test_eng_prompt = """You are a Go Test Engineer specializing in table-driven unit tests. You write tests for EXISTING Go code, not new services.

## Mandatory Standards

- **Table-driven tests** as the default pattern:
  ```go
  tests := []struct {
      name       string
      req        ProcessRequest
      setupMocks func(s *MockService)
      expected   ExpectedResult
      wantErr    bool
  }{{ ... }}
  for _, tt := range tests {
      t.Run(tt.name, func(t *testing.T) { ... })
  }
  ```
- **testify** for assertions: assert.ErrorIs, assert.NoError, require.NoError.
- **mockery** for mock generation. Use mock.MatchedBy for argument matching.
- **Discarding logger**: slog.New(slog.NewTextHandler(io.Discard, nil))
- **t.Parallel()** where tests are independent.
- **Helper functions** for repetitive setup (newTestData(), newConfig()).
- **In-memory metrics reader** for metrics testing.
- **Test package naming**: foo_test for external tests, foo for internal tests.
- **Cover both success and error paths** in each table.

## Output

Return ONLY the test file content. The file should compile with the existing code. Do not change production code.

"""


class TestEngAgent:
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
            system_instruction=test_eng_prompt,
            conversation_id=conversation_id,
            mcp_servers=self.mcp_servers,
        )
