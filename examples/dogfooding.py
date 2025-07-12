#!/usr/bin/env python3
"""
Dogfooding Example: Using Shippopotamus to improve Shippopotamus!

This demonstrates how we use our own prompt management tools to develop better.
"""

import sys
sys.path.append('..')

from tools.prompt_registry import save_prompt, load_prompts
from tools.prompt_composer import compose_prompts, list_available, estimate_tokens

def main():
    print("🚢🦛 Shippopotamus Dogfooding Demo\n")
    
    # 1. List what's available
    print("=== Available Prompts ===")
    available = list_available()
    print(f"Default prompts: {sum(len(cat) for cat in available['defaults'].values())}")
    print(f"Custom prompts: {len(available['custom'])}")
    
    # 2. Load our core methodology for development
    print("\n=== Loading Development Prompts ===")
    dev_prompts = load_prompts([
        "ask_plan_act",      # Our core methodology
        "quality_axioms",    # Quality guidelines
        "safe_coding"        # Safety practices
    ])
    
    print(f"Loaded {dev_prompts['total_prompts']} prompts")
    print(f"Total tokens: {dev_prompts['total_tokens']}")
    
    # 3. Compose a specialized prompt for tool development
    print("\n=== Composing Tool Development Prompt ===")
    composed = compose_prompts(
        ["ask_plan_act", "safe_coding", "context_economy"],
        deduplicate=True
    )
    
    print(f"Composed tokens: {composed['tokens']}")
    if composed['metadata']['removed_duplicates']:
        print(f"Removed {len(composed['metadata']['removed_duplicates'])} duplicates")
    
    # 4. Save our custom development prompt
    print("\n=== Saving Custom Development Prompt ===")
    save_result = save_prompt(
        name="shippopotamus_tool_development",
        content=composed['content'],
        tags=["development", "tools", "shippopotamus"],
        parent_prompts=["ask_plan_act", "safe_coding", "context_economy"]
    )
    
    if save_result.get('saved'):
        print("✅ Saved custom prompt for future use!")
    
    # 5. Demonstrate file reference capability
    print("\n=== Using File References ===")
    
    # Save a prompt that references our CLAUDE.md
    claude_ref = save_prompt(
        name="claude_md_guidelines",
        file_path="CLAUDE.md",
        tags=["guidelines", "claude", "development"]
    )
    
    if claude_ref.get('saved'):
        print("✅ Saved reference to CLAUDE.md")
    
    # 6. Load multiple sources including our new custom prompt
    print("\n=== Loading Mixed Sources ===")
    mixed = load_prompts([
        "shippopotamus:ask_plan_act",         # Explicit default
        "custom:shippopotamus_tool_development",  # Our saved prompt
        "file:README.md"                      # Direct file reference
    ])
    
    print(f"Loaded from {mixed['total_prompts']} sources")
    print(f"Total context: {mixed['total_tokens']} tokens")
    
    # 7. Estimate context for a large load
    print("\n=== Context Estimation ===")
    estimate = estimate_tokens(prompt_refs=[
        "ask_plan_act",
        "quality_axioms", 
        "patterns",
        "implementation_guide"
    ])
    
    print(f"Estimated tokens: {estimate['total_tokens']}")
    print(f"Context usage: {estimate['estimated_context_percentage']}%")
    if estimate['recommendations']:
        print("Recommendations:")
        for rec in estimate['recommendations']:
            print(f"  - {rec}")
    
    # 8. Show how we'd use this in practice
    print("\n=== Practical Usage for Development ===")
    print("When developing new Shippopotamus features, we can now:")
    print("1. Load our saved development prompt: get_prompt('shippopotamus_tool_development')")
    print("2. Compose with specific patterns: compose_prompts(['custom:shippopotamus_tool_development', 'echo_emoji'])")
    print("3. Reference our docs directly: load_prompts(['file:CLAUDE.md', 'file:prompts/00_INDEX.md'])")
    
    print("\n🎉 Dogfooding complete! We're using our own tools to build better tools!")

if __name__ == "__main__":
    main()