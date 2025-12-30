# Evaluation & Testing Framework

The Evaluation module helps you test your agents and measure output quality automatically.

## Overview

- **Test Generator** - Auto-generate pytest test suites
- **Agent Evaluator** - Measure output quality with 7 metrics
- **Benchmark** - Performance testing and comparison

---

## Test Generator

### Quick Start

```python
from multi_agent_generator.evaluation import TestGenerator

test_gen = TestGenerator()

# Generate a complete test suite
test_suite = test_gen.generate_test_suite(
    agent_config=your_config,
    test_types=["unit", "integration", "e2e"]
)

# Save to files
test_suite.save("tests/")
```

### Test Types

| Type | Description | What It Tests |
|------|-------------|---------------|
| **Unit** | Individual component testing | Single agent functions |
| **Integration** | Multi-agent interaction | Agent communication |
| **E2E (End-to-End)** | Full workflow validation | Complete pipelines |
| **Performance** | Response time & throughput | Speed and efficiency |
| **Reliability** | Error handling & recovery | Edge cases and failures |
| **Quality** | Output quality metrics | Content accuracy |

### Generating Specific Tests

```python
from multi_agent_generator.evaluation import TestGenerator, TestType

test_gen = TestGenerator()

# Generate only unit tests
unit_tests = test_gen.generate_tests(
    agent_config=config,
    test_type=TestType.UNIT
)

# Generate performance tests
perf_tests = test_gen.generate_tests(
    agent_config=config,
    test_type=TestType.PERFORMANCE,
    options={
        "iterations": 100,
        "timeout": 30
    }
)
```

### Generated Test Example

```python
# Generated test file: test_research_agent.py
import pytest
from your_module import ResearchAgent

class TestResearchAgent:
    """Unit tests for ResearchAgent."""
    
    @pytest.fixture
    def agent(self):
        return ResearchAgent()
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert agent.role == "Researcher"
    
    def test_agent_responds_to_query(self, agent):
        """Test agent responds to basic query."""
        response = agent.run("What is AI?")
        assert response is not None
        assert len(response) > 0
    
    def test_agent_handles_empty_input(self, agent):
        """Test agent handles empty input gracefully."""
        with pytest.raises(ValueError):
            agent.run("")
```

---

## Agent Evaluator

### Quick Start

```python
from multi_agent_generator.evaluation import AgentEvaluator

evaluator = AgentEvaluator()

result = evaluator.evaluate(
    agent_output="The market analysis shows growth of 15%...",
    expected_output="Market trends indicate positive growth...",
    task_description="Analyze Q4 sales data"
)

print(f"Overall Score: {result.overall_score}")  # 0.0 - 1.0
print(f"Metrics: {result.metrics}")
```

### Evaluation Metrics

| Metric | Description | Range |
|--------|-------------|-------|
| **Relevance** | How relevant is the output to the task | 0.0 - 1.0 |
| **Completeness** | Does it cover all required aspects | 0.0 - 1.0 |
| **Coherence** | Is the output logically structured | 0.0 - 1.0 |
| **Accuracy** | Factual correctness (when verifiable) | 0.0 - 1.0 |
| **Conciseness** | Appropriate length without redundancy | 0.0 - 1.0 |
| **Format** | Follows expected format/structure | 0.0 - 1.0 |
| **Tone** | Appropriate tone for the context | 0.0 - 1.0 |

### Detailed Evaluation

```python
from multi_agent_generator.evaluation import AgentEvaluator, EvaluationConfig

evaluator = AgentEvaluator()

# Configure which metrics to use
config = EvaluationConfig(
    metrics=["relevance", "completeness", "accuracy"],
    weights={
        "relevance": 0.4,
        "completeness": 0.3,
        "accuracy": 0.3
    }
)

result = evaluator.evaluate(
    agent_output=output,
    expected_output=expected,
    task_description=task,
    config=config
)

# Access individual metrics
print(result.metrics["relevance"])
print(result.metrics["completeness"])
print(result.metrics["accuracy"])
```

### Batch Evaluation

```python
from multi_agent_generator.evaluation import AgentEvaluator

evaluator = AgentEvaluator()

# Evaluate multiple outputs
test_cases = [
    {"output": "...", "expected": "...", "task": "..."},
    {"output": "...", "expected": "...", "task": "..."},
]

results = evaluator.evaluate_batch(test_cases)

# Get aggregate statistics
avg_score = sum(r.overall_score for r in results) / len(results)
print(f"Average Score: {avg_score}")
```

---

## Benchmark

### Running Benchmarks

```python
from multi_agent_generator.evaluation import Benchmark

benchmark = Benchmark()

# Benchmark a single agent
results = benchmark.run(
    agent=your_agent,
    test_cases=test_cases,
    iterations=10
)

print(f"Avg Response Time: {results.avg_response_time}ms")
print(f"Throughput: {results.throughput} req/s")
print(f"Success Rate: {results.success_rate}%")
```

### Comparing Agents

```python
from multi_agent_generator.evaluation import Benchmark

benchmark = Benchmark()

# Compare multiple agents
comparison = benchmark.compare(
    agents={
        "agent_v1": agent_v1,
        "agent_v2": agent_v2,
    },
    test_cases=test_cases
)

# View comparison report
print(comparison.summary())
```

### Benchmark Metrics

| Metric | Description |
|--------|-------------|
| `avg_response_time` | Average time to respond (ms) |
| `p95_response_time` | 95th percentile response time |
| `throughput` | Requests per second |
| `success_rate` | Percentage of successful responses |
| `error_rate` | Percentage of errors |
| `avg_quality_score` | Average output quality |

---

## Integration with CI/CD

### Running Tests in CI

```yaml
# .github/workflows/test.yml
name: Agent Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -e ".[dev]"
      - run: pytest tests/ -v
```

### Quality Gates

```python
from multi_agent_generator.evaluation import AgentEvaluator

evaluator = AgentEvaluator()
result = evaluator.evaluate(output, expected, task)

# Fail CI if quality is below threshold
assert result.overall_score >= 0.8, f"Quality score {result.overall_score} below threshold"
```

---

## API Reference

### TestGenerator

| Method | Description |
|--------|-------------|
| `generate_test_suite(config, test_types)` | Generate complete test suite |
| `generate_tests(config, test_type)` | Generate specific test type |

### AgentEvaluator

| Method | Description |
|--------|-------------|
| `evaluate(output, expected, task)` | Evaluate single output |
| `evaluate_batch(test_cases)` | Evaluate multiple outputs |

### Benchmark

| Method | Description |
|--------|-------------|
| `run(agent, test_cases, iterations)` | Run benchmark on agent |
| `compare(agents, test_cases)` | Compare multiple agents |

### EvaluationResult

| Property | Type | Description |
|----------|------|-------------|
| `overall_score` | float | Overall quality score (0.0-1.0) |
| `metrics` | dict | Individual metric scores |
| `feedback` | str | Detailed feedback text |
| `passed` | bool | Whether it passed threshold |
