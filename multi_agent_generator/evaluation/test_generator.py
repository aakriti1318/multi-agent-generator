# multi_agent_generator/evaluation/test_generator.py
"""
Test Generator - Auto-generate test cases for multi-agent systems.
No-code approach: Generate comprehensive tests from agent configurations.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
import json


class TestType(Enum):
    """Types of tests that can be generated."""
    UNIT = "unit"                    # Test individual agents
    INTEGRATION = "integration"       # Test agent interactions
    END_TO_END = "end_to_end"        # Test complete workflows
    PERFORMANCE = "performance"       # Test response times
    RELIABILITY = "reliability"       # Test error handling
    QUALITY = "quality"              # Test output quality


@dataclass
class TestCase:
    """Represents a single test case."""
    name: str
    description: str
    test_type: TestType
    input_data: Dict[str, Any]
    expected_behavior: str
    assertions: List[str] = field(default_factory=list)
    timeout_seconds: int = 30
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "test_type": self.test_type.value,
            "input_data": self.input_data,
            "expected_behavior": self.expected_behavior,
            "assertions": self.assertions,
            "timeout_seconds": self.timeout_seconds,
            "tags": self.tags
        }


@dataclass
class TestSuite:
    """Collection of test cases for an agent system."""
    name: str
    description: str
    test_cases: List[TestCase] = field(default_factory=list)
    setup_code: str = ""
    teardown_code: str = ""
    
    def add_test(self, test: TestCase):
        self.test_cases.append(test)
    
    def get_tests_by_type(self, test_type: TestType) -> List[TestCase]:
        return [t for t in self.test_cases if t.test_type == test_type]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "test_cases": [t.to_dict() for t in self.test_cases],
            "setup_code": self.setup_code,
            "teardown_code": self.teardown_code
        }


class TestGenerator:
    """
    Generates test suites for multi-agent systems.
    No-code: Automatically creates tests based on agent configuration.
    """
    
    def __init__(self, model_inference=None):
        """
        Initialize the test generator.
        
        Args:
            model_inference: Optional ModelInference for LLM-based test generation
        """
        self.model = model_inference
    
    def generate_test_suite(
        self,
        config: Dict[str, Any],
        framework: str,
        include_types: Optional[List[TestType]] = None
    ) -> TestSuite:
        """
        Generate a complete test suite for an agent configuration.
        
        Args:
            config: Agent system configuration
            framework: Target framework (crewai, langgraph, etc.)
            include_types: Specific test types to include (all if None)
            
        Returns:
            TestSuite with generated test cases
        """
        agents = config.get("agents", [])
        tasks = config.get("tasks", [])
        
        suite_name = f"{framework}_test_suite"
        suite = TestSuite(
            name=suite_name,
            description=f"Auto-generated test suite for {framework} agent system"
        )
        
        if include_types is None:
            include_types = list(TestType)
        
        # Generate different types of tests
        if TestType.UNIT in include_types:
            suite.test_cases.extend(self._generate_unit_tests(agents, framework))
        
        if TestType.INTEGRATION in include_types:
            suite.test_cases.extend(self._generate_integration_tests(agents, tasks, framework))
        
        if TestType.END_TO_END in include_types:
            suite.test_cases.extend(self._generate_e2e_tests(config, framework))
        
        if TestType.PERFORMANCE in include_types:
            suite.test_cases.extend(self._generate_performance_tests(config, framework))
        
        if TestType.RELIABILITY in include_types:
            suite.test_cases.extend(self._generate_reliability_tests(agents, framework))
        
        if TestType.QUALITY in include_types:
            suite.test_cases.extend(self._generate_quality_tests(config, framework))
        
        # Generate setup/teardown code
        suite.setup_code = self._generate_setup_code(config, framework)
        suite.teardown_code = self._generate_teardown_code(framework)
        
        return suite
    
    def _generate_unit_tests(self, agents: List[Dict], framework: str) -> List[TestCase]:
        """Generate unit tests for individual agents."""
        tests = []
        
        for agent in agents:
            agent_name = agent.get("name", "agent")
            agent_role = agent.get("role", "Agent")
            
            # Test agent initialization
            tests.append(TestCase(
                name=f"test_{agent_name}_initialization",
                description=f"Test that {agent_name} initializes correctly",
                test_type=TestType.UNIT,
                input_data={"agent_config": agent},
                expected_behavior="Agent should initialize without errors",
                assertions=[
                    f"agent.role == '{agent_role}'",
                    "agent is not None",
                    "hasattr(agent, 'execute') or hasattr(agent, 'invoke')"
                ],
                tags=["unit", agent_name, "initialization"]
            ))
            
            # Test agent can process input
            tests.append(TestCase(
                name=f"test_{agent_name}_basic_execution",
                description=f"Test that {agent_name} can process basic input",
                test_type=TestType.UNIT,
                input_data={
                    "agent_config": agent,
                    "test_input": "Hello, please respond."
                },
                expected_behavior="Agent should return a non-empty response",
                assertions=[
                    "response is not None",
                    "len(str(response)) > 0",
                    "isinstance(response, (str, dict))"
                ],
                tags=["unit", agent_name, "execution"]
            ))
            
            # Test agent tools (if any)
            tools = agent.get("tools", [])
            if tools:
                tests.append(TestCase(
                    name=f"test_{agent_name}_tools_available",
                    description=f"Test that {agent_name} has access to its tools",
                    test_type=TestType.UNIT,
                    input_data={"agent_config": agent, "expected_tools": tools},
                    expected_behavior="Agent should have all configured tools available",
                    assertions=[
                        f"len(agent.tools) >= {len(tools)}",
                        "all(hasattr(t, 'name') for t in agent.tools)"
                    ],
                    tags=["unit", agent_name, "tools"]
                ))
        
        return tests
    
    def _generate_integration_tests(
        self,
        agents: List[Dict],
        tasks: List[Dict],
        framework: str
    ) -> List[TestCase]:
        """Generate integration tests for agent interactions."""
        tests = []
        
        if len(agents) < 2:
            return tests
        
        # Test agent communication
        tests.append(TestCase(
            name="test_agent_communication",
            description="Test that agents can communicate with each other",
            test_type=TestType.INTEGRATION,
            input_data={
                "agents": agents[:2],
                "message": "Pass this information to the next agent"
            },
            expected_behavior="Information should be passed between agents",
            assertions=[
                "response contains information from both agents",
                "no communication errors occurred"
            ],
            tags=["integration", "communication"]
        ))
        
        # Test task handoff
        for i, task in enumerate(tasks):
            if i == 0:
                continue
            tests.append(TestCase(
                name=f"test_task_handoff_{i}",
                description=f"Test handoff between task {i-1} and task {i}",
                test_type=TestType.INTEGRATION,
                input_data={
                    "previous_task": tasks[i-1],
                    "current_task": task
                },
                expected_behavior="Task output should be available as input to next task",
                assertions=[
                    "previous_task_output is available",
                    "current_task received correct input"
                ],
                tags=["integration", "handoff", f"task_{i}"]
            ))
        
        # Test agent delegation (if supported)
        delegation_agents = [a for a in agents if a.get("allow_delegation", False)]
        if delegation_agents:
            tests.append(TestCase(
                name="test_agent_delegation",
                description="Test that agents can delegate tasks appropriately",
                test_type=TestType.INTEGRATION,
                input_data={
                    "delegating_agent": delegation_agents[0],
                    "task": "Complex task requiring delegation"
                },
                expected_behavior="Agent should successfully delegate subtasks",
                assertions=[
                    "delegation was triggered",
                    "subtask was completed by appropriate agent"
                ],
                tags=["integration", "delegation"]
            ))
        
        return tests
    
    def _generate_e2e_tests(self, config: Dict[str, Any], framework: str) -> List[TestCase]:
        """Generate end-to-end tests for complete workflows."""
        tests = []
        
        # Test complete workflow execution
        tests.append(TestCase(
            name="test_complete_workflow",
            description="Test the complete agent workflow from start to finish",
            test_type=TestType.END_TO_END,
            input_data={
                "config": config,
                "sample_query": "Process this complete request through all agents"
            },
            expected_behavior="Workflow should complete successfully with final output",
            assertions=[
                "workflow completed without errors",
                "final_output is not None",
                "all tasks were executed"
            ],
            timeout_seconds=120,
            tags=["e2e", "workflow"]
        ))
        
        # Test with various input types
        input_variations = [
            {"type": "short", "input": "Brief query"},
            {"type": "detailed", "input": "A much more detailed query with specific requirements and multiple aspects to consider"},
            {"type": "technical", "input": "Technical query: analyze the API response and generate documentation"},
        ]
        
        for variation in input_variations:
            tests.append(TestCase(
                name=f"test_workflow_{variation['type']}_input",
                description=f"Test workflow with {variation['type']} input",
                test_type=TestType.END_TO_END,
                input_data={
                    "config": config,
                    "query": variation["input"]
                },
                expected_behavior=f"Workflow should handle {variation['type']} input correctly",
                assertions=[
                    "response is appropriate for input type",
                    "no errors during processing"
                ],
                timeout_seconds=60,
                tags=["e2e", variation["type"]]
            ))
        
        return tests
    
    def _generate_performance_tests(self, config: Dict[str, Any], framework: str) -> List[TestCase]:
        """Generate performance tests."""
        tests = []
        
        # Response time test
        tests.append(TestCase(
            name="test_response_time",
            description="Test that agent response time is within acceptable limits",
            test_type=TestType.PERFORMANCE,
            input_data={
                "config": config,
                "query": "Simple query for timing",
                "max_response_time_ms": 30000
            },
            expected_behavior="Response should be received within 30 seconds",
            assertions=[
                "response_time_ms < 30000",
                "response is valid"
            ],
            timeout_seconds=60,
            tags=["performance", "timing"]
        ))
        
        # Throughput test
        tests.append(TestCase(
            name="test_throughput",
            description="Test system throughput with multiple queries",
            test_type=TestType.PERFORMANCE,
            input_data={
                "config": config,
                "queries": ["Query 1", "Query 2", "Query 3"],
                "concurrent": False
            },
            expected_behavior="System should handle multiple queries efficiently",
            assertions=[
                "all queries processed successfully",
                "average_response_time is reasonable"
            ],
            timeout_seconds=180,
            tags=["performance", "throughput"]
        ))
        
        # Memory usage test
        tests.append(TestCase(
            name="test_memory_usage",
            description="Test that memory usage stays within bounds",
            test_type=TestType.PERFORMANCE,
            input_data={
                "config": config,
                "max_memory_mb": 500
            },
            expected_behavior="Memory usage should not exceed 500MB",
            assertions=[
                "peak_memory_mb < 500",
                "no memory leaks detected"
            ],
            tags=["performance", "memory"]
        ))
        
        return tests
    
    def _generate_reliability_tests(self, agents: List[Dict], framework: str) -> List[TestCase]:
        """Generate reliability and error handling tests."""
        tests = []
        
        # Test error handling
        tests.append(TestCase(
            name="test_invalid_input_handling",
            description="Test that agents handle invalid input gracefully",
            test_type=TestType.RELIABILITY,
            input_data={
                "agents": agents,
                "invalid_inputs": [None, "", {}, [], "   "]
            },
            expected_behavior="Agents should handle invalid input without crashing",
            assertions=[
                "no unhandled exceptions",
                "appropriate error message returned"
            ],
            tags=["reliability", "error_handling"]
        ))
        
        # Test timeout handling
        tests.append(TestCase(
            name="test_timeout_handling",
            description="Test that system handles timeouts appropriately",
            test_type=TestType.RELIABILITY,
            input_data={
                "agents": agents,
                "timeout_ms": 100,  # Very short timeout to trigger
                "query": "Process this request"
            },
            expected_behavior="System should handle timeout gracefully",
            assertions=[
                "timeout exception is caught",
                "system remains responsive"
            ],
            tags=["reliability", "timeout"]
        ))
        
        # Test recovery
        tests.append(TestCase(
            name="test_failure_recovery",
            description="Test system recovery after partial failure",
            test_type=TestType.RELIABILITY,
            input_data={
                "agents": agents,
                "simulate_failure": True
            },
            expected_behavior="System should recover from partial failures",
            assertions=[
                "system recovered successfully",
                "subsequent requests work correctly"
            ],
            tags=["reliability", "recovery"]
        ))
        
        # Test idempotency
        tests.append(TestCase(
            name="test_idempotency",
            description="Test that repeated calls produce consistent results",
            test_type=TestType.RELIABILITY,
            input_data={
                "agents": agents,
                "query": "Deterministic query",
                "repetitions": 3
            },
            expected_behavior="Repeated calls should produce similar/consistent results",
            assertions=[
                "results are consistent across calls",
                "no side effects from repetition"
            ],
            tags=["reliability", "idempotency"]
        ))
        
        return tests
    
    def _generate_quality_tests(self, config: Dict[str, Any], framework: str) -> List[TestCase]:
        """Generate output quality tests."""
        tests = []
        
        # Test output relevance
        tests.append(TestCase(
            name="test_output_relevance",
            description="Test that output is relevant to the input query",
            test_type=TestType.QUALITY,
            input_data={
                "config": config,
                "query": "What is machine learning?",
                "expected_keywords": ["machine", "learning", "data", "algorithm", "model"]
            },
            expected_behavior="Output should contain relevant keywords and concepts",
            assertions=[
                "relevance_score > 0.7",
                "contains expected keywords"
            ],
            tags=["quality", "relevance"]
        ))
        
        # Test output completeness
        tests.append(TestCase(
            name="test_output_completeness",
            description="Test that output addresses all aspects of the query",
            test_type=TestType.QUALITY,
            input_data={
                "config": config,
                "query": "Compare Python and JavaScript for web development",
                "required_aspects": ["Python", "JavaScript", "comparison", "web"]
            },
            expected_behavior="Output should address all aspects of the comparison",
            assertions=[
                "all required aspects mentioned",
                "comparison is balanced"
            ],
            tags=["quality", "completeness"]
        ))
        
        # Test output coherence
        tests.append(TestCase(
            name="test_output_coherence",
            description="Test that output is coherent and well-structured",
            test_type=TestType.QUALITY,
            input_data={
                "config": config,
                "query": "Explain the software development lifecycle"
            },
            expected_behavior="Output should be coherent and logically structured",
            assertions=[
                "coherence_score > 0.8",
                "has logical flow"
            ],
            tags=["quality", "coherence"]
        ))
        
        # Test output format
        tests.append(TestCase(
            name="test_output_format",
            description="Test that output follows expected format",
            test_type=TestType.QUALITY,
            input_data={
                "config": config,
                "query": "List 5 programming best practices",
                "expected_format": "numbered_list"
            },
            expected_behavior="Output should be in the expected format",
            assertions=[
                "format matches expected",
                "contains 5 items"
            ],
            tags=["quality", "format"]
        ))
        
        return tests
    
    def _generate_setup_code(self, config: Dict[str, Any], framework: str) -> str:
        """Generate test setup code."""
        if framework == "crewai":
            return '''
import pytest
from crewai import Agent, Task, Crew
import os

@pytest.fixture(scope="module")
def setup_agents():
    """Setup agents for testing."""
    # Configure environment
    os.environ.setdefault("OPENAI_API_KEY", "test-key")
    
    # Initialize agents from config
    agents = []
    # Add agent initialization here
    yield agents
    
    # Cleanup
    agents.clear()

@pytest.fixture
def sample_query():
    return "Test query for agent system"
'''
        elif framework == "langgraph":
            return '''
import pytest
from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
import os

@pytest.fixture(scope="module")
def setup_graph():
    """Setup LangGraph for testing."""
    os.environ.setdefault("OPENAI_API_KEY", "test-key")
    
    # Initialize graph
    # Add graph setup here
    yield None
    
    # Cleanup

@pytest.fixture
def sample_state():
    return {"messages": [], "next": ""}
'''
        else:
            return '''
import pytest
import os

@pytest.fixture(scope="module")
def setup_system():
    """Setup agent system for testing."""
    os.environ.setdefault("OPENAI_API_KEY", "test-key")
    yield None

@pytest.fixture
def sample_input():
    return "Test input"
'''
    
    def _generate_teardown_code(self, framework: str) -> str:
        """Generate test teardown code."""
        return '''
def teardown_module():
    """Cleanup after all tests."""
    # Add cleanup logic here
    pass
'''
    
    def generate_pytest_file(self, suite: TestSuite) -> str:
        """
        Generate a complete pytest test file from a test suite.
        
        Args:
            suite: TestSuite to convert
            
        Returns:
            Python code string for pytest file
        """
        code = f'''"""
{suite.description}
Auto-generated test suite: {suite.name}
"""

import pytest
import time
import tracemalloc
from typing import Dict, Any, List

{suite.setup_code}

{suite.teardown_code}

'''
        
        # Generate test functions
        for test in suite.test_cases:
            code += self._generate_test_function(test)
            code += "\n\n"
        
        # Add test runner section
        code += '''
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
'''
        
        return code
    
    def _generate_test_function(self, test: TestCase) -> str:
        """Generate a pytest test function from a TestCase."""
        tags_str = ", ".join([f'"{t}"' for t in test.tags])
        
        code = f'''
@pytest.mark.timeout({test.timeout_seconds})
@pytest.mark.parametrize("tags", [[{tags_str}]])
def {test.name}(tags):
    """
    {test.description}
    
    Test Type: {test.test_type.value}
    Expected: {test.expected_behavior}
    """
    # Test input
    input_data = {json.dumps(test.input_data, indent=8)}
    
    # Execute test
    try:
        # TODO: Add actual test implementation
        # This is a placeholder that should be customized
        result = None  # Replace with actual execution
        
        # Assertions
'''
        
        for assertion in test.assertions:
            # Convert assertion to pytest assert
            code += f'        # assert {assertion}\n'
        
        code += '''        
        assert True  # Placeholder - replace with actual assertions
        
    except Exception as e:
        pytest.fail(f"Test failed: {e}")
'''
        
        return code


def generate_tests(
    config: Dict[str, Any],
    framework: str,
    output_format: str = "pytest"
) -> str:
    """
    Convenience function to generate tests for an agent configuration.
    
    Args:
        config: Agent system configuration
        framework: Target framework
        output_format: Output format (pytest, json)
        
    Returns:
        Generated test code or JSON
    """
    generator = TestGenerator()
    suite = generator.generate_test_suite(config, framework)
    
    if output_format == "pytest":
        return generator.generate_pytest_file(suite)
    elif output_format == "json":
        return json.dumps(suite.to_dict(), indent=2)
    else:
        raise ValueError(f"Unknown output format: {output_format}")
