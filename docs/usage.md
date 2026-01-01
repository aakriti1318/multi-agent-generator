# Usage

## Command Line Interface

### Basic Usage

Generate agent code with OpenAI (default):

```bash
multi-agent-generator "I need a research assistant that summarizes papers and answers questions" --framework crewai
```

### Specifying a Provider

Using WatsonX:

```bash
multi-agent-generator "I need a research assistant" --framework crewai --provider watsonx
```

Using Ollama locally:

```bash
multi-agent-generator "Build me a ReAct assistant for customer support" --framework react-lcel --provider ollama
```

### Using Agno Framework

```bash
multi-agent-generator "build a researcher and writer" --framework agno --provider openai --output agno.py --format code
```

### Saving Output

Save to a Python file:

```bash
multi-agent-generator "I need a team to create viral social media content" --framework langgraph --output social_team.py
```

### Output Formats

Get JSON configuration only:

```bash
multi-agent-generator "I need a team to analyze customer data" --framework react --format json
```

Get code only:

```bash
multi-agent-generator "Build a support team" --framework crewai --format code
```

Get both (default):

```bash
multi-agent-generator "Build a support team" --framework crewai --format both
```

### CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `--framework` | Target framework (crewai, crewai-flow, langgraph, react, react-lcel, agno) | crewai |
| `--provider` | LLM provider (openai, watsonx, ollama, anthropic) | openai |
| `--output` | Output file path | stdout |
| `--format` | Output format (code, json, both) | both || `--tool` | Generate a custom tool from description | - |
| `--list-tools` | List all available tools | - |
| `--tool-category` | Filter tools by category | - |
| `--evaluate` | Enable evaluation mode | - |
| `--query` | Query for evaluation | - |
| `--response` | Response to evaluate | - |
| `--expected` | Expected output (optional) | - |
| `--threshold` | Minimum passing score | 0.7 |
| `--orchestrate` | Get orchestration pattern suggestion | - |
| `--list-patterns` | List orchestration patterns | - |
| `--pattern` | Generate code for specific pattern | - |
| `--num-agents` | Number of agents for orchestration | 3 |

---

## Tool Generation via CLI

Generate custom tools from natural language descriptions:

```bash
# Generate a tool from description
multi-agent-generator --tool "Create a tool to fetch weather data for a city"
```

**Output:**
```python
# Auto-generated tool: fetch_weather_data
# Category: api_integration
# Description: Fetches weather data for a given city

import os
import requests
from typing import Dict, Any

def fetch_weather_data(city: str) -> Dict[str, Any]:
    """Fetch weather data for a city."""
    api_key = os.getenv("WEATHER_API_KEY")
    url = f"https://api.weatherapi.com/v1/current.json?key={api_key}&q={city}"
    response = requests.get(url)
    return response.json()
```

### List Available Tools

```bash
# List all tools
multi-agent-generator --list-tools
```

**Output:**
```
📦 All Available Tools:

  [API_INTEGRATION]
    • http_request: Make HTTP requests (GET, POST, PUT, DELETE) to any API endpoint.

  [CODE_EXECUTION]
    • python_executor: Execute Python code safely in an isolated environment.
    • shell_command: Execute shell commands. Use with caution.

  [FILE_OPERATIONS]
    • read_file: Read content from a file. Supports text files, JSON, CSV, etc.
    • write_file: Write content to a file. Creates the file if it doesn't exist.
    • list_directory: List all files and folders in a directory.
    ...
```

### Filter by Category

```bash
multi-agent-generator --list-tools --tool-category api_integration
```

---

## Evaluation via CLI

Evaluate agent output quality directly from the command line:

### Basic Evaluation

```bash
multi-agent-generator --evaluate \
  --query "What is machine learning?" \
  --response "Machine learning is a subset of AI that enables systems to learn from data"
```

**Output:**
```
📊 Evaluating agent output...

Evaluation Results: ✅ PASSED
==================================================
Query: What is machine learning?
Response: Machine learning is a subset of AI that enables systems to learn from data

Metrics:
  • Relevance:        1.00
  • Completeness:     0.50
  • Coherence:        0.80
  • Accuracy:         0.70
  • Task Completion:  0.70
  • Response Time:    0.00ms
  • Token Count:      18

Overall Score: 0.740 (threshold: 0.7)
```

### With Expected Output

Provide expected output for accuracy comparison:

```bash
multi-agent-generator --evaluate \
  --query "Summarize AI" \
  --response "AI is artificial intelligence" \
  --expected "Artificial intelligence is technology that mimics human cognition" \
  --threshold 0.8
```

### Save Results to File

```bash
multi-agent-generator --evaluate \
  --query "Test query" \
  --response "Test response" \
  --output evaluation_results.json
```

---

## Orchestration via CLI

Create orchestrated multi-agent systems from the command line:

### List Available Patterns

```bash
multi-agent-generator --list-patterns
```

**Output:**
```
🔄 Available Orchestration Patterns:

  [SUPERVISOR PATTERN]
    Description: A supervisor agent coordinates and delegates tasks to specialized worker agents
    Use Cases:
      • Project management workflows
      • Quality assurance processes
      • Customer service escalation

  [DEBATE PATTERN]
    Description: Multiple agents argue different perspectives and reach consensus
    Use Cases:
      • Decision making processes
      • Fact checking and verification
      • Brainstorming sessions
  ...
```

### Get Pattern Suggestion

Describe your needs and get a recommended pattern:

```bash
multi-agent-generator --orchestrate "I need agents to work together on a document, each reviewing the previous agent's work"
```

**Output:**
```
🔄 Analyzing task description...
   "I need agents to work together on a document, each reviewing the previous agent's work"

📌 Recommended pattern: pipeline

🏗️  Generating pipeline orchestration code for langgraph...

# Generated LangGraph Pipeline Code
from langgraph.graph import StateGraph, END
...
```

### Generate Code for Specific Pattern

```bash
# Generate supervisor pattern with LangGraph
multi-agent-generator --pattern supervisor --framework langgraph --output supervisor_agents.py

# Generate debate pattern with CrewAI
multi-agent-generator --pattern debate --framework crewai --num-agents 3

# Generate voting pattern with 5 agents
multi-agent-generator --pattern voting --num-agents 5 --framework langgraph
```
---

## Streamlit UI

Launch the interactive web interface:

```bash
streamlit run streamlit_app.py
```

### Available Pages

1. **Agent Generator** - Generate agent code from natural language descriptions
2. **Tool Discovery** - Browse pre-built tools and create custom ones
3. **Orchestration Patterns** - Configure multi-agent coordination patterns
4. **Evaluation & Testing** - Generate tests and evaluate agent outputs

---

## Python API

### Basic Code Generation

```python
from multi_agent_generator import generate_agents

# Generate CrewAI agents
result = generate_agents(
    prompt="I need a research team with a lead and two specialists",
    framework="crewai",
    provider="openai"
)

print(result["code"])
print(result["config"])
```

### Tool Discovery

```python
from multi_agent_generator.tools import ToolRegistry, ToolGenerator, ToolCategory

# Browse pre-built tools
registry = ToolRegistry()
categories = [cat for cat in ToolCategory]
web_tools = registry.list_by_category(ToolCategory.WEB_SEARCH)

# Generate custom tools
generator = ToolGenerator()
tool = generator.generate_from_description("Create a tool that fetches weather data")
print(tool.code)
```

### Orchestration Patterns

```python
from multi_agent_generator.orchestration import Orchestrator, PatternType

orchestrator = Orchestrator()

# Generate from description
result = orchestrator.generate_from_description(
    "I need a supervisor managing a team of specialists"
)

# Or configure manually
config = orchestrator.create_pattern_config(
    pattern_type=PatternType.SUPERVISOR,
    agents=["researcher", "writer", "reviewer"],
    task_description="Analyze market trends"
)
```

### Evaluation & Testing

```python
from multi_agent_generator.evaluation import TestGenerator, AgentEvaluator

# Generate test suites
test_gen = TestGenerator()
test_suite = test_gen.generate_test_suite(
    agent_config=your_config,
    test_types=["unit", "integration"]
)
test_suite.save("tests/")

# Evaluate outputs
evaluator = AgentEvaluator()
result = evaluator.evaluate(
    agent_output="The analysis shows...",
    expected_output="Market trends indicate...",
    task_description="Analyze Q4 sales"
)
print(result.overall_score)
```
