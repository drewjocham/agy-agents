import os
import logging
from google.antigravity.connections.local import LocalAgentConfig
from google.antigravity import types

from agy_agents.hooks import get_standard_hooks

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def create_agent_config(
    system_instruction: str, save_dir: str = ".agy_memory", conversation_id: str = None
) -> LocalAgentConfig:
    """
    Creates a standardized Antigravity agent configuration with:
    - Persistence (conversation saving/loading)
    - Subagents enabled (for advice, checking work, and handover)
    - Hooks (Observability, Metrics, Tracing, Self-Healing)
    """
    os.makedirs(save_dir, exist_ok=True)

    return LocalAgentConfig(
        system_instruction=system_instruction,
        save_dir=save_dir,
        conversation_id=conversation_id,
        capabilities=types.CapabilitiesConfig(
            enable_subagents=True,
        ),
        hooks=get_standard_hooks(),
    )
