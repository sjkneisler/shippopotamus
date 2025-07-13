"""
id: prompt_composer
tag: prompt_ops

Intelligent prompt composition and management tools.
Helps combine, deduplicate, and optimize prompts for context efficiency.
"""

import json
import re
import sqlite3
from typing import List, Optional
from collections import OrderedDict

from fastmcp import FastMCP
try:
    from .prompt_registry import load_prompts, estimate_tokens, init_db, DB_PATH
except ImportError:
    from prompt_registry import load_prompts, estimate_tokens, init_db, DB_PATH

mcp = FastMCP()

@mcp.tool()
def compose_prompts(
    prompt_refs: List[str],
    deduplicate: bool = True,
    max_tokens: Optional[int] = None,
    separator: str = "\n\n---\n\n"
) -> dict:
    """
    Intelligently compose multiple prompts into a single prompt.
    
    Args:
        prompt_refs: List of prompt references (same format as load_prompts)
        deduplicate: Remove duplicate sections/paragraphs
        max_tokens: Maximum token budget (will prioritize based on order)
        separator: String to separate prompts
    
    Returns:
        dict: Composed prompt with metadata
    """
    # First load all prompts
    loaded_result = load_prompts(prompt_refs)
    
    if not loaded_result["loaded"]:
        return {
            "error": "No prompts could be loaded",
            "errors": loaded_result["errors"]
        }
    
    # Extract contents
    contents = []
    metadata = {
        "sources": [],
        "total_original_tokens": 0,
        "removed_duplicates": []
    }
    
    for prompt in loaded_result["loaded"]:
        contents.append(prompt["content"])
        metadata["sources"].append({
            "ref": prompt["ref"],
            "type": prompt["type"],
            "tokens": prompt["tokens"]
        })
        metadata["total_original_tokens"] += prompt["tokens"]
    
    # Compose the content
    if deduplicate:
        composed_content, duplicates = deduplicate_content(contents, separator)
        metadata["removed_duplicates"] = duplicates
    else:
        composed_content = separator.join(contents)
    
    # Check token budget
    composed_tokens = estimate_tokens(composed_content)
    
    if max_tokens and composed_tokens > max_tokens:
        # Trim to fit budget
        composed_content, metadata["trimmed"] = trim_to_budget(
            contents, max_tokens, separator
        )
        composed_tokens = estimate_tokens(composed_content)
    
    return {
        "content": composed_content,
        "tokens": composed_tokens,
        "metadata": metadata,
        "sources": loaded_result["loaded"],
        "errors": loaded_result["errors"]
    }

@mcp.tool()
def list_available(
    include_defaults: bool = True,
    include_custom: bool = True,
    tags: Optional[List[str]] = None
) -> dict:
    """
    List all available prompts in the registry.
    
    Args:
        include_defaults: Include default Shippopotamus prompts
        include_custom: Include user-saved custom prompts
        tags: Filter by tags (for custom prompts)
    
    Returns:
        dict: Categorized list of available prompts
    """
    init_db()
    
    result = {
        "defaults": {},
        "custom": [],
        "total": 0
    }
    
    # Default prompts with categories
    if include_defaults:
        result["defaults"] = {
            "methodologies": [
                {"name": "ask_plan_act", "description": "Core Ask→Plan→Act methodology"},
                {"name": "quality_axioms", "description": "Quality and best practices"},
                {"name": "patterns", "description": "Meta-patterns for prompt design"}
            ],
            "patterns": [
                {"name": "safe_coding", "description": "Safe coding practices"},
                {"name": "context_economy", "description": "Context-aware prompt loading"},
                {"name": "echo_emoji", "description": "Echo-emoji contract pattern"},
                {"name": "debugging_methodology", "description": "Systematic debugging approach"},
                {"name": "code_review", "description": "Comprehensive code review checklist"},
                {"name": "documentation", "description": "Documentation best practices"},
                {"name": "testing_strategy", "description": "Test-driven development guide"}
            ],
            "meta": [
                {"name": "implementation_guide", "description": "Implementation planning"},
                {"name": "design_rationale", "description": "Design decisions and rationale"}
            ]
        }
        # Count defaults
        for category in result["defaults"].values():
            result["total"] += len(category)
    
    # Custom prompts
    if include_custom:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        query = """
            SELECT name, tags, created_at, updated_at, usage_count, tokens
            FROM custom_prompts
        """
        params = []
        
        if tags:
            # Filter by tags (match any)
            tag_conditions = []
            for tag in tags:
                tag_conditions.append("tags LIKE ?")
                params.append(f'%"{tag}"%')
            query += " WHERE " + " OR ".join(tag_conditions)
        
        query += " ORDER BY usage_count DESC, updated_at DESC"
        
        cursor.execute(query, params)
        
        for row in cursor.fetchall():
            name, tags_json, created, updated, usage, tokens = row
            result["custom"].append({
                "name": name,
                "tags": json.loads(tags_json),
                "created_at": created,
                "updated_at": updated,
                "usage_count": usage,
                "tokens": tokens
            })
        
        conn.close()
        result["total"] += len(result["custom"])
    
    return result

@mcp.tool()
def estimate_context(
    content: Optional[str] = None,
    prompt_refs: Optional[List[str]] = None
) -> dict:
    """
    Estimate token count for content or prompt references.
    
    Args:
        content: Direct content to estimate
        prompt_refs: List of prompt references to estimate
    
    Returns:
        dict: Token estimates and context usage
    """
    if not content and not prompt_refs:
        return {"error": "Must provide either content or prompt_refs"}
    
    if content and prompt_refs:
        return {"error": "Provide either content or prompt_refs, not both"}
    
    if content:
        tokens = estimate_tokens(content)  # Import from prompt_registry
        return {
            "tokens": tokens,
            "characters": len(content),
            "estimated_context_percentage": round(tokens / 200000 * 100, 1),
            "fits_in_small_context": tokens < 4000,
            "fits_in_medium_context": tokens < 20000,
            "fits_in_large_context": tokens < 100000
        }
    
    # Estimate for prompt references
    loaded = load_prompts(prompt_refs)
    
    total_tokens = loaded["total_tokens"]
    breakdown = []
    
    for prompt in loaded["loaded"]:
        breakdown.append({
            "ref": prompt["ref"],
            "tokens": prompt["tokens"],
            "percentage": round(prompt["tokens"] / total_tokens * 100, 1) if total_tokens > 0 else 0
        })
    
    return {
        "total_tokens": total_tokens,
        "breakdown": breakdown,
        "errors": loaded["errors"],
        "estimated_context_percentage": round(total_tokens / 200000 * 100, 1),
        "recommendations": get_token_recommendations(total_tokens)
    }

def deduplicate_content(contents: List[str], separator: str) -> tuple[str, List[str]]:
    """Remove duplicate paragraphs while preserving order."""
    seen_paragraphs = OrderedDict()
    duplicates = []
    
    for content in contents:
        # Split into paragraphs
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', content) if p.strip()]
        
        for para in paragraphs:
            # Normalize whitespace for comparison
            normalized = ' '.join(para.split())
            
            if normalized not in seen_paragraphs:
                seen_paragraphs[normalized] = para
            else:
                duplicates.append(para[:50] + "...")
    
    # Reconstruct with original formatting
    unique_paragraphs = list(seen_paragraphs.values())
    return '\n\n'.join(unique_paragraphs), duplicates

def trim_to_budget(contents: List[str], max_tokens: int, separator: str) -> tuple[str, dict]:
    """Trim content to fit token budget."""
    trimmed = []
    current_tokens = 0
    trimmed_info = {
        "kept_prompts": 0,
        "dropped_prompts": 0
    }
    
    for content in contents:
        content_tokens = estimate_tokens(content)
        if current_tokens + content_tokens <= max_tokens:
            trimmed.append(content)
            current_tokens += content_tokens
            trimmed_info["kept_prompts"] += 1
        else:
            trimmed_info["dropped_prompts"] += 1
    
    return separator.join(trimmed), trimmed_info

def get_token_recommendations(tokens: int) -> List[str]:
    """Get recommendations based on token count."""
    recommendations = []
    
    if tokens > 100000:
        recommendations.append("Very large context - consider splitting into multiple interactions")
    elif tokens > 50000:
        recommendations.append("Large context - ensure all content is necessary")
    elif tokens > 20000:
        recommendations.append("Moderate context - good for detailed work")
    
    if tokens > 10000:
        recommendations.append("Consider using compose_prompts with deduplication")
    
    return recommendations

@mcp.tool()
def bootstrap_session() -> dict:
    """
    🚀 RECOMMENDED FIRST CALL: Initialize your session with Shippopotamus! 
    
    This tool loads essential prompts and methodologies to enhance your capabilities.
    Call this at the start of any task to get access to battle-tested patterns like
    Ask→Plan→Act methodology, quality axioms, and context management strategies.
    
    Returns:
        dict: Session initialization results with loaded prompts and quick reference
    """
    # Curated starter pack of prompts
    starter_prompts = [
        "ask_plan_act",      # Core methodology
        "quality_axioms",    # Quality principles
        "context_economy",   # Token efficiency
        "safe_coding"        # Security best practices
    ]
    
    # Load the starter pack
    result = compose_prompts(
        prompt_refs=starter_prompts,
        deduplicate=True,
        separator="\n\n" + "="*60 + "\n\n"
    )
    
    if "error" in result:
        return {
            "error": "Failed to bootstrap session",
            "details": result["error"]
        }
    
    # Build helpful response
    loaded_prompts = []
    capabilities = []
    
    for source in result["sources"]:
        ref = source["ref"]
        loaded_prompts.append(f"✓ {ref}")
        
        # Add capability descriptions
        if ref == "ask_plan_act":
            capabilities.append("• Ask→Plan→Act methodology for structured problem solving")
        elif ref == "quality_axioms":
            capabilities.append("• Quality principles for robust implementations")
        elif ref == "context_economy":
            capabilities.append("• Context-aware loading to optimize token usage")
        elif ref == "safe_coding":
            capabilities.append("• Security best practices for safe code generation")
    
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
        "tokens_loaded": result["tokens"],
        "capabilities_enabled": capabilities,
        "quick_reference": quick_reference,
        "tip": "💡 Your session now includes proven methodologies. Use them to approach tasks systematically!"
    }