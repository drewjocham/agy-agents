from google.antigravity import Agent
from agy_agents.factory import create_agent_config

REVIEW_BLUEPRINT_SUMMARY = (
    "Event-driven hexagonal services, gRPC-enabled, CloudEvents-compliant."
)
REVIEW_BOUNDED_CONTEXTS = ["payments", "notifications", "users"]
REVIEW_STRICT_MODE = True


def _build_review_prompt() -> str:
    strict_clause = (
        "CRITICAL: Strict mode is ENABLED. Any warning must be treated as a hard failure."
        if REVIEW_STRICT_MODE
        else "NOTE: Strict mode is disabled. Provide warnings for minor infractions."
    )
    bounded = ", ".join(REVIEW_BOUNDED_CONTEXTS)
    return f"""You represent the final governance layer. Your role is to act as a **Qualified Security Assessor (QSA)**.
You analyze artifacts (Go code, Terraform, Test results) to ensure they meet production-readiness standards. You perform risk-based assessments of the entire system state before milestone approval.

{strict_clause}

### 1. Security (Zero-Trust)
* mTLS must be explicitly enabled everywhere.
* Absolutely NO hardcoded secrets, tokens, or sensitive data in any artifact.

### 2. Architecture Constraints
* Artifacts must perfectly match the approved Event-Driven Blueprint: {REVIEW_BLUEPRINT_SUMMARY}
* Artifacts must strictly adhere to these Bounded Contexts: {bounded}

### 3. Infrastructure (Terraform)
* NO 'Destroy' actions permitted in production plans.
* ALL modules must be version-pinned (no 'latest' or unversioned branches).

### Output Instructions
Populate your output exactly according to the requested schema. Provide specific line numbers or file names where violations occur to make your review actionable."""


review_prompt = _build_review_prompt()


async def run_review(conversation_id: str = None, prompt: str = "Perform code review."):
    """Runs the Review Agent."""
    config = create_agent_config(
        system_instruction=review_prompt, conversation_id=conversation_id
    )

    async with Agent(config) as agent:
        response = await agent.chat(prompt)
        print(f"Review Agent Output: {await response.text()}")

        usage = agent.conversation.total_usage
        print(
            f"Review Agent Token Usage - Prompt: {usage.prompt_token_count}, Total: {usage.total_token_count}"
        )
        return agent.conversation_id
