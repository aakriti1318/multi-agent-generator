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
| `--format` | Output format (code, json, both) | both |

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
from multi_agent_generator.tools import ToolRegistry, ToolGenerator

# Browse pre-built tools
registry = ToolRegistry()
categories = registry.get_categories()
web_tools = registry.get_tools_by_category("web_search")

# Generate custom tools
generator = ToolGenerator()
tool = generator.generate_tool("Create a tool that fetches weather data")
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
