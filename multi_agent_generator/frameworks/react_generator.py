# multi_agent_generator/frameworks/react_generator.py
"""
Generator for ReAct code.
"""
from typing import Dict, Any

def create_react_code(config: Dict[str, Any]) -> str:
    code = """from langchain_core.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from typing import Dict, List, Any

"""

    # Define tools
    code += "# Define tools\n"
    for tool in config.get("tools", []):
        params = ", ".join(tool.get("parameters", {}).keys()) if tool.get("parameters") else ""
        param_names = ", ".join(tool.get("parameters", {}).keys()) if tool.get("parameters") else ""
        class_name = f"{tool['name'].capitalize()}Tool"
        # Use double braces for literal {self.name} and {locals()} inside the generated code
        code += f"""class {class_name}(BaseTool):
    name = "{tool['name']}"
    description = "{tool['description']}"
    
    def _run(self{', ' if params else ''}{params}) -> str:
        try:
            # TODO: implement actual functionality
            return f"Executed {{self.name}} with inputs: {{locals()}}"
        except Exception as e:
            return f"Error in {{self.name}}: {{str(e)}}"
    
    async def _arun(self{', ' if params else ''}{params}) -> str:
        return self._run({param_names})

"""

    # Collect tools
    code += "tools = [\n"
    for tool in config.get("tools", []):
        code += f"    {tool['name'].capitalize()}Tool(),\n"
    code += "]\n\n"

    # Agent setup
    if config.get("agents"):
        agent = config["agents"][0]
        # safe fallback for missing llm field
        llm_model = agent.get("llm", "gpt-4.1-mini")
        code += f"""llm = ChatOpenAI(model="{llm_model}")

react_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are {agent['role']}. Your goal is {agent['goal']}. Use tools when needed."),
    ("human", "{{input}}")
])

agent = create_react_agent(llm, tools, react_prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

def run_agent(query: str) -> str:
    response = agent_executor.invoke({{"input": query}})
    # Try to show intermediate trace if available
    try:
        if isinstance(response, dict) and 'intermediate_steps' in response:
            print('--- Agent Trace ---')
            for step in response['intermediate_steps']:
                print(step)
            print('-------------------')
    except Exception:
        pass
    return response.get("output", "No response generated") if isinstance(response, dict) else str(response)

if __name__ == "__main__":
    result = run_agent("Your query here")
    print(result)
"""
    return code


# LCEL-based ReAct code generator

def create_react_lcel_code(config: Dict[str, Any]) -> str:
    code = """from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_core.tools import BaseTool

"""

    # Define tools
    code += "# Define tools\n"
    for tool in config.get("tools", []):
        params = ", ".join(tool.get("parameters", {}).keys()) if tool.get("parameters") else ""
        param_names = ", ".join(tool.get("parameters", {}).keys()) if tool.get("parameters") else ""
        class_name = f"{tool['name'].capitalize()}Tool"
        code += f"""class {class_name}(BaseTool):
    name = "{tool['name']}"
    description = "{tool['description']}"
    
    def _run(self{', ' if params else ''}{params}) -> str:
        try:
            # TODO: implement actual logic for the tool
            return f"Executed {{self.name}} with inputs: {{locals()}}"
        except Exception as e:
            return f"Error in {{self.name}}: {{str(e)}}"
    
    async def _arun(self{', ' if params else ''}{params}) -> str:
        return self._run({param_names})

"""

    # Collect tools
    code += "tools = [\n"
    for tool in config.get("tools", []):
        code += f"    {tool['name'].capitalize()}Tool(),\n"
    code += "]\n\n"

    if config.get("agents"):
        agent = config["agents"][0]
        llm_model = agent.get("llm", "gpt-4.1-mini")
        code += f"""llm = ChatOpenAI(model="{llm_model}")

react_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are {agent['role']}. Your goal is {agent['goal']}. Use tools when needed."),
    MessagesPlaceholder("history"),
    ("human", "{{input}}")
])

chain = (
    {{"input": RunnablePassthrough(), "history": RunnablePassthrough()}}
    | react_prompt
    | llm
    | StrOutputParser()
)

def run_agent(query: str, history: List[str] = []) -> str:
    response = chain.invoke({{"input": query, "history": history}})
    # If the config included examples with thoughts/actions/observations, print them for debugging
    try:
        print("\\n=== Example Traces (from config) ===")
        # placeholder: in generated file, the config may be embedded or passed in; this prints examples if present
    except Exception:
        pass
    return response

if __name__ == "__main__":
    result = run_agent("Your query here")
    print(result)
"""
    return code
