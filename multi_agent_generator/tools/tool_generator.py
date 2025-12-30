# multi_agent_generator/tools/tool_generator.py
"""
Tool Generator - Auto-generate custom tools from natural language descriptions.
No-code approach: Users describe what they need, and the tool is generated automatically.
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .tool_registry import ToolRegistry, ToolDefinition, ToolCategory, get_tool_registry


@dataclass
class GeneratedTool:
    """Represents an auto-generated tool."""
    name: str
    description: str
    parameters: Dict[str, Any]
    code: str
    category: ToolCategory
    

class ToolGenerator:
    """
    Generates custom tools from natural language descriptions.
    Uses LLM to understand requirements and generate appropriate tool code.
    """
    
    def __init__(self, model_inference=None):
        """
        Initialize the tool generator.
        
        Args:
            model_inference: Optional ModelInference instance for LLM-based generation
        """
        self.model = model_inference
        self.registry = get_tool_registry()
    
    def generate_from_description(self, description: str) -> GeneratedTool:
        """
        Generate a tool from a natural language description.
        
        Args:
            description: Natural language description of the desired tool
            
        Returns:
            GeneratedTool with name, code, and metadata
        """
        if self.model:
            return self._generate_with_llm(description)
        else:
            return self._generate_with_templates(description)
    
    def _generate_with_templates(self, description: str) -> GeneratedTool:
        """Generate tool using pattern matching and templates."""
        description_lower = description.lower()
        
        # Pattern matching for common tool types
        patterns = {
            "api": {
                "keywords": ["api", "endpoint", "rest", "http", "fetch", "request"],
                "category": ToolCategory.API_INTEGRATION,
                "template": self._api_tool_template
            },
            "file": {
                "keywords": ["file", "read", "write", "save", "load", "document"],
                "category": ToolCategory.FILE_OPERATIONS,
                "template": self._file_tool_template
            },
            "data": {
                "keywords": ["data", "csv", "json", "parse", "analyze", "process"],
                "category": ToolCategory.DATA_PROCESSING,
                "template": self._data_tool_template
            },
            "search": {
                "keywords": ["search", "find", "lookup", "query", "web", "google"],
                "category": ToolCategory.WEB_SEARCH,
                "template": self._search_tool_template
            },
            "calculate": {
                "keywords": ["calculate", "compute", "math", "formula", "convert"],
                "category": ToolCategory.MATH_CALCULATION,
                "template": self._calculator_tool_template
            },
            "text": {
                "keywords": ["text", "string", "extract", "transform", "format", "summarize"],
                "category": ToolCategory.TEXT_PROCESSING,
                "template": self._text_tool_template
            },
            "database": {
                "keywords": ["database", "sql", "query", "table", "record"],
                "category": ToolCategory.DATABASE,
                "template": self._database_tool_template
            },
        }
        
        # Find matching pattern
        best_match = None
        best_score = 0
        
        for pattern_name, pattern_info in patterns.items():
            score = sum(1 for kw in pattern_info["keywords"] if kw in description_lower)
            if score > best_score:
                best_score = score
                best_match = pattern_info
        
        if best_match and best_score > 0:
            return best_match["template"](description)
        else:
            return self._generic_tool_template(description)
    
    def _generate_with_llm(self, description: str) -> GeneratedTool:
        """Generate tool using LLM for more accurate understanding."""
        from ..model_inference import Message
        
        system_prompt = """You are an expert at creating Python tools for AI agents.
Given a description of what a tool should do, generate the appropriate tool code.

Return a JSON object with:
{
    "name": "snake_case_tool_name",
    "description": "Clear description of what the tool does",
    "category": "one of: web_search, file_operations, data_processing, code_execution, api_integration, database, communication, math_calculation, text_processing, custom",
    "parameters": {
        "param_name": {"type": "str/int/float/bool/dict/list", "description": "param description", "required": true/false}
    },
    "code": "Full Python class code inheriting from BaseTool"
}

Make the tool practical and include error handling."""
        
        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=f"Create a tool that: {description}")
        ]
        
        try:
            response = self.model.generate_text(messages)
            
            # Parse JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                tool_data = json.loads(response[json_start:json_end])
                
                category = ToolCategory.CUSTOM
                try:
                    category = ToolCategory(tool_data.get("category", "custom"))
                except ValueError:
                    pass
                
                return GeneratedTool(
                    name=tool_data["name"],
                    description=tool_data["description"],
                    parameters=tool_data.get("parameters", {}),
                    code=tool_data["code"],
                    category=category
                )
        except Exception:
            pass
        
        # Fallback to template-based generation
        return self._generate_with_templates(description)
    
    def _extract_tool_name(self, description: str) -> str:
        """Extract a tool name from description."""
        # Remove common words and create snake_case name
        words = description.lower().split()
        stop_words = {"a", "an", "the", "to", "for", "that", "which", "can", "will", "should", "tool", "create", "make", "build"}
        name_words = [w for w in words[:5] if w not in stop_words and w.isalnum()]
        return "_".join(name_words[:3]) + "_tool" if name_words else "custom_tool"
    
    def _api_tool_template(self, description: str) -> GeneratedTool:
        """Generate an API integration tool."""
        name = self._extract_tool_name(description)
        
        code = f'''
class {self._to_class_name(name)}(BaseTool):
    name = "{name}"
    description = """{description}"""
    
    def _run(self, endpoint: str, method: str = "GET", params: dict = None, headers: dict = None) -> str:
        import requests
        try:
            response = requests.request(
                method=method.upper(),
                url=endpoint,
                params=params,
                headers=headers or {{}},
                timeout=30
            )
            response.raise_for_status()
            return response.text[:2000]
        except requests.RequestException as e:
            return f"API Error: {{str(e)}}"
    
    async def _arun(self, endpoint: str, method: str = "GET", params: dict = None, headers: dict = None) -> str:
        return self._run(endpoint, method, params, headers)
'''
        
        return GeneratedTool(
            name=name,
            description=description,
            parameters={
                "endpoint": {"type": "str", "description": "API endpoint URL", "required": True},
                "method": {"type": "str", "description": "HTTP method", "required": False},
                "params": {"type": "dict", "description": "Query parameters", "required": False},
                "headers": {"type": "dict", "description": "Request headers", "required": False}
            },
            code=code,
            category=ToolCategory.API_INTEGRATION
        )
    
    def _file_tool_template(self, description: str) -> GeneratedTool:
        """Generate a file operations tool."""
        name = self._extract_tool_name(description)
        
        code = f'''
class {self._to_class_name(name)}(BaseTool):
    name = "{name}"
    description = """{description}"""
    
    def _run(self, file_path: str, operation: str = "read", content: str = None) -> str:
        import os
        try:
            if operation == "read":
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            elif operation == "write" and content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return f"Successfully wrote to {{file_path}}"
            elif operation == "append" and content:
                with open(file_path, 'a', encoding='utf-8') as f:
                    f.write(content)
                return f"Successfully appended to {{file_path}}"
            elif operation == "exists":
                return str(os.path.exists(file_path))
            else:
                return "Invalid operation. Use: read, write, append, or exists"
        except Exception as e:
            return f"File operation error: {{str(e)}}"
    
    async def _arun(self, file_path: str, operation: str = "read", content: str = None) -> str:
        return self._run(file_path, operation, content)
'''
        
        return GeneratedTool(
            name=name,
            description=description,
            parameters={
                "file_path": {"type": "str", "description": "Path to the file", "required": True},
                "operation": {"type": "str", "description": "Operation: read, write, append, exists", "required": False},
                "content": {"type": "str", "description": "Content for write/append", "required": False}
            },
            code=code,
            category=ToolCategory.FILE_OPERATIONS
        )
    
    def _data_tool_template(self, description: str) -> GeneratedTool:
        """Generate a data processing tool."""
        name = self._extract_tool_name(description)
        
        code = f'''
class {self._to_class_name(name)}(BaseTool):
    name = "{name}"
    description = """{description}"""
    
    def _run(self, data: str, operation: str = "parse") -> str:
        import json
        try:
            if operation == "parse":
                # Try to parse as JSON
                parsed = json.loads(data)
                return json.dumps(parsed, indent=2)
            elif operation == "keys":
                parsed = json.loads(data)
                if isinstance(parsed, dict):
                    return str(list(parsed.keys()))
                return "Data is not a dictionary"
            elif operation == "count":
                parsed = json.loads(data)
                if isinstance(parsed, (list, dict)):
                    return str(len(parsed))
                return "1"
            else:
                return json.dumps(json.loads(data), indent=2)
        except json.JSONDecodeError:
            return f"Could not parse as JSON: {{data[:100]}}..."
        except Exception as e:
            return f"Data processing error: {{str(e)}}"
    
    async def _arun(self, data: str, operation: str = "parse") -> str:
        return self._run(data, operation)
'''
        
        return GeneratedTool(
            name=name,
            description=description,
            parameters={
                "data": {"type": "str", "description": "Data to process", "required": True},
                "operation": {"type": "str", "description": "Operation: parse, keys, count", "required": False}
            },
            code=code,
            category=ToolCategory.DATA_PROCESSING
        )
    
    def _search_tool_template(self, description: str) -> GeneratedTool:
        """Generate a search tool."""
        name = self._extract_tool_name(description)
        
        code = f'''
class {self._to_class_name(name)}(BaseTool):
    name = "{name}"
    description = """{description}"""
    
    def _run(self, query: str, source: str = "web") -> str:
        # Placeholder for search implementation
        # In production, integrate with actual search APIs
        return f"Search results for '{{query}}' from {{source}}: [Implement actual search API integration]"
    
    async def _arun(self, query: str, source: str = "web") -> str:
        return self._run(query, source)
'''
        
        return GeneratedTool(
            name=name,
            description=description,
            parameters={
                "query": {"type": "str", "description": "Search query", "required": True},
                "source": {"type": "str", "description": "Search source", "required": False}
            },
            code=code,
            category=ToolCategory.WEB_SEARCH
        )
    
    def _calculator_tool_template(self, description: str) -> GeneratedTool:
        """Generate a calculation tool."""
        name = self._extract_tool_name(description)
        
        code = f'''
class {self._to_class_name(name)}(BaseTool):
    name = "{name}"
    description = """{description}"""
    
    def _run(self, expression: str) -> str:
        import math
        try:
            # Safe evaluation with math functions
            allowed = {{
                'abs': abs, 'round': round, 'min': min, 'max': max,
                'sum': sum, 'pow': pow, 'sqrt': math.sqrt, 'sin': math.sin,
                'cos': math.cos, 'tan': math.tan, 'log': math.log, 'log10': math.log10,
                'exp': math.exp, 'pi': math.pi, 'e': math.e
            }}
            result = eval(expression, {{"__builtins__": {{}}}}, allowed)
            return str(result)
        except Exception as e:
            return f"Calculation error: {{str(e)}}"
    
    async def _arun(self, expression: str) -> str:
        return self._run(expression)
'''
        
        return GeneratedTool(
            name=name,
            description=description,
            parameters={
                "expression": {"type": "str", "description": "Mathematical expression", "required": True}
            },
            code=code,
            category=ToolCategory.MATH_CALCULATION
        )
    
    def _text_tool_template(self, description: str) -> GeneratedTool:
        """Generate a text processing tool."""
        name = self._extract_tool_name(description)
        
        code = f'''
class {self._to_class_name(name)}(BaseTool):
    name = "{name}"
    description = """{description}"""
    
    def _run(self, text: str, operation: str = "analyze") -> str:
        import re
        try:
            if operation == "analyze":
                words = len(text.split())
                chars = len(text)
                sentences = len(re.split(r'[.!?]+', text))
                return f"Words: {{words}}, Characters: {{chars}}, Sentences: {{sentences}}"
            elif operation == "upper":
                return text.upper()
            elif operation == "lower":
                return text.lower()
            elif operation == "reverse":
                return text[::-1]
            elif operation == "words":
                return str(text.split())
            else:
                return text
        except Exception as e:
            return f"Text processing error: {{str(e)}}"
    
    async def _arun(self, text: str, operation: str = "analyze") -> str:
        return self._run(text, operation)
'''
        
        return GeneratedTool(
            name=name,
            description=description,
            parameters={
                "text": {"type": "str", "description": "Text to process", "required": True},
                "operation": {"type": "str", "description": "Operation: analyze, upper, lower, reverse, words", "required": False}
            },
            code=code,
            category=ToolCategory.TEXT_PROCESSING
        )
    
    def _database_tool_template(self, description: str) -> GeneratedTool:
        """Generate a database tool."""
        name = self._extract_tool_name(description)
        
        code = f'''
class {self._to_class_name(name)}(BaseTool):
    name = "{name}"
    description = """{description}"""
    
    def _run(self, query: str, database_path: str = "database.db") -> str:
        import sqlite3
        try:
            conn = sqlite3.connect(database_path)
            cursor = conn.cursor()
            cursor.execute(query)
            
            if query.strip().upper().startswith("SELECT"):
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                conn.close()
                return f"Columns: {{columns}}\\nResults: {{results}}"
            else:
                conn.commit()
                affected = cursor.rowcount
                conn.close()
                return f"Query executed. Rows affected: {{affected}}"
        except Exception as e:
            return f"Database error: {{str(e)}}"
    
    async def _arun(self, query: str, database_path: str = "database.db") -> str:
        return self._run(query, database_path)
'''
        
        return GeneratedTool(
            name=name,
            description=description,
            parameters={
                "query": {"type": "str", "description": "SQL query", "required": True},
                "database_path": {"type": "str", "description": "Path to SQLite database", "required": False}
            },
            code=code,
            category=ToolCategory.DATABASE
        )
    
    def _generic_tool_template(self, description: str) -> GeneratedTool:
        """Generate a generic tool when no specific pattern matches."""
        name = self._extract_tool_name(description)
        
        code = f'''
class {self._to_class_name(name)}(BaseTool):
    name = "{name}"
    description = """{description}"""
    
    def _run(self, input_data: str) -> str:
        # Implement the tool logic here
        # This is a placeholder - customize based on your needs
        return f"Processed: {{input_data}}"
    
    async def _arun(self, input_data: str) -> str:
        return self._run(input_data)
'''
        
        return GeneratedTool(
            name=name,
            description=description,
            parameters={
                "input_data": {"type": "str", "description": "Input data to process", "required": True}
            },
            code=code,
            category=ToolCategory.CUSTOM
        )
    
    def _to_class_name(self, snake_case: str) -> str:
        """Convert snake_case to PascalCase."""
        return ''.join(word.capitalize() for word in snake_case.split('_'))
    
    def suggest_tools(self, task_description: str) -> List[ToolDefinition]:
        """
        Suggest relevant tools from the registry based on task description.
        
        Args:
            task_description: Description of what the agent needs to do
            
        Returns:
            List of suggested ToolDefinitions
        """
        suggested = []
        description_lower = task_description.lower()
        
        # Keyword-based suggestions
        keyword_mappings = {
            "search": ["web_search", "wikipedia_search", "arxiv_search"],
            "research": ["web_search", "arxiv_search", "wikipedia_search"],
            "file": ["read_file", "write_file", "list_directory"],
            "read": ["read_file", "csv_analyzer"],
            "write": ["write_file"],
            "data": ["csv_analyzer", "json_processor"],
            "csv": ["csv_analyzer"],
            "json": ["json_processor"],
            "calculate": ["calculator"],
            "math": ["calculator"],
            "code": ["python_executor", "shell_command"],
            "execute": ["python_executor", "shell_command"],
            "api": ["http_request"],
            "http": ["http_request"],
            "database": ["sql_query"],
            "sql": ["sql_query"],
            "email": ["send_email"],
            "text": ["text_summarizer", "regex_extractor"],
            "summarize": ["text_summarizer"],
            "extract": ["regex_extractor"],
        }
        
        suggested_names = set()
        for keyword, tool_names in keyword_mappings.items():
            if keyword in description_lower:
                suggested_names.update(tool_names)
        
        for name in suggested_names:
            tool = self.registry.get(name)
            if tool:
                suggested.append(tool)
        
        return suggested


def generate_tool_from_description(description: str, model_inference=None) -> GeneratedTool:
    """
    Convenience function to generate a tool from description.
    
    Args:
        description: Natural language description of desired tool
        model_inference: Optional ModelInference for LLM-based generation
        
    Returns:
        GeneratedTool instance
    """
    generator = ToolGenerator(model_inference)
    return generator.generate_from_description(description)
