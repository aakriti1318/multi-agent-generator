# Multi-Agent Generator
<img width="807" height="264" alt="Screenshot 2025-08-18 at 12 59 52 PM" src="https://github.com/user-attachments/assets/90665135-80a3-43e2-82cc-ae7fa1dcc6a3" />

**PyPi Link** - [Multi-agent-generator](https://pypi.org/project/multi-agent-generator/)

A powerful tool that transforms plain English instructions into fully configured multi-agent AI teams — no scripting, no complexity.
Powered by [LiteLLM](https://docs.litellm.ai/) for **provider-agnostic support** (OpenAI, WatsonX, Ollama, Anthropic, etc.) with both a **CLI** and an optional **Streamlit UI**.

---

## Features

* Generate agent code for multiple frameworks:

  * **CrewAI**: Structured workflows for multi-agent collaboration
  * **CrewAI Flow**: Event-driven workflows with state management
  * **LangGraph**: LangChain’s framework for stateful, multi-actor applications
  * **Agno**: Agno framework for Agents Team orchestration
  * **ReAct (classic)**: Reasoning + Acting agents using `AgentExecutor`
  * **ReAct (LCEL)**: Future-proof ReAct built with LangChain Expression Language (LCEL)

* **Provider-Agnostic Inference** via LiteLLM:

  * Supports OpenAI, IBM WatsonX, Ollama, Anthropic, and more
  * Swap providers with a single CLI flag or environment variable

* **Flexible Output**:

  * Generate Python code
  * Generate JSON configs
  * Or both combined

* **Streamlit UI** (optional):

  * Interactive prompt entry
  * Framework selection
  * Config visualization
  * Copy or download generated code

---

## Installation

### Basic Installation

```bash
pip install multi-agent-generator
```

---

## Prerequisites

* At least one supported LLM provider (OpenAI, WatsonX, Ollama, etc.)
* Environment variables setup:

  * `OPENAI_API_KEY` (for OpenAI)
  * `WATSONX_API_KEY`, `WATSONX_PROJECT_ID`, `WATSONX_URL` (for WatsonX)
  * `OLLAMA_URL` (for Ollama)
  * `GROQ_API_KEY` (for Groq)
  * Or a generic `API_KEY` / `API_BASE` if supported by LiteLLM

* Be aware `Agno` only works with `OPENAI_API_KEY` without tools for Now, and will be expanded for further API's and tools in the future.

> ⚡ You can freely switch providers using `--provider` in CLI or by setting environment variables.

---

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
Using Agno:

```bash
multi_agent_generator "build a researcher and writer" --framework agno --provider openai --output agno.py --format code
```
Using Ollama locally:

```bash
multi-agent-generator "Build me a ReAct assistant for customer support" --framework react-lcel --provider ollama
```

Using Grqo

```bash
multi-agent-generator "I need a team to analyze customer data" --framework langgraph --provider groq
```

Save output to a file:

```bash
multi-agent-generator "I need a team to create viral social media content" --framework langgraph --output social_team.py
```

Get JSON configuration only:

```bash
multi-agent-generator "I need a team to analyze customer data" --framework react --format json
```

---

## Examples

### Research Assistant

```
I need a research assistant that summarizes papers and answers questions
```

### Content Creation Team

```
I need a team to create viral social media content and manage our brand presence
```

### Customer Support (LangGraph)

```
Build me a LangGraph workflow for customer support
```

---

## Frameworks

### CrewAI

Role-playing autonomous AI agents with goals, roles, and backstories.

### CrewAI Flow

Event-driven workflows with sequential, parallel, or conditional execution.

### LangGraph

Directed graph of agents/tools with stateful execution.

### Agno

Role-playing Team orchestration AI agents with goals, roles, backstories and instructions.

### ReAct (classic)

Reasoning + Acting agents built with `AgentExecutor`.

### ReAct (LCEL)

Modern ReAct implementation using LangChain Expression Language — better for debugging and future-proof orchestration.

---

## LLM Providers

### OpenAI

State-of-the-art GPT models (default: `gpt-4o-mini`).

### IBM WatsonX

Enterprise-grade access to Llama and other foundation models (default: `llama-3-70b-instruct`).

### Ollama

Run Llama and other models locally.

### Anthropic

Use Claude models for agent generation.

### Groq
High-performance models optimized for speed and cost.
(default: `llama-3.3-70b-versatile-instruct`)

…and more, via LiteLLM.

---

## License

MIT

Made with ❤️ If you like star the repo and share it with AI Enthusiasts.
