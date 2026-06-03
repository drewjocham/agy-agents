import pytest
import subprocess
from agy_agents.mcp_server import (
    define_user_stories,
    map_event_triggers,
    scaffold_go_service,
    run_agent_by_name,
)


def test_define_user_stories():
    res = define_user_stories("User needs to login")
    assert len(res) == 1
    assert res[0]["description"] == "User needs to login"
    assert res[0]["story_id"] == "EXAMPLE-01"


def test_map_event_triggers():
    res = map_event_triggers("EXAMPLE-01", "Given user...")
    assert len(res) == 1
    assert res[0]["name"] == "example.Triggered"


def test_scaffold_go_service():
    res = scaffold_go_service("auth", "users")
    assert "cmd/server/main.go" in res
    assert "auth" in res["cmd/server/main.go"]
    assert "go.mod" in res
    assert "internal/domain/auth.go" in res


@pytest.mark.asyncio
async def test_run_agent_by_name_local():
    result = run_agent_by_name("architect", "design auth", run_on_gks=False)
    assert "[LOCAL EXECUTION]" in result
    assert "architect" in result


@pytest.mark.asyncio
async def test_run_agent_by_name_gks_success(mocker):
    # Mock config existence
    mocker.patch("agy_agents.mcp_server.Path.exists", return_value=True)

    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value.stdout = '{"status": "success", "data": "auth designed"}'

    result = run_agent_by_name("architect", "design auth", run_on_gks=True)
    assert "success" in result
    assert "auth designed" in result
    # It should be formatted JSON
    assert result.startswith("{")


@pytest.mark.asyncio
async def test_run_agent_by_name_gks_raw_fallback(mocker):
    mocker.patch("agy_agents.mcp_server.Path.exists", return_value=True)

    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value.stdout = "Raw response from GKS without JSON wrapping"

    result = run_agent_by_name("architect", "design auth", run_on_gks=True)
    assert result == "Raw response from GKS without JSON wrapping"


@pytest.mark.asyncio
async def test_run_agent_by_name_gks_error_code(mocker):
    mocker.patch("agy_agents.mcp_server.Path.exists", return_value=True)

    mock_run = mocker.patch("subprocess.run")
    mock_run.side_effect = subprocess.CalledProcessError(
        returncode=1,
        cmd=["openclaw"],
        output="Command failed",
        stderr="Connection refused",
    )

    result = run_agent_by_name("architect", "design auth", run_on_gks=True)
    assert "GatewayTransportError" in result
    assert "Connection refused" in result


@pytest.mark.asyncio
async def test_run_agent_by_name_gks_missing_config(mocker):
    mocker.patch("agy_agents.mcp_server.Path.exists", return_value=False)

    result = run_agent_by_name("architect", "design auth", run_on_gks=True)
    assert "Error: Remote GKS is not configured" in result
    assert "~/.openclaw/openclaw.json" in result
