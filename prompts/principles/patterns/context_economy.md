<!-- id:context_economy emoji:💰 -->

# Context Economy Pattern

Optimize your use of context to maximize effectiveness within token limits.

## Key Principles

1. **Load What You Need**: Only load prompts and files that are directly relevant
2. **Compose Wisely**: Use prompt composition to avoid duplication
3. **Monitor Usage**: Track token consumption throughout your session

## Loading Strategies

### Progressive Loading
Start with essential prompts, then load additional context as needed:
```
1. Core methodology (ask_plan_act)
2. Domain-specific patterns
3. Project-specific guidelines
4. Examples only if necessary
```

### Batch Loading
When you know what you need, load multiple prompts at once:
```python
load_prompts(["ask_plan_act", "safe_coding", "file:./guidelines.md"])
```

## Token Budgeting

- **Small tasks** (<4K tokens): Single methodology prompt
- **Medium tasks** (<20K tokens): Core + domain patterns  
- **Large tasks** (<100K tokens): Full context with examples
- **Very large** (>100K tokens): Split into multiple interactions

## Optimization Techniques

1. Use `compose_prompts()` with deduplication enabled
2. Reference files instead of copying content when possible
3. Save successful prompt combinations for reuse
4. Monitor token usage with `estimate_tokens()`