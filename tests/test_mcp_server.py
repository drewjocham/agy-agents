from agy_agents.mcp_server import (
    define_user_stories,
    map_event_triggers,
    scaffold_go_service,
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
