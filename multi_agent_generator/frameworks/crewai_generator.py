# multi_agent_generator/frameworks/crewai_generator.py
"""
Generator for CrewAI code.
"""
from typing import Dict, Any

def _sanitize_var_name(name: str) -> str:
    """Convert agent/task name to a valid Python variable name."""
    return name.strip().lower().replace(" ", "_").replace("-", "_").replace("'", "").replace('"', "")

def create_crewai_code(config: Dict[str, Any]) -> str:
    # Get process type from config (default to sequential)
    process_type = config.get("process", "sequential").lower()
    
    # Start with the basic imports plus Flow imports
    code = "from crewai import Agent, Task, Crew, Process\n"
    if process_type == "sequential":
        code += "from crewai.flow.flow import Flow, listen, start\n"
    code += "from typing import Dict, List, Any\n"
    code += "from pydantic import BaseModel, Field\n\n"
    
    if process_type == "sequential":
        # Define state model for the flow (only for sequential)
        code += "# Define flow state\n"
        code += "class AgentState(BaseModel):\n"
        code += "    query: str = Field(default=\"\")\n"
        code += "    results: Dict[str, Any] = Field(default_factory=dict)\n"
        code += "    current_step: str = Field(default=\"\")\n\n"
    
    # Create a mapping of agent names to sanitized variable names
    agent_name_to_var = {}
    
    # Generate Agent configurations
    for i, agent in enumerate(config["agents"]):
        agent_var = f"agent_{_sanitize_var_name(agent['name'])}"
        agent_name_to_var[agent['name']] = agent_var
        
        code += f"# Agent: {agent['name']}\n"
        code += f"{agent_var} = Agent(\n"
        code += f"    role={agent['role']!r},\n"
        code += f"    goal={agent['goal']!r},\n"
        code += f"    backstory={agent['backstory']!r},\n"
        code += f"    verbose={agent['verbose']},\n"
        code += f"    allow_delegation={agent['allow_delegation']},\n"
        code += f"    tools={agent['tools']}"
        
        # For hierarchical process, mark the first agent as manager
        if process_type == "hierarchical" and i == 0:
            code += ",\n    max_iter=5,\n"
            code += "    max_execution_time=300\n"
        else:
            code += "\n"
        
        code += ")\n\n"

    # Generate Task configurations
    for task in config["tasks"]:
        task_var = f"task_{_sanitize_var_name(task['name'])}"
        code += f"# Task: {task['name']}\n"
        code += f"{task_var} = Task(\n"
        code += f"    description={task['description']!r},\n"
        
        # Always assign agents to tasks, even in hierarchical mode
        agent_name = task.get('agent')
        if agent_name and agent_name in agent_name_to_var:
            agent_var = agent_name_to_var[agent_name]
            code += f"    agent={agent_var},\n"
        else:
            # If no agent specified or agent not found, find the most suitable one
            # or assign to the first non-manager agent (for hierarchical)
            if process_type == "hierarchical" and len(config["agents"]) > 1:
                # Assign to first worker agent (not the manager)
                fallback_agent = config["agents"][1]["name"]
            else:
                # For sequential, assign to first agent
                fallback_agent = config["agents"][0]["name"]
            
            fallback_var = agent_name_to_var[fallback_agent]
            code += f"    # Auto-assigned to: {fallback_agent}\n"
            code += f"    agent={fallback_var},\n"
        
        code += f"    expected_output={task['expected_output']!r}\n"
        code += ")\n\n"

    # Generate Crew configuration
    code += "# Crew Configuration\n"
    code += "crew = Crew(\n"
    code += "    agents=[" + ", ".join(agent_name_to_var.values()) + "],\n"
    code += "    tasks=[" + ", ".join(f"task_{_sanitize_var_name(t['name'])}" for t in config["tasks"]) + "],\n"
    
    # Set process type
    if process_type == "hierarchical":
        code += "    process=Process.hierarchical,\n"
        # The first agent becomes the manager
        manager_var = list(agent_name_to_var.values())[0]
        code += f"    manager_agent={manager_var},\n"
    else:
        code += "    process=Process.sequential,\n"
    
    code += "    verbose=True\n"
    code += ")\n\n"
    
    # Run the workflow (up to kickoff) for both process types
    code += "# Run the workflow\n"
    code += "def run_workflow(query: str):\n"
    code += "    \"\"\"Run workflow using CrewAI.\"\"\"\n"
    code += "    result = crew.kickoff(\n"
    code += "        inputs={\n"
    code += "            \"query\": query\n"
    code += "        }\n"
    code += "    )\n"
    code += "    return result\n\n"
    
    # Example usage
    code += "# Example usage\n"
    code += "if __name__ == \"__main__\":\n"
    code += "    result = run_workflow(\"Your query here\")\n"
    code += "    print(result)\n"
    return code 
