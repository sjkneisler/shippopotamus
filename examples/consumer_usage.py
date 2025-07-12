#!/usr/bin/env python3
"""
Example: How external consumers would use Shippopotamus MCP

This shows typical usage patterns for teams building AI applications.
"""

# In a real scenario, users would access these via MCP protocol
# This example shows the conceptual usage

def example_basic_usage():
    """Basic usage - loading a methodology"""
    print("=== Basic Usage ===")
    
    # Load a proven methodology
    prompt = get_prompt("ask_plan_act")
    print(f"Loaded {prompt['tokens']} tokens of battle-tested methodology")
    
    # Use it in your AI interaction
    # ai_response = ai.complete(prompt['content'] + user_query)

def example_save_company_guidelines():
    """Save company-specific guidelines"""
    print("\n=== Saving Company Guidelines ===")
    
    # Save your company's coding standards
    save_prompt(
        name="acme_python_standards",
        content="""
        # ACME Corp Python Standards
        
        - Use type hints for all functions
        - Maximum line length: 88 characters (Black)
        - Docstrings required for all public functions
        - Follow PEP 8 with our specific exceptions
        """,
        tags=["python", "standards", "acme"]
    )
    
    # Reference an existing file in your repo
    save_prompt(
        name="acme_api_guidelines",
        file_path="./docs/api-design.md",
        tags=["api", "guidelines", "acme"]
    )

def example_compose_for_task():
    """Compose prompts for a specific task"""
    print("\n=== Composing for API Development ===")
    
    # Combine methodologies with your standards
    composed = compose_prompts([
        "ask_plan_act",              # Shippopotamus methodology
        "safe_coding",               # Shippopotamus safety patterns  
        "custom:acme_python_standards",  # Your standards
        "custom:acme_api_guidelines"     # Your guidelines
    ])
    
    print(f"Composed prompt: {composed['tokens']} tokens")
    # Use: ai.complete(composed['content'] + "Build a REST API for user management")

def example_context_aware_loading():
    """Load prompts based on available context"""
    print("\n=== Context-Aware Loading ===")
    
    # Estimate before loading
    estimate = estimate_tokens(prompt_refs=[
        "ask_plan_act",
        "quality_axioms",
        "custom:acme_python_standards",
        "file:./docs/examples/user-api.md"
    ])
    
    print(f"Estimated tokens: {estimate['total_tokens']}")
    
    # Load with budget
    if estimate['total_tokens'] < 10000:
        # We have room, load everything
        load_prompts(estimate['prompt_refs'])
    else:
        # Need to be selective
        compose_prompts(
            estimate['prompt_refs'],
            max_tokens=10000
        )

def example_team_collaboration():
    """Share prompts across team"""
    print("\n=== Team Collaboration ===")
    
    # Save a successful prompt combination
    save_prompt(
        name="acme_api_assistant_v2", 
        content="[Combined prompt content that worked well]",
        tags=["assistant", "api", "v2"],
        parent_prompts=["ask_plan_act", "acme_python_standards"]
    )
    
    # List what the team has created
    custom_prompts = list_available(include_defaults=False)
    print(f"Team has created {len(custom_prompts['custom'])} custom prompts")
    
    # Load the most used prompt
    most_used = max(custom_prompts['custom'], key=lambda x: x['usage_count'])
    print(f"Most used: {most_used['name']} ({most_used['usage_count']} uses)")

def example_specialized_assistant():
    """Build a specialized AI assistant"""
    print("\n=== Specialized Assistant ===")
    
    # For a code review assistant
    review_prompt = compose_prompts([
        "quality_axioms",           # Shippopotamus quality patterns
        "safe_coding",              # Security considerations
        "custom:acme_python_standards",
        "file:./docs/review-checklist.md"
    ])
    
    # Save for reuse
    save_prompt(
        name="acme_code_reviewer",
        content=review_prompt['content'],
        tags=["code-review", "assistant", "python"]
    )
    
    print("Created specialized code review assistant")

# Simulated MCP tool functions (in reality, these come from the MCP server)
def get_prompt(name): 
    return {"content": f"[{name} prompt content]", "tokens": 500}

def save_prompt(**kwargs): 
    return {"saved": True}

def load_prompts(refs): 
    return {"loaded": refs, "total_tokens": len(refs) * 500}

def compose_prompts(refs, **kwargs): 
    return {"content": "[composed]", "tokens": len(refs) * 400}

def list_available(**kwargs): 
    return {"custom": [{"name": "example", "usage_count": 5}]}

def estimate_tokens(**kwargs): 
    return {"total_tokens": 2000, "prompt_refs": kwargs.get('prompt_refs', [])}

if __name__ == "__main__":
    print("🚢🦛 Shippopotamus Consumer Usage Examples\n")
    
    example_basic_usage()
    example_save_company_guidelines()
    example_compose_for_task()
    example_context_aware_loading()
    example_team_collaboration()
    example_specialized_assistant()
    
    print("\n✨ Ready to build better AI applications with Shippopotamus!")