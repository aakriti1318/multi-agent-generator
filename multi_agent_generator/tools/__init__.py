# multi_agent_generator/tools/__init__.py
"""
Tool Auto-Discovery & Generation Module.
Provides pre-built tools and auto-generates custom tools from natural language descriptions.
"""

from .tool_registry import (
    ToolRegistry,
    ToolCategory,
    ToolDefinition,
    get_tool_registry,
)

from .tool_generator import (
    ToolGenerator,
    generate_tool_from_description,
)

__all__ = [
    'ToolRegistry',
    'ToolCategory', 
    'ToolDefinition',
    'get_tool_registry',
    'ToolGenerator',
    'generate_tool_from_description',
]
