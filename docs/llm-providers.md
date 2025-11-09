# 🧠 LLM Providers

Multi-Agent Generator is **provider-agnostic**, thanks to [LiteLLM](https://docs.litellm.ai/).
You can seamlessly switch between **OpenAI**, **WatsonX**, **Ollama**, **Groq**, **Anthropic**, and **AIML API** — using a single CLI flag or environment variable.

---

## 🌍 Supported Providers

| **Provider**    | **Default Model**             | **Best For**              | **Key Strengths**                                  |
| --------------- | ----------------------------- | ------------------------- | -------------------------------------------------- |
| **OpenAI**      | `gpt-4o-mini`                 | General-purpose reasoning | Best reasoning, reliability, context length        |
| **IBM WatsonX** | `llama-3-70b-instruct`        | Enterprise use            | Compliance, data governance, IBM Cloud integration |
| **Groq**        | `llama-3-8b`                  | Real-time pipelines       | Lightning-fast inference, low latency              |
| **Ollama**      | `llama3`, `mistral`           | Local development         | Privacy-friendly, runs fully offline               |
| **AIML API**    | `custom-finetuned`, `llama-2` | Flexible deployments      | Open, customizable, on-prem/cloud/hybrid           |
| **Anthropic**   | `claude-3-opus`               | Natural reasoning         | Long-context understanding, alignment focus        |

---

## ⚙️ Environment Setup

Set up your API credentials in your environment variables.
Depending on your provider, you can configure one or more of the following:

### 🔹 OpenAI

```bash
export OPENAI_API_KEY="your_openai_api_key"
```

### 🔹 IBM WatsonX

```bash
export WATSONX_API_KEY="your_watsonx_api_key"
export WATSONX_PROJECT_ID="your_project_id"
export WATSONX_URL="your_instance_url"
```

### 🔹 Ollama (local)

```bash
export OLLAMA_URL="http://localhost:11434"
```

### 🔹 Groq

```bash
export GROQ_API_KEY="your_groq_api_key"
```

### 🔹 AIML API

```bash
export AIML_API_KEY="your_aiml_api_key"
export AIML_BASE_URL="https://api.aimlapi.com/v1"
```

### 🔹 Anthropic

```bash
export ANTHROPIC_API_KEY="your_anthropic_api_key"
```

---

## ⚡ CLI Usage

You can switch providers instantly from the command line.

### OpenAI (default)

```bash
multi-agent-generator "Create a summarizer and QA assistant" --framework crewai
```

### WatsonX

```bash
multi-agent-generator "Build a document classifier" --framework langgraph --provider watsonx
```

### Groq

```bash
multi-agent-generator "Generate a real-time customer feedback analyzer" --framework crewai --provider groq
```

### Ollama (local)

```bash
multi-agent-generator "Build a ReAct chatbot for support" --framework react-lcel --provider ollama
```

### AIML API

```bash
multi-agent-generator "Create a custom marketing team workflow" --framework agno --provider aimlapi
```

### Anthropic

```bash
multi-agent-generator "Develop a debate-style reasoning agent" --framework react --provider anthropic
```

---

## 🔄 Switching Providers in Code

You can also use the provider argument programmatically if you integrate this library:

```python
from multi_agent_generator import generate_agents

agents = generate_agents(
    prompt="I need a content creation team",
    framework="crewai",
    provider="groq"   # or openai, watsonx, ollama, aimlapi, anthropic
)
```

---

## 🧩 Comparison Summary

| **Feature**               | **OpenAI** | **WatsonX**         | **Groq**      | **Ollama** | **AIML API**             | **Anthropic** |
| ------------------------- | ---------- | ------------------- | ------------- | ---------- | ------------------------ | ------------- |
| **Speed**                 | ⚡⚡         | ⚡                   | ⚡⚡⚡           | ⚡          | ⚡⚡                       | ⚡             |
| **Offline Support**       | ❌          | ❌                   | ⚙️ Limited    | ✅          | ✅                        | ❌             |
| **Latency**               | Medium     | Medium              | 🔥 Ultra-low  | Low        | Medium                   | Medium        |
| **Deployment**            | Cloud      | IBM Cloud           | Edge / Cloud  | Local      | Cloud / On-prem / Hybrid | Cloud         |
| **Customization**         | Low        | Medium              | Medium        | High       | 🔥 Very High             | Low           |
| **Security / Compliance** | High       | 🔥 Enterprise-grade | Medium        | Local      | High                     | High          |
| **Ease of Integration**   | ✅ SDKs     | ✅ Enterprise APIs   | ✅ Simple REST | ✅ Simple   | ✅ REST/GraphQL           | ✅ SDKs        |

---

## 💡 Notes

* All providers are managed under **LiteLLM**, so configuration and switching remain consistent.
* You can override base URLs using `LITELLM_API_BASE` or provider-specific variables.
* Some frameworks (like **Agno**) currently support only OpenAI-compatible APIs — support for more is coming soon.

---

## ❤️ Contribute

If you’ve tested or configured new models (like **Gemini**, **Cohere**, or **Mistral API**) with Multi-Agent Generator, feel free to open a PR to add them here.

