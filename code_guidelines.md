# OpenClaw Python & Agent Coding Standards — Single Source of Truth

These standards apply to all Python services and agents generated within the repository. As a Python-only ecosystem, strict adherence to Pydantic AI, the Antigravity SDK, and Hexagonal Architecture is mandatory.

## 1. Python Code & Framework Standards

### 1.1 Language & Typing Rules
- **Framework:** Strictly adhere to `pydantic-ai` paradigms and Pydantic V2 validation rules.
- **Typing:** Provide exhaustive type hints for all function signatures, return types, and context variables. Pydantic AI relies on strict typing for schema generation.
- **Async First:** Default to asynchronous programming (`async def`) for all tool definitions, MCP interactions, and agent executions.

### 1.2 Repository Architecture
- `deps.py`: Defines dependencies using standard Python dataclasses or pydantic models.
- `agent.py`: Instantiates the `pydantic_ai.Agent` objects and defines internal tools.
- `main.py`: Handles execution, dependency instantiation, and async event loops.
- `mcp_server.py`: Centralized FastMCP server containing tools to be consumed by agents.
- `rag.py`: Houses vector store clients, embedding models, and retrieval logic.

### 1.3 Python Code Comments
- **Minimalist Approach:** Keep the code clean and concise. Do not leave too many comments. Strip all narrative comments during code generation. Only include comments when strictly necessary for complex algorithms or strict business-rule justifications.

## 2. Agent Architecture & Antigravity SDK

### 2.1 Architectural Abstraction (Ports & Adapters)
Agents must never directly import or depend on the Antigravity SDK (`google.antigravity`). Implement the Hexagonal Architecture pattern:
- **Port:** Define an `AgentProviderPort` protocol that outlines the required execution signature (e.g., `execute_agent(prompt, system_instruction, mcp_servers)`).
- **Adapter:** Implement this port using an `AntigravityAgentAdapter` which bridges the domain model into `LocalAgentConfig` and runs the SDK logic.
- **Dependency Injection:** Agents should receive the `AgentProviderPort` via their constructor or `RunContext`. This ensures agents remain completely decoupled from the LLM framework and execution environment.

### 2.2 Centralized MCP Tooling
Tools within the ecosystem (such as `openclaw` and `antigravity`) are distinct and must be isolated via standard Model Context Protocol (MCP) integrations.
- Agents should avoid declaring Python function tools directly via SDK decorators unless absolutely necessary for internal agent logic.
- Define a central FastMCP server containing shared ecosystem tools.
- Configure agents to point to this server using an `McpServerDef` list passed to the `AgentProviderPort`.
- The `AntigravityAgentAdapter` maps these into `types.McpStdioServer` and attaches them to the `LocalAgentConfig`, ensuring all tools run in isolated subprocesses and can be shared effortlessly.
- **Type Mapping:** Ensure MCP tool JSON Schemas are correctly mapped to standard Pydantic models for strict type validation during parameter passing.

### 2.3 Modular RAG Pipelines
- **Dependency Injection:** Inject vector database clients and embedding providers into the agent via `RunContext` dependencies. Do not hardcode database connections inside tools.
- **Separation of Concerns:** Keep document loading, chunking, and embedding logic entirely separate from the agent's definition. The agent should only interact with a clean `retrieve_context(query: str)` interface.
- **Structured Context:** RAG tools must return typed Pydantic models representing the retrieved chunks and their metadata.

### 2.4 Subagents and Delegation
- When defining complex pipelines, leverage the Antigravity SDK's native `CapabilitiesConfig(enable_subagents=True)`.
- Extract subagents into local Antigravity Plugin folders (`~/.gemini/config/plugins/`) so they can be invoked consistently across the entire ecosystem.

## 3. Observability & Resilience

### 3.1 Observability and Tracing
Never run AI workloads blindly.
- **SDK Lifecycle Hooks:** Implement observability through the SDK's hook system (e.g., `PostToolCallHook`, `OnToolErrorHook`). Register these hooks centrally in the `AntigravityAgentAdapter` so they apply to all agents.
- **Pydantic Tracing:** Always wrap MCP server tool endpoints with Logfire (with `logfire.span("mcp.tool_name"):`) and configure `logfire.instrument_fastapi()` or `logfire.configure()`.
- **Metrics:** Extract and log token usage from `agent.conversation.total_usage` after execution.

### 3.2 Self-Healing Mechanisms
- Rely on automated error recovery by intercepting SDK `OnToolErrorHook` events.
- Analyze the error trace and inject self-correction prompts dynamically to allow the agent up to 3 retry loops before gracefully failing.

## 4. Testing Standards

### 4.1 Unit & Integration Tests
- Use `pytest` for all unit and integration testing.
- Mock all external dependencies (adapters/secondary ports) and SDK adapters.
- Use `testcontainers-python` for real dependency containers (e.g., vector databases) in integration test suites.

### 4.2 Coverage Gate
- Minimum coverage: 80% per module.
- Enforced in CI via `pytest-cov`.
- Skippable with `[skip-test-check]` in commit message.

## 5. Documentation Standards

### 5.1 AGENTS.md
- Include AI-agent coding guidelines at the repository root.
- Cover: build/lint/test commands, architecture rules, testing patterns, and agent boundaries.

### 5.2 README.md
- One-line description.
- Architecture overview with diagrams.
- Quick start: prerequisites, install, configure, run.

## 6. Enforcement & Cross-Communication

When any agent generates or reviews code, it MUST:
1. **Model Restraint:** All agents must use Gemini 1.5 Pro or Flash models exclusively for generation and review tasks. Do not default to or configure workflows for OpenAI, DeepSeek, or other external providers.
2. Load this document (`CODING_STANDARDS.md`) at the start of its run.
3. Check each file against the relevant sections before emitting output.
4. Cite violations by section number (e.g., §1.3 — excessive/unnecessary comments, §2.1 — direct SDK import violation).
5. **Cross-reference:** if a violation spans multiple agent domains, the reviewing agent MUST flag it and reference the agent responsible for remediation.
6. **No silent compliance:** if standards pass, state explicitly: "All artifacts comply with CODING_STANDARDS.md."

### Review Pipeline Standard Flow

`code-reviewer` starts:
1. Load `CODING_STANDARDS.md`
2. Verify active model provider is Gemini 1.5.
3. For each artifact file:
    - Check 1 for Core Python/Pydantic rules
    - Check 2 for Architecture & SDK Adapter rules
    - Check 3 for Tracing & Resilience
    - Check 4 for Test artifacts
    - Check 5 for Docs artifacts
4. For each violation:
    - Record: `file:line`, section violated, evidence, agent responsible
5. Output: pass/fail with `findings[]`