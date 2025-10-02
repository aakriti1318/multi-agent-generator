# multi_agent_generator/frameworks/agno_generator.py
"""
Generator for Agno team code.
"""
from typing import Dict, Any

def _sanitize(name: str) -> str:
    return (
        name.strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("'", "")
        .replace('"', "")
    )

def create_agno_code(config: Dict[str, Any]) -> str:
    """
    Generate Agno code from a configuration.

    the structure of the generator:
      - imports
      - agents
      - tasks
      - team config
      - run_workflow(query)
    """
    model_id = config.get("model_id", "gpt-4o")
    process_type = (config.get("process") or "sequential").lower()

    code = ""
    # Imports
    code += "from agno.agent import Agent\n"
    code += "from agno.models.openai import OpenAIChat\n"
    code += "from agno.team import Team\n"
    code += "from typing import Dict, List, Any\n"
    code += "from pydantic import BaseModel, Field\n\n"
    code += "from dotenv import load_dotenv\n\n"
    code += "load_dotenv()  # Load environment variables from .env file\n\n"
    
    # Agents
    agent_vars = []
    for agent in config.get("agents", []):
        var = f"agent_{_sanitize(agent['name'])}"
        agent_vars.append(var)

        role = agent.get("role", "")
        goal = agent.get("goal", "")
        backstory = agent.get("backstory", "")
        instructions = (goal + (" " if goal and backstory else "") + backstory) if (goal or backstory) else ""

        code += f"# Agent: {agent['name']}\n"
        code += f"{var} = Agent(\n"
        code += f"    name={agent['name']!r},\n"
        code += f"    model=OpenAIChat(id={model_id!r}),\n"
        code += f"    role={role!r},\n"
        if instructions:
            code += f"    instructions={instructions!r},\n"
        # Agno expects tool objects. To keep runnable, emit empty list.
        code += f"    tools=[],\n"
        code += f"    markdown=True,\n"
        code += ")\n\n"

    # Tasks
    task_vars = []
    tasks = config.get("tasks", [])
    for task in tasks:
        tvar = f"task_{_sanitize(task['name'])}"
        task_vars.append(tvar)

        desc = task.get("description", "")
        expected = task.get("expected_output", "")

        # resolve agent
        assigned = task.get("agent")
        if assigned:
            try:
                assigned_var = f"agent_{_sanitize(assigned)}"
            except Exception:
                assigned_var = agent_vars[0]
        else:
            if process_type == "hierarchical" and len(agent_vars) > 1:
                assigned_var = agent_vars[1]
            else:
                assigned_var = agent_vars[0]

        code += f"# Task: {task['name']}\n"
        code += f"def {tvar}(query: str) -> Any:\n"
        if not assigned:
            # parity with Crew output comment
            fallback_name = assigned or (config['agents'][1]['name'] if process_type == 'hierarchical' and len(config.get('agents', [])) > 1 else config['agents'][0]['name'])
            code += f"    # Auto-assigned to: {fallback_name}\n"
        code += "    prompt = (\n"
        code += f"        {desc!r} + '\\n\\n' +\n"
        code += "        'User query: ' + str(query) + '\\n' +\n"
        code += f"        'Expected output: ' + {expected!r}\n"
        code += "    )\n"
        code += f"    return {assigned_var}.run(prompt).content\n\n"

    # Team
    code += "# Team Configuration\n"
    code += "team = Team(\n"
    code += "    name='Auto Team',\n"
    code += "    mode='coordinate',\n"
    code += f"    model=OpenAIChat(id={model_id!r}),\n"
    code += f"    members=[{', '.join(agent_vars)}],\n"
    code += "    instructions=[\n"
    code += "        'Coordinate members to complete the tasks in order.',\n"
    code += "        'Use the query as shared context.',\n"
    code += "    ],\n"
    code += "    markdown=True,\n"
    code += "    debug_mode=True,\n"
    code += "    show_members_responses=True,\n"
    code += ")\n\n"

    # Runner
    code += "# Run the workflow\n"
    code += "def run_workflow(query: str):\n"
    code += "    \"\"\"Run workflow using Agno Team. Executes tasks in order and returns a dict of results.\"\"\"\n"
    code += "    results: Dict[str, Any] = {}\n"
    for tvar in task_vars:
        code += f"    results[{tvar!r}] = {tvar}(query)\n"
    code += "    return results\n\n"

    # Example usage
    code += "if __name__ == \"__main__\":\n"
    code += "    result = run_workflow(\"Your query here\")\n"
    code += "    print(result)\n"

    return code
