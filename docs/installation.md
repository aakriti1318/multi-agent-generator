# Installation

## Basic Installation

```bash
pip install multi-agent-generator
```

## Development Installation

```bash
git clone https://github.com/aakriti1318/multi-agent-generator.git
cd multi-agent-generator
pip install -e ".[dev]"
```

## Prerequisites

- Python 3.8 or higher
- At least one supported LLM provider (OpenAI, WatsonX, Ollama, etc.)

## Environment Variables

Set up environment variables for your chosen LLM provider:

### OpenAI

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

### IBM WatsonX

```bash
export WATSONX_API_KEY="your-watsonx-api-key"
export WATSONX_PROJECT_ID="your-project-id"
export WATSONX_URL="https://us-south.ml.cloud.ibm.com"
```

### Ollama (Local)

```bash
export OLLAMA_URL="http://localhost:11434"
```

### Generic LiteLLM

```bash
export API_KEY="your-api-key"
export API_BASE="https://your-api-endpoint"
```

## Provider Notes

- **Agno** currently only works with `OPENAI_API_KEY` without tools. Support for additional APIs and tools will be expanded in future releases.

You can freely switch providers using `--provider` in CLI or by setting environment variables.

## Verifying Installation

After installation, verify everything works:

```bash
# Check CLI is available
multi-agent-generator --help

# Test a simple generation
multi-agent-generator "Create a simple assistant" --framework crewai
```

## Optional: Streamlit UI

The Streamlit UI is included by default. Launch it with:

```bash
streamlit run streamlit_app.py
```
