# Agno Framework

Agno coordinates and orchestrates **role-playing autonomous AI agents**.
Each agent has:

- **Name and Role**: what they do
- **Goal**: their objective
- **Backstory**: context
- **Tools**: available abilities


Tasks are assigned to agents with expected outputs.

## Example

```bash
multi-agent-generator "Research AI trends and write a summary" --framework agno
```

### Produces agents like:
```json
{
  "model_id": "gpt-4o",
  "process": "sequential",
  "agents": [
    {
      "name": "research_specialist",
      "role": "Research Specialist",
      "goal": "Gather AI research trends",
      "backstory": "Expert in sourcing and aggregating technology news",
      "tools": ["DuckDuckGoTools", "Newspaper4kTools"]
    },
    {
      "name": "writer",
      "role": "Content Writer",
      "goal": "Write a clear summary",
      "backstory": "Skilled at concise technical writing",
      "tools": []
    }
  ],
  "tasks": [
    {
      "name": "research_task",
      "description": "Find recent AI trends across news and blogs",
      "agent": "research_specialist",
      "expected_output": "Bullet list of trends with links"
    },
    {
      "name": "writing_task",
      "description": "Summarize the trends for a general audience",
      "agent": "writer",
      "expected_output": "400-word Markdown summary"
    }
  ]
}
```