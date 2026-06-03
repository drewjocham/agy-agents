import asyncio
import logfire
from typing import Tuple

from agy_agents.ports import AgentProviderPort
from agy_agents.architect import ArchitectAgent
from agy_agents.library_curator import LibraryCuratorAgent
from agy_agents.kube_guardian import KubeGuardianAgent


class CouncilOrchestratorAgent:
    """
    Triggers the strict Council Review multi-agent system.
    Spins up Architect, Library Curator, and Kube Guardian in parallel,
    then synthesizes their output into a Unified Review.
    """

    def __init__(self, provider: AgentProviderPort):
        self.provider = provider
        self.system_instruction = (
            "You are the Council Orchestrator. You receive the independent audits from the "
            "Architect, Library Curator, and Kube Guardian. Your job is to synthesize these into a "
            "Unified Review Output Format and create an actionable remediation plan."
        )

    async def run(self, prompt: str) -> Tuple[str, str]:
        with logfire.span("agent.council_orchestrator", prompt=prompt):
            # 1. Instantiate the parallel sub-agents
            architect = ArchitectAgent(self.provider)
            curator = LibraryCuratorAgent(self.provider)
            guardian = KubeGuardianAgent(self.provider)

            # 2. Fan-out tasks concurrently
            arch_task = architect.run(f"Directional Audit. Context: {prompt}")
            curator_task = curator.run(
                f"The 'Wheel' Audit (dependencies). Context: {prompt}"
            )
            guard_task = guardian.run(f"Infrastructure Hardening. Context: {prompt}")

            results = await asyncio.gather(arch_task, curator_task, guard_task)

            # Extract the string responses (ignoring conversation IDs)
            arch_resp = results[0][0]
            curator_resp = results[1][0]
            guard_resp = results[2][0]

            # 3. Fan-in and synthesize
            synthesis_prompt = (
                f"Original Context: {prompt}\n\n"
                f"=== Phase 1: Architect Audit ===\n{arch_resp}\n\n"
                f"=== Phase 2: Library Curator Audit ===\n{curator_resp}\n\n"
                f"=== Phase 3: Kube Guardian Audit ===\n{guard_resp}\n\n"
                "Synthesize this into a Unified Review Output Format and Actionable Remediation Plan."
            )

            return await self.provider.execute_agent(
                agent_name="CouncilOrchestrator",
                system_instruction=self.system_instruction,
                prompt=synthesis_prompt,
            )
