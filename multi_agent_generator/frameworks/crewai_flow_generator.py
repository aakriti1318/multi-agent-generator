# multi_agent_generator/frameworks/crewai_flow_generator.py
"""
Generator for CrewAI Flow code.
"""
from typing import Dict, Any

def create_crewai_flow_code(config: Dict[str, Any]) -> str:
    """
    Generate CrewAI Flow code from a configuration.
    
    This function creates event-driven workflow code using the CrewAI Flow framework,
    with proper transitions between different workflow steps.
    
    Args:
        config: Dictionary containing agents, tasks, and workflow configuration
        
    Returns:
        Generated Python code as a string
    """
    # Start with the basic imports
    code = "from crewai import Agent, Task, Crew\n"
    code += "from crewai.flow.flow import Flow, listen, start\n"
    code += "from typing import Dict, List, Any\n"
    code += "from pydantic import BaseModel, Field\n\n"
    
    # Define state model for the flow
    code += "# Define flow state\n"
    code += "class AgentState(BaseModel):\n"
    code += "    query: str = Field(default=\"\")\n"
    code += "    results: Dict[str, Any] = Field(default_factory=dict)\n"
    code += "    current_step: str = Field(default=\"\")\n\n"
    
    # Generate Agent configurations
    for agent in config["agents"]:
        code += f"# Agent: {agent['name']}\n"
        code += f"agent_{agent['name']} = Agent(\n"
        code += f"    role='{agent['role']}',\n"
        code += f"    goal='{agent['goal']}',\n"
        code += f"    backstory='{agent['backstory']}',\n"
        code += f"    verbose={agent['verbose']},\n"
        code += f"    allow_delegation={agent['allow_delegation']},\n"
        code += f"    tools={agent['tools']}\n"
        code += ")\n\n"

    # Generate Task configurations
    for task in config["tasks"]:
        code += f"# Task: {task['name']}\n"
        code += f"task_{task['name']} = Task(\n"
        code += f"    description='{task['description']}',\n"
        code += f"    agent=agent_{task['agent']},\n"
        code += f"    expected_output='{task['expected_output']}'\n"
        code += ")\n\n"

    # Generate Crew configuration
    code += "# Crew Configuration\n"
    code += "crew = Crew(\n"
    code += "    agents=[" + ", ".join(f"agent_{a['name']}" for a in config["agents"]) + "],\n"
    code += "    tasks=[" + ", ".join(f"task_{t['name']}" for t in config["tasks"]) + "],\n"
    code += "    verbose=True\n"
    code += ")\n\n"
    
    # Create Flow class
    code += "# Define CrewAI Flow\n"
    code += "class WorkflowFlow(Flow[AgentState]):\n"
    
    # Define initial step with @start decorator
    code += "    @start()\n"
    code += "    def initial_input(self):\n"
    code += "        \"\"\"Process the initial user query.\"\"\"\n"
    code += "        print(\"Starting workflow...\")\n"
    
    # Set the first task as the current step
    first_task = config["tasks"][0]["name"] if config["tasks"] else "completed"
    code += f"        self.state.current_step = \"{first_task}\"\n"
    code += "        return self.state\n\n"
    
    # Add task steps with @listen decorators
    tasks = config["tasks"]
    previous_step = "initial_input"
    
    for i, task in enumerate(tasks):
        task_name = task["name"].replace("-", "_")
        code += f"    @listen('{previous_step}')\n"
        code += f"    def execute_{task_name}(self, state):\n"
        code += f"        \"\"\"Execute the {task['name']} task.\"\"\"\n"
        code += f"        print(f\"Executing task: {task['name']}\")\n"
        code += "        \n"
        code += f"        # Run the specific task with the crew\n"
        code += f"        result = crew.kickoff(\n"
        code += f"            tasks=[task_{task['name']}],\n"
        code += f"            inputs={{\n"
        code += f"                \"query\": self.state.query,\n"
        code += f"                \"previous_results\": self.state.results\n"
        code += f"            }}\n"
        code += f"        )\n"
        code += f"        \n"
        code += f"        # Store results in state\n"
        code += f"        self.state.results[\"{task['name']}\"] = result\n"
        
        if i < len(tasks) - 1:
            next_task = tasks[i+1]["name"]
            code += f"        self.state.current_step = \"{next_task}\"\n"
        else:
            code += f"        self.state.current_step = \"completed\"\n"
            
        code += f"        return self.state\n\n"
        previous_step = f"execute_{task_name}"
    
    # Add final aggregation step
    code += f"    @listen('{previous_step}')\n"
    code += f"    def aggregate_results(self, state):\n"
    code += f"        \"\"\"Combine all results from tasks.\"\"\"\n"
    code += f"        print(\"Workflow completed, aggregating results...\")\n"
    code += f"        \n"
    code += f"        # Combine all results\n"
    code += f"        combined_result = \"\"\n"
    code += f"        for task_name, result in state.results.items():\n"
    code += f"            combined_result += f\"\\n\\n=== {task_name} ===\\n{{result}}\"\n"
    code += f"        \n"
    code += f"        return combined_result\n\n"
    
    # Add execution code
    code += "# Run the flow\n"
    code += "def run_workflow(query: str):\n"
    code += "    flow = WorkflowFlow()\n"
    code += "    flow.state.query = query\n"
    code += "    result = flow.kickoff()\n"
    code += "    return result\n\n"
    
    # Visualization function
    code += "# Generate a visualization of the flow\n"
    code += "def visualize_flow():\n"
    code += "    flow = WorkflowFlow()\n"
    code += "    flow.plot(\"workflow_flow\")\n"
    code += "    print(\"Flow visualization saved to workflow_flow.html\")\n\n"
    
    code += "# Example usage\n"
    code += "if __name__ == \"__main__\":\n"
    code += "    result = run_workflow(\"Your query here\")\n"
    code += "    print(result)\n"
    
    return code