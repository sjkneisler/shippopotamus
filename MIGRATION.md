# Migration Guide

## From v0.0.x (Internal Tools) to v0.1.0 (Prompt Platform)

Shippopotamus has evolved from an internal PromptOps framework to a consumer-focused prompt management platform. Here's what changed:

### 🚨 Breaking Changes

#### Removed Tools
The following tools have been removed:
- `prune_memory` - Memory pruning functionality
- `progress_queue` - Task queue management  
- `tool_dedup_guard` - Deduplication guard

#### New Tools
Replace old workflows with new prompt management tools:
- `get_prompt` - Load prompts from registry
- `save_prompt` - Save custom prompts
- `load_prompts` - Batch loading with multiple sources
- `compose_prompts` - Intelligent prompt combination
- `list_available` - Discover prompts
- `estimate_context` - Token budgeting

### 📝 Migration Steps

1. **Remove old tool imports**
   ```python
   # Old (remove these)
   from tools.prune_memory import prune_memory
   from tools.progress_queue import progress_push, progress_pop
   from tools.tool_dedup_guard import tool_dedup_guard
   ```

2. **Update to new imports**
   ```python
   # New
   from tools.prompt_registry import get_prompt, save_prompt, load_prompts
   from tools.prompt_composer import compose_prompts, list_available, estimate_context
   ```

3. **Convert memory management to prompts**
   ```python
   # Old: Managing memory with pruning
   prune_memory(count=10, archive=True)
   
   # New: Save important prompts instead
   save_prompt("important_context", content=context, tags=["memory"])
   ```

4. **Convert progress tracking to prompt management**
   ```python
   # Old: Task queue
   progress_push("Task description", importance=1)
   
   # New: Save as prompt for reuse
   save_prompt("task_prompt", content="Task: ...", tags=["task", "active"])
   ```

5. **Update database references**
   - Old: `tmp/progress.db`, `tmp/dedup.db`
   - New: `tmp/prompt_registry.db`

### 🎯 New Workflow

Instead of managing internal state, focus on prompt management:

```python
# 1. Load proven methodologies
methodology = get_prompt("ask_plan_act")

# 2. Save your project-specific prompts
save_prompt("project_context", 
            content="Project guidelines...",
            tags=["project", "context"])

# 3. Compose prompts intelligently
full_prompt = compose_prompts([
    "ask_plan_act",
    "project_context",
    "file:./docs/requirements.md"
])

# 4. Use in your AI workflow
response = ai.complete(full_prompt["content"])
```

### 💡 Benefits of Migration

1. **Reusability** - Prompts can be shared across projects
2. **Composition** - Build complex prompts from simple ones
3. **Version Control** - Track prompt evolution with your code
4. **Team Collaboration** - Share prompts with your team
5. **Token Awareness** - Know context costs before loading

### 🆘 Need Help?

- See `examples/consumer_usage.py` for common patterns
- Check `tools/README.md` for detailed API documentation
- Open an issue if you need migration assistance

Welcome to the new Shippopotamus! 🚢🦛