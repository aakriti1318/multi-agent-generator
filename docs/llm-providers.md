# LLM Providers

Multi-Agent Generator supports multiple LLM providers through LiteLLM, making it easy to switch between providers.

---

## Supported Providers

| Provider | Models | Default Model |
|----------|--------|---------------|
| **OpenAI** | GPT-4, GPT-4o, GPT-3.5 | gpt-4o-mini |
| **IBM WatsonX** | Llama 3, Granite | llama-3-70b-instruct |
| **Ollama** | Llama, Mistral, CodeLlama | llama3 |
| **Anthropic** | Claude 3, Claude 2 | claude-3-sonnet |
| **Azure OpenAI** | GPT-4, GPT-3.5 | gpt-4 |
| **Google** | Gemini Pro, PaLM | gemini-pro |
| **Cohere** | Command, Command-Light | command |

---

## Configuration

### OpenAI

```bash
export OPENAI_API_KEY="sk-..."
```

```bash
multi-agent-generator "Your prompt" --provider openai
```

**Available Models:**
- `gpt-4o` - Latest GPT-4 optimized
- `gpt-4o-mini` - Smaller, faster GPT-4 (default)
- `gpt-4-turbo` - GPT-4 with vision
- `gpt-3.5-turbo` - Fast and cost-effective

---

### IBM WatsonX

```bash
export WATSONX_API_KEY="your-api-key"
export WATSONX_PROJECT_ID="your-project-id"
export WATSONX_URL="https://us-south.ml.cloud.ibm.com"
```

```bash
multi-agent-generator "Your prompt" --provider watsonx
```

**Available Models:**
- `llama-3-70b-instruct` - Llama 3 70B (default)
- `llama-3-8b-instruct` - Llama 3 8B
- `granite-13b-chat-v2` - IBM Granite
- `mixtral-8x7b-instruct` - Mixtral

---

### Ollama (Local)

Run models locally with Ollama:

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama3

# Set environment
export OLLAMA_URL="http://localhost:11434"
```

```bash
multi-agent-generator "Your prompt" --provider ollama
```

**Available Models:**
- `llama3` - Llama 3 (default)
- `llama3:70b` - Llama 3 70B
- `mistral` - Mistral 7B
- `codellama` - Code Llama
- `mixtral` - Mixtral 8x7B

---

### Anthropic

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

```bash
multi-agent-generator "Your prompt" --provider anthropic
```

**Available Models:**
- `claude-3-opus` - Most capable
- `claude-3-sonnet` - Balanced (default)
- `claude-3-haiku` - Fast and efficient

---

### Azure OpenAI

```bash
export AZURE_API_KEY="your-key"
export AZURE_API_BASE="https://your-resource.openai.azure.com"
export AZURE_API_VERSION="2024-02-01"
```

```bash
multi-agent-generator "Your prompt" --provider azure
```

---

### Google (Vertex AI / Gemini)

```bash
export GOOGLE_API_KEY="your-api-key"
# Or for Vertex AI
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
```

```bash
multi-agent-generator "Your prompt" --provider google
```

**Available Models:**
- `gemini-pro` - Gemini Pro (default)
- `gemini-pro-vision` - With vision capabilities

---

## Switching Providers

### CLI

Use the `--provider` flag:

```bash
# OpenAI (default)
multi-agent-generator "prompt" --framework crewai

# WatsonX
multi-agent-generator "prompt" --framework crewai --provider watsonx

# Ollama
multi-agent-generator "prompt" --framework crewai --provider ollama

# Anthropic
multi-agent-generator "prompt" --framework crewai --provider anthropic
```

### Python API

```python
from multi_agent_generator import generate_agents

# OpenAI
result = generate_agents(prompt, framework="crewai", provider="openai")

# WatsonX
result = generate_agents(prompt, framework="crewai", provider="watsonx")

# Ollama
result = generate_agents(prompt, framework="crewai", provider="ollama")
```

### Streamlit UI

Select the provider from the dropdown in the sidebar.

---

## Custom Models

### Specifying a Model

```python
from multi_agent_generator import generate_agents

result = generate_agents(
    prompt="Your prompt",
    framework="crewai",
    provider="openai",
    model="gpt-4-turbo"  # Specify model
)
```

### Using LiteLLM Directly

For advanced use cases, access LiteLLM directly:

```python
import litellm

response = litellm.completion(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello"}]
)
```

---

## Provider Comparison

| Provider | Speed | Cost | Quality | Local |
|----------|-------|------|---------|-------|
| OpenAI GPT-4o | Fast | $$ | Excellent | No |
| WatsonX Llama | Medium | $$ | Very Good | No |
| Ollama | Varies | Free | Good | Yes |
| Anthropic Claude | Fast | $$$ | Excellent | No |
| Google Gemini | Fast | $ | Very Good | No |

---

## Troubleshooting

### API Key Issues

```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Test with a simple call
python -c "import litellm; print(litellm.completion(model='gpt-4o-mini', messages=[{'role':'user','content':'hi'}]))"
```

### Rate Limits

If you hit rate limits, consider:
- Using a different model (e.g., gpt-3.5-turbo)
- Adding delays between requests
- Using a local model with Ollama

### Connection Issues

For Ollama:
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
ollama serve
```

### Provider Not Found

Ensure you have the correct provider name:
- `openai` (not "OpenAI")
- `watsonx` (not "ibm" or "watson")
- `ollama` (not "local")
- `anthropic` (not "claude")
