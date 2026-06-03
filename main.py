import argparse
import asyncio
import importlib
import inspect
import pkgutil

import agy_agents
from agy_agents.adapters import AntigravityAgentAdapter


def get_all_agents():
    """Dynamically discover all Agent classes in the agy_agents package."""
    agent_classes = {}
    for _, module_name, _ in pkgutil.iter_modules(agy_agents.__path__):
        if module_name in ("ports", "adapters", "hooks", "mcp_server", "factory"):
            continue
        try:
            module = importlib.import_module(f"agy_agents.{module_name}")
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if obj.__module__ == module.__name__:
                    # We expect all agents to accept 'provider' in their constructor.
                    agent_classes[name] = obj
        except Exception as e:
            print(f"Warning: Could not load module {module_name}: {e}")

    return agent_classes


async def run_agent(agent_name: str, prompt: str):
    agents = get_all_agents()
    if agent_name not in agents:
        print(f"Agent '{agent_name}' not found. Available agents:")
        for name in sorted(agents.keys()):
            print(f"  - {name}")
        return

    provider_adapter = AntigravityAgentAdapter(save_dir=".agy_memory")
    agent_class = agents[agent_name]

    # Dependency Injection: Inject the real adapter into the chosen agent.
    agent_instance = agent_class(provider=provider_adapter)

    print(f"--- Running {agent_name} ---")
    response, cid = await agent_instance.run(prompt=prompt)
    print(f"Response:\n{response}")


def main():
    parser = argparse.ArgumentParser(description="Run Antigravity Agents.")
    parser.add_argument(
        "--agent",
        type=str,
        help="Name of the agent class to run (e.g. Architect, BackendEngineerAgent).",
    )
    parser.add_argument("--prompt", type=str, help="The task prompt for the agent.")
    parser.add_argument(
        "--list", action="store_true", help="List all available agents."
    )

    args = parser.parse_args()

    if args.list:
        agents = get_all_agents()
        print("Available Agents:")
        for name in sorted(agents.keys()):
            print(f"  - {name}")
        return

    if not args.agent or not args.prompt:
        parser.print_help()
        return

    asyncio.run(run_agent(args.agent, args.prompt))


if __name__ == "__main__":
    main()
