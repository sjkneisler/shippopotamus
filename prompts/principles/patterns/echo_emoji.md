<!-- id:echo_emoji emoji:📣 -->

# Echo-Emoji Contract Pattern

A simple yet powerful pattern for confirming prompt loading and establishing visual contracts.

## The Contract

When loading any prompt file that contains an emoji in its header, the agent MUST echo that emoji at the start of their response. This serves as:

1. **Visual Confirmation**: Immediately shows which prompts were loaded
2. **Attention Signal**: Indicates the agent has processed the prompt
3. **Context Marker**: Helps track which guidelines are active

## Implementation

### For Prompt Authors
```markdown
<!-- id:your_prompt emoji:🎯 -->
# Your Prompt Title
```

### For Agents
When loading the above prompt, start your response with: `🎯`

When loading multiple prompts, echo all emojis in order:
- Load CORE (🧭) + QUALITY (⚖️) → Start with: `🧭⚖️`

## Benefits

- **Zero-cost verification**: No extra tokens for explanation
- **Universal understanding**: Emojis transcend language barriers  
- **Quick scanning**: Easily see which prompts are active
- **Encourages compliance**: Simple, memorable action

## Example Usage

```python
# User loads prompts
prompts = load_prompts(["safe_coding", "context_economy"])

# Agent response starts with
🛡️💰 I'll help you with safe, context-efficient coding...
```