# multi_agent_generator/orchestration/patterns.py
"""
Orchestration Patterns - Pre-built patterns for multi-agent collaboration.
Low-code approach: Users select a pattern and the system generates the orchestration code.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum


class PatternType(Enum):
    """Types of orchestration patterns."""
    SUPERVISOR = "supervisor"           # One agent coordinates others
    DEBATE = "debate"                   # Agents argue to reach consensus
    VOTING = "voting"                   # Democratic decision making
    PIPELINE = "pipeline"               # Sequential processing chain
    MAP_REDUCE = "map_reduce"           # Parallel processing with aggregation
    ROUND_ROBIN = "round_robin"         # Rotating agent turns
    HIERARCHICAL = "hierarchical"       # Tree-based delegation
    BROADCAST = "broadcast"             # One-to-many communication


@dataclass
class PatternConfig:
    """Configuration for an orchestration pattern."""
    pattern_type: PatternType
    agents: List[Dict[str, Any]]
    settings: Dict[str, Any] = field(default_factory=dict)
    description: str = ""


class OrchestrationPattern(ABC):
    """Base class for orchestration patterns."""
    
    pattern_type: PatternType
    name: str
    description: str
    use_cases: List[str]
    
    @abstractmethod
    def generate_code(self, config: Dict[str, Any], framework: str) -> str:
        """Generate orchestration code for the specified framework."""
        pass
    
    @abstractmethod
    def get_config_template(self) -> Dict[str, Any]:
        """Get the configuration template for this pattern."""
        pass
    
    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate the configuration. Returns list of errors."""
        errors = []
        if "agents" not in config or len(config.get("agents", [])) < 2:
            errors.append("At least 2 agents are required for orchestration")
        return errors


class SupervisorPattern(OrchestrationPattern):
    """
    Supervisor Pattern: A manager agent coordinates worker agents.
    
    Use cases:
    - Task delegation and coordination
    - Quality control workflows
    - Complex multi-step processes
    """
    
    pattern_type = PatternType.SUPERVISOR
    name = "Supervisor Pattern"
    description = "A supervisor agent coordinates and delegates tasks to specialized worker agents"
    use_cases = [
        "Project management workflows",
        "Quality assurance processes",
        "Customer service escalation",
        "Research coordination"
    ]
    
    def get_config_template(self) -> Dict[str, Any]:
        return {
            "supervisor": {
                "name": "supervisor",
                "role": "Project Coordinator",
                "goal": "Coordinate team and ensure quality output",
                "can_delegate": True
            },
            "workers": [
                {
                    "name": "worker_1",
                    "role": "Specialist",
                    "goal": "Complete assigned tasks",
                    "skills": []
                }
            ],
            "settings": {
                "max_iterations": 10,
                "require_approval": False,
                "parallel_execution": False
            }
        }
    
    def generate_code(self, config: Dict[str, Any], framework: str) -> str:
        if framework == "langgraph":
            return self._generate_langgraph_code(config)
        elif framework in ["crewai", "crewai-flow"]:
            return self._generate_crewai_code(config)
        else:
            return self._generate_generic_code(config)
    
    def _generate_langgraph_code(self, config: Dict[str, Any]) -> str:
        agents = config.get("agents", [])
        settings = config.get("settings", {})
        
        # Find supervisor (first agent or one marked as supervisor)
        supervisor = agents[0] if agents else {"name": "supervisor", "role": "Coordinator"}
        workers = agents[1:] if len(agents) > 1 else []
        
        code = '''"""
Supervisor Pattern Implementation using LangGraph
A supervisor agent coordinates and delegates tasks to worker agents.
"""

from typing import TypedDict, List, Literal, Annotated
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
import operator

# Define state
class SupervisorState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    next_agent: str
    task_queue: List[str]
    completed_tasks: List[str]
    final_result: str

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

'''
        # Generate supervisor node
        worker_names_str = ', '.join([f'"{w.get("name", f"worker_{i}")}"' for i, w in enumerate(workers)])
        code += f'''
# Supervisor Agent - Coordinates all workers
def supervisor_node(state: SupervisorState) -> SupervisorState:
    """
    {supervisor.get('role', 'Supervisor')} - {supervisor.get('goal', 'Coordinate team')}
    Decides which worker should handle the next task.
    """
    messages = state["messages"]
    task_queue = state.get("task_queue", [])
    completed = state.get("completed_tasks", [])
    
    # Determine next action
    worker_names = [{worker_names_str}]
    
    prompt = f"""You are a supervisor coordinating a team of workers: {{worker_names}}
    
Current task queue: {{task_queue}}
Completed tasks: {{completed}}
Messages so far: {{[m.content for m in messages[-3:]]}}

Based on the current state, decide:
1. Which worker should handle the next task? (respond with worker name)
2. Or if all tasks are complete, respond with "FINISH"

Respond with just the worker name or "FINISH"."""

    response = llm.invoke([HumanMessage(content=prompt)])
    next_agent = response.content.strip().lower().replace('"', '')
    
    if next_agent == "finish" or not task_queue:
        return {{
            "messages": messages + [AIMessage(content="All tasks completed by supervisor")],
            "next_agent": "FINISH",
            "task_queue": task_queue,
            "completed_tasks": completed,
            "final_result": state.get("final_result", "")
        }}
    
    return {{
        "messages": messages,
        "next_agent": next_agent,
        "task_queue": task_queue,
        "completed_tasks": completed,
        "final_result": state.get("final_result", "")
    }}

'''
        
        # Generate worker nodes
        for i, worker in enumerate(workers):
            worker_name = worker.get('name', f'worker_{i}')
            worker_role = worker.get('role', 'Worker')
            worker_goal = worker.get('goal', 'Complete assigned tasks')
            
            code += f'''
def {worker_name}_node(state: SupervisorState) -> SupervisorState:
    """
    {worker_role} - {worker_goal}
    """
    messages = state["messages"]
    task_queue = state.get("task_queue", [])
    completed = state.get("completed_tasks", [])
    
    current_task = task_queue[0] if task_queue else "No task assigned"
    
    prompt = f"""You are a {worker_role}. Your goal: {worker_goal}
    
Your current task: {{current_task}}

Complete this task and provide your output."""

    response = llm.invoke([HumanMessage(content=prompt)])
    
    # Update state
    new_task_queue = task_queue[1:] if task_queue else []
    new_completed = completed + [current_task] if task_queue else completed
    
    return {{
        "messages": messages + [AIMessage(content=f"[{worker_name}]: {{response.content}}")],
        "next_agent": "supervisor",
        "task_queue": new_task_queue,
        "completed_tasks": new_completed,
        "final_result": response.content
    }}

'''
        
        # Generate graph setup
        code += '''
# Build the graph
def build_supervisor_graph():
    workflow = StateGraph(SupervisorState)
    
    # Add nodes
    workflow.add_node("supervisor", supervisor_node)
'''
        
        for i, worker in enumerate(workers):
            worker_name = worker.get('name', f'worker_{i}')
            code += f'    workflow.add_node("{worker_name}", {worker_name}_node)\n'
        
        code += '''
    # Add routing logic
    def route_from_supervisor(state: SupervisorState) -> str:
        next_agent = state.get("next_agent", "FINISH")
        if next_agent == "FINISH":
            return END
        return next_agent
    
    # Add edges
    workflow.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
'''
        
        for i, worker in enumerate(workers):
            worker_name = worker.get('name', f'worker_{i}')
            code += f'            "{worker_name}": "{worker_name}",\n'
        
        code += '''            END: END
        }
    )
    
'''
        
        for i, worker in enumerate(workers):
            worker_name = worker.get('name', f'worker_{i}')
            code += f'    workflow.add_edge("{worker_name}", "supervisor")\n'
        
        code += '''
    # Set entry point
    workflow.set_entry_point("supervisor")
    
    return workflow.compile()

# Create and run
def run_supervisor_workflow(tasks: List[str], query: str) -> str:
    """Run the supervisor workflow with given tasks."""
    app = build_supervisor_graph()
    
    initial_state = {
        "messages": [HumanMessage(content=query)],
        "next_agent": "supervisor",
        "task_queue": tasks,
        "completed_tasks": [],
        "final_result": ""
    }
    
    result = app.invoke(initial_state)
    return result.get("final_result", "No result")

# Example usage
if __name__ == "__main__":
    tasks = ["Research the topic", "Analyze findings", "Write summary"]
    result = run_supervisor_workflow(tasks, "Help me understand AI agents")
    print(result)
'''
        
        return code
    
    def _generate_crewai_code(self, config: Dict[str, Any]) -> str:
        agents = config.get("agents", [])
        
        code = '''"""
Supervisor Pattern Implementation using CrewAI
A supervisor agent coordinates and delegates tasks to worker agents.
"""

from crewai import Agent, Task, Crew, Process
from typing import List, Dict, Any

'''
        
        # Generate agents
        supervisor = agents[0] if agents else {"name": "supervisor", "role": "Project Manager"}
        workers = agents[1:] if len(agents) > 1 else []
        
        code += f'''
# Supervisor Agent
supervisor = Agent(
    role="{supervisor.get('role', 'Project Manager')}",
    goal="{supervisor.get('goal', 'Coordinate team and ensure quality deliverables')}",
    backstory="{supervisor.get('backstory', 'Experienced project manager skilled in delegation')}",
    verbose=True,
    allow_delegation=True
)

'''
        
        for i, worker in enumerate(workers):
            var_name = f"worker_{worker.get('name', i)}".replace(" ", "_").lower()
            code += f'''
{var_name} = Agent(
    role="{worker.get('role', f'Worker {i+1}')}",
    goal="{worker.get('goal', 'Complete assigned tasks efficiently')}",
    backstory="{worker.get('backstory', 'Skilled professional')}",
    verbose=True,
    allow_delegation=False
)

'''
        
        code += '''
# Create Crew with hierarchical process
def create_supervisor_crew(tasks_descriptions: List[str]) -> Crew:
    """Create a supervised crew for the given tasks."""
    
    tasks = []
    workers = ['''
        
        code += ', '.join([f"worker_{w.get('name', i)}".replace(" ", "_").lower() for i, w in enumerate(workers)])
        
        code += ''']
    
    for i, desc in enumerate(tasks_descriptions):
        worker = workers[i % len(workers)]  # Round-robin assignment
        task = Task(
            description=desc,
            agent=worker,
            expected_output=f"Completed: {desc}"
        )
        tasks.append(task)
    
    crew = Crew(
        agents=[supervisor] + workers,
        tasks=tasks,
        process=Process.hierarchical,
        manager_agent=supervisor,
        verbose=True
    )
    
    return crew

# Example usage
if __name__ == "__main__":
    tasks = [
        "Research the latest AI trends",
        "Analyze the collected data",
        "Write a comprehensive report"
    ]
    crew = create_supervisor_crew(tasks)
    result = crew.kickoff()
    print(result)
'''
        
        return code
    
    def _generate_generic_code(self, config: Dict[str, Any]) -> str:
        return '''"""
Supervisor Pattern - Generic Implementation
"""

class SupervisorOrchestrator:
    def __init__(self, workers):
        self.workers = workers
        self.task_queue = []
        
    def assign_task(self, task, worker_name):
        worker = next((w for w in self.workers if w.name == worker_name), None)
        if worker:
            return worker.execute(task)
        return None
    
    def run(self, tasks):
        results = []
        for task in tasks:
            # Simple round-robin assignment
            worker = self.workers[len(results) % len(self.workers)]
            result = self.assign_task(task, worker.name)
            results.append(result)
        return results
'''


class DebatePattern(OrchestrationPattern):
    """
    Debate Pattern: Agents argue different perspectives to reach consensus.
    
    Use cases:
    - Decision making
    - Fact verification
    - Creative brainstorming
    """
    
    pattern_type = PatternType.DEBATE
    name = "Debate Pattern"
    description = "Multiple agents argue different perspectives and reach consensus through structured debate"
    use_cases = [
        "Decision making processes",
        "Fact checking and verification",
        "Brainstorming sessions",
        "Risk assessment"
    ]
    
    def get_config_template(self) -> Dict[str, Any]:
        return {
            "debaters": [
                {
                    "name": "advocate",
                    "role": "Advocate",
                    "position": "pro",
                    "goal": "Argue in favor"
                },
                {
                    "name": "critic",
                    "role": "Critic", 
                    "position": "con",
                    "goal": "Argue against"
                }
            ],
            "moderator": {
                "name": "moderator",
                "role": "Debate Moderator",
                "goal": "Facilitate fair debate and synthesize conclusion"
            },
            "settings": {
                "max_rounds": 3,
                "require_consensus": True
            }
        }
    
    def generate_code(self, config: Dict[str, Any], framework: str) -> str:
        agents = config.get("agents", [])
        settings = config.get("settings", {})
        max_rounds = settings.get("max_rounds", 3)
        
        code = '''"""
Debate Pattern Implementation
Agents argue different perspectives to reach consensus.
"""

from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
import operator

class DebateState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    topic: str
    current_round: int
    positions: dict
    consensus: str
    is_concluded: bool

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

'''
        
        # Generate debater functions
        for i, agent in enumerate(agents[:2]):  # At least 2 debaters
            name = agent.get('name', f'debater_{i}')
            role = agent.get('role', 'Debater')
            position = agent.get('position', 'neutral')
            
            code += f'''
def {name}_node(state: DebateState) -> DebateState:
    """
    {role} - Argues {position} position
    """
    topic = state["topic"]
    messages = state["messages"]
    current_round = state["current_round"]
    
    # Get previous arguments
    prev_args = [m.content for m in messages if isinstance(m, AIMessage)]
    
    prompt = f"""You are a {role} in a structured debate.
Topic: {{topic}}
Your position: {position}
Current round: {{current_round}}

Previous arguments in this debate:
{{chr(10).join(prev_args[-4:]) if prev_args else 'None yet'}}

Present your argument for round {{current_round}}. Be persuasive but fair.
If you find the opposing argument compelling, acknowledge it."""

    response = llm.invoke([HumanMessage(content=prompt)])
    
    return {{
        "messages": messages + [AIMessage(content=f"[{name} - Round {{current_round}}]: {{response.content}}")],
        "topic": topic,
        "current_round": current_round,
        "positions": state.get("positions", {{}}),
        "consensus": state.get("consensus", ""),
        "is_concluded": False
    }}

'''
        
        # Generate moderator
        code += f'''
def moderator_node(state: DebateState) -> DebateState:
    """
    Moderator - Synthesizes arguments and determines consensus
    """
    messages = state["messages"]
    current_round = state["current_round"]
    max_rounds = {max_rounds}
    
    # Collect all arguments
    arguments = [m.content for m in messages if isinstance(m, AIMessage)]
    
    if current_round >= max_rounds:
        # Final synthesis
        prompt = f"""You are a debate moderator. The debate has concluded after {{current_round}} rounds.

All arguments presented:
{{chr(10).join(arguments)}}

Provide a final synthesis:
1. Summarize the key points from each side
2. Identify areas of agreement
3. State the consensus conclusion or remaining points of disagreement"""

        response = llm.invoke([HumanMessage(content=prompt)])
        
        return {{
            "messages": messages + [AIMessage(content=f"[MODERATOR CONCLUSION]: {{response.content}}")],
            "topic": state["topic"],
            "current_round": current_round,
            "positions": state.get("positions", {{}}),
            "consensus": response.content,
            "is_concluded": True
        }}
    else:
        # Continue debate
        return {{
            "messages": messages,
            "topic": state["topic"],
            "current_round": current_round + 1,
            "positions": state.get("positions", {{}}),
            "consensus": "",
            "is_concluded": False
        }}

def should_continue(state: DebateState) -> str:
    if state.get("is_concluded", False):
        return END
    return "debater_1"

def build_debate_graph():
    workflow = StateGraph(DebateState)
    
    # Add nodes
'''
        
        for i, agent in enumerate(agents[:2]):
            name = agent.get('name', f'debater_{i}')
            code += f'    workflow.add_node("{name}", {name}_node)\n'
        
        code += '''    workflow.add_node("moderator", moderator_node)
    
    # Add edges - alternating debate structure
'''
        
        if len(agents) >= 2:
            name1 = agents[0].get('name', 'debater_0')
            name2 = agents[1].get('name', 'debater_1')
            code += f'''    workflow.add_edge("{name1}", "{name2}")
    workflow.add_edge("{name2}", "moderator")
    workflow.add_conditional_edges("moderator", should_continue, {{END: END, "debater_1": "{name1}"}})
    
    workflow.set_entry_point("{name1}")
'''
        
        code += '''
    return workflow.compile()

def run_debate(topic: str) -> str:
    """Run a debate on the given topic."""
    app = build_debate_graph()
    
    initial_state = {
        "messages": [HumanMessage(content=f"Debate topic: {topic}")],
        "topic": topic,
        "current_round": 1,
        "positions": {},
        "consensus": "",
        "is_concluded": False
    }
    
    result = app.invoke(initial_state)
    return result.get("consensus", "No consensus reached")

if __name__ == "__main__":
    topic = "Should AI systems be given autonomous decision-making authority?"
    conclusion = run_debate(topic)
    print("Debate Conclusion:", conclusion)
'''
        
        return code


class VotingPattern(OrchestrationPattern):
    """
    Voting Pattern: Multiple agents vote to make decisions democratically.
    
    Use cases:
    - Ensemble decisions
    - Quality assessment
    - Multi-perspective evaluation
    """
    
    pattern_type = PatternType.VOTING
    name = "Voting Pattern"  
    description = "Multiple agents vote on decisions, with configurable voting rules"
    use_cases = [
        "Ensemble AI decisions",
        "Content moderation",
        "Quality assessment",
        "Multi-model consensus"
    ]
    
    def get_config_template(self) -> Dict[str, Any]:
        return {
            "voters": [
                {"name": "voter_1", "role": "Expert 1", "weight": 1},
                {"name": "voter_2", "role": "Expert 2", "weight": 1},
                {"name": "voter_3", "role": "Expert 3", "weight": 1}
            ],
            "settings": {
                "voting_method": "majority",  # majority, unanimous, weighted
                "min_votes": 2,
                "allow_abstain": False
            }
        }
    
    def generate_code(self, config: Dict[str, Any], framework: str) -> str:
        agents = config.get("agents", [])
        settings = config.get("settings", {})
        voting_method = settings.get("voting_method", "majority")
        
        code = f'''"""
Voting Pattern Implementation
Multiple agents vote democratically on decisions.
Voting method: {voting_method}
"""

from typing import TypedDict, List, Dict, Annotated
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from collections import Counter
import operator

class VotingState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    question: str
    options: List[str]
    votes: Dict[str, str]
    result: str
    is_complete: bool

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

'''
        
        # Generate voter nodes
        for i, agent in enumerate(agents):
            name = agent.get('name', f'voter_{i}')
            role = agent.get('role', f'Voter {i+1}')
            weight = agent.get('weight', 1)
            
            code += f'''
def {name}_node(state: VotingState) -> VotingState:
    """
    {role} - Weight: {weight}
    """
    question = state["question"]
    options = state["options"]
    
    prompt = f"""You are {role}, an expert voter in a decision-making panel.

Question: {{question}}
Available options: {{options}}

Analyze the options carefully and cast your vote.
Respond with ONLY the exact option text you're voting for."""

    response = llm.invoke([HumanMessage(content=prompt)])
    vote = response.content.strip()
    
    # Validate vote
    if vote not in options:
        # Find closest match
        vote = min(options, key=lambda x: len(set(x.lower()) - set(vote.lower())))
    
    votes = state.get("votes", {{}})
    votes["{name}"] = vote
    
    return {{
        "messages": state["messages"] + [AIMessage(content=f"[{name}] votes: {{vote}}")],
        "question": question,
        "options": options,
        "votes": votes,
        "result": "",
        "is_complete": False
    }}

'''
        
        # Generate aggregator
        code += f'''
def vote_aggregator(state: VotingState) -> VotingState:
    """Aggregate votes and determine result using {voting_method} voting."""
    votes = state.get("votes", {{}})
    options = state["options"]
    
    # Count votes (with weights if applicable)
    vote_counts = Counter()
    weights = {{'''
        
        for agent in agents:
            name = agent.get('name', f'voter_{agents.index(agent)}')
            weight = agent.get('weight', 1)
            code += f'"{name}": {weight}, '
        
        code += f'''}}
    
    for voter, vote in votes.items():
        weight = weights.get(voter, 1)
        vote_counts[vote] += weight
    
    # Determine winner based on voting method
    voting_method = "{voting_method}"
    total_weight = sum(weights.values())
    
    if voting_method == "unanimous":
        if len(set(votes.values())) == 1:
            result = list(votes.values())[0]
        else:
            result = "No unanimous decision"
    elif voting_method == "majority":
        winner, count = vote_counts.most_common(1)[0]
        if count > total_weight / 2:
            result = winner
        else:
            result = f"No majority - Top: {{winner}} ({{count}}/{{total_weight}})"
    else:  # weighted or default
        winner, count = vote_counts.most_common(1)[0]
        result = f"{{winner}} ({{count}} weighted votes)"
    
    summary = f"Votes: {{dict(votes)}}\\nResult: {{result}}"
    
    return {{
        "messages": state["messages"] + [AIMessage(content=f"[RESULT]: {{summary}}")],
        "question": state["question"],
        "options": options,
        "votes": votes,
        "result": result,
        "is_complete": True
    }}

def build_voting_graph():
    workflow = StateGraph(VotingState)
    
    # Add voter nodes
'''
        
        for i, agent in enumerate(agents):
            name = agent.get('name', f'voter_{i}')
            code += f'    workflow.add_node("{name}", {name}_node)\n'
        
        code += '''    workflow.add_node("aggregator", vote_aggregator)
    
    # Chain voters then aggregate
'''
        
        # Chain voters
        for i in range(len(agents) - 1):
            name1 = agents[i].get('name', f'voter_{i}')
            name2 = agents[i + 1].get('name', f'voter_{i + 1}')
            code += f'    workflow.add_edge("{name1}", "{name2}")\n'
        
        if agents:
            last_voter = agents[-1].get('name', f'voter_{len(agents) - 1}')
            first_voter = agents[0].get('name', 'voter_0')
            code += f'''    workflow.add_edge("{last_voter}", "aggregator")
    workflow.add_edge("aggregator", END)
    
    workflow.set_entry_point("{first_voter}")
'''
        
        code += '''
    return workflow.compile()

def run_vote(question: str, options: List[str]) -> Dict:
    """Run a vote on the given question with options."""
    app = build_voting_graph()
    
    initial_state = {
        "messages": [HumanMessage(content=f"Vote: {question}")],
        "question": question,
        "options": options,
        "votes": {},
        "result": "",
        "is_complete": False
    }
    
    result = app.invoke(initial_state)
    return {
        "result": result.get("result"),
        "votes": result.get("votes"),
        "messages": [m.content for m in result.get("messages", [])]
    }

if __name__ == "__main__":
    question = "What is the best programming language for AI development?"
    options = ["Python", "JavaScript", "Rust", "Go"]
    outcome = run_vote(question, options)
    print("Decision:", outcome["result"])
    print("Individual votes:", outcome["votes"])
'''
        
        return code


class PipelinePattern(OrchestrationPattern):
    """
    Pipeline Pattern: Sequential processing where each agent builds on previous output.
    
    Use cases:
    - Content creation workflows
    - Data processing pipelines
    - Review and refinement processes
    """
    
    pattern_type = PatternType.PIPELINE
    name = "Pipeline Pattern"
    description = "Sequential processing chain where each agent transforms and passes data to the next"
    use_cases = [
        "Content creation and editing",
        "Data transformation pipelines",
        "Multi-stage processing",
        "Review and approval workflows"
    ]
    
    def get_config_template(self) -> Dict[str, Any]:
        return {
            "stages": [
                {"name": "stage_1", "role": "Initial Processor", "goal": "First transformation"},
                {"name": "stage_2", "role": "Enhancer", "goal": "Enhance output"},
                {"name": "stage_3", "role": "Finalizer", "goal": "Final polish"}
            ],
            "settings": {
                "pass_full_history": True,
                "allow_skip": False
            }
        }
    
    def generate_code(self, config: Dict[str, Any], framework: str) -> str:
        agents = config.get("agents", [])
        
        code = '''"""
Pipeline Pattern Implementation
Sequential processing chain with agents building on each other's output.
"""

from typing import TypedDict, List, Annotated, Optional
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
import operator

class PipelineState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    input_data: str
    current_output: str
    stage_outputs: dict
    current_stage: int

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)

'''
        
        # Generate stage nodes
        for i, agent in enumerate(agents):
            name = agent.get('name', f'stage_{i}')
            role = agent.get('role', f'Stage {i+1}')
            goal = agent.get('goal', 'Process data')
            
            code += f'''
def {name}_node(state: PipelineState) -> PipelineState:
    """
    Pipeline Stage {i+1}: {role}
    Goal: {goal}
    """
    current_output = state.get("current_output") or state.get("input_data", "")
    stage_outputs = state.get("stage_outputs", {{}})
    
    prompt = f"""You are {role} in a processing pipeline.
Your goal: {goal}

Input from previous stage:
{{current_output}}

Process this input according to your role and provide your output."""

    response = llm.invoke([HumanMessage(content=prompt)])
    new_output = response.content
    
    stage_outputs["{name}"] = new_output
    
    return {{
        "messages": state["messages"] + [AIMessage(content=f"[{name}]: {{new_output[:200]}}...")],
        "input_data": state["input_data"],
        "current_output": new_output,
        "stage_outputs": stage_outputs,
        "current_stage": {i + 1}
    }}

'''
        
        code += '''
def build_pipeline_graph():
    workflow = StateGraph(PipelineState)
    
    # Add stage nodes
'''
        
        for i, agent in enumerate(agents):
            name = agent.get('name', f'stage_{i}')
            code += f'    workflow.add_node("{name}", {name}_node)\n'
        
        code += '''
    # Chain stages sequentially
'''
        
        for i in range(len(agents) - 1):
            name1 = agents[i].get('name', f'stage_{i}')
            name2 = agents[i + 1].get('name', f'stage_{i + 1}')
            code += f'    workflow.add_edge("{name1}", "{name2}")\n'
        
        if agents:
            last_stage = agents[-1].get('name', f'stage_{len(agents) - 1}')
            first_stage = agents[0].get('name', 'stage_0')
            code += f'''    workflow.add_edge("{last_stage}", END)
    
    workflow.set_entry_point("{first_stage}")
'''
        
        code += '''
    return workflow.compile()

def run_pipeline(input_data: str) -> dict:
    """Run the pipeline with given input."""
    app = build_pipeline_graph()
    
    initial_state = {
        "messages": [HumanMessage(content=f"Pipeline input: {input_data[:100]}...")],
        "input_data": input_data,
        "current_output": input_data,
        "stage_outputs": {},
        "current_stage": 0
    }
    
    result = app.invoke(initial_state)
    return {
        "final_output": result.get("current_output"),
        "stage_outputs": result.get("stage_outputs"),
        "stages_completed": result.get("current_stage")
    }

if __name__ == "__main__":
    input_text = "Raw data that needs processing through multiple stages"
    result = run_pipeline(input_text)
    print("Final output:", result["final_output"])
    print("Stages completed:", result["stages_completed"])
'''
        
        return code


class MapReducePattern(OrchestrationPattern):
    """
    Map-Reduce Pattern: Parallel processing with aggregation.
    
    Use cases:
    - Large-scale data processing
    - Parallel analysis
    - Distributed summarization
    """
    
    pattern_type = PatternType.MAP_REDUCE
    name = "Map-Reduce Pattern"
    description = "Parallel processing where multiple agents work on chunks, then results are aggregated"
    use_cases = [
        "Large document summarization",
        "Parallel data analysis",
        "Distributed processing",
        "Multi-source aggregation"
    ]
    
    def get_config_template(self) -> Dict[str, Any]:
        return {
            "mappers": [
                {"name": "mapper_1", "role": "Processor 1"},
                {"name": "mapper_2", "role": "Processor 2"},
                {"name": "mapper_3", "role": "Processor 3"}
            ],
            "reducer": {
                "name": "reducer",
                "role": "Aggregator",
                "goal": "Combine and synthesize results"
            },
            "settings": {
                "chunk_size": 1000,
                "parallel": True
            }
        }
    
    def generate_code(self, config: Dict[str, Any], framework: str) -> str:
        agents = config.get("agents", [])
        settings = config.get("settings", {})
        
        # Separate mappers and reducer
        mappers = [a for a in agents if "mapper" in a.get("name", "").lower() or a.get("role", "").lower() != "aggregator"]
        reducer = next((a for a in agents if "reducer" in a.get("name", "").lower() or a.get("role", "").lower() == "aggregator"), None)
        
        if not mappers:
            mappers = agents[:-1] if len(agents) > 1 else agents
        if not reducer and agents:
            reducer = agents[-1]
        
        code = '''"""
Map-Reduce Pattern Implementation
Parallel processing with aggregation.
"""

from typing import TypedDict, List, Dict, Annotated
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
import operator

class MapReduceState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    input_chunks: List[str]
    mapper_outputs: Dict[str, str]
    final_result: str
    mappers_complete: int

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)

def chunk_input(text: str, num_chunks: int) -> List[str]:
    """Split input into roughly equal chunks."""
    chunk_size = len(text) // num_chunks + 1
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

'''
        
        # Generate mapper nodes
        for i, mapper in enumerate(mappers):
            name = mapper.get('name', f'mapper_{i}')
            role = mapper.get('role', f'Mapper {i+1}')
            
            code += f'''
def {name}_node(state: MapReduceState) -> MapReduceState:
    """
    Mapper: {role}
    Processes a chunk of the input.
    """
    chunks = state.get("input_chunks", [])
    mapper_outputs = state.get("mapper_outputs", {{}})
    
    # Get this mapper's chunk
    chunk_idx = {i}
    chunk = chunks[chunk_idx] if chunk_idx < len(chunks) else ""
    
    if not chunk:
        return state
    
    prompt = f"""You are a {role} in a map-reduce system.
Process this chunk of data and extract key information:

{{chunk}}

Provide a concise summary of the key points."""

    response = llm.invoke([HumanMessage(content=prompt)])
    mapper_outputs["{name}"] = response.content
    
    return {{
        "messages": state["messages"] + [AIMessage(content=f"[{name}]: Processed chunk {{{{chunk_idx + 1}}}}")],
        "input_chunks": chunks,
        "mapper_outputs": mapper_outputs,
        "final_result": "",
        "mappers_complete": state.get("mappers_complete", 0) + 1
    }}

'''
        
        # Generate reducer node
        reducer_name = reducer.get('name', 'reducer') if reducer else 'reducer'
        reducer_role = reducer.get('role', 'Aggregator') if reducer else 'Aggregator'
        
        code += f'''
def {reducer_name}_node(state: MapReduceState) -> MapReduceState:
    """
    Reducer: {reducer_role}
    Aggregates all mapper outputs into final result.
    """
    mapper_outputs = state.get("mapper_outputs", {{}})
    
    # Combine all mapper outputs
    combined = "\\n\\n".join([f"{{k}}:\\n{{v}}" for k, v in mapper_outputs.items()])
    
    prompt = f"""You are the reducer in a map-reduce system.
Combine and synthesize these processed chunks into a coherent final result:

{{combined}}

Provide a unified summary that captures all key information."""

    response = llm.invoke([HumanMessage(content=prompt)])
    
    return {{
        "messages": state["messages"] + [AIMessage(content=f"[REDUCER]: Final result generated")],
        "input_chunks": state["input_chunks"],
        "mapper_outputs": mapper_outputs,
        "final_result": response.content,
        "mappers_complete": state.get("mappers_complete", 0)
    }}

def build_map_reduce_graph():
    workflow = StateGraph(MapReduceState)
    
    # Add mapper nodes
'''
        
        for i, mapper in enumerate(mappers):
            name = mapper.get('name', f'mapper_{i}')
            code += f'    workflow.add_node("{name}", {name}_node)\n'
        
        code += f'    workflow.add_node("{reducer_name}", {reducer_name}_node)\n'
        
        code += '''
    # Connect mappers in sequence (for simplicity - could be parallelized)
'''
        
        for i in range(len(mappers) - 1):
            name1 = mappers[i].get('name', f'mapper_{i}')
            name2 = mappers[i + 1].get('name', f'mapper_{i + 1}')
            code += f'    workflow.add_edge("{name1}", "{name2}")\n'
        
        if mappers:
            last_mapper = mappers[-1].get('name', f'mapper_{len(mappers) - 1}')
            first_mapper = mappers[0].get('name', 'mapper_0')
            code += f'''    workflow.add_edge("{last_mapper}", "{reducer_name}")
    workflow.add_edge("{reducer_name}", END)
    
    workflow.set_entry_point("{first_mapper}")
'''
        
        num_mappers = len(mappers)
        code += f'''
    return workflow.compile()

def run_map_reduce(input_data: str) -> dict:
    """Run map-reduce on the input data."""
    app = build_map_reduce_graph()
    
    # Split input into chunks for mappers
    num_mappers = {num_mappers}
    chunks = chunk_input(input_data, num_mappers)
    
    initial_state = {{
        "messages": [HumanMessage(content="Starting map-reduce processing")],
        "input_chunks": chunks,
        "mapper_outputs": {{}},
        "final_result": "",
        "mappers_complete": 0
    }}
    
    result = app.invoke(initial_state)
    return {{
        "final_result": result.get("final_result"),
        "mapper_outputs": result.get("mapper_outputs"),
        "chunks_processed": len(chunks)
    }}

if __name__ == "__main__":
    long_text = "This is a long document... " * 100  # Simulated long input
    result = run_map_reduce(long_text)
    print("Final Result:", result["final_result"])
    print("Chunks processed:", result["chunks_processed"])
'''
        
        return code


# Pattern registry
_PATTERNS: Dict[PatternType, type] = {
    PatternType.SUPERVISOR: SupervisorPattern,
    PatternType.DEBATE: DebatePattern,
    PatternType.VOTING: VotingPattern,
    PatternType.PIPELINE: PipelinePattern,
    PatternType.MAP_REDUCE: MapReducePattern,
}


def get_pattern(pattern_type: PatternType) -> OrchestrationPattern:
    """Get an instance of the specified pattern."""
    pattern_class = _PATTERNS.get(pattern_type)
    if pattern_class:
        return pattern_class()
    raise ValueError(f"Unknown pattern type: {pattern_type}")


def list_patterns() -> List[Dict[str, Any]]:
    """List all available patterns with their metadata."""
    patterns = []
    for pattern_type, pattern_class in _PATTERNS.items():
        instance = pattern_class()
        patterns.append({
            "type": pattern_type.value,
            "name": instance.name,
            "description": instance.description,
            "use_cases": instance.use_cases
        })
    return patterns
