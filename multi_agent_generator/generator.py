# multi_agent_generator/generator.py
"""
Agent configuration generator that analyzes user requirements.
Unified across multiple LLM providers via LiteLLM.
"""
import os
import json
import streamlit as st
from typing import Dict, Any, Optional, List
from .model_inference import ModelInference, Message


class AgentGenerator:
    """
    Generates agent configurations based on natural language descriptions.
    Uses LiteLLM for provider-agnostic inference.
    """

    def __init__(self, provider: str = "openai"):
        """
        Initialize the generator with the specified provider.

        Args:
            provider: The LLM provider to use (openai, watsonx, ollama, etc.)
        """
        self.provider = provider.lower()
        self.model: Optional[ModelInference] = None

    def set_provider(self, provider: str):
        """
        Change the LLM provider.

        Args:
            provider: The LLM provider (openai, watsonx, ollama, etc.)
        """
        self.provider = provider.lower()
        self.model = None  # reset for re-init

    def _initialize_model(self):
        """Initialize the LiteLLM ModelInference if not already done."""
        if self.model is not None:
            return

        default_models = {
            "openai": "gpt-4o-mini",
            "watsonx": "watsonx/meta-llama/llama-3-3-70b-instruct",
            "ollama": "ollama/llama3.2:3b",
        }
        model_name = default_models.get(self.provider, self.provider)
        model_name = os.getenv("DEFAULT_MODEL", model_name)

        common_kwargs = dict(
            model=model_name,
            max_tokens=1000,
            temperature=0.7,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
        )

        if self.provider == "watsonx":
            self.model = ModelInference(**common_kwargs, project_id=os.getenv("WATSONX_PROJECT_ID"))
        else:
            self.model = ModelInference(**common_kwargs)
            
    def analyze_prompt(self, user_prompt: str, framework: str) -> Dict[str, Any]:
        """
        Analyze a natural language prompt to generate agent configuration.

        Args:
            user_prompt: The natural language description
            framework: The agent framework to use

        Returns:
            A dictionary containing the agent configuration
        """
        self._initialize_model()
        system_prompt = self._get_system_prompt_for_framework(framework)

        try:
            messages: List[Message] = [
                Message(role="system", content=system_prompt),
                Message(role="user", content=user_prompt)
            ]

            response = self.model.generate_text(messages)

            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                if st is not None:
                    st.warning("Could not extract valid JSON from model response. Using default configuration.")
                return self._get_default_config(framework)

        except Exception as e:
            if st is not None:
                st.error(f"Error in analyzing prompt: {e}")
            return self._get_default_config(framework)


    def _get_system_prompt_for_framework(self, framework: str) -> str:
        """
        Get the system prompt for the specified framework.
        
        Args:
            framework: The agent framework to use
            
        Returns:
            The system prompt for the framework
        """
        if framework == "crewai":
            return """
            You are an expert at creating AI research assistants using CrewAI. Based on the user's request,
            suggest appropriate agents, their roles, tools, and tasks. 
            
            CRITICAL REQUIREMENTS:
            1. Create specialized agents with distinct roles and expertise
            2. ALWAYS assign the most appropriate agent to each task based on their role/expertise
            3. Each task must have an "agent" field with the exact agent name
            4. Match agent specialization to task requirements
            
            Process Types:
            - Sequential: Tasks executed one after another in order
            - Hierarchical: A manager agent coordinates and delegates tasks to specialized agents
            
            Format your response as JSON with this structure:
            {
                "process": "sequential" or "hierarchical",
                "agents": [
                    {
                        "name": "agent_name",
                        "role": "specific specialized role",
                        "goal": "clear specific goal",
                        "backstory": "relevant professional backstory",
                        "tools": ["relevant_tool1", "relevant_tool2"],
                        "verbose": true,
                        "allow_delegation": true/false
                    }
                ],
                "tasks": [
                    {
                        "name": "task_name",
                        "description": "detailed task description",
                        "tools": ["required tools for this task"],
                        "agent": "exact_agent_name_from_above",
                        "expected_output": "specific expected output"
                    }
                ]
            }
            
            AGENT-TASK ASSIGNMENT RULES:
            - Research tasks → Research Specialist/Analyst
            - Data collection → Data Specialist/Collector  
            - Analysis tasks → Data Analyst/Statistician
            - Writing tasks → Content Writer/Technical Writer
            - Review tasks → Quality Reviewer/Editor
            - Coordination tasks → Project Manager/Coordinator
            
            ALWAYS ensure each task has the most suitable agent assigned based on the agent's role and expertise.
            Use exact agent names (matching the "name" field in agents array) in the "agent" field of tasks.
            """
        elif framework == "crewai-flow":
            return """
            You are an expert at creating AI research assistants using CrewAI Flow. Based on the user's request,
            suggest appropriate agents, their roles, tools, and tasks organized in a workflow. 
            
            CRITICAL REQUIREMENTS:
            1. Create specialized agents with distinct roles and expertise
            2. ALWAYS assign the most appropriate agent to each task based on their role/expertise
            3. Each task must have an "agent" field with the exact agent name
            4. Match agent specialization to task requirements
            
            Process Types:
            - Sequential: Tasks flow through a predefined sequence with specific agent assignments
            - Hierarchical: A manager coordinates the flow and delegates to specialized agents
            
            Format your response as JSON with this structure:
            {
                "process": "sequential" or "hierarchical",
                "agents": [
                    {
                        "name": "agent_name",
                        "role": "specific specialized role",
                        "goal": "clear specific goal",
                        "backstory": "relevant professional backstory",
                        "tools": ["relevant_tool1", "relevant_tool2"],
                        "verbose": true,
                        "allow_delegation": true/false
                    }
                ],
                "tasks": [
                    {
                        "name": "task_name",
                        "description": "detailed task description",
                        "tools": ["required tools for this task"],
                        "agent": "exact_agent_name_from_above",
                        "expected_output": "specific expected output"
                    }
                ]
            }
            
            ALWAYS ensure proper agent-to-task matching based on expertise and specialization.
            """
        elif framework == "langgraph":
            return """
            You are an expert at creating AI agents using LangChain's LangGraph framework. Based on the user's request,
            suggest appropriate agents, their roles, tools, and nodes for the graph. Format your response as JSON with this structure:
            {
                "agents": [
                    {
                        "name": "agent name",
                        "role": "specific role description",
                        "goal": "clear goal",
                        "tools": ["tool1", "tool2"],
                        "llm": "model name (e.g., gpt-4.1-mini)"
                    }
                ],
                "nodes": [
                    {
                        "name": "node name",
                        "description": "detailed description",
                        "agent": "agent name"
                    }
                ],
                "edges": [
                    {
                        "source": "source node name",
                        "target": "target node name",
                        "condition": "condition description (optional)"
                    }
                ]
            }
            """
        elif framework == "react":
            return """
            You are an expert at creating AI agents using the ReAct (Reasoning + Acting) framework. 
            Based on the user's request, design an agent with reasoning steps and tool usage.

            Format your response strictly as JSON with this structure:
            {
                "agents": [
                    {
                        "name": "agent name",
                        "role": "specific role description",
                        "goal": "clear goal",
                        "tools": ["tool1", "tool2"],
                        "llm": "model name (e.g., gpt-4.1-mini)"
                    }
                ],
                "tools": [
                    {
                        "name": "tool name",
                        "description": "detailed description of what the tool does",
                        "parameters": {
                            "param1": "parameter description",
                            "param2": "parameter description"
                        }
                    }
                ],
                "examples": [
                    {
                        "query": "example user query",
                        "thought": "single-step thought",
                        "action": "example action",
                        "observation": "example observation",
                        "final_answer": "example final answer"
                    }
                ]
            }
            """
        elif framework == "react-lcel":
            return """
            You are an expert at creating AI agents using the ReAct (Reasoning + Acting) framework, 
            implemented with LangChain Expression Language (LCEL). 
            The agent should demonstrate **multi-step reasoning** with clear intermediate steps.

            Format your response strictly as JSON with this structure:
            {
                "agents": [
                    {
                        "name": "agent name",
                        "role": "specific role description",
                        "goal": "clear goal",
                        "tools": ["tool1", "tool2"],
                        "llm": "model name (e.g., gpt-4.1-mini)"
                    }
                ],
                "tools": [
                    {
                        "name": "tool name",
                        "description": "detailed description of what the tool does",
                        "parameters": {
                            "param1": "parameter description",
                            "param2": "parameter description"
                        },
                        "examples": [
                            {"input": "example input", "output": "expected output"}
                        ]
                    }
                ],
                "examples": [
                    {
                        "query": "example user query",
                        "thoughts": [
                            "step 1 thought",
                            "step 2 thought"
                        ],
                        "actions": [
                            {"tool": "tool name", "input": "tool input"}
                        ],
                        "observations": [
                            "result from tool call"
                        ],
                        "final_answer": "example final answer"
                    }
                ]
            }
            """
        elif framework == "agno":
            return """
            You are an expert at creating AI agents using the Agno framework. Based on the user's request,
            suggest appropriate agents, their roles, tools, and tasks. 
            
            CRITICAL REQUIREMENTS:
            1. Create specialized agents with distinct roles and expertise
            2. ALWAYS assign the most appropriate agent to each task based on their role/expertise
            3. Each task must have an "agent" field with the exact agent name
            4. Match agent specialization to task requirements
            
            Process Types:
            - Sequential: Tasks executed one after another in order
            
            Format your response as JSON with this structure:
            {
                "model_id": "model name (e.g., gpt-4o)",
                "process": "sequential",
                "agents": [
                    {
                        "name": "agent_name",
                        "role": "specific specialized role",
                        "goal": "clear specific goal",
                        "backstory": "relevant professional backstory",
                        "tools": ["relevant_tool1", "relevant_tool2"],
                        "verbose": true,
                        "allow_delegation": true/false
                    }
                ],
                "tasks": [
                    {
                        "name": "task_name",
                        "description": "detailed task description",
                        "tools": ["required tools for this task"],
                        "agent": "exact_agent_name_from_above",
                        "expected_output": "specific expected output"
                    }
                ]
            }
            """
        else:
            return """
            You are an expert at creating AI research assistants. Based on the user's request,
            suggest appropriate agents, their roles, tools, and tasks.
            """

    def _get_default_config(self, framework: str) -> Dict[str, Any]:
        """
        Get a default configuration for the specified framework.
        
        Args:
            framework: The agent framework to use
            
        Returns:
            A default configuration dictionary
        """
        if framework == "crewai":
            return {
                "process": "sequential",  # Default to sequential
                "agents": [
                    {
                        "name": "research_specialist",
                        "role": "Research Specialist",
                        "goal": "Conduct thorough research and gather information",
                        "backstory": "Expert researcher with years of experience in data gathering and analysis",
                        "tools": ["search_tool", "web_scraper"],
                        "verbose": True,
                        "allow_delegation": False
                    },
                    {
                        "name": "content_writer",
                        "role": "Content Writer",
                        "goal": "Create clear and comprehensive written content",
                        "backstory": "Professional writer skilled in creating engaging and informative content",
                        "tools": ["writing_tool", "grammar_checker"],
                        "verbose": True,
                        "allow_delegation": False
                    }
                ],
                "tasks": [
                    {
                        "name": "research_task",
                        "description": "Gather information and conduct research on the given topic",
                        "tools": ["search_tool"],
                        "agent": "research_specialist",
                        "expected_output": "Comprehensive research findings and data"
                    },
                    {
                        "name": "writing_task",
                        "description": "Create written content based on research findings",
                        "tools": ["writing_tool"],
                        "agent": "content_writer",
                        "expected_output": "Well-written content document"
                    }
                ]
            }
        elif framework == "crewai-flow":
            return {
                "process": "sequential",  # Default to sequential
                "agents": [
                    {
                        "name": "research_specialist",
                        "role": "Research Specialist",
                        "goal": "Conduct thorough research and gather information",
                        "backstory": "Expert researcher with years of experience in data gathering and analysis",
                        "tools": ["search_tool", "web_scraper"],
                        "verbose": True,
                        "allow_delegation": False
                    },
                    {
                        "name": "content_writer",
                        "role": "Content Writer",
                        "goal": "Create clear and comprehensive written content",
                        "backstory": "Professional writer skilled in creating engaging and informative content",
                        "tools": ["writing_tool", "grammar_checker"],
                        "verbose": True,
                        "allow_delegation": False
                    }
                ],
                "tasks": [
                    {
                        "name": "research_task",
                        "description": "Gather information and conduct research on the given topic",
                        "tools": ["search_tool"],
                        "agent": "research_specialist",
                        "expected_output": "Comprehensive research findings and data"
                    },
                    {
                        "name": "writing_task",
                        "description": "Create written content based on research findings",
                        "tools": ["writing_tool"],
                        "agent": "content_writer",
                        "expected_output": "Well-written content document"
                    }
                ]
            }
        
        elif framework == "langgraph":
            return {
                "agents": [{
                    "name": "default_assistant",
                    "role": "General Assistant",
                    "goal": "Help with basic tasks",
                    "tools": ["basic_tool"],
                    "llm": "gpt-4.1-mini"
                }],
                "nodes": [{
                    "name": "process_input",
                    "description": "Process user input",
                    "agent": "default_assistant"
                }],
                "edges": [{
                    "source": "process_input",
                    "target": "END",
                    "condition": "task completed"
                }]
            }
        elif framework == "react":
            return {
                "agents": [{
                    "name": "default_assistant",
                    "role": "General Assistant",
                    "goal": "Help with basic tasks",
                    "tools": ["basic_tool"],
                    "llm": "gpt-4.1-mini"
                }],
                "tools": [{
                    "name": "basic_tool",
                    "description": "A basic utility tool",
                    "parameters": {"input": "User input to process"}
                }],
                "examples": [...]
            }
        elif framework == "react-lcel":
            return {
                "agents": [{
                    "name": "default_assistant",
                    "role": "General A"
                    "ssistant",
                    "goal": "Help with multi-step tasks",
                    "tools": ["basic_tool"],
                    "llm": "llm"
                }],
                "tools": [{
                    "name": "basic_tool",
                    "description": "A basic utility tool",
                    "parameters": {"input": "User input to process"},
                    "examples": [{"input": "search cats", "output": "cat info"}]
                }],
                "examples": [{
                    "query": "Find trending AI research papers",
                    "thoughts": [
                        "I should search for trending AI papers",
                        "I should summarize the findings"
                    ],
                    "actions": [
                        {"tool": "basic_tool", "input": "trending AI papers"}
                    ],
                    "observations": [
                        "Found 3 relevant papers"
                    ],
                    "final_answer": "Here are the latest AI papers..."
                }]
            }
        elif framework == "agno":
            return {
                "model_id": "gpt-4o",
                "process": "sequential",  # Default to sequential
                "agents": [
                    {
                        "name": "research_specialist",
                        "role": "Research Specialist",
                        "goal": "Conduct thorough research and gather information",
                        "backstory": "Expert researcher with years of experience in data gathering and analysis",
                        "tools": ["search_tool", "web_scraper"],
                        "verbose": True,
                        "allow_delegation": False
                    },
                    {
                        "name": "content_writer",
                        "role": "Content Writer",
                        "goal": "Create clear and comprehensive written content",
                        "backstory": "Professional writer skilled in creating engaging and informative content",
                        "tools": ["writing_tool", "grammar_checker"],
                        "verbose": True,
                        "allow_delegation": False
                    }
                ],
                "tasks": [
                    {
                        "name": "research_task",
                        "description": "Gather information and conduct research on the given topic",
                        "tools": ["search_tool"],
                        "agent": "research_specialist",
                        "expected_output": "Comprehensive research findings and data"
                    },
                    {
                        "name": "writing_task",
                        "description": "Create written content based on research findings",
                        "tools": ["writing_tool"],
                        "agent": "content_writer",
                        "expected_output": "Well-written content document"
                    }
                ]
            }

        else:
            return {}
