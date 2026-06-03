import os
import glob
import ast

src_dir = "/Users/jocham/programming/agents/src/openclaw/agents"
dest_dir = "/Users/jocham/programming/agy-agents/agy_agents"

skip_files = ["__init__.py", "registration.py", "ba.py", "backend.py"]

for filepath in glob.glob(os.path.join(src_dir, "*.py")):
    filename = os.path.basename(filepath)
    if filename in skip_files:
        continue

    module_name = filename[:-3]

    with open(filepath, "r") as f:
        source_code = f.read()

    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        print(f"Syntax error in {filename}, skipping.")
        continue

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
        continue

    # Escape triple quotes in prompt
    prompt_str = prompt_str.replace('"""', '\\"\\"\\"')

    agent_code = f'''from google.antigravity import Agent
from agy_agents.factory import create_agent_config

{module_name}_prompt = """{prompt_str}"""

async def run_{module_name}(conversation_id: str = None, prompt: str = "Perform your task."):
    """Runs the {module_name.title()} Agent."""
    config = create_agent_config(
        system_instruction={module_name}_prompt, 
        conversation_id=conversation_id
    )
    # Note: Tool definitions should be migrated manually if needed.
    
    async with Agent(config) as agent:
        response = await agent.chat(prompt)
        print(f"{module_name.title()} Agent Output: {{await response.text()}}")
        
        usage = agent.conversation.total_usage
        print(f"{module_name.title()} Agent Token Usage - Prompt: {{usage.prompt_token_count}}, Total: {{usage.total_token_count}}")
        return agent.conversation_id
'''
    with open(os.path.join(dest_dir, filename), "w") as f:
        f.write(agent_code)
    print(f"Successfully generated {filename}")
