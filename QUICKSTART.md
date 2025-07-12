# 🚢🦛 Shippopotamus Quickstart Guide

Get up and running with professional prompt management in 5 minutes!

## Installation

### 1. Install in your AI project

Add Shippopotamus to your MCP configuration:

```json
// .mcp.json or claude_desktop_config.json
{
  "mcpServers": {
    "shippopotamus": {
      "command": "npx",
      "args": ["shippopotamus"]
    }
  }
}
```

### 2. Verify installation

In your AI assistant, try:
```
list_available()
```

You should see our curated prompt library!

## Your First Prompt

### Load a methodology

Let's start with our battle-tested Ask→Plan→Act methodology:

```python
# Load the prompt
prompt = get_prompt("ask_plan_act")

# Use it in your workflow
print(prompt["content"])
```

This gives you a structured approach to any coding task!

## Save Your Own Prompts

### Example: Save your coding standards

```python
# Save your team's Python standards
save_prompt(
    name="python_standards",
    content="""
    # Our Python Coding Standards
    
    - Use Python 3.10+
    - Follow PEP 8 with 88 char line limit (Black)
    - Type hints required for all public functions
    - Docstrings in Google style
    - Tests required for all new features
    """,
    tags=["python", "standards", "team"]
)
```

### Reference existing documentation

Instead of copying, link to your docs:

```python
save_prompt(
    name="api_guidelines",
    file_path="./docs/api-design.md",
    tags=["api", "guidelines"]
)
```

## Compose Complex Prompts

### Combine methodologies with your standards

```python
# Load and combine multiple prompts
all_prompts = load_prompts([
    "ask_plan_act",           # Shippopotamus methodology
    "safe_coding",            # Security practices
    "custom:python_standards" # Your saved standards
])

# Or compose them into one
composed = compose_prompts(
    ["ask_plan_act", "python_standards", "testing_strategy"],
    deduplicate=True  # Remove any duplicate sections
)

print(f"Total tokens: {composed['tokens']}")
```

## Real-World Example

### Building a Code Review Assistant

```python
# 1. Save your team's review criteria
save_prompt(
    name="team_review_checklist",
    content="""
    Additional review points for our team:
    - Check for proper error handling with our ErrorLogger
    - Verify API endpoints follow our naming convention
    - Ensure database migrations are included
    """,
    tags=["review", "team", "checklist"]
)

# 2. Compose a comprehensive review prompt
review_prompt = compose_prompts([
    "code_review",              # Shippopotamus comprehensive checklist
    "team_review_checklist",    # Your team additions
    "safe_coding"              # Security considerations
])

# 3. Use it for reviews
# ai_response = ai.complete(review_prompt["content"] + code_to_review)
```

## Context Management

### Plan your token usage

```python
# Estimate before loading
estimate = estimate_context(prompt_refs=[
    "ask_plan_act",
    "code_review", 
    "debugging_methodology",
    "file:./docs/architecture.md"
])

print(f"Total tokens: {estimate['total_tokens']}")
print(f"Context usage: {estimate['estimated_context_percentage']}%")

# Get recommendations
for rec in estimate['recommendations']:
    print(f"- {rec}")
```

### Load within budget

```python
# Only load what fits
if estimate['total_tokens'] < 10000:
    prompts = load_prompts(estimate['prompt_refs'])
else:
    # Use composition with token limit
    prompts = compose_prompts(
        estimate['prompt_refs'],
        max_tokens=10000
    )
```

## Discover Available Prompts

### Browse the library

```python
# See all available prompts
available = list_available()

# Default Shippopotamus prompts
for category, prompts in available['defaults'].items():
    print(f"\n{category}:")
    for prompt in prompts:
        print(f"  - {prompt['name']}: {prompt['description']}")

# Your custom prompts
print(f"\nCustom prompts: {len(available['custom'])}")
for prompt in available['custom']:
    print(f"  - {prompt['name']} (used {prompt['usage_count']} times)")
```

## Best Practices

### 1. Start with defaults
Our curated prompts are battle-tested. Try them before creating custom ones.

### 2. Save successful combinations
When you find a prompt combination that works well, save it:
```python
save_prompt(
    name="our_debug_assistant",
    content=composed_prompt,
    parent_prompts=["debugging_methodology", "team_standards"]
)
```

### 3. Use tags effectively
Tags help you find prompts later:
```python
# Find all testing-related prompts
testing_prompts = list_available(tags=["testing"])
```

### 4. Version important prompts
Include version in the name or content:
```python
save_prompt(
    name="api_spec_v2",
    content="# API Specification v2.0\n...",
    tags=["api", "v2"]
)
```

## Next Steps

1. **Explore the patterns library**: Try `get_prompt("debugging_methodology")` or `get_prompt("code_review")`
2. **Save your team's standards**: Create reusable prompts for your workflows
3. **Compose specialized assistants**: Combine prompts for specific tasks
4. **Track usage**: Use `list_available()` to see which prompts are most valuable

## Need Help?

- Check out the [examples directory](./examples/) for more use cases
- Read the [full documentation](./README.md)
- Open an issue on GitHub for support

Happy prompting! 🚢🦛