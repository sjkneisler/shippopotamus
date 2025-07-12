"""
id: prompt_loader
tag: prompt_ops

Smart prompt loading system that enforces context economy and the echo-emoji contract.
This is the core innovation of Shippopotamus - treating prompts as first-class operational contracts.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

mcp = FastMCP()

# Configuration
INDEX_MAX_KB = float(os.getenv("PROMPT_INDEX_MAX_KB", "2"))
VERBOSE = os.getenv("PROMPT_LOADER_VERBOSE", "false").lower() == "true"
TOKEN_RATIO = float(os.getenv("TOKEN_ESTIMATE_RATIO", "0.25"))

# Cache for loaded prompts in this session
_loaded_prompts: Dict[str, Dict] = {}
_load_history: List[Dict] = []

def parse_prompt_header(content: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract id and emoji from prompt file header."""
    # Try to match both id and emoji
    header_match = re.search(r'<!-- id:(\w+) emoji:(.+?) -->', content)
    if header_match:
        return header_match.group(1), header_match.group(2)
    
    # Try to match just id
    id_match = re.search(r'<!-- id:(\w+)', content)
    # Try to match just emoji
    emoji_match = re.search(r'emoji:(.+?) -->', content)
    
    return (id_match.group(1) if id_match else None, 
            emoji_match.group(1) if emoji_match else None)

def estimate_tokens(text: str) -> int:
    """Estimate token count from character count."""
    return int(len(text) * TOKEN_RATIO)

def get_file_size_kb(file_path: Path) -> float:
    """Get file size in KB."""
    return file_path.stat().st_size / 1024

@mcp.tool()
def load_prompt(
    prompt_id: str,
    force_reload: bool = False
) -> dict:
    """
    Load a specific prompt by ID, enforcing the echo-emoji contract.
    
    Args:
        prompt_id: The prompt ID to load (e.g., "CORE", "QUALITY")
        force_reload: Force reload even if already loaded
    
    Returns:
        dict: {
            "id": prompt_id,
            "emoji": emoji_symbol,
            "content": full_content,
            "tokens": estimated_tokens,
            "size_kb": file_size,
            "path": file_path,
            "loaded_at": timestamp,
            "echo_required": True
        }
    """
    # Check cache first
    if prompt_id in _loaded_prompts and not force_reload:
        prompt_data = _loaded_prompts[prompt_id]
        prompt_data["from_cache"] = True
        return prompt_data
    
    # Search for prompt file
    prompts_dir = Path("prompts")
    
    # Search for prompt file by scanning all .md files
    matching_files = []
    for file_path in prompts_dir.rglob("*.md"):
        if file_path.name == "README.md":
            continue
        try:
            content = file_path.read_text()
            found_id, _ = parse_prompt_header(content)
            if found_id == prompt_id:
                matching_files.append(str(file_path))
                break  # Found it, no need to continue
        except Exception:
            continue
    
    if not matching_files or not matching_files[0]:
        return {
            "error": f"Prompt with id '{prompt_id}' not found",
            "searched_in": str(prompts_dir)
        }
    
    # Load the first matching file
    file_path = Path(matching_files[0])
    content = file_path.read_text()
    
    # Parse header
    found_id, emoji = parse_prompt_header(content)
    
    if found_id != prompt_id:
        return {
            "error": f"ID mismatch: file claims to be '{found_id}' but looking for '{prompt_id}'",
            "file": str(file_path)
        }
    
    # Build response
    prompt_data = {
        "id": prompt_id,
        "emoji": emoji or "📄",  # Default emoji if none specified
        "content": content,
        "tokens": estimate_tokens(content),
        "size_kb": get_file_size_kb(file_path),
        "path": str(file_path),
        "loaded_at": datetime.now().isoformat(),
        "echo_required": True,
        "from_cache": False
    }
    
    # Cache it
    _loaded_prompts[prompt_id] = prompt_data.copy()
    
    # Log to history
    _load_history.append({
        "prompt_id": prompt_id,
        "tokens": prompt_data["tokens"],
        "timestamp": prompt_data["loaded_at"]
    })
    
    return prompt_data

@mcp.tool()
def load_index() -> dict:
    """
    Load the prompt index file, enforcing size constraints.
    
    Returns:
        dict: {
            "content": index_content,
            "size_kb": actual_size,
            "max_kb": configured_max,
            "tokens": estimated_tokens,
            "within_limit": bool,
            "warning": optional_warning
        }
    """
    index_path = Path("prompts/00_INDEX.md")
    
    if not index_path.exists():
        return {
            "error": "Index file not found at prompts/00_INDEX.md"
        }
    
    size_kb = get_file_size_kb(index_path)
    content = index_path.read_text()
    tokens = estimate_tokens(content)
    
    result = {
        "content": content,
        "size_kb": round(size_kb, 2),
        "max_kb": INDEX_MAX_KB,
        "tokens": tokens,
        "within_limit": size_kb <= INDEX_MAX_KB
    }
    
    if not result["within_limit"]:
        result["warning"] = f"Index file exceeds {INDEX_MAX_KB}KB limit! Consider pruning."
    
    # Parse emoji from index
    _, emoji = parse_prompt_header(content)
    if emoji:
        result["emoji"] = emoji
        result["echo_required"] = True
    
    return result

@mcp.tool()
def list_prompts(
    category: Optional[str] = None
) -> dict:
    """
    List all available prompts with their metadata.
    
    Args:
        category: Filter by category (e.g., "axioms", "meta")
    
    Returns:
        dict: {
            "prompts": [...],
            "total": count,
            "total_tokens": sum_of_tokens,
            "categories": {...}
        }
    """
    prompts_dir = Path("prompts")
    prompts = []
    categories = {}
    
    # Walk through all prompt files
    for file_path in prompts_dir.rglob("*.md"):
        if file_path.name == "README.md":
            continue
            
        content = file_path.read_text()
        prompt_id, emoji = parse_prompt_header(content)
        
        if not prompt_id:
            continue
        
        # Determine category from path
        relative_path = file_path.relative_to(prompts_dir)
        file_category = relative_path.parts[0] if len(relative_path.parts) > 1 else "root"
        
        # Apply filter if specified
        if category and file_category != category:
            continue
        
        prompt_info = {
            "id": prompt_id,
            "emoji": emoji or "📄",
            "path": str(file_path),
            "category": file_category,
            "size_kb": round(get_file_size_kb(file_path), 2),
            "tokens": estimate_tokens(content)
        }
        
        prompts.append(prompt_info)
        
        # Track by category
        if file_category not in categories:
            categories[file_category] = {"count": 0, "tokens": 0}
        categories[file_category]["count"] += 1
        categories[file_category]["tokens"] += prompt_info["tokens"]
    
    # Sort by category then ID
    prompts.sort(key=lambda p: (p["category"], p["id"]))
    
    return {
        "prompts": prompts,
        "total": len(prompts),
        "total_tokens": sum(p["tokens"] for p in prompts),
        "categories": categories
    }

@mcp.tool()
def get_load_stats() -> dict:
    """
    Get statistics about prompt loading in this session.
    
    Returns:
        dict: {
            "loaded_prompts": [...],
            "total_loaded": count,
            "total_tokens": sum,
            "load_history": [...],
            "cache_hits": count
        }
    """
    loaded_list = []
    for prompt_id, data in _loaded_prompts.items():
        loaded_list.append({
            "id": prompt_id,
            "emoji": data.get("emoji", "📄"),
            "tokens": data["tokens"],
            "size_kb": data["size_kb"],
            "loaded_at": data["loaded_at"]
        })
    
    # Count cache hits from history
    cache_hits = sum(1 for h in _load_history if h.get("from_cache", False))
    
    return {
        "loaded_prompts": loaded_list,
        "total_loaded": len(_loaded_prompts),
        "total_tokens": sum(p["tokens"] for p in loaded_list),
        "load_history": _load_history[-10:],  # Last 10 loads
        "cache_hits": cache_hits,
        "session_start": _load_history[0]["timestamp"] if _load_history else None
    }

@mcp.tool()
def validate_prompts() -> dict:
    """
    Validate all prompts for consistency and compliance.
    
    Returns:
        dict: {
            "valid": bool,
            "issues": [...],
            "stats": {...}
        }
    """
    issues = []
    stats = {
        "total_files": 0,
        "valid_headers": 0,
        "missing_emoji": 0,
        "missing_id": 0,
        "oversized_files": 0
    }
    
    prompts_dir = Path("prompts")
    
    for file_path in prompts_dir.rglob("*.md"):
        if file_path.name == "README.md":
            continue
            
        stats["total_files"] += 1
        content = file_path.read_text()
        prompt_id, emoji = parse_prompt_header(content)
        
        if not prompt_id:
            issues.append({
                "file": str(file_path),
                "issue": "Missing id in header"
            })
            stats["missing_id"] += 1
        
        if not emoji:
            issues.append({
                "file": str(file_path),
                "issue": "Missing emoji in header"
            })
            stats["missing_emoji"] += 1
        
        if prompt_id and emoji:
            stats["valid_headers"] += 1
        
        # Check for oversized files (>10KB warning)
        size_kb = get_file_size_kb(file_path)
        if size_kb > 10:
            issues.append({
                "file": str(file_path),
                "issue": f"Large file ({size_kb:.1f}KB) - consider splitting"
            })
            stats["oversized_files"] += 1
    
    # Special check for index
    index_path = prompts_dir / "00_INDEX.md"
    if index_path.exists():
        index_size = get_file_size_kb(index_path)
        if index_size > INDEX_MAX_KB:
            issues.insert(0, {
                "file": "prompts/00_INDEX.md",
                "issue": f"Index exceeds {INDEX_MAX_KB}KB limit ({index_size:.2f}KB)",
                "severity": "high"
            })
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "stats": stats
    }

def _reset_cache():
    """Reset the prompt cache for testing purposes."""
    global _loaded_prompts, _load_history
    _loaded_prompts = {}
    _load_history = []