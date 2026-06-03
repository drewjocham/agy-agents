import os
import glob
import ast


def to_class_name(name):
    # e.g., service-coder -> ServiceCoder, or ba -> Ba
    clean_name = name.replace("-", "_")
    return "".join(word.capitalize() for word in clean_name.split("_")) + "Agent"


def write_agent_file(dest_dir, module_name, prompt_str):
    class_name = to_class_name(module_name)
    safe_module_name = module_name.replace("-", "_")
    # safely escape triple quotes and backslashes
    prompt_escaped = prompt_str.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')

    agent_code = f'''from typing import Optional, Tuple
from agy_agents.ports import AgentProviderPort, McpServerDef

{safe_module_name}_prompt = """{prompt_escaped}
"""

class {class_name}:
    """
    Hexagonal Agent: Isolated from the LLM provider.
    Relies entirely on the injected AgentProviderPort and consumes tools via MCP.
    """
    def __init__(self, provider: AgentProviderPort):
        self.provider = provider
        self.mcp_servers = [
            McpServerDef(command="python3", args=["-m", "agy_agents.mcp_server"])
        ]

    async def run(self, prompt: str, conversation_id: Optional[str] = None) -> Tuple[str, str]:
        return await self.provider.execute_agent(
            prompt=prompt,
            system_instruction={safe_module_name}_prompt,
            conversation_id=conversation_id,
            mcp_servers=self.mcp_servers
        )
'''
    with open(os.path.join(dest_dir, f"{safe_module_name}.py"), "w") as f:
        f.write(agent_code)
    print(f"Successfully generated {safe_module_name}.py")


def process_python_agent(filepath, dest_dir):
    filename = os.path.basename(filepath)
    if filename in [
        "__init__.py",
        "registration.py",
        "ba.py",
        "backend.py",
        "review.py",
    ]:
        return

    module_name = filename[:-3]
    with open(filepath, "r") as f:
        source_code = f.read()

    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        print(f"Syntax error in {filename}, skipping.")
        return

    prompt_str = ""
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.endswith("_prompt"):
                    if isinstance(node.value, ast.Constant):
                        prompt_str = str(node.value.value)
                    elif isinstance(node.value, ast.JoinedStr):
                        prompt_str = "".join(
                            [
                                str(v.value)
                                if isinstance(v, ast.Constant)
                                else "{expr}"
                                for v in node.value.values
                            ]
                        )
                    break

    if not prompt_str:
        for node in tree.body:
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
                if hasattr(node.value.func, "id") and node.value.func.id == "Agent":
                    for kw in node.value.keywords:
                        if kw.arg == "system_prompt" and isinstance(
                            kw.value, ast.Constant
                        ):
                            prompt_str = str(kw.value.value)
                            break

    if not prompt_str:
        print(f"Could not find prompt for {filename}")
        return

    write_agent_file(dest_dir, module_name, prompt_str)


def process_markdown_agent(filepath, dest_dir):
    filename = os.path.basename(filepath)
    module_name = filename[:-3]

    with open(filepath, "r") as f:
        content = f.read()

    parts = content.split("---")
    if len(parts) >= 3:
        # parts[0] is usually empty before the first ---
        # parts[1] is the yaml frontmatter
        # parts[2:] is the markdown content
        prompt_str = "---".join(parts[2:]).strip()
    else:
        prompt_str = content.strip()

    if not prompt_str:
        print(f"Empty prompt for {filename}")
        return

    write_agent_file(dest_dir, module_name, prompt_str)


if __name__ == "__main__":
    src_dir = "/Users/jocham/programming/agents/src/openclaw/agents"
    non_tech_src_dir = (
        "/Users/jocham/programming/agents/src/openclaw/agents/non_technical"
    )
    opencode_src_dir = "/Users/jocham/programming/agents/.opencode/agents"
    dest_dir = "/Users/jocham/programming/agy-agents/agy_agents"

    print("Processing Technical Agents...")
    for filepath in glob.glob(os.path.join(src_dir, "*.py")):
        process_python_agent(filepath, dest_dir)

    print("Processing Non-Technical Agents...")
    for filepath in glob.glob(os.path.join(non_tech_src_dir, "*.py")):
        process_python_agent(filepath, dest_dir)

    print("Processing OpenCode Markdown Agents...")
    for filepath in glob.glob(os.path.join(opencode_src_dir, "*.md")):
        process_markdown_agent(filepath, dest_dir)
