# Shippopotamus PromptOps Tools

🚢🦛 **Professional prompt management for AI applications**

## Overview

Shippopotamus provides MCP tools for managing prompts in AI applications. It combines a curated library of battle-tested prompts with a flexible registry for custom prompts.

## Core Tools

### Registry Tools (`prompt_registry.py`)

- **`get_prompt(name)`** - Load prompts from registry or library
- **`save_prompt(name, content/file_path, tags, parent_prompts)`** - Save custom prompts  
- **`load_prompts(prompt_refs)`** - Batch load multiple prompts

### Composition Tools (`prompt_composer.py`)

- **`compose_prompts(prompt_refs, deduplicate, max_tokens)`** - Intelligently combine prompts
- **`list_available(include_defaults, include_custom, tags)`** - Discover available prompts
- **`estimate_context(content/prompt_refs)`** - Estimate token usage

## Usage Examples

### Basic Usage
```python
# Load a battle-tested methodology
prompt = get_prompt("ask_plan_act")

# Save your company standards
save_prompt("company_style", content="...", tags=["standards"])

# Reference external files
save_prompt("api_docs", file_path="./docs/api.md")
```

### Advanced Composition
```python
# Load multiple sources
prompts = load_prompts([
    "ask_plan_act",              # Default prompt
    "custom:company_style",      # Custom prompt
    "file:./guidelines.md"       # Direct file reference
])

# Compose with deduplication
composed = compose_prompts([
    "ask_plan_act",
    "company_style"
], deduplicate=True, max_tokens=10000)
```

## Default Prompt Library

### Methodologies
- `ask_plan_act` - Core Ask→Plan→Act methodology
- `quality_axioms` - Quality and best practices
- `patterns` - Meta-patterns for prompt design

### Patterns  
- `safe_coding` - Security practices (🛡️)
- `context_economy` - Token optimization (💰)
- `echo_emoji` - Visual contracts (📣)

### Meta
- `implementation_guide` - Planning guidance
- `design_rationale` - Design decisions

## File Structure

```
tools/
├── __init__.py           # FastMCP registration
├── prompt_registry.py    # Core registry functionality  
├── prompt_composer.py    # Composition and utilities
└── README.md            # This file

tmp/                     # Created automatically
└── prompt_registry.db   # SQLite database
```

## Installation

Install Shippopotamus MCP in your project:

```json
{
  "mcpServers": {
    "shippopotamus": {
      "command": "npx",
      "args": ["@shippopotamus/mcp-server"]
    }
  }
}
```

## Testing

Run the test suite:
```bash
python test_comprehensive.py
```

## Contributing

See the main project documentation for contribution guidelines.

---

Built with ❤️ for the AI engineering community