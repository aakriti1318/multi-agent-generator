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
    else:
        return "# Invalid framework"

def main():
    """Main entry point for the Streamlit app."""
    st.set_page_config(page_title="Multi-Framework Agent Generator", page_icon="🚀", layout="wide")
    
    st.title("Multi-Framework Agent Generator")
    st.write("Generate agent code for different frameworks based on your requirements!")
    
    # Initialize session state for model provider
    if 'model_provider' not in st.session_state:
        st.session_state.model_provider = 'openai'
    
    # Initialize keys in session state if not present
    for key in ['openai_api_key', 'watsonx_api_key', 'watsonx_project_id']:
        if key not in st.session_state:
            st.session_state[key] = ''
    
    # Sidebar for LLM provider selection and API keys
    st.sidebar.title("🤖 LLM Provider Settings")
    model_provider = st.sidebar.radio(
        "Choose LLM Provider:",
        ["OpenAI", "WatsonX","Groq"],
        index=0
        if st.session_state.model_provider == "openai"
        else (1 if st.session_state.model_provider == "watsonx" else 2),
        key="provider_radio",
    )
    
    st.session_state.model_provider = model_provider.lower()
    
    # Display provider badge
    if model_provider == "OpenAI":
        st.sidebar.markdown("![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)")
    elif model_provider == "WatsonX":
        st.sidebar.markdown("![IBM](https://img.shields.io/badge/IBM-052FAD?style=for-the-badge&logo=ibm&logoColor=white)")
    else:
        st.sidebar.markdown("![Groq](https://img.shields.io/badge/Groq-FF4C00?style=for-the-badge&logo=groq&logoColor=white)")
    
    # API Key management in sidebar
    with st.sidebar.expander("🔑 API Credentials", expanded=False):
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
                        
        elif model_provider == "WatsonX": # WatsonX
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
        else:  # Groq
            groq_key_env = os.getenv("GROQ_API_KEY", "")
            if groq_key_env:
                st.success("Groq API Key found in environment variables.")
                st.session_state.groq_api_key = groq_key_env
            else:
                api_key = st.text_input(
                    "Enter Groq API Key:",
                    value=st.session_state.groq_api_key,
                    type="password",
                    key="groq_key_input",
                )
                if api_key:
                    st.session_state.groq_api_key = api_key
                    st.success("Groq API Key saved for this session.")

    # Show model information
    with st.sidebar.expander("ℹ️ Model Information", expanded=False):
        if model_provider == "OpenAI":
            st.write("**Model**: GPT-4.1-mini")
            st.write("OpenAI's models provide advanced capabilities for natural language understanding and code generation.")
        elif model_provider == "WatsonX":
            st.write("**Model**: Llama-3-70B-Instruct (via WatsonX)")
            st.write("IBM WatsonX provides enterprise-grade access to Llama and other foundation models with IBM's security and governance features.")
        else:
            st.write("**Model:** Llama-3.3-70b-versatile via Groq Cloud")
            st.write(
                "Groq Cloud delivers lightning-fast inference on open-weight models optimized for low-latency workloads."
            )
    # Framework selection
    st.sidebar.title("🔄 Framework Selection")
    framework = st.sidebar.radio(
        "Choose a framework:",
        ["crewai", "crewai-flow", "langgraph", "react"],
        format_func=lambda x: {
            "crewai": "CrewAI",
            "crewai-flow": "CrewAI Flow",
            "langgraph": "LangGraph",
            "react": "ReAct Framework"
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
        """
    }
    
    st.sidebar.markdown(framework_descriptions[framework])
    
    # Sidebar for examples
    st.sidebar.title("📚 Example Prompts")
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
        st.subheader("🎯 Define Your Requirements")
        user_prompt = st.text_area(
            "Describe what you need:",
            value=example_prompts[selected_example],
            height=100,
            key="user_prompt"
        )
        
        # Add workflow steps input for CrewAI Flow
        if framework == "crewai-flow":
            st.subheader("🔄 Define Workflow Steps")
            workflow_steps = st.text_area(
                "List the steps in your workflow (one per line):",
                value="1. Data collection\n2. Analysis\n3. Report generation",
                height=100,
                key="workflow_steps"
            )
        
        # Generate button with LLM provider name
        if st.button(f"🚀 Generate using {model_provider} & {framework.upper()}", key="generate_button"):
            # Validation checks
            api_key_missing = False
            if model_provider == "OpenAI" and not st.session_state.openai_api_key:
                st.error("Please set your OpenAI API Key in the sidebar")
                api_key_missing = True
            elif model_provider == "WatsonX" and (not st.session_state.watsonx_api_key or not st.session_state.watsonx_project_id):
                st.error("Please set your WatsonX API Key and Project ID in the sidebar")
                api_key_missing = True
            elif model_provider == "Groq" and not st.session_state.groq_api_key:
                st.error("Please set your Groq API Key in the sidebar")
                api_key_missing = True
                
            if not api_key_missing:
                with st.spinner(f"Generating your {framework} code using {model_provider}..."):
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
                    st.success(f"✨ {framework.upper()} code generated successfully with {model_provider}!")
                    
                    # Add info about the model used
                    if model_provider == "OpenAI":
                        st.info("Generated using GPT-4.1-mini")
                    else:
                        st.info("Generated using Llama-3-70B-Instruct via WatsonX")

    with col2:
        st.subheader("💡 Framework Tips")
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
        else:  # react
            st.info("""
            **ReAct Tips:**
            - Focus on the reasoning steps
            - Define tools with clear descriptions
            - Provide examples of thought processes
            - Consider the observation/action cycle
            """)
        
        # Add provider comparison
        st.subheader("🔄 LLM Provider Comparison")
        comparison_md = """
        | Feature | OpenAI | WatsonX | Groq | 
        | ------- | ------ | ------- |------|
        | Models | GPT-4o, GPT-3.5, etc. | Llama-3, Granite, etc. |Llama3.3, GPT-4o, etc. |
        | Strengths | State-of-the-art performance | Enterprise security & governance | Lightning-fast inference |
        | Best for | Consumer apps, research | Enterprise deployments | Enterpsrie workloads |
        | Pricing | Token-based | Enterprise contracts | Enterprise contracts |
        """
        st.markdown(comparison_md)

    # Display results
    if 'config' in st.session_state:
        st.subheader("🔍 Generated Configuration")
        
        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["📊 Visual Overview", "💻 Code", "🔄 JSON Config"])
        
        with tab1:
            current_framework = st.session_state.framework
            
            if current_framework in ["crewai", "crewai-flow"]:
                # Display Agents
                st.subheader("Agents")
                for agent in st.session_state.config["agents"]:
                    with st.expander(f"🤖 {agent['role']}", expanded=True):
                        st.write(f"**Goal:** {agent['goal']}")
                        st.write(f"**Backstory:** {agent['backstory']}")
                        st.write(f"**Tools:** {', '.join(agent['tools'])}")
                
                # Display Tasks
                st.subheader("Tasks")
                for task in st.session_state.config["tasks"]:
                    with st.expander(f"📋 {task['name']}", expanded=True):
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
                    with st.expander(f"🤖 {agent['role']}", expanded=True):
                        st.write(f"**Goal:** {agent['goal']}")
                        st.write(f"**Tools:** {', '.join(agent['tools'])}")
                        st.write(f"**LLM:** {agent['llm']}")
                
                # Display Nodes
                st.subheader("Graph Nodes")
                for node in st.session_state.config["nodes"]:
                    with st.expander(f"📍 {node['name']}", expanded=True):
                        st.write(f"**Description:** {node['description']}")
                        st.write(f"**Agent:** {node['agent']}")
                
                # Display Edges
                st.subheader("Graph Edges")
                for edge in st.session_state.config["edges"]:
                    with st.expander(f"🔗 {edge['source']} → {edge['target']}", expanded=True):
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
                    with st.expander(f"🤖 {agent['role']}", expanded=True):
                        st.write(f"**Goal:** {agent['goal']}")
                        st.write(f"**Tools:** {', '.join(agent['tools'])}")
                        st.write(f"**LLM:** {agent['llm']}")
                
                # Display Tools
                st.subheader("Tools")
                for tool in st.session_state.config.get("tools", []):
                    with st.expander(f"🔧 {tool['name']}", expanded=True):
                        st.write(f"**Description:** {tool['description']}")
                        st.write("**Parameters:**")
                        for param, desc in tool["parameters"].items():
                            st.write(f"- **{param}**: {desc}")
                
                # Display Examples
                if "examples" in st.session_state.config:
                    st.subheader("Examples")
                    for i, example in enumerate(st.session_state.config["examples"]):
                        with st.expander(f"📝 Example {i+1}: {example['query'][:30]}...", expanded=True):
                            st.write(f"**Query:** {example['query']}")
                            st.write(f"**Thought:** {example['thought']}")
                            st.write(f"**Action:** {example['action']}")
                            st.write(f"**Observation:** {example['observation']}")
                            st.write(f"**Final Answer:** {example['final_answer']}")
        
        with tab2:
            # Display code with copy button and syntax highlighting
            st.code(st.session_state.code, language="python")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📋 Copy Code to Clipboard", key="copy_code_btn"):
                    st.toast("Code copied to clipboard! 📋", icon="📋")
            
            with col2:
                if st.download_button(
                    "💾 Download as Python File",
                    st.session_state.code,
                    file_name=f"{st.session_state.framework}_agent.py",
                    mime="text/plain",
                    key="download_code_btn"
                ):
                    st.toast("File downloaded! 💾", icon="💾")
        
        with tab3:
            # Display the raw JSON configuration
            st.json(st.session_state.config)
            
            if st.download_button(
                "💾 Download Configuration as JSON",
                json.dumps(st.session_state.config, indent=2),
                file_name=f"{st.session_state.framework}_config.json",
                mime="application/json",
                key="download_json_btn"
            ):
                st.toast("JSON configuration downloaded! 💾", icon="💾")

if __name__ == "__main__":
    main()