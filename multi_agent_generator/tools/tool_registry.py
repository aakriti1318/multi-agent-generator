# multi_agent_generator/tools/tool_registry.py
"""
Tool Registry - Pre-built tools library with categories and easy discovery.
Low-code approach: Users can browse and select tools without writing code.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class ToolCategory(Enum):
    """Categories for organizing tools."""
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


@dataclass
class ToolDefinition:
    """Definition of a tool with all metadata for code generation."""
    name: str
    description: str
    category: ToolCategory
    parameters: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    returns: str = "str"
    requires_api_key: bool = False
    api_key_env_var: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    code_template: str = ""
    example_usage: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "parameters": self.parameters,
            "returns": self.returns,
            "requires_api_key": self.requires_api_key,
            "api_key_env_var": self.api_key_env_var,
            "dependencies": self.dependencies,
            "example_usage": self.example_usage,
        }


class ToolRegistry:
    """
    Registry of pre-built tools organized by category.
    Provides easy discovery and selection for no-code users.
    """
    
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._load_builtin_tools()
    
    def _load_builtin_tools(self):
        """Load all pre-built tools into the registry."""
        
        # ==================== WEB SEARCH TOOLS ====================
        self.register(ToolDefinition(
            name="web_search",
            description="Search the web for information using a search query. Returns relevant search results.",
            category=ToolCategory.WEB_SEARCH,
            parameters={
                "query": {"type": "str", "description": "The search query", "required": True},
                "num_results": {"type": "int", "description": "Number of results to return", "required": False, "default": 5}
            },
            returns="List[Dict[str, str]]",
            requires_api_key=True,
            api_key_env_var="SERPER_API_KEY",
            dependencies=["requests"],
            code_template='''
class WebSearchTool(BaseTool):
    name = "web_search"
    description = "Search the web for information using a search query"
    
    def _run(self, query: str, num_results: int = 5) -> str:
        import requests
        import os
        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            return "Error: SERPER_API_KEY not set"
        
        response = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": api_key},
            json={"q": query, "num": num_results}
        )
        results = response.json().get("organic", [])
        return "\\n".join([f"- {r['title']}: {r['snippet']}" for r in results[:num_results]])
''',
            example_usage='web_search("latest AI news", num_results=3)'
        ))
        
        self.register(ToolDefinition(
            name="wikipedia_search",
            description="Search Wikipedia for information on a topic. Great for factual knowledge.",
            category=ToolCategory.WEB_SEARCH,
            parameters={
                "query": {"type": "str", "description": "Topic to search for", "required": True}
            },
            returns="str",
            dependencies=["wikipedia"],
            code_template='''
class WikipediaSearchTool(BaseTool):
    name = "wikipedia_search"
    description = "Search Wikipedia for information on a topic"
    
    def _run(self, query: str) -> str:
        try:
            import wikipedia
            return wikipedia.summary(query, sentences=3)
        except Exception as e:
            return f"Error searching Wikipedia: {str(e)}"
''',
            example_usage='wikipedia_search("Machine Learning")'
        ))
        
        self.register(ToolDefinition(
            name="arxiv_search",
            description="Search arXiv for academic papers and research. Returns paper titles, authors, and summaries.",
            category=ToolCategory.WEB_SEARCH,
            parameters={
                "query": {"type": "str", "description": "Research topic to search", "required": True},
                "max_results": {"type": "int", "description": "Maximum papers to return", "required": False, "default": 5}
            },
            returns="List[Dict]",
            dependencies=["arxiv"],
            code_template='''
class ArxivSearchTool(BaseTool):
    name = "arxiv_search"
    description = "Search arXiv for academic papers and research"
    
    def _run(self, query: str, max_results: int = 5) -> str:
        import arxiv
        search = arxiv.Search(query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance)
        results = []
        for paper in search.results():
            results.append(f"Title: {paper.title}\\nAuthors: {', '.join([a.name for a in paper.authors])}\\nSummary: {paper.summary[:200]}...")
        return "\\n\\n".join(results) if results else "No papers found"
''',
            example_usage='arxiv_search("transformer attention mechanism", max_results=3)'
        ))

        # ==================== FILE OPERATIONS TOOLS ====================
        self.register(ToolDefinition(
            name="read_file",
            description="Read content from a file. Supports text files, JSON, CSV, etc.",
            category=ToolCategory.FILE_OPERATIONS,
            parameters={
                "file_path": {"type": "str", "description": "Path to the file", "required": True},
                "encoding": {"type": "str", "description": "File encoding", "required": False, "default": "utf-8"}
            },
            returns="str",
            code_template='''
class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Read content from a file"
    
    def _run(self, file_path: str, encoding: str = "utf-8") -> str:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
''',
            example_usage='read_file("data.txt")'
        ))
        
        self.register(ToolDefinition(
            name="write_file",
            description="Write content to a file. Creates the file if it doesn't exist.",
            category=ToolCategory.FILE_OPERATIONS,
            parameters={
                "file_path": {"type": "str", "description": "Path to the file", "required": True},
                "content": {"type": "str", "description": "Content to write", "required": True},
                "mode": {"type": "str", "description": "Write mode ('w' or 'a')", "required": False, "default": "w"}
            },
            returns="str",
            code_template='''
class WriteFileTool(BaseTool):
    name = "write_file"
    description = "Write content to a file"
    
    def _run(self, file_path: str, content: str, mode: str = "w") -> str:
        try:
            with open(file_path, mode, encoding="utf-8") as f:
                f.write(content)
            return f"Successfully wrote to {file_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"
''',
            example_usage='write_file("output.txt", "Hello World")'
        ))
        
        self.register(ToolDefinition(
            name="list_directory",
            description="List all files and folders in a directory.",
            category=ToolCategory.FILE_OPERATIONS,
            parameters={
                "path": {"type": "str", "description": "Directory path", "required": True},
                "pattern": {"type": "str", "description": "Filter pattern (e.g., '*.py')", "required": False, "default": "*"}
            },
            returns="List[str]",
            code_template='''
class ListDirectoryTool(BaseTool):
    name = "list_directory"
    description = "List all files and folders in a directory"
    
    def _run(self, path: str, pattern: str = "*") -> str:
        import glob
        import os
        try:
            files = glob.glob(os.path.join(path, pattern))
            return "\\n".join(files) if files else "No files found"
        except Exception as e:
            return f"Error listing directory: {str(e)}"
''',
            example_usage='list_directory("./data", pattern="*.csv")'
        ))

        # ==================== DATA PROCESSING TOOLS ====================
        self.register(ToolDefinition(
            name="csv_analyzer",
            description="Analyze a CSV file - get statistics, column info, and sample data.",
            category=ToolCategory.DATA_PROCESSING,
            parameters={
                "file_path": {"type": "str", "description": "Path to CSV file", "required": True},
                "operation": {"type": "str", "description": "Operation: 'describe', 'head', 'columns', 'shape'", "required": False, "default": "describe"}
            },
            returns="str",
            dependencies=["pandas"],
            code_template='''
class CSVAnalyzerTool(BaseTool):
    name = "csv_analyzer"
    description = "Analyze a CSV file - get statistics, column info, and sample data"
    
    def _run(self, file_path: str, operation: str = "describe") -> str:
        import pandas as pd
        try:
            df = pd.read_csv(file_path)
            if operation == "describe":
                return df.describe().to_string()
            elif operation == "head":
                return df.head().to_string()
            elif operation == "columns":
                return f"Columns: {list(df.columns)}"
            elif operation == "shape":
                return f"Rows: {df.shape[0]}, Columns: {df.shape[1]}"
            else:
                return df.describe().to_string()
        except Exception as e:
            return f"Error analyzing CSV: {str(e)}"
''',
            example_usage='csv_analyzer("data.csv", operation="describe")'
        ))
        
        self.register(ToolDefinition(
            name="json_processor",
            description="Process and query JSON data using JSONPath expressions.",
            category=ToolCategory.DATA_PROCESSING,
            parameters={
                "json_data": {"type": "str", "description": "JSON string or file path", "required": True},
                "query": {"type": "str", "description": "JSONPath query (e.g., '$.store.book[*].author')", "required": False, "default": "$"}
            },
            returns="str",
            dependencies=["jsonpath-ng"],
            code_template='''
class JSONProcessorTool(BaseTool):
    name = "json_processor"
    description = "Process and query JSON data using JSONPath expressions"
    
    def _run(self, json_data: str, query: str = "$") -> str:
        import json
        from jsonpath_ng import parse
        try:
            # Try to load as file first, then as string
            try:
                with open(json_data, 'r') as f:
                    data = json.load(f)
            except:
                data = json.loads(json_data)
            
            jsonpath_expr = parse(query)
            matches = [match.value for match in jsonpath_expr.find(data)]
            return json.dumps(matches, indent=2)
        except Exception as e:
            return f"Error processing JSON: {str(e)}"
''',
            example_usage='json_processor(\'{"users": [{"name": "John"}]}\', "$.users[*].name")'
        ))

        # ==================== CODE EXECUTION TOOLS ====================
        self.register(ToolDefinition(
            name="python_executor",
            description="Execute Python code safely in an isolated environment. Returns the output.",
            category=ToolCategory.CODE_EXECUTION,
            parameters={
                "code": {"type": "str", "description": "Python code to execute", "required": True},
                "timeout": {"type": "int", "description": "Execution timeout in seconds", "required": False, "default": 30}
            },
            returns="str",
            code_template='''
class PythonExecutorTool(BaseTool):
    name = "python_executor"
    description = "Execute Python code safely and return the output"
    
    def _run(self, code: str, timeout: int = 30) -> str:
        import subprocess
        import tempfile
        import os
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_path = f.name
            
            result = subprocess.run(
                ['python', temp_path],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            os.unlink(temp_path)
            
            if result.returncode == 0:
                return result.stdout or "Code executed successfully (no output)"
            else:
                return f"Error: {result.stderr}"
        except subprocess.TimeoutExpired:
            return f"Execution timed out after {timeout} seconds"
        except Exception as e:
            return f"Error executing code: {str(e)}"
''',
            example_usage='python_executor("print(2 + 2)")'
        ))
        
        self.register(ToolDefinition(
            name="shell_command",
            description="Execute shell commands. Use with caution.",
            category=ToolCategory.CODE_EXECUTION,
            parameters={
                "command": {"type": "str", "description": "Shell command to execute", "required": True}
            },
            returns="str",
            code_template='''
class ShellCommandTool(BaseTool):
    name = "shell_command"
    description = "Execute shell commands"
    
    def _run(self, command: str) -> str:
        import subprocess
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            output = result.stdout + result.stderr
            return output if output else "Command executed successfully"
        except Exception as e:
            return f"Error executing command: {str(e)}"
''',
            example_usage='shell_command("ls -la")'
        ))

        # ==================== API INTEGRATION TOOLS ====================
        self.register(ToolDefinition(
            name="http_request",
            description="Make HTTP requests (GET, POST, PUT, DELETE) to any API endpoint.",
            category=ToolCategory.API_INTEGRATION,
            parameters={
                "url": {"type": "str", "description": "API endpoint URL", "required": True},
                "method": {"type": "str", "description": "HTTP method", "required": False, "default": "GET"},
                "headers": {"type": "dict", "description": "Request headers", "required": False, "default": {}},
                "data": {"type": "dict", "description": "Request body for POST/PUT", "required": False, "default": {}}
            },
            returns="str",
            dependencies=["requests"],
            code_template='''
class HTTPRequestTool(BaseTool):
    name = "http_request"
    description = "Make HTTP requests to any API endpoint"
    
    def _run(self, url: str, method: str = "GET", headers: dict = None, data: dict = None) -> str:
        import requests
        import json
        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=headers or {},
                json=data if data else None,
                timeout=30
            )
            return f"Status: {response.status_code}\\nResponse: {response.text[:1000]}"
        except Exception as e:
            return f"Error making request: {str(e)}"
''',
            example_usage='http_request("https://api.github.com/users/octocat")'
        ))

        # ==================== DATABASE TOOLS ====================
        self.register(ToolDefinition(
            name="sql_query",
            description="Execute SQL queries on SQLite databases.",
            category=ToolCategory.DATABASE,
            parameters={
                "database_path": {"type": "str", "description": "Path to SQLite database", "required": True},
                "query": {"type": "str", "description": "SQL query to execute", "required": True}
            },
            returns="str",
            code_template='''
class SQLQueryTool(BaseTool):
    name = "sql_query"
    description = "Execute SQL queries on SQLite databases"
    
    def _run(self, database_path: str, query: str) -> str:
        import sqlite3
        try:
            conn = sqlite3.connect(database_path)
            cursor = conn.cursor()
            cursor.execute(query)
            
            if query.strip().upper().startswith("SELECT"):
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                conn.close()
                return f"Columns: {columns}\\nResults: {results}"
            else:
                conn.commit()
                conn.close()
                return f"Query executed successfully. Rows affected: {cursor.rowcount}"
        except Exception as e:
            return f"SQL Error: {str(e)}"
''',
            example_usage='sql_query("database.db", "SELECT * FROM users LIMIT 5")'
        ))

        # ==================== COMMUNICATION TOOLS ====================
        self.register(ToolDefinition(
            name="send_email",
            description="Send emails using SMTP. Requires email credentials.",
            category=ToolCategory.COMMUNICATION,
            parameters={
                "to": {"type": "str", "description": "Recipient email address", "required": True},
                "subject": {"type": "str", "description": "Email subject", "required": True},
                "body": {"type": "str", "description": "Email body content", "required": True}
            },
            returns="str",
            requires_api_key=True,
            api_key_env_var="EMAIL_PASSWORD",
            code_template='''
class SendEmailTool(BaseTool):
    name = "send_email"
    description = "Send emails using SMTP"
    
    def _run(self, to: str, subject: str, body: str) -> str:
        import smtplib
        import os
        from email.mime.text import MIMEText
        
        email_user = os.getenv("EMAIL_USER")
        email_password = os.getenv("EMAIL_PASSWORD")
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        
        if not email_user or not email_password:
            return "Error: EMAIL_USER and EMAIL_PASSWORD environment variables required"
        
        try:
            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = email_user
            msg["To"] = to
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(email_user, email_password)
                server.send_message(msg)
            return f"Email sent successfully to {to}"
        except Exception as e:
            return f"Error sending email: {str(e)}"
''',
            example_usage='send_email("user@example.com", "Hello", "This is the email body")'
        ))

        # ==================== MATH & CALCULATION TOOLS ====================
        self.register(ToolDefinition(
            name="calculator",
            description="Perform mathematical calculations. Supports basic and advanced math operations.",
            category=ToolCategory.MATH_CALCULATION,
            parameters={
                "expression": {"type": "str", "description": "Mathematical expression to evaluate", "required": True}
            },
            returns="str",
            code_template='''
class CalculatorTool(BaseTool):
    name = "calculator"
    description = "Perform mathematical calculations"
    
    def _run(self, expression: str) -> str:
        import math
        try:
            # Safe evaluation with math functions
            allowed_names = {
                k: v for k, v in math.__dict__.items() if not k.startswith("_")
            }
            allowed_names.update({"abs": abs, "round": round, "min": min, "max": max})
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return str(result)
        except Exception as e:
            return f"Calculation error: {str(e)}"
''',
            example_usage='calculator("sqrt(16) + pow(2, 3)")'
        ))

        # ==================== TEXT PROCESSING TOOLS ====================
        self.register(ToolDefinition(
            name="text_summarizer",
            description="Summarize long text into key points. Uses extractive summarization.",
            category=ToolCategory.TEXT_PROCESSING,
            parameters={
                "text": {"type": "str", "description": "Text to summarize", "required": True},
                "num_sentences": {"type": "int", "description": "Number of sentences in summary", "required": False, "default": 3}
            },
            returns="str",
            code_template='''
class TextSummarizerTool(BaseTool):
    name = "text_summarizer"
    description = "Summarize long text into key points"
    
    def _run(self, text: str, num_sentences: int = 3) -> str:
        # Simple extractive summarization based on sentence importance
        import re
        from collections import Counter
        
        sentences = re.split(r'(?<=[.!?])\\s+', text)
        if len(sentences) <= num_sentences:
            return text
        
        # Score sentences by word frequency
        words = re.findall(r'\\w+', text.lower())
        word_freq = Counter(words)
        
        sentence_scores = []
        for sent in sentences:
            score = sum(word_freq.get(w.lower(), 0) for w in re.findall(r'\\w+', sent))
            sentence_scores.append((score, sent))
        
        # Get top sentences in original order
        top_sentences = sorted(sentence_scores, key=lambda x: x[0], reverse=True)[:num_sentences]
        top_sentences = sorted(top_sentences, key=lambda x: sentences.index(x[1]))
        
        return " ".join([s[1] for s in top_sentences])
''',
            example_usage='text_summarizer("Long article text here...", num_sentences=3)'
        ))
        
        self.register(ToolDefinition(
            name="regex_extractor",
            description="Extract patterns from text using regular expressions.",
            category=ToolCategory.TEXT_PROCESSING,
            parameters={
                "text": {"type": "str", "description": "Text to search in", "required": True},
                "pattern": {"type": "str", "description": "Regex pattern", "required": True}
            },
            returns="List[str]",
            code_template='''
class RegexExtractorTool(BaseTool):
    name = "regex_extractor"
    description = "Extract patterns from text using regular expressions"
    
    def _run(self, text: str, pattern: str) -> str:
        import re
        try:
            matches = re.findall(pattern, text)
            return f"Found {len(matches)} matches: {matches}"
        except Exception as e:
            return f"Regex error: {str(e)}"
''',
            example_usage='regex_extractor("Contact: user@email.com", r"[\\w.-]+@[\\w.-]+")'
        ))

    def register(self, tool: ToolDefinition) -> None:
        """Register a tool in the registry."""
        self._tools[tool.name] = tool
    
    def get(self, name: str) -> Optional[ToolDefinition]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def list_all(self) -> List[ToolDefinition]:
        """List all registered tools."""
        return list(self._tools.values())
    
    def list_by_category(self, category: ToolCategory) -> List[ToolDefinition]:
        """List tools in a specific category."""
        return [t for t in self._tools.values() if t.category == category]
    
    def search(self, query: str) -> List[ToolDefinition]:
        """Search tools by name or description."""
        query = query.lower()
        results = []
        for tool in self._tools.values():
            if query in tool.name.lower() or query in tool.description.lower():
                results.append(tool)
        return results
    
    def get_categories(self) -> List[ToolCategory]:
        """Get all available categories."""
        return list(ToolCategory)
    
    def get_tool_names(self) -> List[str]:
        """Get all tool names."""
        return list(self._tools.keys())
    
    def generate_tool_code(self, tool_names: List[str]) -> str:
        """Generate code for the specified tools."""
        code = "from langchain_core.tools import BaseTool\nfrom typing import Optional, List, Dict, Any\n\n"
        
        for name in tool_names:
            tool = self.get(name)
            if tool and tool.code_template:
                code += tool.code_template + "\n\n"
        
        # Generate tools list
        code += "# Initialize tools\ntools = [\n"
        for name in tool_names:
            tool = self.get(name)
            if tool:
                class_name = ''.join(word.capitalize() for word in name.split('_')) + "Tool"
                code += f"    {class_name}(),\n"
        code += "]\n"
        
        return code


# Singleton instance
_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry
