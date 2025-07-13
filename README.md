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

2. Bootstrap your session with principles:
```python
# Initialize with core principles (recommended first call!)
bootstrap_session()

# Or load specific principles
prompt = get_prompt("ask_plan_act")
```

3. Use workflows for specific tasks:
```python
# Load a workflow to update documentation
workflow = get_prompt("update_docs")

# Save your own workflows
save_prompt("deploy_process", content="...", tags=["workflow", "deployment"])

# Compose principles with workflows
composed = compose_prompts(["quality_axioms", "update_docs"])
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

Shippopotamus provides two types of prompts:

### 🧭 Principles - "How to Work"
Working conditions, methodologies, and best practices that guide AI agents:

**Axioms**
- **ask_plan_act** (🧭) - Core Ask→Plan→Act methodology
- **quality_axioms** (⚖️) - Quality and best practices
- **patterns** (🪢) - Meta-patterns for prompt design

**Patterns**
- **safe_coding** (🛡️) - Security practices
- **context_economy** (💰) - Token optimization  
- **documentation** (📝) - Documentation best practices
- **debugging_methodology** (🐛) - Systematic debugging approach

### 🎯 Workflows - "What to Do"
Task-oriented prompts that guide specific actions:

**Documentation**
- **update_docs** (📚) - Update documentation after completing work

More workflows coming soon: testing, refactoring, feature implementation, etc.

### When to Use Each Type

**Use Principles when:**
- Setting up a new AI agent or session
- Establishing coding standards and practices  
- Training team members on methodologies
- Defining "ground rules" for AI behavior

**Use Workflows when:**
- Performing specific tasks (update docs, write tests, etc.)
- Following repeatable processes
- Implementing features with consistent steps
- Automating routine development activities

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