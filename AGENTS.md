# OpenClaw Ecosystem: AGENTS.md

**Notice to all AI Agents:** You are operating in a Python-exclusive repository powered by the `pydantic-ai` framework. You must read and adhere to these directives before executing any tasks, modifying code, or generating artifacts.

## 1. Core Operating Constraints

* **Model Restraint:** You must use **Gemini 1.5 Pro or Flash** models exclusively for all generation, evaluation, and review tasks. Do not configure workflows, agents, or evaluators to use OpenAI or DeepSeek.
* **Architectural Isolation:** Do not import the Antigravity SDK (`google.antigravity`) directly into agent logic. Use Hexagonal Architecture (Ports and Adapters) and inject an `AgentProviderPort`.
* **Tooling Boundaries:** "Antigravity" and "OpenClaw" are distinct tools. They must be integrated via isolated Model Context Protocol (MCP) servers, not direct Python function decorators unless internal to the agent's immediate logic.
* **Clean Shutdowns:** Ensure clean shutdown sequences by intercepting OS signals (`signal.SIGINT`, `signal.SIGTERM`) and gracefully terminating servers and background workers using `asyncio` context cancellations with reasonable timeouts.

## 2. Autonomous Native Turnaround Loop

You are designed to act on your own and manage turnaround checks autonomously. You are bound by a strict verify-then-commit loop executed directly within the host environment.

1.  **Modify:** When you write or modify code, you must immediately transition to the VERIFY state.
2.  **Verify:** You MUST execute turnaround hooks to test the project correctly every time. Run `pytest` for tests and your configured linter (`ruff` or `mypy`).
3.  **Analyze:** * If the tools return a non-zero exit code or error trace, you are in a FAILED state.
    * You MUST NOT ask the user for help.
    * You MUST analyze the `stderr`/`stdout` trace, formulate a fix, apply it, and return to Step 2.
    * You have a maximum of **3 autonomous retry loops**. If you fail 3 times, output the error trace to the user and halt.
4.  **Complete:** You may only declare the task successful and return control to the user if the turnaround hooks return absolute success (exit code 0).

**Strict Testing Constraints:**
* Never write untyped Python code. Always enforce strict typing.
* Never mock an implementation just to pass a test; write the actual logic.
* Generate mocks for external interfaces using `pytest-mock`.

## 3. Native Execution & Optional Delegation

You are fundamentally designed to execute tasks natively and autonomously, but you may utilize external worker pools when necessary.

1.  **Analyze Requirements:** Determine which domains are involved in the current task.
2.  **Execute Natively:** By default, generate the necessary code autonomously, running the turnaround loop entirely within your native execution context.
3.  **Optional OpenClaw Delegation:** If a task requires highly specialized delegation, invoke the OpenClaw agent collective as a worker pool via available MCP tools.
4.  **Integrate & Validate:** Whether the code was generated natively or retrieved from a worker agent, you must perform the final integration into the repository and guarantee it passes the standard test and linting gates.

## 4. AI-Powered Evaluation Requirements

You are strictly required to build observability and evaluation into every AI-driven feature you implement. **Do not merge AI features without automated grading.**

### 4.1 Mandatory Implementation Steps
1.  **Instrument Everything:** Call `logfire.instrument_pydantic_ai()` before initializing any agent.
2.  **Define an Evaluator:** For every new AI capability, write a custom evaluator inheriting from `pydantic_evals.evaluators.Evaluator`.
3.  **Assert Quality:** Do not use simple boolean checks for complex outputs. Use `LLMJudge` for qualitative grading or custom `@dataclass` evaluators for deterministic JSON structure validation.

```python
from pydantic_ai import Agent
from pydantic_evals.evaluators import LLMJudge
from pydantic_evals.online_capability import OnlineEvaluation
import logfire

logfire.configure()
logfire.instrument_pydantic_ai()

judge = LLMJudge(
    rubric='The answer is factually correct and directly addresses the question.',
    model='gemini-1.5-flash',
    include_input=True,
)

agent = Agent(
    'gemini-1.5-flash',
    capabilities=[OnlineEvaluation(evaluators=[judge])],
)

agent.run_sync('What is the capital of the UK?')
```
### 4.2 Custom Evaluator Syntax
All evaluators must inherit from Evaluator, implement evaluate, and utilize EvaluatorContext:
```python
from dataclasses import dataclass
from pydantic_evals.evaluators import Evaluator, EvaluatorContext, EvaluatorOutput, EvaluationReason

@dataclass
class ComprehensiveCheck(Evaluator):
    def evaluate(self, ctx: EvaluatorContext) -> EvaluatorOutput:
        return {
            'valid_format': EvaluationReason(
                value=isinstance(ctx.output, dict),
                reason='Valid dict format' if isinstance(ctx.output, dict) else 'Invalid format',
            ),
            'quality_score': min(1.0, len(str(ctx.output)) / 100.0),
        }
```
## 5. Council Review — Multi-Agent System
Trigger: Run Council Review
### 5.1 Agents
1. @architect (System Design & Strategy) • Focus: Long-term scalability, data isolation, structural integrity. • Core Logic: Analyze multi-tenancy models (Silo vs Pool vs Bridge). Distinguish Control Plane (admin/billing) from Data Plane (tenant workloads).
2. @library-curator (Efficiency & Dependency Management) • Focus: Avoid reinventing the wheel. • Core Logic: Compare custom logic against industry standards. Minimize custom code to reduce maintenance.
3. @kube-guardian (Kubernetes & Infrastructure SRE) • Focus: Security, automation, K8s-native orchestration. • Core Logic: Enforce GitOps, auto-scaling, and policy engines. Ensure kubectl syntax uses the double-dash (--) for exec commands (e.g., kubectl exec <pod> -- <command>).
### 5.2 Workflow Execution
1. Launch all 3 agents in parallel via the Task tool.
2. Each receives the project context (ADRs, codebase structure, configs).
3. Collect and synthesize results into a Unified Review.
### 5.3 Unified Review Output Format
• Phase 1: Directional Audit (@architect): Trajectory evaluation for Enterprise SaaS; missing critical systems.
• Phase 2: The "Wheel" Audit (@library-curator): Custom modules to deprecate → specific 3rd-party replacements; tech stack assessment.
• Phase 3: Infrastructure Hardening (@kube-guardian): K8s features to Add/Remove; GitOps-readiness score.
### 5.4 Post-Review Action
Automatically create an actionable remediation plan. If critical violations are flagged, propose a refactor using the modify_existing_code tool to resolve the flagged issues before proceeding with new feature work.
## 6. Security & IAM (Zero Trust)
When generating infrastructure-as-code or Kubernetes manifests, you must never use broad or primitive owner permissions. You are required to define granular, custom IAM roles and use least-privilege access.
