# Examples

This page contains practical examples for all major features of multi-agent-generator.

---

## Agent Generation Examples

### Research Assistant

**Prompt:**
```
I need a research assistant that summarizes papers and answers questions
```

**Command:**
```bash
multi-agent-generator "I need a research assistant that summarizes papers and answers questions" --framework crewai --output researcher.py
```

### Content Creation Team

**Prompt:**
```
I need a team to create viral social media content and manage our brand presence
```

**Command:**
```bash
multi-agent-generator "I need a team to create viral social media content and manage our brand presence" --framework langgraph --output content_team.py
```

### Customer Support (LangGraph)

**Prompt:**
```
Build me a LangGraph workflow for customer support with routing and escalation
```

**Command:**
```bash
multi-agent-generator "Build me a LangGraph workflow for customer support with routing and escalation" --framework langgraph --output support.py
```

### Data Analysis Pipeline

**Prompt:**
```
Create a data analysis team with a collector, processor, and reporter
```

**Command:**
```bash
multi-agent-generator "Create a data analysis team with a collector, processor, and reporter" --framework crewai-flow --output data_pipeline.py
```

---

## Tool Discovery Examples

### Browse Pre-built Tools

```python
from multi_agent_generator.tools import ToolRegistry

registry = ToolRegistry()

# List all categories
for category in registry.get_categories():
    print(f"Category: {category}")
    for tool in registry.get_tools_by_category(category):
        print(f"  - {tool.name}: {tool.description}")
```

### Get Tool Code for a Framework

```python
from multi_agent_generator.tools import ToolRegistry

registry = ToolRegistry()
tool = registry.get_tool("tavily_search")

# Get CrewAI-compatible code
crewai_code = tool.get_code("crewai")
print(crewai_code)

# Get LangGraph-compatible code
langgraph_code = tool.get_code("langgraph")
print(langgraph_code)
```

### Generate Custom Tools

```python
from multi_agent_generator.tools import ToolGenerator

generator = ToolGenerator()

# From description
tool = generator.generate_tool(
    "Create a tool that fetches stock prices from Yahoo Finance"
)
print(tool.code)
print(tool.dependencies)

# Generate multiple tools from a task
tools = generator.generate_tools_for_task(
    "Build a financial analysis agent",
    max_tools=5
)
for tool in tools:
    print(f"- {tool.name}: {tool.description}")
```

---

## Orchestration Pattern Examples

### Supervisor Pattern

```python
from multi_agent_generator.orchestration import Orchestrator, PatternType

orchestrator = Orchestrator()

config = orchestrator.create_pattern_config(
    pattern_type=PatternType.SUPERVISOR,
    agents=["researcher", "writer", "reviewer"],
    task_description="Write a comprehensive market analysis report"
)

code = orchestrator.generate_code(config, framework="langgraph")
print(code)
```

### Debate Pattern

```python
from multi_agent_generator.orchestration import Orchestrator, PatternType

orchestrator = Orchestrator()

config = orchestrator.create_pattern_config(
    pattern_type=PatternType.DEBATE,
    agents=["optimist", "pessimist", "moderator"],
    task_description="Evaluate the investment opportunity",
    debate_rounds=3
)

code = orchestrator.generate_code(config, framework="crewai")
print(code)
```

### Voting Pattern

```python
from multi_agent_generator.orchestration import Orchestrator, PatternType

orchestrator = Orchestrator()

config = orchestrator.create_pattern_config(
    pattern_type=PatternType.VOTING,
    agents=["analyst_1", "analyst_2", "analyst_3"],
    task_description="Classify customer feedback sentiment",
    voting_threshold=0.6
)

code = orchestrator.generate_code(config, framework="langgraph")
print(code)
```

### Pipeline Pattern

```python
from multi_agent_generator.orchestration import Orchestrator, PatternType

orchestrator = Orchestrator()

config = orchestrator.create_pattern_config(
    pattern_type=PatternType.PIPELINE,
    agents=["data_collector", "data_cleaner", "analyzer", "reporter"],
    task_description="Process and analyze sales data"
)

code = orchestrator.generate_code(config, framework="crewai-flow")
print(code)
```

### Map-Reduce Pattern

```python
from multi_agent_generator.orchestration import Orchestrator, PatternType

orchestrator = Orchestrator()

config = orchestrator.create_pattern_config(
    pattern_type=PatternType.MAP_REDUCE,
    agents=["mapper_1", "mapper_2", "mapper_3", "reducer"],
    task_description="Analyze customer reviews across regions"
)

code = orchestrator.generate_code(config, framework="langgraph")
print(code)
```

### Generate from Description

```python
from multi_agent_generator.orchestration import Orchestrator

orchestrator = Orchestrator()

# Let the system choose the best pattern
result = orchestrator.generate_from_description(
    "I need agents that vote on the best marketing strategy"
)

print(f"Selected pattern: {result['pattern']}")
print(result['code'])
```

---

## Evaluation Examples

### Generate Unit Tests

```python
from multi_agent_generator.evaluation import TestGenerator

test_gen = TestGenerator()

agent_config = {
    "agents": [
        {"name": "researcher", "role": "Research Specialist"},
        {"name": "writer", "role": "Content Writer"}
    ],
    "tasks": [
        {"name": "research_task", "description": "Research the topic"},
        {"name": "write_task", "description": "Write the article"}
    ]
}

test_suite = test_gen.generate_test_suite(
    agent_config=agent_config,
    test_types=["unit", "integration"]
)

# Save tests to directory
test_suite.save("tests/")
print(f"Generated {len(test_suite.tests)} tests")
```

### Evaluate Agent Output

```python
from multi_agent_generator.evaluation import AgentEvaluator

evaluator = AgentEvaluator()

result = evaluator.evaluate(
    agent_output="The quarterly analysis shows a 15% increase in revenue...",
    expected_output="Revenue increased by approximately 15% this quarter...",
    task_description="Analyze Q4 financial performance"
)

print(f"Overall Score: {result.overall_score}")
print(f"Relevance: {result.relevance_score}")
print(f"Completeness: {result.completeness_score}")
print(f"Accuracy: {result.accuracy_score}")
```

### Run Benchmarks

```python
from multi_agent_generator.evaluation import Benchmark

benchmark = Benchmark()

# Define test cases
test_cases = [
    {
        "input": "Summarize the Q4 earnings report",
        "expected": "Q4 earnings showed growth..."
    },
    {
        "input": "Compare product A vs product B",
        "expected": "Product A excels in..."
    }
]

# Run benchmark
results = benchmark.run(
    agent_function=your_agent.run,
    test_cases=test_cases,
    metrics=["latency", "accuracy", "relevance"]
)

# Generate report
report = benchmark.generate_report(results)
print(report)
```

### Compare Frameworks

```python
from multi_agent_generator.evaluation import Benchmark

benchmark = Benchmark()

# Compare the same prompt across frameworks
comparison = benchmark.compare_frameworks(
    prompt="Build a customer support agent",
    frameworks=["crewai", "langgraph", "react"],
    metrics=["code_quality", "execution_time"]
)

for framework, scores in comparison.items():
    print(f"{framework}: {scores}")
```

---

## Complete Workflow Example

Here's a complete example combining all features:

```python
from multi_agent_generator import generate_agents
from multi_agent_generator.tools import ToolRegistry, ToolGenerator
from multi_agent_generator.orchestration import Orchestrator, PatternType
from multi_agent_generator.evaluation import TestGenerator, AgentEvaluator

# 1. Discover and select tools
registry = ToolRegistry()
web_tools = registry.get_tools_by_category("web_search")
file_tools = registry.get_tools_by_category("file_operations")

# 2. Generate custom tool if needed
tool_gen = ToolGenerator()
custom_tool = tool_gen.generate_tool(
    "Create a tool that fetches company financial data from SEC EDGAR"
)

# 3. Configure orchestration pattern
orchestrator = Orchestrator()
pattern_config = orchestrator.create_pattern_config(
    pattern_type=PatternType.PIPELINE,
    agents=["data_gatherer", "analyzer", "report_writer"],
    task_description="Analyze company financials and write report"
)

# 4. Generate the agent code
result = generate_agents(
    prompt="Build a financial analysis team",
    framework="langgraph",
    provider="openai"
)

# Save the generated code
with open("financial_team.py", "w") as f:
    f.write(result["code"])

# 5. Generate tests
test_gen = TestGenerator()
test_suite = test_gen.generate_test_suite(
    agent_config=result["config"],
    test_types=["unit", "integration", "edge_case"]
)
test_suite.save("tests/")

# 6. Set up evaluation
evaluator = AgentEvaluator()

# Ready to run and evaluate
print("Agent team generated successfully")
print(f"Tools available: {len(web_tools) + len(file_tools) + 1}")
print(f"Tests generated: {len(test_suite.tests)}")
```