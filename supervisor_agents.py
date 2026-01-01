"""
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


# Supervisor Agent - Coordinates all workers
def supervisor_node(state: SupervisorState) -> SupervisorState:
    """
    Project Coordinator - Coordinate team members and ensure quality output
    Decides which worker should handle the next task.
    """
    messages = state["messages"]
    task_queue = state.get("task_queue", [])
    completed = state.get("completed_tasks", [])
    
    # Determine next action
    worker_names = ["worker_1", "worker_2"]
    
    prompt = f"""You are a supervisor coordinating a team of workers: {worker_names}
    
Current task queue: {task_queue}
Completed tasks: {completed}
Messages so far: {[m.content for m in messages[-3:]]}

Based on the current state, decide:
1. Which worker should handle the next task? (respond with worker name)
2. Or if all tasks are complete, respond with "FINISH"

Respond with just the worker name or "FINISH"."""

    response = llm.invoke([HumanMessage(content=prompt)])
    next_agent = response.content.strip().lower().replace('"', '')
    
    if next_agent == "finish" or not task_queue:
        return {
            "messages": messages + [AIMessage(content="All tasks completed by supervisor")],
            "next_agent": "FINISH",
            "task_queue": task_queue,
            "completed_tasks": completed,
            "final_result": state.get("final_result", "")
        }
    
    return {
        "messages": messages,
        "next_agent": next_agent,
        "task_queue": task_queue,
        "completed_tasks": completed,
        "final_result": state.get("final_result", "")
    }


def worker_1_node(state: SupervisorState) -> SupervisorState:
    """
    Specialist 1 - Complete assigned tasks efficiently
    """
    messages = state["messages"]
    task_queue = state.get("task_queue", [])
    completed = state.get("completed_tasks", [])
    
    current_task = task_queue[0] if task_queue else "No task assigned"
    
    prompt = f"""You are a Specialist 1. Your goal: Complete assigned tasks efficiently
    
Your current task: {current_task}

Complete this task and provide your output."""

    response = llm.invoke([HumanMessage(content=prompt)])
    
    # Update state
    new_task_queue = task_queue[1:] if task_queue else []
    new_completed = completed + [current_task] if task_queue else completed
    
    return {
        "messages": messages + [AIMessage(content=f"[worker_1]: {response.content}")],
        "next_agent": "supervisor",
        "task_queue": new_task_queue,
        "completed_tasks": new_completed,
        "final_result": response.content
    }


def worker_2_node(state: SupervisorState) -> SupervisorState:
    """
    Specialist 2 - Complete assigned tasks efficiently
    """
    messages = state["messages"]
    task_queue = state.get("task_queue", [])
    completed = state.get("completed_tasks", [])
    
    current_task = task_queue[0] if task_queue else "No task assigned"
    
    prompt = f"""You are a Specialist 2. Your goal: Complete assigned tasks efficiently
    
Your current task: {current_task}

Complete this task and provide your output."""

    response = llm.invoke([HumanMessage(content=prompt)])
    
    # Update state
    new_task_queue = task_queue[1:] if task_queue else []
    new_completed = completed + [current_task] if task_queue else completed
    
    return {
        "messages": messages + [AIMessage(content=f"[worker_2]: {response.content}")],
        "next_agent": "supervisor",
        "task_queue": new_task_queue,
        "completed_tasks": new_completed,
        "final_result": response.content
    }


# Build the graph
def build_supervisor_graph():
    workflow = StateGraph(SupervisorState)
    
    # Add nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("worker_1", worker_1_node)
    workflow.add_node("worker_2", worker_2_node)

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
            "worker_1": "worker_1",
            "worker_2": "worker_2",
            END: END
        }
    )
    
    workflow.add_edge("worker_1", "supervisor")
    workflow.add_edge("worker_2", "supervisor")

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
