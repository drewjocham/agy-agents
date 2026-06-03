# Antigravity SDK Best Practices & Guidelines

## 1. Architectural Abstraction (Ports & Adapters)
Agents should **never** directly import or depend on the Antigravity SDK (`google.antigravity`). Instead, implement the Hexagonal Architecture pattern:
- **Port:** Define an `AgentProviderPort` protocol that outlines the required execution signature (e.g., `execute_agent(prompt, system_instruction, mcp_servers)`).
- **Adapter:** Implement this port using `AntigravityAgentAdapter` which bridges the domain model into `LocalAgentConfig` and runs the SDK logic.
- **Dependency Injection:** Agents should receive the `AgentProviderPort` via their constructor.

This ensures agents remain completely uncoupled from the LLM framework and execution environment.

## 2. Centralized MCP Tooling
Agents should avoid declaring Python function tools directly via SDK decorators unless absolutely necessary.
- Define a central **FastMCP server** (e.g., `mcp_server.py`) containing all tools.
- Configure agents to point to this server using an `McpServerDef` list passed to the `AgentProviderPort`.
- The `AntigravityAgentAdapter` will map these into `types.McpStdioServer` and attach them to the `LocalAgentConfig`.
- This ensures all tools run in isolated subprocesses and can be shared effortlessly across the entire agent collective.

## 3. Observability and Tracing
Never run AI workloads blindly.
- **SDK Lifecycle Hooks:** Implement observability through the SDK's hook system (e.g., `PostToolCallHook`, `OnToolErrorHook`). Register these hooks centrally in the `AntigravityAgentAdapter` so they apply to all agents.
- **Pydantic Tracing:** Always wrap MCP server tool endpoints with Logfire (`with logfire.span("mcp.tool_name"):`) and configure `logfire.instrument_fastapi()` or `logfire.configure()`.
- **Metrics:** Extract and log token usage from `agent.conversation.total_usage` after execution.

## 4. Self-Healing Mechanisms
- Rely on automated error recovery by intercepting SDK `OnToolErrorHook` events.
- Analyze the error trace and inject self-correction prompts dynamically to allow the agent up to 3 retry loops before gracefully failing.

## 5. Subagents and Delegation
- When defining complex pipelines, leverage the SDK's native `CapabilitiesConfig(enable_subagents=True)`.
- Extract subagents into local Antigravity Plugin folders (`~/.gemini/config/plugins/`) so they can be invoked across the entire ecosystem consistently.
