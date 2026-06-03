import pytest
from unittest.mock import AsyncMock
from agy_agents.adapters import AntigravityAgentAdapter
from agy_agents.ports import McpServerDef


@pytest.mark.asyncio
async def test_antigravity_agent_adapter(mocker):
    # Mock the google.antigravity Agent context manager to avoid network calls
    mock_agent_instance = AsyncMock()
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value="Agent response")

    mock_agent_instance.chat = AsyncMock(return_value=mock_response)
    mock_agent_instance.conversation_id = "test-123"

    # Setup token usage mock
    mock_usage = mocker.MagicMock()
    mock_usage.prompt_token_count = 10
    mock_usage.total_token_count = 20
    mock_agent_instance.conversation.total_usage = mock_usage

    # Mock the __aenter__ to return our mock_agent_instance
    mock_agent_class = mocker.patch("agy_agents.adapters.Agent")
    mock_agent_class.return_value.__aenter__.return_value = mock_agent_instance

    adapter = AntigravityAgentAdapter(save_dir=".test_memory")

    mcp_servers = [McpServerDef(command="python3", args=["-m", "dummy"])]

    response, cid = await adapter.execute_agent(
        prompt="Hello",
        system_instruction="You are a test agent",
        conversation_id="conv-old",
        mcp_servers=mcp_servers,
    )

    assert response == "Agent response"
    assert cid == "test-123"

    # Verify Agent was instantiated
    mock_agent_class.assert_called_once()
    config_passed = mock_agent_class.call_args[0][0]

    assert config_passed.system_instruction == "You are a test agent"
    assert config_passed.conversation_id == "conv-old"
    assert config_passed.save_dir == ".test_memory"
    assert len(config_passed.mcp_servers) == 1
    assert config_passed.mcp_servers[0].command == "python3"
