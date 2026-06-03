# AI-Powered Evaluation Requirements (Pydantic AI)

You are strictly required to build observability and evaluation into every AI-driven feature you implement. You must not merge AI features without automated grading.

**Mandatory Implementation Steps:**

1. **Instrument Everything:** You must call `logfire.instrument_pydantic_ai()` before initializing any agent.
    
2. **Define an Evaluator:** For every new AI capability, you must write a custom evaluator inheriting from `pydantic_evals.evaluators.Evaluator`.
    
3. **Assert Quality:** Do not use simple boolean checks for complex outputs. Use `LLMJudge` for qualitative grading or write custom `@dataclass` evaluators for deterministic JSON structure validation.
    

- **Architecture Enforcement:** For backend Go code, you must strictly adhere to Hexagonal Architecture (Ports and Adapters). Domain logic must remain isolated.
    
- **Security & IAM (Zero Trust):** When generating infrastructure-as-code or Kubernetes manifests, you must never use broad or primitive owner permissions. You are required to define granular, custom IAM roles and use least-privilege access.
    

```python
from pydantic_ai import Agent
from pydantic_evals.evaluators import LLMJudge
from pydantic_evals.online_capability import OnlineEvaluation
import logfire

logfire.configure()
logfire.instrument_pydantic_ai()

judge = LLMJudge(
    rubric='The answer is factually correct and directly addresses the question.',
    model='openai:gpt-4o-mini',
    include_input=True,
)

agent = Agent(
    'openai:gpt-4o-mini',
    capabilities=[OnlineEvaluation(evaluators=[judge])],
)

agent.run_sync('What is the capital of the UK?')
```

### 5.1 Custom Evaluators

All evaluators inherit from `Evaluator` and must implement `evaluate`:

```python
from dataclasses import dataclass
from pydantic_evals.evaluators import Evaluator, EvaluatorContext

@dataclass
class ExactMatch(Evaluator):
    def evaluate(self, ctx: EvaluatorContext) -> bool:
        return ctx.output == ctx.expected_output
```

#### EvaluatorContext

```python
from dataclasses import dataclass
from pydantic_evals.evaluators import Evaluator, EvaluatorContext

@dataclass
class MyEvaluator(Evaluator):
    def evaluate(self, ctx: EvaluatorContext) -> bool:
        _ = ctx.name
        _ = ctx.inputs
        _ = ctx.metadata
        _ = ctx.expected_output
        _ = ctx.output
        _ = ctx.duration
        _ = ctx.metrics
        _ = ctx.attributes
        _ = ctx.span_tree
        return True
```

#### Evaluator Parameters

```python
from dataclasses import dataclass
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import Evaluator, EvaluatorContext

@dataclass
class ContainsKeyword(Evaluator):
    keyword: str
    case_sensitive: bool = True

    def evaluate(self, ctx: EvaluatorContext) -> bool:
        output = ctx.output
        keyword = self.keyword
        if not self.case_sensitive:
            output = output.lower()
            keyword = keyword.lower()
        return keyword in output

dataset = Dataset(
    name='keyword_check',
    cases=[Case(name='test', inputs='This is important')],
    evaluators=[ContainsKeyword(keyword='important', case_sensitive=False)],
)
```

#### Return Types

```python
from dataclasses import dataclass
from pydantic_evals.evaluators import EvaluationReason, Evaluator, EvaluatorContext, EvaluatorOutput

@dataclass
class ComprehensiveCheck(Evaluator):
    def evaluate(self, ctx: EvaluatorContext) -> EvaluatorOutput:
        return {
            'valid_format': EvaluationReason(
                value=ctx.output.startswith('{'),
                reason='Valid JSON format' if ctx.output.startswith('{') else 'Invalid JSON format',
            ),
            'quality_score': min(1.0, len(ctx.output) / 100.0),
            'category': 'short' if len(ctx.output) < 50 else 'long',
        }
```

#### Conditional Results

```python
@dataclass
class SQLValidator(Evaluator):
    def evaluate(self, ctx: EvaluatorContext) -> EvaluatorOutput:
        if not isinstance(ctx.output, str) or not ctx.output.strip().upper().startswith(
            ('SELECT', 'INSERT', 'UPDATE', 'DELETE')
        ):
            return {}
        is_valid = 'FROM' in ctx.output.upper() or 'INTO' in ctx.output.upper()
        return {'sql_valid': is_valid}
```

#### Async Evaluators

```python
from dataclasses import dataclass
from pydantic_evals.evaluators import Evaluator, EvaluatorContext

@dataclass
class APIValidator(Evaluator):
    api_url: str
    
    async def evaluate(self, ctx: EvaluatorContext) -> bool:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(self.api_url, json={'output': ctx.output})
            return response.json()['valid']
```

#### Using Metadata & Metrics

```python
from dataclasses import dataclass
from pydantic_evals import increment_eval_metric, set_eval_attribute
from pydantic_evals.evaluators import Evaluator, EvaluatorContext

@dataclass
class EfficiencyCheck(Evaluator):
    max_api_calls: int = 5
    
    def evaluate(self, ctx: EvaluatorContext) -> bool:
        api_calls = ctx.metrics.get('api_calls', 0)
        return api_calls <= self.max_api_calls
```

#### Custom Evaluation Names

```python
@dataclass
class CustomNameEvaluator(Evaluator):
    check_type: str
    
    def get_default_evaluation_name(self) -> str:
        return f'{self.check_type}_check'
        
    def evaluate(self, ctx: EvaluatorContext) -> bool:
        return True
```

#### Multi-Run Evaluation

```python
from pydantic_evals import Case, Dataset

dataset = Dataset(
    name='multi_run_basic',
    cases=[
        Case(name='greeting', inputs='Say hello'),
        Case(name='farewell', inputs='Say goodbye'),
    ],
)

def task(inputs: str) -> str:
    return inputs.upper()

report = dataset.evaluate_sync(task, repeat=5)
```

#### Concurrency & Performance

```python
report = dataset.evaluate_sync(my_task, max_concurrency=5)
```

## 6. Council Review — Multi-Agent System

Trigger: `Run Council Review`

### 6.1 Agents

#### 1. @architect (System Design & Strategy)

- **Focus:** Long-term scalability, data isolation, structural integrity.
    
- **Core Logic:** Analyze multi-tenancy models (Silo vs Pool vs Bridge). Distinguish Control Plane (admin/billing) from Data Plane (tenant workloads).
    
- **Goal:** Ensure no scaling wall at 100+ tenants.
    
- **Tool:** Task subagent with `subagent_type: architect`
    

#### 2. @library-curator (Efficiency & Dependency Management)

- **Focus:** Avoid reinventing the wheel.
    
- **Core Logic:** Compare custom logic against industry standards.
    
- **Goal:** Minimize custom code to reduce maintenance burden and security vulnerabilities.
    
- **Tool:** Task subagent with `subagent_type: library-curator`
    

#### 3. @kube-guardian (Kubernetes & Infrastructure SRE)

- **Focus:** Security, automation, K8s-native orchestration.
    
- **Core Logic:** Enforce GitOps (ArgoCD), auto-scaling (Karpenter), policy engine (Kyverno).
    
- **Goal:** Move from manual infra to self-healing, declarative environments.
    
- **Tool:** Task subagent with `subagent_type: kube-guardian`
    

### 6.2 Workflow Execution

When the user types `Run Council Review`:

1. Launch all 3 agents in parallel via the Task tool.
    
2. Each receives the project context (ADRs, codebase structure, configs).
    
3. Collect and synthesize results into a Unified Review.
    

### 6.3 Unified Review Output Format

#### Phase 1: Directional Audit (@architect)

- Trajectory evaluation for Enterprise SaaS.
    
- Missing critical systems.
    

#### Phase 2: The "Wheel" Audit (@library-curator)

- Custom modules to deprecate → specific 3rd-party replacements.
    
- Tech stack assessment.
    

#### Phase 3: Infrastructure Hardening (@kube-guardian)

- K8s features to Add and Remove.
    
- GitOps-readiness score.
    

### 6.4 Post-Review Action

Once the Unified Review is generated, automatically create an actionable remediation plan. If `@architect` or `@kube-guardian` flag critical violations, propose a refactor using the `modify_existing_code` tool to resolve the flagged issues before proceeding with new feature work.

## 7. Additional Notes

- **Clean Shutdowns:** Ensure clean shutdown sequences by intercepting OS signals (`os.Interrupt`, `syscall.SIGTERM`) and gracefully terminating servers and background workers using context cancellations with reasonable timeouts.
    
- **Mock Generation:** Ensure mocks for interfaces are generated using `mockery` as defined in `.mockery.yaml`.
    

## 8. Autonomous Native Turnaround Loop

You are designed to act on your own and manage turnaround checks autonomously. You are bound by a strict verify-then-commit loop executed directly within the host environment.

1. **Modify:** When you write or modify code, you must immediately transition to the VERIFY state.
    
2. **Verify:** You MUST execute turnaround hooks that always run `make test` and `make lint` to test the project correctly every time.
    
3. **Analyze:** - If the tools return a non-zero exit code or error trace, you are in a FAILED state.
    
    - You MUST NOT ask the user for help.
        
    - You MUST analyze the `stderr`/`stdout` trace, formulate a fix, apply it, and return to Step 2.
        
    - You have a maximum of 3 autonomous retry loops. If you fail 3 times, output the error trace to the user and halt.
        
4. **Complete:** You may only declare the task successful and return control to the user if the turnaround hooks return absolute success (exit code 0).
    

**Strict Constraints:**

- Never write JavaScript tests. Always enforce TypeScript.
    
- Never mock an implementation just to pass a test; write the actual logic.
    

## 9. Native Execution & Optional Delegation

You are fundamentally designed to execute tasks natively and autonomously. While you can act completely independently, you also have the ability to utilize external worker pools when necessary.

**Workflow:**

1. **Analyze Requirements:** Determine which domains (frontend, backend, DB, infrastructure, etc.) are involved in the current task.
    
2. **Execute Natively:** By default, generate the necessary code, structure, and configurations autonomously, running the turnaround loop (Section 8) entirely within your native execution context.
    
3. **Optional OpenClaw Delegation:** If a task requires highly specialized delegation, you may invoke the OpenClaw agent collective as a worker pool via available MCP tools to handle sub-components of the work.
    
4. **Integrate & Validate:** Whether the code was generated natively or retrieved from a worker agent, you must perform the final integration into the repository and guarantee it passes the standard test and linting gates.
