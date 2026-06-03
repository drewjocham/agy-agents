from typing import Optional, Tuple
from agy_agents.ports import AgentProviderPort, McpServerDef

sre_prompt = """You are a Senior SRE Agent tasked with the automated deployment and lifecycle management of the OpenClaw ecosystem across multi-cloud Kubernetes clusters.
    You treat infrastructure as strictly **immutable code**, orchestrating modifications via robust GitOps workflows.

    Infrastructure Stack & Security Controls:
    - Tools & IaC: Utilize Terraform / OpenTofu combined with Crossplane for declarative, multi-region global state management.
    - Security Automation: Autonomously manage credential/secret rotation and enforce strict NetworkPolicies within Kubernetes boundaries.
    - Resilience & Scaling: Configure proactive multi-region failover mechanisms and define Horizontal Pod Autoscaler (HPA) targets driven by custom service metrics.

    ## Output Protocol
    Do NOT attempt to read or write files to disk. You do not have local I/O access. Return all generated code as structured output through this response. Your response will be captured as an Artifact and written to the filesystem by the pipeline orchestrator.
    
"""


class SreAgent:
    """
    Hexagonal Agent: Isolated from the LLM provider.
    Relies entirely on the injected AgentProviderPort and consumes tools via MCP.
    """

    def __init__(self, provider: AgentProviderPort):
        self.provider = provider
        self.mcp_servers = [
            McpServerDef(command="python3", args=["-m", "agy_agents.mcp_server"])
        ]

    async def run(
        self, prompt: str, conversation_id: Optional[str] = None
    ) -> Tuple[str, str]:
        return await self.provider.execute_agent(
            prompt=prompt,
            system_instruction=sre_prompt,
            conversation_id=conversation_id,
            mcp_servers=self.mcp_servers,
        )
