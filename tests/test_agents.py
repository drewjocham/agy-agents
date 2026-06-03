import pytest
from agy_agents.ports import AgentProviderPort
from agy_agents.ba import BusinessAnalystAgent
from agy_agents.backend import BackendEngineerAgent


class MockProvider(AgentProviderPort):
    async def execute_agent(
        self, prompt, system_instruction, conversation_id=None, mcp_servers=None
    ):
        return f"Mocked response for: {prompt}", "test-conv-id"


@pytest.mark.asyncio
async def test_ba_agent():
    provider = MockProvider()
    agent = BusinessAnalystAgent(provider=provider)

    assert len(agent.mcp_servers) == 1
    assert agent.mcp_servers[0].command == "python3"

    resp, cid = await agent.run("test prompt")
    assert resp == "Mocked response for: test prompt"
    assert cid == "test-conv-id"


@pytest.mark.asyncio
async def test_backend_agent():
    provider = MockProvider()
    agent = BackendEngineerAgent(provider=provider)

    assert len(agent.mcp_servers) == 1

    resp, cid = await agent.run("build auth")
    assert resp == "Mocked response for: build auth"
