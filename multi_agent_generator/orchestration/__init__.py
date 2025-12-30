# multi_agent_generator/orchestration/__init__.py
"""
Multi-Agent Orchestration Patterns Module.
Provides pre-built orchestration patterns for agent collaboration.
"""

from .patterns import (
    OrchestrationPattern,
    PatternType,
    SupervisorPattern,
    DebatePattern,
    VotingPattern,
    PipelinePattern,
    MapReducePattern,
    get_pattern,
    list_patterns,
)

from .orchestrator import (
    Orchestrator,
    create_orchestrated_system,
)

__all__ = [
    'OrchestrationPattern',
    'PatternType',
    'SupervisorPattern',
    'DebatePattern',
    'VotingPattern',
    'PipelinePattern',
    'MapReducePattern',
    'get_pattern',
    'list_patterns',
    'Orchestrator',
    'create_orchestrated_system',
]
