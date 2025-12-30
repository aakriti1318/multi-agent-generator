"""
Streamlit UI for Multi-Agent Generator.
"""
import os
import time
import streamlit as st
import json
from dotenv import load_dotenv

from multi_agent_generator.generator import AgentGenerator
from multi_agent_generator.frameworks.crewai_generator import create_crewai_code
from multi_agent_generator.frameworks.langgraph_generator import create_langgraph_code
from multi_agent_generator.frameworks.react_generator import create_react_code
from multi_agent_generator.frameworks.crewai_flow_generator import create_crewai_flow_code
from multi_agent_generator.frameworks.agno_generator import create_agno_code

# New imports for advanced features
from multi_agent_generator.tools import get_tool_registry, ToolCategory, ToolGenerator, generate_tool_from_description
from multi_agent_generator.orchestration import (
    PatternType, get_pattern, list_patterns, Orchestrator, create_orchestrated_system
)
from multi_agent_generator.evaluation import (
    TestGenerator, generate_tests, AgentEvaluator, evaluate_agent_output
)

# Load environment variables
load_dotenv()

def create_code_block(config, framework):
    """Generate code for the selected framework."""
    if framework == "crewai":
        return create_crewai_code(config)
    elif framework == "crewai-flow":
        return create_crewai_flow_code(config)
    elif framework == "langgraph":
        return create_langgraph_code(config)
    elif framework == "react":
        return create_react_code(config)
    elif framework == "agno":
        return create_agno_code(config)
    else:
        return "# Invalid framework"


# ==================== NEW FEATURE PAGES ====================

def render_tool_discovery_page():
    """Render the Tool Auto-Discovery page."""
    st.header("Tool Auto-Discovery & Generation")
    st.write("Browse pre-built tools or generate custom tools from descriptions.")
    
    tab1, tab2, tab3 = st.tabs(["Tool Library", "Generate Custom Tool", "Suggest Tools"])
    
    with tab1:
        st.subheader("Pre-built Tool Library")
        registry = get_tool_registry()
        
        # Category filter
        categories = ["All"] + [c.value for c in ToolCategory]
        selected_category = st.selectbox("Filter by Category:", categories)
        
        # Get tools
        if selected_category == "All":
            tools = registry.list_all()
        else:
            tools = registry.list_by_category(ToolCategory(selected_category))
        
        # Display tools
        for tool in tools:
            with st.expander(f"{tool.name}", expanded=False):
                st.write(f"**Description:** {tool.description}")
                st.write(f"**Category:** {tool.category.value}")
                
                if tool.parameters:
                    st.write("**Parameters:**")
                    for param, info in tool.parameters.items():
                        required = "Required" if info.get("required", False) else "Optional"
                        st.write(f"  - `{param}` ({info.get('type', 'str')}): {info.get('description', '')} [{required}]")
                
                if tool.requires_api_key:
                    st.warning(f"Requires API key: `{tool.api_key_env_var}`")
                
                if tool.dependencies:
                    st.info(f"Dependencies: {', '.join(tool.dependencies)}")
                
                if st.button(f"Copy Code", key=f"copy_{tool.name}"):
                    st.code(tool.code_template, language="python")
    
    with tab2:
        st.subheader("Generate Custom Tool")
        st.write("Describe what you need, and we'll generate the tool code for you.")
        
        tool_description = st.text_area(
            "Describe your tool:",
            placeholder="e.g., A tool that fetches weather data from an API and returns temperature and conditions",
            height=100
        )
        
        if st.button("Generate Tool", disabled=not tool_description):
            with st.spinner("Generating tool..."):
                try:
                    generated = generate_tool_from_description(tool_description)
                    
                    st.success(f"Generated tool: `{generated.name}`")
                    st.write(f"**Category:** {generated.category.value}")
                    
                    st.subheader("Generated Code:")
                    st.code(generated.code, language="python")
                    
                    st.download_button(
                        "Download Tool",
                        generated.code,
                        file_name=f"{generated.name}.py",
                        mime="text/plain"
                    )
                except Exception as e:
                    st.error(f"Error generating tool: {str(e)}")
    
    with tab3:
        st.subheader("Suggest Tools for Your Task")
        st.write("Describe your agent's task, and we'll suggest relevant tools.")
        
        task_description = st.text_area(
            "Describe your agent's task:",
            placeholder="e.g., Research the latest AI news and summarize the findings into a report",
            height=100
        )
        
        if st.button("Get Suggestions", disabled=not task_description):
            generator = ToolGenerator()
            suggestions = generator.suggest_tools(task_description)
            
            if suggestions:
                st.success(f"Found {len(suggestions)} relevant tools:")
                for tool in suggestions:
                    with st.expander(f"{tool.name}", expanded=True):
                        st.write(tool.description)
                        if tool.code_template:
                            st.code(tool.code_template, language="python")
            else:
                st.info("No pre-built tools found. Try generating a custom tool!")


def render_orchestration_page():
    """Render the Orchestration Patterns page."""
    st.header("Multi-Agent Orchestration Patterns")
    st.write("Select a pre-built orchestration pattern for your multi-agent system.")
    
    tab1, tab2, tab3 = st.tabs(["Pattern Selector", "Configure Pattern", "Generate Code"])
    
    # Get available patterns
    patterns = list_patterns()
    
    with tab1:
        st.subheader("Available Patterns")
        
        cols = st.columns(2)
        for i, pattern_info in enumerate(patterns):
            with cols[i % 2]:
                with st.container(border=True):
                    st.subheader(f"{pattern_info['name']}")
                    st.write(pattern_info['description'])
                    st.write("**Best for:**")
                    for use_case in pattern_info['use_cases'][:3]:
                        st.write(f"  • {use_case}")
                    
                    if st.button(f"Select", key=f"select_{pattern_info['type']}"):
                        st.session_state.selected_pattern = pattern_info['type']
                        st.success(f"Selected: {pattern_info['name']}")
    
    with tab2:
        st.subheader("Configure Your Pattern")
        
        # Pattern selection
        pattern_options = {p['name']: p['type'] for p in patterns}
        selected_pattern_name = st.selectbox(
            "Select Pattern:",
            list(pattern_options.keys()),
            index=0
        )
        selected_pattern_type = PatternType(pattern_options[selected_pattern_name])
        st.session_state.selected_pattern = selected_pattern_type.value
        
        # Number of agents
        num_agents = st.slider("Number of Agents:", min_value=2, max_value=6, value=3)
        
        # Framework selection
        framework = st.selectbox(
            "Target Framework:",
            ["langgraph", "crewai", "crewai-flow"]
        )
        
        # Task description
        task_description = st.text_area(
            "Describe your task:",
            placeholder="e.g., Research a topic, analyze the findings, and create a comprehensive report",
            height=100
        )
        
        st.session_state.orchestration_config = {
            "pattern": selected_pattern_type,
            "num_agents": num_agents,
            "framework": framework,
            "description": task_description
        }
        
        # Show pattern template
        pattern = get_pattern(selected_pattern_type)
        st.write("**Pattern Configuration Template:**")
        st.json(pattern.get_config_template())
    
    with tab3:
        st.subheader("Generate Orchestration Code")
        
        config = st.session_state.get("orchestration_config", {})
        
        if config and config.get("description"):
            if st.button("Generate Orchestration Code"):
                with st.spinner("Generating orchestration code..."):
                    try:
                        code = create_orchestrated_system(
                            description=config["description"],
                            num_agents=config["num_agents"],
                            framework=config["framework"],
                            pattern=config["pattern"]
                        )
                        
                        st.session_state.orchestration_code = code
                        st.success("Orchestration code generated!")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        if "orchestration_code" in st.session_state:
            st.code(st.session_state.orchestration_code, language="python")
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "Download Code",
                    st.session_state.orchestration_code,
                    file_name="orchestrated_agents.py",
                    mime="text/plain"
                )


def render_evaluation_page():
    """Render the Evaluation & Testing page."""
    st.header("Evaluation & Testing Framework")
    st.write("Generate tests and evaluate your agent outputs.")
    
    tab1, tab2, tab3 = st.tabs(["Generate Tests", "Evaluate Output", "Test Results"])
    
    with tab1:
        st.subheader("Auto-Generate Test Suite")
        
        # Use existing config if available
        if "config" in st.session_state:
            st.info("Using your generated agent configuration")
            use_existing = st.checkbox("Use existing configuration", value=True)
        else:
            use_existing = False
        
        if use_existing and "config" in st.session_state:
            config = st.session_state.config
            framework = st.session_state.get("framework", "crewai")
        else:
            st.write("Or provide a sample configuration:")
            config_json = st.text_area(
                "Agent Configuration (JSON):",
                value=json.dumps({
                    "agents": [
                        {"name": "researcher", "role": "Research Specialist", "goal": "Research topics", "tools": ["web_search"]},
                        {"name": "writer", "role": "Content Writer", "goal": "Write content", "tools": []}
                    ],
                    "tasks": [
                        {"name": "research_task", "description": "Research the topic", "agent": "researcher", "expected_output": "Research findings"},
                        {"name": "write_task", "description": "Write the report", "agent": "writer", "expected_output": "Written report"}
                    ]
                }, indent=2),
                height=300
            )
            try:
                config = json.loads(config_json)
            except:
                config = {}
            
            framework = st.selectbox("Framework:", ["crewai", "langgraph", "react", "agno"])
        
        # Test types to include
        st.write("**Select Test Types:**")
        col1, col2 = st.columns(2)
        with col1:
            include_unit = st.checkbox("Unit Tests", value=True)
            include_integration = st.checkbox("Integration Tests", value=True)
            include_e2e = st.checkbox("End-to-End Tests", value=True)
        with col2:
            include_performance = st.checkbox("Performance Tests", value=False)
            include_reliability = st.checkbox("Reliability Tests", value=True)
            include_quality = st.checkbox("Quality Tests", value=True)
        
        if st.button("Generate Test Suite", disabled=not config):
            with st.spinner("Generating tests..."):
                try:
                    test_code = generate_tests(config, framework, "pytest")
                    st.session_state.generated_tests = test_code
                    st.success("Test suite generated!")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        if "generated_tests" in st.session_state:
            st.code(st.session_state.generated_tests, language="python")
            st.download_button(
                "Download Test File",
                st.session_state.generated_tests,
                file_name="test_agents.py",
                mime="text/plain"
            )
    
    with tab2:
        st.subheader("Evaluate Agent Output")
        st.write("Test your agent's response quality.")
        
        query = st.text_input(
            "Input Query:",
            placeholder="What is machine learning?"
        )
        
        response = st.text_area(
            "Agent Response:",
            placeholder="Paste your agent's response here...",
            height=200
        )
        
        # Optional evaluation parameters
        with st.expander("Advanced Options"):
            expected_keywords = st.text_input(
                "Expected Keywords (comma-separated):",
                placeholder="machine, learning, data, algorithm"
            )
            expected_format = st.selectbox(
                "Expected Format:",
                ["", "numbered_list", "bullet_list", "json", "markdown", "code"]
            )
            ground_truth = st.text_area(
                "Ground Truth (optional):",
                placeholder="The expected correct answer...",
                height=100
            )
        
        if st.button("Evaluate", disabled=not (query and response)):
            with st.spinner("Evaluating..."):
                keywords = [k.strip() for k in expected_keywords.split(",")] if expected_keywords else None
                
                result = evaluate_agent_output(
                    query=query,
                    response=response,
                    expected_keywords=keywords,
                    expected_format=expected_format if expected_format else None,
                    ground_truth=ground_truth if ground_truth else None
                )
                
                st.session_state.evaluation_result = result
        
        if "evaluation_result" in st.session_state:
            result = st.session_state.evaluation_result
            
            # Status badge
            if result.passed:
                st.success(f"PASSED - Overall Score: {result.metrics.overall_score():.2f}")
            else:
                st.error(f"FAILED - Overall Score: {result.metrics.overall_score():.2f}")
            
            # Metrics visualization
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Relevance", f"{result.metrics.relevance_score:.2f}")
            with col2:
                st.metric("Completeness", f"{result.metrics.completeness_score:.2f}")
            with col3:
                st.metric("Coherence", f"{result.metrics.coherence_score:.2f}")
            with col4:
                st.metric("Task Completion", f"{result.metrics.task_completion_rate:.2f}")
            
            # Feedback
            st.write("**Feedback:**")
            for feedback in result.feedback:
                st.write(f"  • {feedback}")
            
            if result.errors:
                st.write("**Errors:**")
                for error in result.errors:
                    st.write(f"  - {error}")
    
    with tab3:
        st.subheader("Test Results Dashboard")
        
        if "evaluation_result" in st.session_state:
            result = st.session_state.evaluation_result
            
            # Export options
            st.write("**Export Results:**")
            st.json(result.to_dict())
            
            st.download_button(
                "Download Results (JSON)",
                json.dumps(result.to_dict(), indent=2),
                file_name="evaluation_results.json",
                mime="application/json"
            )
        else:
            st.info("Run an evaluation to see results here.")


def main():
    """Main entry point for the Streamlit app."""
    st.set_page_config(page_title="Multi-Framework Agent Generator", page_icon="", layout="wide")
    
    # Initialize session state for model provider
    if 'model_provider' not in st.session_state:
        st.session_state.model_provider = 'openai'
    
    # Initialize keys in session state if not present
    for key in ['openai_api_key', 'watsonx_api_key', 'watsonx_project_id']:
        if key not in st.session_state:
            st.session_state[key] = ''
    
    # Page Navigation in Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select a page:",
        [
            "Agent Generator",
            "Tool Discovery",
            "Orchestration Patterns",
            "Evaluation & Testing"
        ],
        key="page_nav"
    )
    
    st.sidebar.markdown("---")
    
    # Route to the appropriate page
    if page == "Tool Discovery":
        render_tool_discovery_page()
        return
    elif page == "Orchestration Patterns":
        render_orchestration_page()
        return
    elif page == "Evaluation & Testing":
        render_evaluation_page()
        return
    
    # Default: Agent Generator page
    st.title("Multi-Framework Agent Generator")
    st.write("Generate agent code for different frameworks based on your requirements!")
    
    # Sidebar for LLM provider selection and API keys
    st.sidebar.title("LLM Provider Settings")
    model_provider = st.sidebar.radio(
        "Choose LLM Provider:",
        ["OpenAI", "WatsonX"],
        index=0 if st.session_state.model_provider == 'openai' else 1,
        key="provider_radio"
    )
    
    st.session_state.model_provider = model_provider.lower()
    
    # Display provider badge
    if model_provider == "OpenAI":
        st.sidebar.markdown("![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)")
    else:
        st.sidebar.markdown("![IBM](https://img.shields.io/badge/IBM-052FAD?style=for-the-badge&logo=ibm&logoColor=white)")
    
    # API Key management in sidebar
    with st.sidebar.expander("API Credentials", expanded=False):
        if model_provider == "OpenAI":
            # Check for environment variable first
            openai_key_env = os.getenv("OPENAI_API_KEY", "")
            if openai_key_env:
                st.success("OpenAI API Key found in environment variables.")
                st.session_state.openai_api_key = openai_key_env
            else:
                # Then check session state
                if st.session_state.openai_api_key:
                    st.success("OpenAI API Key set for this session.")
                else:
                    # Otherwise prompt for key
                    api_key = st.text_input(
                        "Enter OpenAI API Key:", 
                        value=st.session_state.openai_api_key,
                        type="password",
                        key="openai_key_input"
                    )
                    if api_key:
                        st.session_state.openai_api_key = api_key
                        st.success("API Key saved for this session.")
                        
        else:  # WatsonX
            # Check for environment variables first
            watsonx_key_env = os.getenv("WATSONX_API_KEY", "")
            watsonx_project_env = os.getenv("WATSONX_PROJECT_ID", "")
            
            if watsonx_key_env and watsonx_project_env:
                st.success("WatsonX credentials found in environment variables.")
                st.session_state.watsonx_api_key = watsonx_key_env
                st.session_state.watsonx_project_id = watsonx_project_env
            else:
                # Otherwise check session state or prompt
                col1, col2 = st.columns(2)
                with col1:
                    api_key = st.text_input(
                        "WatsonX API Key:", 
                        value=st.session_state.watsonx_api_key,
                        type="password",
                        key="watsonx_key_input"
                    )
                    if api_key:
                        st.session_state.watsonx_api_key = api_key
                        
                with col2:
                    project_id = st.text_input(
                        "WatsonX Project ID:",
                        value=st.session_state.watsonx_project_id,
                        key="watsonx_project_input"
                    )
                    if project_id:
                        st.session_state.watsonx_project_id = project_id
                        
                if st.session_state.watsonx_api_key and st.session_state.watsonx_project_id:
                    st.success("WatsonX credentials saved for this session.")
    
    # Show model information
    with st.sidebar.expander("Model Information", expanded=False):
        if model_provider == "OpenAI":
            st.write("**Model**: GPT-4.1-mini")
            st.write("OpenAI's models provide advanced capabilities for natural language understanding and code generation.")
        else:
            st.write("**Model**: Llama-3-70B-Instruct (via WatsonX)")
            st.write("IBM WatsonX provides enterprise-grade access to Llama and other foundation models with IBM's security and governance features.")
    
    # Framework selection
    st.sidebar.title("Framework Selection")
    framework = st.sidebar.radio(
        "Choose a framework:",
        ["crewai", "crewai-flow", "langgraph", "react", "agno"],
        format_func=lambda x: {
            "crewai": "CrewAI",
            "crewai-flow": "CrewAI Flow",
            "langgraph": "LangGraph",
            "react": "ReAct Framework",
            "agno": "Agno Framework"
        }[x],
        key="framework_radio"
    )
    
    framework_descriptions = {
        "crewai": """
        **CrewAI** is a framework for orchestrating role-playing autonomous AI agents. 
        It allows you to create a crew of agents that work together to accomplish tasks, 
        with each agent having a specific role, goal, and backstory.
        """,
        "crewai-flow": """
        **CrewAI Flow** extends CrewAI with event-driven workflows. 
        It enables you to define multi-step processes with clear transitions between steps,
        maintaining state throughout the execution, and allowing for complex orchestration
        patterns like sequential, parallel, and conditional execution.
        """,
        "langgraph": """
        **LangGraph** is LangChain's framework for building stateful, multi-actor applications with LLMs.
        It provides a way to create directed graphs where nodes are LLM calls, tools, or other operations, 
        and edges represent the flow of information between them.
        """,
        "react": """
        **ReAct** (Reasoning + Acting) is a framework that combines reasoning and action in LLM agents.
        It prompts the model to generate both reasoning traces and task-specific actions in an interleaved manner, 
        creating a synergy between the two that leads to improved performance.
        """,
        "agno": """
        **Agno** is a framework for building and managing agent-based applications.
        It provides a way to define agents, their goals, and the tasks they need to accomplish,
        along with tools for coordinating their actions and sharing information.
        """
    }
    
    st.sidebar.markdown(framework_descriptions[framework])
    
    # Sidebar for examples
    st.sidebar.title("Example Prompts")
    example_prompts = {
        "Research Assistant": "I need a research assistant that summarizes papers and answers questions",
        "Content Creation": "I need a team to create viral social media content and manage our brand presence",
        "Data Analysis": "I need a team to analyze customer data and create visualizations",
        "Technical Writing": "I need a team to create technical documentation and API guides"
    }
    
    selected_example = st.sidebar.selectbox("Choose an example:", list(example_prompts.keys()), key="example_select")
    
    # Main input area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Define Your Requirements")
        user_prompt = st.text_area(
            "Describe what you need:",
            value=example_prompts[selected_example],
            height=100,
            key="user_prompt"
        )
        
        # Add workflow steps input for CrewAI Flow
        if framework == "crewai-flow":
            st.subheader("Define Workflow Steps")
            workflow_steps = st.text_area(
                "List the steps in your workflow (one per line):",
                value="1. Data collection\n2. Analysis\n3. Report generation",
                height=100,
                key="workflow_steps"
            )
        
        # Generate button with LLM provider name
        if st.button(f"Generate using {model_provider} & {framework.upper()}", key="generate_button"):
            # Validation checks
            api_key_missing = False
            if model_provider == "OpenAI" and not st.session_state.openai_api_key:
                st.error("Please set your OpenAI API Key in the sidebar")
                api_key_missing = True
            elif model_provider == "WatsonX" and (not st.session_state.watsonx_api_key or not st.session_state.watsonx_project_id):
                st.error("Please set your WatsonX API Key and Project ID in the sidebar")
                api_key_missing = True
                
            if not api_key_missing:
                with st.spinner(f"Generating your {framework} code using {model_provider}..."):
                    
                    if model_provider == "OpenAI" and st.session_state.openai_api_key:
                        os.environ["OPENAI_API_KEY"] = st.session_state.openai_api_key
                    elif model_provider == "WatsonX":
                        if st.session_state.watsonx_api_key:
                            os.environ["WATSONX_API_KEY"] = st.session_state.watsonx_api_key
                        if st.session_state.watsonx_project_id:
                            os.environ["WATSONX_PROJECT_ID"] = st.session_state.watsonx_project_id
                            
                    # Initialize generator with selected provider
                    generator = AgentGenerator(provider=model_provider.lower())
                    
                    # Handle CrewAI Flow differently
                    if framework == "crewai-flow":
                        # Extract workflow steps
                        steps = [step.strip() for step in workflow_steps.split("\n") if step.strip()]
                        steps = [step[2:].strip() if step[0].isdigit() and step[1] == "." else step for step in steps]
                        
                        # Append workflow information to the prompt
                        flow_prompt = f"{user_prompt}\n\nWorkflow steps:\n"
                        for i, step in enumerate(steps):
                            flow_prompt += f"{i+1}. {step}\n"
                        
                        # Use the CrewAI analyzer but modify for flow
                        config = generator.analyze_prompt(flow_prompt, "crewai")
                        
                        # Modify config to ensure tasks align with workflow steps
                        if len(config["tasks"]) < len(steps):
                            # Add missing tasks
                            for i in range(len(config["tasks"]), len(steps)):
                                config["tasks"].append({
                                    "name": f"step_{i+1}",
                                    "description": f"Execute step: {steps[i]}",
                                    "tools": config["tasks"][0]["tools"] if config["tasks"] else ["basic_tool"],
                                    "agent": config["agents"][0]["name"] if config["agents"] else "default_assistant",
                                    "expected_output": f"Results from {steps[i]}"
                                })
                        elif len(config["tasks"]) > len(steps):
                            # Trim extra tasks
                            config["tasks"] = config["tasks"][:len(steps)]
                            
                        # Update task names and descriptions to match steps
                        for i, step in enumerate(steps):
                            config["tasks"][i]["name"] = f"{step.lower().replace(' ', '_')}"
                            config["tasks"][i]["description"] = f"Execute the '{step}' step"
                        
                        st.session_state.config = config
                        st.session_state.code = create_crewai_flow_code(config)  # Function for Flow
                    else:
                        config = generator.analyze_prompt(user_prompt, framework)
                        st.session_state.config = config
                        st.session_state.code = create_code_block(config, framework)
                        
                    st.session_state.framework = framework
                    
                    time.sleep(0.5)  # Small delay for better UX
                    st.success(f"{framework.upper()} code generated successfully with {model_provider}!")
                    
                    # Add info about the model used
                    if model_provider == "OpenAI":
                        st.info("Generated using GPT-4.1-mini")
                    else:
                        st.info("Generated using Llama-3-70B-Instruct via WatsonX")

    with col2:
        st.subheader("Framework Tips")
        if framework == "crewai":
            st.info("""
            **CrewAI Tips:**
            - Define clear roles for each agent
            - Set specific goals for better performance
            - Consider how agents should collaborate
            - Specify task delegation permissions
            """)
        elif framework == "crewai-flow":
            st.info("""
            **CrewAI Flow Tips:**
            - Define a clear sequence of workflow steps
            - Use the @start decorator for the entry point
            - Use @listen decorators to define step transitions
            - Maintain state between workflow steps
            - Consider how to aggregate results at the end
            """)
        elif framework == "langgraph":
            st.info("""
            **LangGraph Tips:**
            - Design your graph flow carefully
            - Define clear node responsibilities
            - Consider conditional routing between nodes
            - Think about how state is passed between nodes
            """)
        elif framework == "agno":
            st.info("""
            **Agno Tips:**
            - Define clear roles and goals for each agent
            - Assign tasks to appropriate agents
            - Utilize tools effectively for task completion
            - Coordinate agent interactions through the Team
            """)
        else:  # react
            st.info("""
            **ReAct Tips:**
            - Focus on the reasoning steps
            - Define tools with clear descriptions
            - Provide examples of thought processes
            - Consider the observation/action cycle
            """)
        
        # Add provider comparison
        st.subheader("LLM Provider Comparison")
        comparison_md = """
        | Feature | OpenAI | WatsonX |
        | ------- | ------ | ------- |
        | Models | GPT-4o, GPT-3.5, etc. | Llama-3, Granite, etc. |
        | Strengths | State-of-the-art performance | Enterprise security & governance |
        | Best for | Consumer apps, research | Enterprise deployments |
        | Pricing | Token-based | Enterprise contracts |
        """
        st.markdown(comparison_md)

    # Display results
    if 'config' in st.session_state:
        st.subheader("Generated Configuration")
        
        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["Visual Overview", "Code", "JSON Config"])
        
        with tab1:
            current_framework = st.session_state.framework
            
            if current_framework in ["crewai", "crewai-flow"]:
                # Display Agents
                st.subheader("Agents")
                for agent in st.session_state.config["agents"]:
                    with st.expander(f"{agent['role']}", expanded=True):
                        st.write(f"**Goal:** {agent['goal']}")
                        st.write(f"**Backstory:** {agent['backstory']}")
                        st.write(f"**Tools:** {', '.join(agent['tools'])}")
                
                # Display Tasks
                st.subheader("Tasks")
                for task in st.session_state.config["tasks"]:
                    with st.expander(f"{task['name']}", expanded=True):
                        st.write(f"**Description:** {task['description']}")
                        st.write(f"**Expected Output:** {task['expected_output']}")
                        st.write(f"**Assigned to:** {task['agent']}")
                        
                # Show Flow Diagram for CrewAI Flow
                if current_framework == "crewai-flow":
                    st.subheader("Flow Diagram")
                    task_names = [task["name"] for task in st.session_state.config["tasks"]]
                    
                    # Create a simple graph visualization
                    st.write("Event Flow:")
                    flow_html = f"""
                    <div style="text-align: center; padding: 20px;">
                        <div style="display: flex; justify-content: center; align-items: center; flex-wrap: wrap;">
                            <div style="padding: 10px; margin: 5px; background-color: #f0f0f0; border-radius: 5px; text-align: center;">
                                Start
                            </div>
                            <div style="margin: 0 10px;">→</div>
                    """
                    
                    for i, task in enumerate(task_names):
                        flow_html += f"""
                            <div style="padding: 10px; margin: 5px; background-color: #e1f5fe; border-radius: 5px; text-align: center;">
                                {task}
                            </div>
                        """
                        if i < len(task_names) - 1:
                            flow_html += f"""<div style="margin: 0 10px;">→</div>"""
                    
                    flow_html += f"""
                            <div style="margin: 0 10px;">→</div>
                            <div style="padding: 10px; margin: 5px; background-color: #f0f0f0; border-radius: 5px; text-align: center;">
                                End
                            </div>
                        </div>
                    </div>
                    """
                    
                    st.components.v1.html(flow_html, height=150)
                    
                    # Show state elements
                    st.subheader("State Elements")
                    st.code("""
class AgentState(BaseModel):
    query: str
    results: Dict[str, Any]
    current_step: str
                    """, language="python")
                    
                    # Show execution visualization 
                    st.subheader("Execution Flow")
                    st.write("The workflow executes through these phases:")
                    
                    # Create execution flow diagram
                    exec_flow = """
                    ```mermaid
                    flowchart LR
                        A[Initialize] --> B[Process Query]
                        B --> C[Execute Tasks]
                        C --> D[Compile Results]
                        D --> E[Return Final Output]
                    ```
                    """
                    st.markdown(exec_flow)
                    
                    # Show event listeners
                    st.subheader("Event Listeners")
                    event_listeners = "```python\n"
                    event_listeners += "@start()\ndef initialize_workflow(self):\n    # Initialize workflow state\n\n"
                    
                    # Add each task's listener
                    for i, task in enumerate(st.session_state.config["tasks"]):
                        task_name = task["name"].replace("-", "_")
                        previous = "initialize_workflow" if i == 0 else f"execute_{st.session_state.config['tasks'][i-1]['name'].replace('-', '_')}"
                        event_listeners += f"@listen('{previous}')\ndef execute_{task_name}(self, state):\n    # Execute {task['name']} task\n\n"
                    
                    # Add final listener
                    last_task = st.session_state.config["tasks"][-1]["name"].replace("-", "_")
                    event_listeners += f"@listen('execute_{last_task}')\ndef finalize_workflow(self, state):\n    # Compile final results\n"
                    event_listeners += "```"
                    
                    st.markdown(event_listeners)
            
            elif current_framework == "langgraph":
                # Display Agents
                st.subheader("Agents")
                for agent in st.session_state.config["agents"]:
                    with st.expander(f"{agent['role']}", expanded=True):
                        st.write(f"**Goal:** {agent['goal']}")
                        st.write(f"**Tools:** {', '.join(agent['tools'])}")
                        st.write(f"**LLM:** {agent['llm']}")
                
                # Display Nodes
                st.subheader("Graph Nodes")
                for node in st.session_state.config["nodes"]:
                    with st.expander(f"{node['name']}", expanded=True):
                        st.write(f"**Description:** {node['description']}")
                        st.write(f"**Agent:** {node['agent']}")
                
                # Display Edges
                st.subheader("Graph Edges")
                for edge in st.session_state.config["edges"]:
                    with st.expander(f"{edge['source']} -> {edge['target']}", expanded=True):
                        if "condition" in edge:
                            st.write(f"**Condition:** {edge['condition']}")
                
                # Try to render a simple graph visualization
                st.subheader("Graph Visualization")
                st.markdown("""
                ```mermaid
                graph LR
                """)
                
                for edge in st.session_state.config["edges"]:
                    if edge["target"] == "END":
                        st.markdown(f"    {edge['source']}-->END")
                    else:
                        st.markdown(f"    {edge['source']}-->{edge['target']}")
                
                st.markdown("```")
            
            elif current_framework == "react":
                # Display Agents
                st.subheader("Agents")
                for agent in st.session_state.config["agents"]:
                    with st.expander(f"{agent['role']}", expanded=True):
                        st.write(f"**Goal:** {agent['goal']}")
                        st.write(f"**Tools:** {', '.join(agent['tools'])}")
                        st.write(f"**LLM:** {agent['llm']}")
                
                # Display Tools
                st.subheader("Tools")
                for tool in st.session_state.config.get("tools", []):
                    with st.expander(f"{tool['name']}", expanded=True):
                        st.write(f"**Description:** {tool['description']}")
                        st.write("**Parameters:**")
                        for param, desc in tool["parameters"].items():
                            st.write(f"- **{param}**: {desc}")
                
                # Display Examples
                if "examples" in st.session_state.config:
                    st.subheader("Examples")
                    for i, example in enumerate(st.session_state.config["examples"]):
                        with st.expander(f"Example {i+1}: {example['query'][:30]}...", expanded=True):
                            st.write(f"**Query:** {example['query']}")
                            st.write(f"**Thought:** {example['thought']}")
                            st.write(f"**Action:** {example['action']}")
                            st.write(f"**Observation:** {example['observation']}")
                            st.write(f"**Final Answer:** {example['final_answer']}")
            
            # Agno framework display
            elif current_framework == "agno":
                st.subheader("Agents")
                for agent in st.session_state.config.get("agents", []):
                    with st.expander(f"{agent.get('name','agent')}", expanded=True):
                        st.write(f"**Role:** {agent.get('role','')}")
                        if agent.get("goal"): st.write(f"**Goal:** {agent['goal']}")
                        if agent.get("backstory"): st.write(f"**Backstory:** {agent['backstory']}")

                st.subheader("Tasks")
                for task in st.session_state.config.get("tasks", []):
                    with st.expander(f"{task.get('name','task')}", expanded=True):
                        st.write(f"**Description:** {task.get('description','')}")
                        st.write(f"**Expected Output:** {task.get('expected_output','')}")
                        st.write(f"**Assigned to:** {task.get('agent','')}")

        with tab2:
            # Display code with copy button and syntax highlighting
            st.code(st.session_state.code, language="python")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Copy Code to Clipboard", key="copy_code_btn"):
                    st.toast("Code copied to clipboard!")
            
            with col2:
                if st.download_button(
                    "Download as Python File",
                    st.session_state.code,
                    file_name=f"{st.session_state.framework}_agent.py",
                    mime="text/plain",
                    key="download_code_btn"
                ):
                    st.toast("File downloaded!")
        
        with tab3:
            # Display the raw JSON configuration
            st.json(st.session_state.config)
            
            if st.download_button(
                "Download Configuration as JSON",
                json.dumps(st.session_state.config, indent=2),
                file_name=f"{st.session_state.framework}_config.json",
                mime="application/json",
                key="download_json_btn"
            ):
                st.toast("JSON configuration downloaded!")

if __name__ == "__main__":
    main()