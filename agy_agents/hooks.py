import logfire
from typing import Any, Optional

from google.antigravity.hooks import hooks


class TelemetryHook(hooks.PostToolCallHook):
    """Tracks and logs tool execution metrics for observability."""

    async def run(self, context: hooks.HookContext, data: Any) -> None:
        logfire.info(
            "Tool executed",
            tool_name=context.tool_name,
            data_size=len(str(data)) if data else 0,
        )


class ErrorRecoveryHook(hooks.OnToolErrorHook):
    """Provides self-healing capabilities by catching errors and guiding the agent to recover."""

    async def run(self, context: hooks.HookContext, data: Exception) -> Optional[str]:
        logfire.error(
            "Tool failed (Self-Healing Triggered)",
            tool_name=context.tool_name,
            error=str(data),
        )
        return (
            f"[Error: Tool {context.tool_name} failed with '{data}'. "
            "Please review the arguments you passed. "
            "If you cannot proceed, invoke a subagent for advice or to hand over the task.]"
        )


class ContextCompactionHook(hooks.OnCompactionHook):
    """Logs when context is compressed, allowing tracing of context window management."""

    async def run(self, context: hooks.HookContext, data: Any) -> None:
        logfire.info("Context compaction triggered", reason="Saving space")


def get_standard_hooks() -> list:
    return [
        TelemetryHook(),
        ErrorRecoveryHook(),
        ContextCompactionHook(),
    ]
