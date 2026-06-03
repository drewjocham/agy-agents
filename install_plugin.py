import os
import json
import glob
import ast

PLUGIN_DIR = "/Users/jocham/.gemini/config/plugins/agy-agents"
AGENTS_DIR = os.path.join(PLUGIN_DIR, "agents")

os.makedirs(AGENTS_DIR, exist_ok=True)

plugin_metadata = {"name": "agy-agents", "description": "OpenClaw AGY Agents Ecosystem"}

with open(os.path.join(PLUGIN_DIR, "plugin.json"), "w") as f:
    json.dump(plugin_metadata, f, indent=2)

src_dir = "/Users/jocham/programming/agy-agents/agy_agents"

for filepath in glob.glob(os.path.join(src_dir, "*.py")):
    filename = os.path.basename(filepath)
    if filename in [
        "__init__.py",
        "hooks.py",
        "factory.py",
        "ports.py",
        "adapters.py",
        "mcp_server.py",
    ]:
        continue

    module_name = filename[:-3]
    with open(filepath, "r") as f:
        source_code = f.read()

    try:
        tree = ast.parse(source_code)
    except SyntaxError:
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
        continue

    agent_def = {
        "name": module_name,
        "description": f"OpenClaw {module_name} Agent",
        "system_prompt": prompt_str,
        "enable_write_tools": True,
        "enable_mcp_tools": True,
        "enable_subagent_tools": True,
    }

    with open(os.path.join(AGENTS_DIR, f"{module_name}.json"), "w") as f:
        json.dump(agent_def, f, indent=2)

print("Plugin installation complete!")
