# API Reference

Complete API reference for the Multi-Agent Generator library.

---

## Core Module

### generate_agents

Generate agent code from a natural language prompt.

```python
from multi_agent_generator import generate_agents

result = generate_agents(
    prompt: str,           # Natural language description
    framework: str,        # Target framework
    provider: str = "openai",  # LLM provider
    format: str = "both"   # Output format: "code", "json", or "both"
) -> dict
```

**Returns:**
```python
{
    "code": str,      # Generated Python code
    "config": dict,   # Agent configuration
    "framework": str  # Framework used
}
```

---

## Tools Module

```python
from multi_agent_generator.tools import (
    ToolRegistry,
    ToolGenerator,
    ToolCategory,
    ToolDefinition,
)
```

### ToolRegistry

Registry of pre-built tools.

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `get_categories()` | - | `List[ToolCategory]` | List all tool categories |
| `get_tools_by_category(category)` | `category: ToolCategory` | `List[ToolDefinition]` | Get tools in category |
| `get_tool(name)` | `name: str` | `ToolDefinition` | Get tool by name |
| `list_all_tools()` | - | `List[ToolDefinition]` | List all tools |
| `search_tools(query)` | `query: str` | `List[ToolDefinition]` | Search tools by keyword |

### ToolGenerator

Generate custom tools from descriptions.

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `generate_tool(description)` | `description: str` | `ToolDefinition` | Generate from natural language |
| `generate_from_template(template, **kwargs)` | `template: str, **kwargs` | `ToolDefinition` | Generate from template |
| `validate_tool(tool)` | `tool: ToolDefinition` | `bool` | Validate tool code |

### ToolCategory (Enum)

```python
class ToolCategory(Enum):
    WEB_SEARCH = "web_search"
    FILE_OPERATIONS = "file_operations"
    DATA_PROCESSING = "data_processing"
    CODE_EXECUTION = "code_execution"
    API_INTEGRATION = "api_integration"
    DATABASE = "database"
    COMMUNICATION = "communication"
    MATH_CALCULATION = "math_calculation"
    TEXT_PROCESSING = "text_processing"
    IMAGE_PROCESSING = "image_processing"
    CUSTOM = "custom"
```

### ToolDefinition (DataClass)

```python
@dataclass
class ToolDefinition:
    name: str                    # Tool name
    description: str             # Tool description
    category: ToolCategory       # Tool category
    parameters: Dict[str, Any]   # Input parameters schema
    returns: str                 # Return type description
    code: str                    # Python implementation
```

---

## Orchestration Module

```python
from multi_agent_generator.orchestration import (
    Orchestrator,
    PatternType,
    SupervisorPattern,
    DebatePattern,
    VotingPattern,
    PipelinePattern,
    MapReducePattern,
)
```

### Orchestrator

High-level orchestration interface.

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `generate_from_description(description)` | `description: str` | `dict` | Generate from natural language |
| `create_pattern_config(pattern_type, agents, task_description, **kwargs)` | Various | `dict` | Create pattern configuration |
| `generate_code(config)` | `config: dict` | `str` | Generate executable code |
| `list_patterns()` | - | `List[PatternType]` | List available patterns |

### PatternType (Enum)

```python
class PatternType(Enum):
    SUPERVISOR = "supervisor"
    DEBATE = "debate"
    VOTING = "voting"
    PIPELINE = "pipeline"
    MAP_REDUCE = "map_reduce"
```

### Pattern Classes

#### SupervisorPattern

```python
SupervisorPattern(
    supervisor_name: str,
    worker_agents: List[str],
    delegation_rules: Optional[Dict] = None
)
```

#### DebatePattern

```python
DebatePattern(
    debaters: List[str],
    moderator: str,
    max_rounds: int = 3
)
```

#### VotingPattern

```python
VotingPattern(
    voters: List[str],
    voting_method: str = "majority"  # "majority", "weighted", "ranked"
)
```

#### PipelinePattern

```python
PipelinePattern(
    stages: List[str],
    error_handling: str = "stop"  # "stop", "skip", "retry"
)
```

#### MapReducePattern

```python
MapReducePattern(
    mappers: List[str],
    reducer: str,
    chunk_strategy: str = "equal"  # "equal", "by_size", "by_topic"
)
```

---

## Evaluation Module

```python
from multi_agent_generator.evaluation import (
    TestGenerator,
    TestCase,
    TestSuite,
    TestType,
    AgentEvaluator,
    EvaluationResult,
    EvaluationConfig,
    Benchmark,
    BenchmarkResult,
)
```

### TestGenerator

Generate test suites for agents.

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `generate_test_suite(agent_config, test_types)` | `config: dict, types: List[str]` | `TestSuite` | Generate complete suite |
| `generate_tests(agent_config, test_type)` | `config: dict, type: TestType` | `List[TestCase]` | Generate specific tests |

### TestType (Enum)

```python
class TestType(Enum):
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    QUALITY = "quality"
```

### TestSuite

```python
class TestSuite:
    tests: List[TestCase]
    
    def save(self, directory: str) -> None:
        """Save test files to directory."""
    
    def to_code(self) -> str:
        """Get all tests as code string."""
```

### TestCase

```python
@dataclass
class TestCase:
    name: str
    test_type: TestType
    code: str
    description: str
```

### AgentEvaluator

Evaluate agent output quality.

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `evaluate(agent_output, expected_output, task_description, config)` | Various | `EvaluationResult` | Evaluate single output |
| `evaluate_batch(test_cases)` | `List[dict]` | `List[EvaluationResult]` | Evaluate multiple outputs |

### EvaluationConfig

```python
@dataclass
class EvaluationConfig:
    metrics: List[str] = field(default_factory=lambda: [
        "relevance", "completeness", "coherence", 
        "accuracy", "conciseness", "format", "tone"
    ])
    weights: Optional[Dict[str, float]] = None
    threshold: float = 0.7
```

### EvaluationResult

```python
@dataclass
class EvaluationResult:
    overall_score: float      # 0.0 - 1.0
    metrics: Dict[str, float] # Individual scores
    feedback: str             # Detailed feedback
    passed: bool              # Above threshold?
```

### Benchmark

Performance benchmarking.

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `run(agent, test_cases, iterations)` | Various | `BenchmarkResult` | Benchmark single agent |
| `compare(agents, test_cases)` | `Dict[str, Agent], List` | `ComparisonResult` | Compare multiple agents |

### BenchmarkResult

```python
@dataclass
class BenchmarkResult:
    avg_response_time: float    # milliseconds
    p95_response_time: float    # 95th percentile
    throughput: float           # requests/second
    success_rate: float         # percentage
    error_rate: float           # percentage
    avg_quality_score: float    # 0.0 - 1.0
```

---

## Framework Generators

Individual framework code generators.

```python
from multi_agent_generator.frameworks import (
    create_crewai_code,
    create_crewai_flow_code,
    create_langgraph_code,
    create_react_code,
    create_react_lcel_code,
    create_agno_code,
)
```

Each function accepts a configuration dictionary and returns generated code:

```python
code = create_crewai_code(config: dict) -> str
```
