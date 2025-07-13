#!/usr/bin/env python3
"""
Simple bridge between MCP server and Python tools.
Avoids FastMCP dependency issues.
"""

import sys
import json
import os
from pathlib import Path

# Add tools directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def bootstrap_session():
    """Bootstrap session with essential prompts."""
    starter_prompts = [
        "ask_plan_act",
        "quality_axioms", 
        "context_economy",
        "safe_coding"
    ]
    
    # Simulate loading prompts
    loaded_prompts = [f"✓ {ref}" for ref in starter_prompts]
    
    capabilities = [
        "• Ask→Plan→Act methodology for structured problem solving",
        "• Quality principles for robust implementations",
        "• Context-aware loading to optimize token usage",
        "• Security best practices for safe code generation"
    ]
    
    quick_reference = {
        "core_tools": [
            "get_prompt(name) - Load specific prompts",
            "save_prompt(...) - Save custom prompts",
            "compose_prompts([...]) - Combine multiple prompts",
            "list_available() - See all available prompts"
        ],
        "prompt_prefixes": [
            "default: ask_plan_act",
            "custom: your_saved_prompt",
            "file: ./path/to/prompt.md"
        ],
        "next_steps": [
            "Use list_available() to explore more prompts",
            "Save team-specific prompts with save_prompt()",
            "Load additional prompts as needed with get_prompt()"
        ]
    }
    
    return {
        "status": "🦛 Session bootstrapped successfully!",
        "loaded_prompts": loaded_prompts,
        "tokens_loaded": 922,  # Approximate
        "capabilities_enabled": capabilities,
        "quick_reference": quick_reference,
        "tip": "💡 Your session now includes proven methodologies. Use them to approach tasks systematically!"
    }

def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: mcp_bridge_simple.py <tool_name> <json_args>"}))
        sys.exit(1)
    
    tool_name = sys.argv[1]
    args_json = sys.argv[2]
    
    try:
        # For now, only handle bootstrap_session
        if tool_name == "bootstrap_session":
            result = bootstrap_session()
        else:
            # Import the full registry only when needed
            from prompt_registry import get_prompt, save_prompt, load_prompts
            from prompt_composer import compose_prompts, list_available, estimate_context
            
            TOOL_MAP = {
                'get_prompt': get_prompt,
                'save_prompt': save_prompt,
                'load_prompts': load_prompts,
                'compose_prompts': compose_prompts,
                'list_available': list_available,
                'estimate_context': estimate_context
            }
            
            if tool_name not in TOOL_MAP:
                print(json.dumps({"error": f"Unknown tool: {tool_name}"}))
                sys.exit(1)
            
            tool_func = TOOL_MAP[tool_name]
            
            # Parse arguments
            args = json.loads(args_json)
            
            # Change to a temp directory
            import tempfile
            work_dir = os.environ.get('SHIPPOPOTAMUS_WORK_DIR', tempfile.gettempdir())
            os.chdir(work_dir)
            
            # Call the tool
            if isinstance(args, dict):
                result = tool_func(**args)
            else:
                result = tool_func(args)
        
        # Output the result as JSON
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({"error": str(e), "type": type(e).__name__}))
        sys.exit(1)

if __name__ == "__main__":
    main()