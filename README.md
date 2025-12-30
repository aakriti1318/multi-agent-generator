# Multi-Agent Generator
<img width="807" height="264" alt="Screenshot 2025-08-18 at 12 59 52 PM" src="https://github.com/user-attachments/assets/90665135-80a3-43e2-82cc-ae7fa1dcc6a3" />

**PyPi Link** - [Multi-agent-generator](https://pypi.org/project/multi-agent-generator/)

A powerful **low-code/no-code** tool that transforms plain English instructions into fully configured multi-agent AI teams — no scripting, no complexity.
Powered by [LiteLLM](https://docs.litellm.ai/) for **provider-agnostic support** (OpenAI, WatsonX, Ollama, Anthropic, etc.) with both a **CLI** and an optional **Streamlit UI**.

### What's New in v0.5.0
- **Tool Auto-Discovery & Generation** - 15+ pre-built tools + natural language tool creation
- **Multi-Agent Orchestration Patterns** - Supervisor, Debate, Voting, Pipeline, MapReduce
- **Evaluation & Testing Framework** - Auto-generated tests + output quality metrics

---

## Features

### Agent Generation

* Generate agent code for multiple frameworks:

  * **CrewAI**: Structured workflows for multi-agent collaboration
  * **CrewAI Flow**: Event-driven workflows with state management
  * **LangGraph**: LangChain's framework for stateful, multi-actor applications
  * **Agno**: Agno framework for Agents Team orchestration
  * **ReAct (classic)**: Reasoning + Acting agents using `AgentExecutor`
  * **ReAct (LCEL)**: Future-proof ReAct built with LangChain Expression Language (LCEL)

* **Provider-Agnostic Inference** via LiteLLM:

  * Supports OpenAI, IBM WatsonX, Ollama, Anthropic, and more
  * Swap providers with a single CLI flag or environment variable

* **Flexible Output**:

  * Generate Python code
  * Generate JSON configs
  * Or both combined

### Tool Auto-Discovery & Generation (NEW!)

Create tools for your agents using plain English — no coding required:

```python
from multi_agent_generator.tools import ToolRegistry, ToolGenerator

# Browse 15+ pre-built tools across 10 categories
registry = ToolRegistry()
web_tools = registry.get_tools_by_category("web_search")
all_tools = registry.list_all_tools()

# Generate custom tools from natural language
generator = ToolGenerator()
tool = generator.generate_tool("Create a tool that fetches weather data for a city")
print(tool.code)  # Ready-to-use Python code!
```

**Pre-built Tool Categories:**
| Category | Examples |
|----------|----------|
| Web Search | Google search, web scraper |
| File Operations | Read, write, list files |
| Data Processing | CSV parser, JSON transformer |
| Code Execution | Python executor, shell runner |
| API Integration | REST client, webhook handler |
| Database | SQL query, document store |
| Communication | Email sender, Slack notifier |
| Math | Calculator, statistics |
| Text Processing | Summarizer, translator |
| Image Processing | Resizer, format converter |

### Multi-Agent Orchestration Patterns (NEW!)

Choose from 5 battle-tested patterns to coordinate your agents:

```python
from multi_agent_generator.orchestration import Orchestrator, PatternType

orchestrator = Orchestrator()

# Generate orchestrated system from description
result = orchestrator.generate_from_description(
    "I need a research team where a manager delegates to specialists"
)
print(result["code"])  # Complete LangGraph/CrewAI code!

# Or configure manually
config = orchestrator.create_pattern_config(
    pattern_type=PatternType.SUPERVISOR,
    agents=["researcher", "writer", "reviewer"],
    task_description="Analyze market trends"
)
```

**Available Patterns:**

| Pattern | Use Case | How It Works |
|---------|----------|--------------|
| **Supervisor** | Delegating tasks to specialists | Central coordinator routes work |
| **Debate** | Reaching consensus | Agents discuss & refine answers |
| **Voting** | Democratic decisions | Agents vote on best response |
| **Pipeline** | Sequential processing | Chain of specialized steps |
| **MapReduce** | Parallel processing | Split, process, aggregate |

### Evaluation & Testing Framework (NEW!)

Auto-generate tests and evaluate agent quality:

```python
from multi_agent_generator.evaluation import TestGenerator, AgentEvaluator

# Generate pytest test suites automatically
test_gen = TestGenerator()
test_suite = test_gen.generate_test_suite(
    agent_config=your_config,
    test_types=["unit", "integration", "e2e"]
)
test_suite.save("tests/")  # Ready to run with pytest!

# Evaluate agent output quality
evaluator = AgentEvaluator()
result = evaluator.evaluate(
    agent_output="The analysis shows...",
    expected_output="Market trends indicate...",
    task_description="Analyze Q4 sales data"
)
print(result.overall_score)  # 0.0 - 1.0
print(result.metrics)  # relevance, completeness, coherence, accuracy
```

**Test Types:**
- Unit Tests - Individual component testing
- Integration Tests - Multi-agent interaction
- End-to-End Tests - Full workflow validation
- Performance Tests - Response time & throughput
- Reliability Tests - Error handling & recovery
- Quality Tests - Output quality metrics

### Streamlit UI

* Interactive prompt entry
* Framework selection
* **Tool discovery & generation** (NEW!)
* **Orchestration pattern configuration** (NEW!)
* **Evaluation & testing dashboard** (NEW!)
* Config visualization
* Copy or download generated code

---

## Installation

### Basic Installation

```bash
pip install multi-agent-generator
```

---

## Prerequisites

* At least one supported LLM provider (OpenAI, WatsonX, Ollama, etc.)
* Environment variables setup:

  * `OPENAI_API_KEY` (for OpenAI)
  * `WATSONX_API_KEY`, `WATSONX_PROJECT_ID`, `WATSONX_URL` (for WatsonX)
  * `OLLAMA_URL` (for Ollama)
  * Or a generic `API_KEY` / `API_BASE` if supported by LiteLLM

* Be aware `Agno` only works with `OPENAI_API_KEY` without tools for Now, and will be expanded for further API's and tools in the future.

> You can freely switch providers using `--provider` in CLI or by setting environment variables.

---

## Usage

### Command Line

Basic usage with OpenAI (default):

```bash
multi-agent-generator "I need a research assistant that summarizes papers and answers questions" --framework crewai
```

Using WatsonX instead:

```bash
multi-agent-generator "I need a research assistant that summarizes papers and answers questions" --framework crewai --provider watsonx
```

Using Agno:

```bash
multi_agent_generator "build a researcher and writer" --framework agno --provider openai --output agno.py --format code
```

Using Ollama locally:

```bash
multi-agent-generator "Build me a ReAct assistant for customer support" --framework react-lcel --provider ollama
```

Save output to a file:

```bash
multi-agent-generator "I need a team to create viral social media content" --framework langgraph --output social_team.py
```

Get JSON configuration only:

```bash
multi-agent-generator "I need a team to analyze customer data" --framework react --format json
```

### Streamlit UI

Launch the interactive web interface:

```bash
streamlit run streamlit_app.py
```

Navigate between pages:
- **Agent Generator** - Generate agent code from natural language
- **Tool Discovery** - Browse and create tools
- **Orchestration Patterns** - Configure multi-agent coordination
- **Evaluation & Testing** - Generate tests and evaluate outputs

---

## Examples

### Research Assistant

```
I need a research assistant that summarizes papers and answers questions
```

### Content Creation Team

```
I need a team to create viral social media content and manage our brand presence
```

### Customer Support (LangGraph)

```
Build me a LangGraph workflow for customer support
```

### Orchestrated Team (NEW!)

```python
from multi_agent_generator.orchestration import Orchestrator

orchestrator = Orchestrator()
result = orchestrator.generate_from_description(
    "Build a content team with a supervisor managing writers and editors"
)
```

---

## Frameworks

### CrewAI

Role-playing autonomous AI agents with goals, roles, and backstories.

### CrewAI Flow

Event-driven workflows with sequential, parallel, or conditional execution.

### LangGraph

Directed graph of agents/tools with stateful execution.

### Agno

Role-playing Team orchestration AI agents with goals, roles, backstories and instructions.

### ReAct (classic)

Reasoning + Acting agents built with `AgentExecutor`.

### ReAct (LCEL)

Modern ReAct implementation using LangChain Expression Language — better for debugging and future-proof orchestration.

---

## LLM Providers

### OpenAI

State-of-the-art GPT models (default: `gpt-4o-mini`).

### IBM WatsonX

Enterprise-grade access to Llama and other foundation models (default: `llama-3-70b-instruct`).

### Ollama

Run Llama and other models locally.

### Anthropic

Use Claude models for agent generation.

...and more, via LiteLLM.

---

## API Reference

### Tools Module

```python
from multi_agent_generator.tools import (
    ToolRegistry,      # Browse pre-built tools
    ToolGenerator,     # Generate custom tools
    ToolCategory,      # Tool category enum
    ToolDefinition,    # Tool data class
)
```

### Orchestration Module

```python
from multi_agent_generator.orchestration import (
    Orchestrator,      # High-level orchestration interface
    PatternType,       # Pattern type enum
    SupervisorPattern, # Supervisor pattern
    DebatePattern,     # Debate pattern
    VotingPattern,     # Voting pattern
    PipelinePattern,   # Pipeline pattern
    MapReducePattern,  # MapReduce pattern
)
```

### Evaluation Module

```python
from multi_agent_generator.evaluation import (
    TestGenerator,     # Auto-generate test suites
    TestCase,          # Individual test case
    TestSuite,         # Collection of tests
    AgentEvaluator,    # Evaluate agent outputs
    EvaluationResult,  # Evaluation results
    Benchmark,         # Performance benchmarking
)
```

---

## License

MIT

Maintainers: **[Nabarko Roy](https://github.com/Nabarko)**

Made with love. If you like star the repo and share it with AI Enthusiasts.
