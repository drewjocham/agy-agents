import asyncio
from agy_agents.adapters import AntigravityAgentAdapter
from agy_agents.ba import BusinessAnalystAgent
from agy_agents.backend import BackendEngineerAgent


async def main():
    # Instantiate the Adapter (the concrete LLM provider implementation)
    provider_adapter = AntigravityAgentAdapter(save_dir=".agy_memory")

    # Inject the Adapter into the Agents
    ba_agent = BusinessAnalystAgent(provider=provider_adapter)
    backend_agent = BackendEngineerAgent(provider=provider_adapter)

    print("--- Running BA Agent ---")
    ba_response, ba_cid = await ba_agent.run(
        prompt="Analyze the requirements for a user authentication system."
    )
    print(f"Response:\n{ba_response}")

    print("\n--- Running Backend Agent ---")
    be_response, be_cid = await backend_agent.run(
        prompt="Build the user authentication system based on the analysis."
    )
    print(f"Response:\n{be_response}")


if __name__ == "__main__":
    # In a real scenario the Antigravity SDK handles the MCP subprocess lifecycle.
    asyncio.run(main())
