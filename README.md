# 🚢🦛 **Shippopotamus** (or **Shippo** or **🚢🦛** for short)

**Professional prompt management for AI applications** - Load, save, compose, and optimize prompts with intelligent MCP tools.

---

## What is Shippopotamus?

Shippopotamus is a prompt management platform that helps teams building AI applications:

* **🎯 Curated Prompt Library** – Battle-tested methodologies like Ask→Plan→Act
* **💾 Custom Prompt Registry** – Save and version your team's prompts  
* **🔗 File References** – Link to existing docs without duplication
* **🧩 Intelligent Composition** – Combine prompts with deduplication
* **📊 Context Budgeting** – Estimate tokens before loading

---

## Quick Start

### For AI Application Developers

1. Install the MCP server in your project:
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

2. Use the tools in your AI workflow:
```python
# Load a proven methodology
prompt = get_prompt("ask_plan_act")

# Save your company standards
save_prompt("company_style", content="...", tags=["standards"])

# Compose multiple prompts
composed = compose_prompts(["ask_plan_act", "company_style"])
```

### For Contributors

1. `git clone https://github.com/yourusername/shippopotamus`
2. `pip install -r requirements.txt`
3. `python test_comprehensive.py`

---

## Core Tools

| Tool | Purpose |
|------|---------|
| `get_prompt(name)` | Load prompts from registry or library |
| `save_prompt(...)` | Save custom prompts with metadata |
| `load_prompts([...])` | Batch load from multiple sources |
| `compose_prompts(...)` | Intelligently combine prompts |
| `list_available()` | Discover all available prompts |
| `estimate_context(...)` | Plan token usage |

---

## Prompt Library

### Methodologies
- **ask_plan_act** (🧭) - Core Ask→Plan→Act methodology
- **quality_axioms** (⚖️) - Quality and best practices
- **patterns** (🪢) - Meta-patterns for prompt design

### Patterns
- **safe_coding** (🛡️) - Security practices
- **context_economy** (💰) - Token optimization  
- **echo_emoji** (📣) - Visual contracts

---

## Key Features

### 🎯 Dual Registry
- Curated default prompts from Shippopotamus
- Your custom prompts saved locally
- Seamless integration between both

### 🔗 Flexible Loading
```python
load_prompts([
    "ask_plan_act",              # Default prompt
    "custom:company_style",      # Your saved prompt
    "file:./docs/api.md"         # Direct file reference
])
```

### 🧩 Smart Composition
- Automatic deduplication of repeated content
- Token budget enforcement
- Metadata tracking for composed prompts

### 📊 Context Awareness
- Estimate tokens before loading
- Get recommendations for large contexts
- Track usage across sessions

---

## Examples

See the `examples/` directory for:
- `consumer_usage.py` - How teams use Shippopotamus
- `dogfooding.py` - How we use our own tools

---

## Architecture

```
tools/
├── prompt_registry.py    # Core registry functionality
├── prompt_composer.py    # Composition and utilities
└── __init__.py          # FastMCP registration

prompts/                 # Curated prompt library
├── axioms/              # Core methodologies
├── patterns/            # Reusable patterns
└── meta/                # Documentation

tmp/
└── prompt_registry.db   # Local storage for custom prompts
```

---

## Contributing

We welcome contributions! Please:
- Follow the existing code style
- Add tests for new functionality
- Update documentation as needed
- Open an issue before major changes

---

## Roadmap

- **v0.2** - Prompt versioning and history
- **v0.3** - Team collaboration features
- **v0.4** - Analytics and insights
- **v0.5** - LLM platform integrations

---

## License

MIT - See LICENSE file

---

Built with ❤️ for the AI engineering community by the Shippopotamus team