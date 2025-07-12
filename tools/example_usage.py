#!/usr/bin/env python3
"""
Example usage of Shippopotamus PromptOps tools

This demonstrates how the prompt_loader and prompt_registry work together
to enforce context economy and the echo-emoji contract.
"""

from prompt_loader import load_index, load_prompt, list_prompts, validate_prompts
from prompt_registry import register_prompt_load, get_session_report, estimate_context_usage

def main():
    print("🚢🦛 Shippopotamus PromptOps Demo\n")
    
    # 1. Load and check the index
    print("1. Loading index...")
    index = load_index()
    if "error" not in index:
        print(f"   ✅ Index loaded: {index['size_kb']:.1f}KB ({index['tokens']} tokens)")
        if index.get("echo_required"):
            print(f"   📣 Echo required: {index['emoji']}")
    else:
        print(f"   ❌ {index['error']}")
    
    # 2. List available prompts
    print("\n2. Available prompts:")
    prompts = list_prompts()
    for category, info in prompts["categories"].items():
        print(f"   {category}: {info['count']} prompts ({info['tokens']} tokens)")
    
    # 3. Load a specific prompt
    print("\n3. Loading CORE axioms...")
    core = load_prompt("CORE")
    if "error" not in core:
        print(f"   ✅ Loaded: {core['emoji']} {core['id']} ({core['tokens']} tokens)")
        
        # Register the load (simulating agent behavior)
        register_prompt_load(
            prompt_id=core["id"],
            emoji=core["emoji"],
            tokens=core["tokens"],
            source_path=core["path"],
            echo_confirmed=True  # Agent echoed the emoji
        )
    
    # 4. Estimate context for multiple prompts
    print("\n4. Estimating context usage for all axioms...")
    estimate = estimate_context_usage(["CORE", "QUALITY", "PATTERNS"])
    print(f"   Total tokens: {estimate['total_estimated_tokens']}")
    print(f"   Context usage: {estimate['context_percentage']}")
    if estimate["recommendations"]:
        print("   Recommendations:")
        for rec in estimate["recommendations"]:
            print(f"   - {rec}")
    
    # 5. Get session report
    print("\n5. Session report:")
    report = get_session_report()
    print(f"   Loads: {report['total_loads']}")
    print(f"   Unique prompts: {report['unique_prompts']}")
    print(f"   Total tokens: {report['total_tokens']}")
    print(f"   Echo compliance: {report['echo_contract_compliance']}")
    
    # 6. Validate all prompts
    print("\n6. Validating all prompts...")
    validation = validate_prompts()
    if validation["valid"]:
        print("   ✅ All prompts valid!")
    else:
        print(f"   ⚠️  Found {len(validation['issues'])} issues")
        for issue in validation["issues"][:3]:  # Show first 3
            print(f"   - {issue['file']}: {issue['issue']}")

if __name__ == "__main__":
    main()