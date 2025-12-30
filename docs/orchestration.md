# Multi-Agent Orchestration Patterns

The Orchestration module provides battle-tested patterns for coordinating multiple agents to work together effectively.

## Overview

Choose from 5 orchestration patterns based on your use case:

| Pattern | Best For | Description |
|---------|----------|-------------|
| **Supervisor** | Delegating tasks | Central coordinator routes work to specialists |
| **Debate** | Reaching consensus | Agents discuss and refine answers |
| **Voting** | Democratic decisions | Agents vote on the best response |
| **Pipeline** | Sequential processing | Chain of specialized processing steps |
| **MapReduce** | Parallel processing | Split work, process in parallel, aggregate |

---

## Quick Start

```python
from multi_agent_generator.orchestration import Orchestrator, PatternType

orchestrator = Orchestrator()

# Generate from natural language
result = orchestrator.generate_from_description(
    "I need a research team where a manager delegates to specialists"
)
print(result["code"])
```

---

## Patterns

### Supervisor Pattern

A central supervisor agent coordinates work among specialist agents.

```python
from multi_agent_generator.orchestration import Orchestrator, PatternType

orchestrator = Orchestrator()

config = orchestrator.create_pattern_config(
    pattern_type=PatternType.SUPERVISOR,
    agents=["researcher", "writer", "reviewer"],
    task_description="Create a comprehensive market analysis report"
)

code = orchestrator.generate_code(config)
```

**Use Cases:**
- Task delegation and management
- Quality control workflows
- Hierarchical team structures

**How It Works:**
1. Supervisor receives the task
2. Supervisor analyzes and delegates to appropriate specialist
3. Specialist completes subtask and reports back
4. Supervisor aggregates results or assigns next task

---

### Debate Pattern

Multiple agents discuss and refine an answer through structured debate.

```python
from multi_agent_generator.orchestration import Orchestrator, PatternType

orchestrator = Orchestrator()

config = orchestrator.create_pattern_config(
    pattern_type=PatternType.DEBATE,
    agents=["optimist", "pessimist", "moderator"],
    task_description="Evaluate the risks and benefits of a new product launch",
    max_rounds=3
)

code = orchestrator.generate_code(config)
```

**Use Cases:**
- Complex decision making
- Risk assessment
- Strategy evaluation

**How It Works:**
1. Each agent presents their perspective
2. Agents critique and respond to each other
3. Moderator synthesizes final consensus
4. Process repeats for specified rounds

---

### Voting Pattern

Agents independently solve a problem, then vote on the best solution.

```python
from multi_agent_generator.orchestration import Orchestrator, PatternType

orchestrator = Orchestrator()

config = orchestrator.create_pattern_config(
    pattern_type=PatternType.VOTING,
    agents=["analyst_1", "analyst_2", "analyst_3"],
    task_description="Determine the best investment strategy",
    voting_method="majority"  # or "weighted", "ranked"
)

code = orchestrator.generate_code(config)
```

**Use Cases:**
- Democratic decision making
- Reducing individual bias
- Ensemble approaches

**Voting Methods:**
- `majority` - Simple majority wins
- `weighted` - Votes weighted by agent expertise
- `ranked` - Ranked choice voting

---

### Pipeline Pattern

Agents process work sequentially, each adding their expertise.

```python
from multi_agent_generator.orchestration import Orchestrator, PatternType

orchestrator = Orchestrator()

config = orchestrator.create_pattern_config(
    pattern_type=PatternType.PIPELINE,
    agents=["data_collector", "analyzer", "report_writer", "reviewer"],
    task_description="Generate a quarterly business report"
)

code = orchestrator.generate_code(config)
```

**Use Cases:**
- Content creation workflows
- Data processing pipelines
- Document review processes

**How It Works:**
1. First agent processes input
2. Output passes to next agent
3. Each agent transforms and enriches
4. Final agent produces output

---

### MapReduce Pattern

Split work across multiple agents, process in parallel, then aggregate.

```python
from multi_agent_generator.orchestration import Orchestrator, PatternType

orchestrator = Orchestrator()

config = orchestrator.create_pattern_config(
    pattern_type=PatternType.MAP_REDUCE,
    agents=["mapper_1", "mapper_2", "mapper_3", "reducer"],
    task_description="Analyze customer feedback from multiple sources",
    chunk_strategy="by_source"  # or "by_size", "by_topic"
)

code = orchestrator.generate_code(config)
```

**Use Cases:**
- Large-scale data analysis
- Parallel document processing
- Distributed research tasks

**How It Works:**
1. Input is split into chunks
2. Mapper agents process chunks in parallel
3. Reducer agent aggregates all results
4. Final output is synthesized

---

## Natural Language Generation

Describe your orchestration needs in plain English:

```python
from multi_agent_generator.orchestration import Orchestrator

orchestrator = Orchestrator()

# The system automatically selects the best pattern
result = orchestrator.generate_from_description(
    "Build a content team with a supervisor managing writers and editors"
)

print(result["pattern"])  # SUPERVISOR
print(result["agents"])   # ["supervisor", "writer", "editor"]
print(result["code"])     # Generated code
```

---

## API Reference

### Orchestrator

| Method | Description |
|--------|-------------|
| `generate_from_description(description)` | Generate orchestration from natural language |
| `create_pattern_config(pattern_type, agents, ...)` | Create configuration for a pattern |
| `generate_code(config)` | Generate executable code from config |
| `list_patterns()` | List all available patterns |

### PatternType

| Value | Description |
|-------|-------------|
| `SUPERVISOR` | Central coordinator pattern |
| `DEBATE` | Discussion and consensus pattern |
| `VOTING` | Democratic voting pattern |
| `PIPELINE` | Sequential processing pattern |
| `MAP_REDUCE` | Parallel processing pattern |

### Pattern Classes

Each pattern has a dedicated class with specific configuration options:

- `SupervisorPattern` - Configure supervisor behavior and delegation rules
- `DebatePattern` - Set debate rounds and moderation style
- `VotingPattern` - Choose voting method and tie-breakers
- `PipelinePattern` - Define stage transitions and error handling
- `MapReducePattern` - Configure chunking and aggregation strategies
