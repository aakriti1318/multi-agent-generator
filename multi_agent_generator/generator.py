"""
Agent configuration generator that analyzes user requirements.
"""
import os
import json
import streamlit as st
from typing import Dict, Any, Optional
from .model_inference import create_model_inference, BaseModelInference

class AgentGenerator:
    """
    Generates agent configurations based on natural language descriptions.
    """
    def __init__(self, provider: str = "openai"):
        """
        Initialize the generator with the specified provider.
        
        Args:
            provider: The LLM provider to use ("openai" or "watsonx")
        """
        self.provider = provider.lower()
        
        # Initialize default model configurations
        self._init_model_configs()
        
        # Initialize model on first use instead of constructor
        self.model = None
    
    def _init_model_configs(self):
        """Initialize model configurations for different providers."""
        # OpenAI configuration
        self.openai_config = {
            "model_id": "gpt-4.1-mini",
            "parameters": {
                "max_new_tokens": 1000,  # Max tokens to generate
                "temperature": 0.7,      # Creativity level
                "top_p": 0.95,           # Nucleus sampling
                "frequency_penalty": 0,  # Discourage repetition
                "presence_penalty": 0    # Discourage topic repetition
            }
        }
        
        # WatsonX configuration
        self.watsonx_config = {
            "model_id": "meta-llama/llama-3-3-70b-instruct", 
            "parameters": {
                "decoding_method": "greedy",
                "max_new_tokens": 1000,  # Increased for complex JSON responses
                "min_new_tokens": 0,
                "repetition_penalty": 1
            }
        }
    
    def set_provider(self, provider: str):
        """
        Change the LLM provider.
        
        Args:
            provider: The LLM provider to use ("openai" or "watsonx")
        """
        if provider.lower() not in ["openai", "watsonx"]:
            raise ValueError(f"Unsupported provider: {provider}. Use 'openai' or 'watsonx'.")
            
        self.provider = provider.lower()
        # Reset model so it will be re-initialized with the new provider
        self.model = None
    
    def _initialize_model(self):
        """Initialize the model if it hasn't been initialized yet."""
        if self.model is not None:
            return
            
        if self.provider == "openai":
            # Get API key from environment
            api_key = os.getenv("OPENAI_API_KEY")
            
            if not api_key and hasattr(st, 'session_state') and 'openai_api_key' in st.session_state:
                api_key = st.session_state.openai_api_key
                
            if not api_key and st is not None:
                st.warning("OpenAI API Key not found in environment. Please enter it below.")
                api_key = st.text_input("Enter OpenAI API Key:", type="password", key="openai_key_input")
                if api_key:
                    st.session_state.openai_api_key = api_key
                else:
                    st.stop()
            
            credentials = {"api_key": api_key}
            
            self.model = create_model_inference(
                provider="openai",
                model_id=self.openai_config["model_id"],
                params=self.openai_config["parameters"],
                credentials=credentials
            )
            
        elif self.provider == "watsonx":
            # Get WatsonX credentials
            api_key = os.getenv("WATSONX_API_KEY")
            url = os.getenv("WATSONX_URL", "https://eu-de.ml.cloud.ibm.com")
            project_id = os.getenv("WATSONX_PROJECT_ID")
            
            if not api_key and hasattr(st, 'session_state') and 'watsonx_api_key' in st.session_state:
                api_key = st.session_state.watsonx_api_key
                
            if not project_id and hasattr(st, 'session_state') and 'watsonx_project_id' in st.session_state:
                project_id = st.session_state.watsonx_project_id
                
            # Request credentials if not available
            if (not api_key or not project_id) and st is not None:
                st.warning("WatsonX credentials not found in environment. Please enter them below.")
                col1, col2 = st.columns(2)
                with col1:
                    api_key = st.text_input("Enter WatsonX API Key:", type="password", key="watsonx_key_input")
                with col2:
                    project_id = st.text_input("Enter WatsonX Project ID:", key="watsonx_project_input")
                
                if api_key and project_id:
                    st.session_state.watsonx_api_key = api_key
                    st.session_state.watsonx_project_id = project_id
                else:
                    st.stop()
            
            credentials = {
                "url": url,
                "apikey": api_key
            }
            
            self.model = create_model_inference(
                provider="watsonx",
                model_id=self.watsonx_config["model_id"],
                params=self.watsonx_config["parameters"],
                credentials=credentials,
                project_id=project_id
            )
    
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
            # Format prompt for LLM
            formatted_prompt = f"""<|begin_of_text|>
                                    <|system|>
                                    {system_prompt}
                                    <|user|>
                                    {user_prompt}
                                    <|assistant|>
                                """
            
            # Generate response using the model
            response = self.model.generate_text(prompt=formatted_prompt)
            
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
            You are an expert at creating AI agents using the ReAct (Reasoning + Acting) framework. Based on the user's request,
            suggest appropriate agents, their roles, tools, and specific reasoning steps. Format your response as JSON with this structure:
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
                        "thought": "example thought process",
                        "action": "example action to take",
                        "observation": "example observation",
                        "final_answer": "example final answer"
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
        if framework == "crewai" or framework == "crewai-flow":
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
                    "parameters": {
                        "input": "User input to process"
                    }
                }],
                "examples": [{
                    "query": "Help me find information",
                    "thought": "I need to search for relevant information",
                    "action": "Use search tool",
                    "observation": "Found relevant results",
                    "final_answer": "Here is the information you requested"
                }]
            }
        else:
            return {}
