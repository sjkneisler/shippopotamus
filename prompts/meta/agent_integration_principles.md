<!-- id:agent_integration_principles emoji:🤝 -->

# Agent Integration Principles

These principles guide how Shippopotamus should integrate with AI agents to provide the best developer experience.

## Core Principle: Zero Friction

**Never force users to call extra tools to make the system work.**

### Bad Pattern ❌
```python
# User has to remember to call this
index_prompts()  
# Before they can use this
search_prompts("refactoring code")
```

### Good Pattern ✅
```python
# Just works - indexing happens automatically
search_prompts("refactoring code")
```

## Implementation Guidelines

### 1. **Auto-initialization**
- Systems should self-initialize on first use
- Caching and indexing should be transparent
- Graceful degradation when optional features aren't available

### 2. **Progressive Enhancement**
- Core features work without dependencies
- Enhanced features activate automatically when dependencies are present
- Never break if optional components are missing

### 3. **Minimize Round Trips**
- Each tool should do as much as reasonable in one call
- Avoid "setup" tools - integrate setup into the first real operation
- Batch operations when possible

### 4. **Smart Defaults**
- Tools should work with minimal parameters
- Infer intent from context when possible
- Provide helpful suggestions in responses

## Examples in Shippopotamus

### ✅ Good: Auto-indexing
The embeddings system automatically indexes all prompts on first search:
```python
# First call triggers indexing transparently
results = search_prompts("documentation")  
```

### ✅ Good: Bootstrap session
One tool loads everything needed:
```python
# Single call sets up entire session
bootstrap_session()
```

### ✅ Good: Smart composition
Discovers and composes in one operation:
```python
# No need to search first, then compose
compose_smart("refactor legacy code")
```

## Remember

> "The best tool is the one that doesn't feel like a tool at all."

Agent integration should feel magical, not mechanical. Every extra step is friction that reduces adoption and satisfaction.