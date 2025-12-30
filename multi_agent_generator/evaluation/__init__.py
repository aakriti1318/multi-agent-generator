# multi_agent_generator/evaluation/__init__.py
"""
Evaluation & Testing Framework Module.
Provides tools for testing, benchmarking, and validating generated agent systems.
"""

from .test_generator import (
    TestGenerator,
    TestCase,
    TestSuite,
    generate_tests,
)

from .evaluator import (
    AgentEvaluator,
    EvaluationResult,
    EvaluationMetrics,
    evaluate_agent_output,
)

from .benchmark import (
    Benchmark,
    BenchmarkResult,
    run_benchmark,
)

__all__ = [
    'TestGenerator',
    'TestCase',
    'TestSuite',
    'generate_tests',
    'AgentEvaluator',
    'EvaluationResult',
    'EvaluationMetrics',
    'evaluate_agent_output',
    'Benchmark',
    'BenchmarkResult',
    'run_benchmark',
]
