import sys
from unittest.mock import MagicMock

google_mock = MagicMock()
types_mock = MagicMock()
hooks_mock = MagicMock()


# We need the Hook base classes to be actual types so we can subclass them
class MockHook:
    async def run(self, context, data):
        pass


google_mock.antigravity = MagicMock()
google_mock.antigravity.types = types_mock
google_mock.antigravity.hooks = hooks_mock
google_mock.antigravity.hooks.hooks = MagicMock()
google_mock.antigravity.hooks.hooks.PostToolCallHook = MockHook
google_mock.antigravity.hooks.hooks.OnToolErrorHook = MockHook
google_mock.antigravity.hooks.hooks.OnCompactionHook = MockHook


class MockConfig:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


types_mock.McpStdioServer = MockConfig
types_mock.CapabilitiesConfig = MockConfig

sys.modules["google"] = google_mock
sys.modules["google.antigravity"] = google_mock.antigravity
sys.modules["google.antigravity.types"] = types_mock
sys.modules["google.antigravity.hooks"] = hooks_mock
sys.modules["google.antigravity.hooks.hooks"] = google_mock.antigravity.hooks.hooks
sys.modules["google.antigravity.connections"] = MagicMock()

local_conn_mock = MagicMock()
local_conn_mock.LocalAgentConfig = MockConfig
sys.modules["google.antigravity.connections.local"] = local_conn_mock

logfire_mock = MagicMock()


# logfire.span acts as a context manager
class MockSpan:
    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


logfire_mock.span = MockSpan
sys.modules["logfire"] = logfire_mock
