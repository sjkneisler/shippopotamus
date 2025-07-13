#!/usr/bin/env python3
"""
Bridge between MCP server and Python tools.
Handles tool invocation and JSON serialization.
"""

import sys
import json
import os
from pathlib import Path

# Add tools directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import our tools
from prompt_registry import get_prompt, save_prompt, load_prompts
from prompt_composer import compose_prompts, list_available, estimate_context, bootstrap_session

# Map tool names to functions
TOOL_MAP = {
    'get_prompt': get_prompt,
    'save_prompt': save_prompt,
    'load_prompts': load_prompts,
    'compose_prompts': compose_prompts,
    'list_available': list_available,
    'estimate_context': estimate_context,
    'bootstrap_session': bootstrap_session
}

def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: mcp_bridge.py <tool_name> <json_args>"}))
        sys.exit(1)
    
    tool_name = sys.argv[1]
    args_json = sys.argv[2]
    
    try:
        # Parse arguments
        args = json.loads(args_json)
        
        # Get the tool function
        if tool_name not in TOOL_MAP:
            print(json.dumps({"error": f"Unknown tool: {tool_name}"}))
            sys.exit(1)
        
        tool_func = TOOL_MAP[tool_name]
        
        # Change to a temp directory to ensure SQLite works properly
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