# Multi-Agent Generator

A powerful tool that transforms plain English instructions into fully configured multi-agent AI teams - no scripting, no complexity. Powered by multiple LLM providers (OpenAI, IBM WatsonX, and Ollama) with an intuitive Streamlit UI.

## Features

- Generate agent code for multiple frameworks:
  - **CrewAI**: Structured workflows for multi-agent collaboration
  - **CrewAI Flow**: Event-driven workflows with state management
  - **LangGraph**: LangChain's framework for stateful, multi-actor applications
  - **ReAct**: Reasoning + Acting framework for adaptive AI agents

- **Multiple LLM Providers**:
  - **OpenAI**: Use GPT models for code generation
  - **IBM WatsonX**: Enterprise-grade access to Llama and other foundation models
  - **Ollama**: Use Ollama models for code generation

- **User-Friendly Interface**: Streamlit-based UI for effortless code generation
- **Intelligent Analysis**: Analyzes natural language requirements to suggest appropriate agents, roles, and tasks
- **Visualizations**: View agent relationships, workflow paths, and execution flow

## Installation

### Basic Installation
```bash
pip install multi-agent-generator
```

### With WatsonX Support
```bash
pip install multi-agent-generator[watsonx]
```

### Development Installation
```bash
pip install multi-agent-generator[dev]
```

## Prerequisites

- OpenAI API key OR WatsonX API key and Project ID OR Ollama API key
- Environment variables setup:
  - `OPENAI_API_KEY`: Your OpenAI API key
  - Or for WatsonX:
    - `WATSONX_API_KEY`: Your WatsonX API key
    - `WATSONX_PROJECT_ID`: Your WatsonX project ID
    - `WATSONX_URL`: WatsonX URL 
  - Or for Ollama:
    - `OLLAMA_API_KEY`: Your Ollama API key

## Usage

### Command Line

Basic usage with OpenAI (default):
```bash
multi-agent-generator "I need a research assistant that summarizes papers and answers questions" --framework crewai
```

Using WatsonX instead:
```bash
multi-agent-generator "I need a research assistant that summarizes papers and answers questions" --framework crewai --provider watsonx
```

Using Ollama instead:
```bash
multi-agent-generator "I need a research assistant that summarizes papers and answers questions" --framework crewai --provider ollama
```

Save output to a file:
```bash
multi-agent-generator "I need a team to create viral social media content" --framework langgraph --output social_team.py
```

Get JSON configuration only:
```bash
multi-agent-generator "I need a team to analyze customer data" --framework react --format json
```

### Streamlit UI

```bash
streamlit run -m multi_agent_generator.streamlit_app.app
```

The UI allows you to:
- Choose between OpenAI, WatsonX, and Ollama
- Select which framework to use
- Enter your requirements in plain English
- Visualize the agent configuration
- Copy or download the generated code

## Examples

### Research Assistant

```
I need a research assistant that summarizes papers and answers questions
```

### Content Creation Team

```
I need a team to create viral social media content and manage our brand presence
```

### Data Analysis

```
I need a team to analyze customer data and create visualizations
```

## Frameworks

### CrewAI

CrewAI is a framework for orchestrating role-playing autonomous AI agents. It allows you to create a crew of agents that work together to accomplish tasks, with each agent having a specific role, goal, and backstory.

### CrewAI Flow

CrewAI Flow extends CrewAI with event-driven workflows. It enables you to define multi-step processes with clear transitions between steps, maintaining state throughout the execution, and allowing for complex orchestration patterns like sequential, parallel, and conditional execution.

### LangGraph

LangGraph is LangChain's framework for building stateful, multi-actor applications with LLMs. It provides a way to create directed graphs where nodes are LLM calls, tools, or other operations, and edges represent the flow of information between them.

### ReAct

ReAct (Reasoning + Acting) is a framework that combines reasoning and action in LLM agents. It prompts the model to generate both reasoning traces and task-specific actions in an interleaved manner, creating a synergy between the two that leads to improved performance.

## LLM Providers

### OpenAI

OpenAI's GPT models provide state-of-the-art natural language understanding and code generation capabilities. The default model used is GPT-4o-mini.

### IBM WatsonX

IBM WatsonX provides enterprise-grade access to foundation models with IBM's security and governance features. The default model used is Llama-3-70B-Instruct.

### Ollama

Ollama's models provide advanced capabilities for natural language understanding and code generation. The default model used is Ollama-Model-ID.

## License

MIT
