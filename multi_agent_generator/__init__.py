## multi-agent-generator/__init__.py
__version__ = "0.5.0"

from .model_inference import (
    ModelInference,
    Message
)

from .frameworks import (
    create_crewai_code,
    create_crewai_flow_code,
    create_langgraph_code,
    create_react_code,
    create_agno_code
)

# New Feature: Tool Auto-Discovery & Generation
from .tools import (
    ToolRegistry,
    ToolCategory,
    ToolDefinition,
    get_tool_registry,
    ToolGenerator,
    generate_tool_from_description,
)

# New Feature: Multi-Agent Orchestration Patterns
from .orchestration import (
    OrchestrationPattern,
    PatternType,
    SupervisorPattern,
    DebatePattern,
    VotingPattern,
    PipelinePattern,
    MapReducePattern,
    get_pattern,
    list_patterns,
    Orchestrator,
    create_orchestrated_system,
)

# New Feature: Evaluation & Testing Framework
from .evaluation import (
    TestGenerator,
    TestCase,
    TestSuite,
    generate_tests,
    AgentEvaluator,
    EvaluationResult,
    EvaluationMetrics,
    evaluate_agent_output,
    Benchmark,
    BenchmarkResult,
    run_benchmark,
)