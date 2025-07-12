# Shippopotamus MCP Server

Professional prompt management for AI applications.

## Installation

Add to your Claude Desktop or MCP-compatible application:

```json
{
  "mcpServers": {
    "shippopotamus": {
      "command": "npx",
      "args": ["shippopotamus"]
    }
  }
}
```

## Features

- 🎯 **Curated Prompt Library** - Battle-tested methodologies
- 💾 **Custom Prompt Registry** - Save your team's prompts
- 🔗 **File References** - Link to existing docs
- 🧩 **Smart Composition** - Combine prompts intelligently
- 📊 **Context Budgeting** - Manage token usage

## Quick Start

```python
# Load a methodology
prompt = get_prompt("ask_plan_act")

# Save your standards
save_prompt("our_style", content="...")

# Compose prompts
composed = compose_prompts(["ask_plan_act", "our_style"])
```

## Documentation

Full documentation at: https://github.com/shippopotamus/shippopotamus

## License

MIT