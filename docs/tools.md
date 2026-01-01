# Tool Auto-Discovery & Generation

The Tools module provides a registry of pre-built tools and the ability to generate custom tools from natural language descriptions.

## Overview

- **15+ pre-built tools** across 10 categories
- **Natural language tool generation** - describe what you need, get working code
- **Framework-agnostic** - tools work with CrewAI, LangGraph, and other frameworks
- **CLI support** - generate and list tools from the command line

---

## CLI Usage

### Generate a Tool

Create tools from natural language descriptions:

```bash
multi-agent-generator --tool "Create a tool to fetch stock prices from an API"
```

**Output:**
```python
# Auto-generated tool: fetch_stock_prices
# Category: api_integration
# Description: Fetches stock prices from an API

import os
import requests
from typing import Dict, Any

def fetch_stock_prices(symbol: str) -> Dict[str, Any]:
    """Fetch stock prices for a given symbol."""
    api_key = os.getenv("STOCK_API_KEY")
    url = f"https://api.stockdata.com/v1/quote?symbol={symbol}&apikey={api_key}"
    response = requests.get(url)
    return response.json()

# Tool metadata
TOOL_INFO = {
    "name": "fetch_stock_prices",
    "description": "Fetches stock prices from an API",
    "category": "api_integration",
    "parameters": {"symbol": {"type": "string", "description": "Stock symbol"}}
}
```

### Save to File

```bash
multi-agent-generator --tool "Create a CSV parser tool" --output csv_parser.py
```

### List All Tools

```bash
multi-agent-generator --list-tools
```

**Output:**
```
📦 All Available Tools:

  [API_INTEGRATION]
    • http_request: Make HTTP requests (GET, POST, PUT, DELETE) to any API endpoint.

  [CODE_EXECUTION]
    • python_executor: Execute Python code safely in an isolated environment.
    • shell_command: Execute shell commands. Use with caution.

  [COMMUNICATION]
    • send_email: Send emails using SMTP. Requires email credentials.

  [DATA_PROCESSING]
    • csv_analyzer: Analyze a CSV file - get statistics, column info, and sample data.
    • json_processor: Process and query JSON data using JSONPath expressions.

  [DATABASE]
    • sql_query: Execute SQL queries on SQLite databases.

  [FILE_OPERATIONS]
    • read_file: Read content from a file. Supports text files, JSON, CSV, etc.
    • write_file: Write content to a file. Creates the file if it doesn't exist.
    • list_directory: List all files and folders in a directory.

  [MATH_CALCULATION]
    • calculator: Perform mathematical calculations.

  [TEXT_PROCESSING]
    • text_summarizer: Summarize long text into key points.
    • regex_extractor: Extract patterns from text using regular expressions.

  [WEB_SEARCH]
    • web_search: Search the web for information using a search query.
    • wikipedia_search: Search Wikipedia for information on a topic.
    • arxiv_search: Search arXiv for academic papers and research.
```

### Filter by Category

```bash
multi-agent-generator --list-tools --tool-category web_search
```

**Output:**
```
📦 Tools in category 'web_search':

  • google_search: Search the web using Google
    Parameters: ['query', 'num_results']
  • web_scraper: Scrape content from web pages
    Parameters: ['url', 'selector']
```

### Available Categories

- `web_search` - Web search and scraping tools
- `file_operations` - File system operations
- `data_processing` - Data parsing and transformation
- `code_execution` - Code runners and executors
- `api_integration` - REST clients and webhooks
- `database` - Database query tools
- `communication` - Email, Slack, notifications
- `math_calculation` - Calculators and statistics
- `text_processing` - Text manipulation tools
- `image_processing` - Image operations
- `custom` - User-defined tools

---

## Tool Registry

### Browsing Tools

```python
from multi_agent_generator.tools import ToolRegistry, ToolCategory

registry = ToolRegistry()

# List all categories
categories = [cat for cat in ToolCategory]
print(categories)
# [ToolCategory.WEB_SEARCH, ToolCategory.FILE_OPERATIONS, ...]

# Get tools by category
web_tools = registry.list_by_category(ToolCategory.WEB_SEARCH)
for tool in web_tools:
    print(f"{tool.name}: {tool.description}")

# List all available tools
all_tools = registry.list_all()
```

### Pre-built Tool Categories

| Category | Tools | Description |
|----------|-------|-------------|
| **Web Search** | google_search, web_scraper | Search the web and scrape content |
| **File Operations** | read_file, write_file, list_directory | File system operations |
| **Data Processing** | csv_parser, json_transformer | Parse and transform data |
| **Code Execution** | python_executor, shell_runner | Execute code snippets |
| **API Integration** | rest_client, webhook_handler | HTTP requests and webhooks |
| **Database** | sql_query, document_store | Database operations |
| **Communication** | email_sender, slack_notifier | Send notifications |
| **Math** | calculator, statistics | Mathematical operations |
| **Text Processing** | summarizer, translator | Text manipulation |
| **Image Processing** | image_resizer, format_converter | Image operations |

### Getting Tool Details

```python
from multi_agent_generator.tools import ToolRegistry

registry = ToolRegistry()

# Get a specific tool
tool = registry.get_tool("google_search")
print(tool.name)
print(tool.description)
print(tool.parameters)
print(tool.code)
```

---

## Tool Generator

### Generating Custom Tools

Create tools from natural language descriptions:

```python
from multi_agent_generator.tools import ToolGenerator

generator = ToolGenerator()

# Generate a tool from description
tool = generator.generate_tool(
    "Create a tool that fetches weather data for a given city using an API"
)

print(tool.name)        # fetch_weather_data
print(tool.description) # Fetches weather data for a given city...
print(tool.code)        # Ready-to-use Python code
```

### Generated Tool Structure

```python
# Example generated tool code
def fetch_weather_data(city: str) -> dict:
    """
    Fetches weather data for a given city using an API.
    
    Args:
        city: The name of the city to fetch weather for
        
    Returns:
        Dictionary containing weather information
    """
    import requests
    
    api_key = os.getenv("WEATHER_API_KEY")
    url = f"https://api.weatherapi.com/v1/current.json?key={api_key}&q={city}"
    
    response = requests.get(url)
    return response.json()
```

### Template-Based Generation

For common patterns, use template-based generation:

```python
from multi_agent_generator.tools import ToolGenerator

generator = ToolGenerator()

# Generate from template
tool = generator.generate_from_template(
    template="api_client",
    name="github_client",
    base_url="https://api.github.com",
    endpoints=["repos", "issues", "pulls"]
)
```

---

## Using Tools with Agents

### With CrewAI

```python
from crewai import Agent
from multi_agent_generator.tools import ToolRegistry

registry = ToolRegistry()
search_tool = registry.get_tool("google_search")

agent = Agent(
    role="Researcher",
    goal="Find information on topics",
    tools=[search_tool.to_crewai_tool()]
)
```

### With LangGraph

```python
from multi_agent_generator.tools import ToolRegistry

registry = ToolRegistry()
tools = registry.get_tools_by_category("web_search")

# Convert to LangChain tools
langchain_tools = [tool.to_langchain_tool() for tool in tools]
```

---

## API Reference

### ToolRegistry

| Method | Description |
|--------|-------------|
| `get_categories()` | List all tool categories |
| `get_tools_by_category(category)` | Get tools in a category |
| `get_tool(name)` | Get a specific tool by name |
| `list_all_tools()` | List all available tools |
| `search_tools(query)` | Search tools by keyword |

### ToolGenerator

| Method | Description |
|--------|-------------|
| `generate_tool(description)` | Generate tool from natural language |
| `generate_from_template(template, **kwargs)` | Generate from predefined template |
| `validate_tool(tool)` | Validate generated tool code |

### ToolDefinition

| Property | Type | Description |
|----------|------|-------------|
| `name` | str | Tool name |
| `description` | str | Tool description |
| `category` | ToolCategory | Tool category |
| `parameters` | dict | Input parameters schema |
| `returns` | str | Return type description |
| `code` | str | Python implementation |
