export function bootstrapSession() {
  const starterPrompts = [
    "ask_plan_act",
    "quality_axioms",
    "context_economy",
    "safe_coding"
  ];
  
  const loadedPrompts = starterPrompts.map(ref => `✓ ${ref}`);
  
  const capabilities = [
    "• Ask→Plan→Act methodology for structured problem solving",
    "• Quality principles for robust implementations",
    "• Context-aware loading to optimize token usage",
    "• Security best practices for safe code generation"
  ];
  
  const quickReference = {
    core_tools: [
      "get_prompt(name) - Load specific prompts",
      "save_prompt(...) - Save custom prompts",
      "compose_prompts([...]) - Combine multiple prompts",
      "list_available() - See all available prompts"
    ],
    prompt_prefixes: [
      "default: ask_plan_act",
      "custom: your_saved_prompt",
      "file: ./path/to/prompt.md"
    ],
    next_steps: [
      "Use list_available() to explore more prompts",
      "Save team-specific prompts with save_prompt()",
      "Load additional prompts as needed with get_prompt()"
    ]
  };
  
  return {
    status: "🦛 Session bootstrapped successfully!",
    loaded_prompts: loadedPrompts,
    tokens_loaded: 922,
    capabilities_enabled: capabilities,
    quick_reference: quickReference,
    tip: "💡 Your session now includes proven methodologies. Use them to approach tasks systematically!"
  };
}