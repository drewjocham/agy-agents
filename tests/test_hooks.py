import pytest
import logfire
from unittest.mock import Mock

from agy_agents.hooks import (
    TelemetryHook,
    ErrorRecoveryHook,
    ContextCompactionHook,
    get_standard_hooks,
)


class MockHookContext:
    def __init__(self, tool_name):
        self.tool_name = tool_name


@pytest.mark.asyncio
async def test_telemetry_hook(mocker):
    # reset mock before test if needed
    logfire.info = Mock()
    hook = TelemetryHook()
    ctx = MockHookContext("my_tool")

    await hook.run(ctx, {"foo": "bar"})

    logfire.info.assert_called_once_with(
        "Tool executed", tool_name="my_tool", data_size=14
    )


@pytest.mark.asyncio
async def test_error_recovery_hook(mocker):
    logfire.error = Mock()
    hook = ErrorRecoveryHook()
    ctx = MockHookContext("broken_tool")
    err = ValueError("Something went wrong")

    result = await hook.run(ctx, err)

    logfire.error.assert_called_once_with(
        "Tool failed (Self-Healing Triggered)",
        tool_name="broken_tool",
        error="Something went wrong",
    )
    assert "broken_tool failed" in result
    assert "Something went wrong" in result
    assert "Please review the arguments" in result


@pytest.mark.asyncio
async def test_context_compaction_hook(mocker):
    logfire.info = Mock()
    hook = ContextCompactionHook()
    ctx = MockHookContext("compactor")

    await hook.run(ctx, None)

    logfire.info.assert_called_once_with(
        "Context compaction triggered", reason="Saving space"
    )


def test_get_standard_hooks():
    hooks = get_standard_hooks()
    assert len(hooks) == 3
    assert any(isinstance(h, TelemetryHook) for h in hooks)
