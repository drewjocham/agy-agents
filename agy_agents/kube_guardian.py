import logfire
from agy_agents.ports import AgentProviderPort


class KubeGuardianAgent:
    """
    Focus: Security, automation, K8s-native orchestration.
    Core Logic: Enforce GitOps (ArgoCD), auto-scaling (Karpenter), policy engine (Kyverno).
    Goal: Move from manual infra to self-healing, declarative environments.
    """

    def __init__(self, provider: AgentProviderPort):
        self.provider = provider
        self.system_instruction = (
            "You are the KubeGuardian agent. Your job is to analyze the infrastructure context "
            "and enforce Kubernetes GitOps, security policies, and auto-scaling best practices. "
            "Output the K8s features to Add/Remove and a GitOps-readiness score."
        )

    async def run(self, prompt: str) -> tuple[str, str]:
        with logfire.span("agent.kube_guardian", prompt=prompt):
            # We wrap the provider run
            return await self.provider.execute_agent(
                agent_name="KubeGuardian",
                system_instruction=self.system_instruction,
                prompt=prompt,
            )
