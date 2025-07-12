"""
id: prompt_registry
tag: prompt_ops

Core registry system for Shippopotamus PromptOps platform.
Manages both default prompts (from our curated library) and custom prompts (user-saved).
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import hashlib

from fastmcp import FastMCP

mcp = FastMCP()

# Database path in project's tmp directory
DB_PATH = Path("tmp/prompt_registry.db")

# Token estimation ratio (roughly 4 chars = 1 token)
TOKEN_RATIO = 0.25

def init_db():
    """Initialize the prompt registry database."""
    DB_PATH.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Table for custom prompts metadata
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS custom_prompts (
            id TEXT PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            content TEXT,
            file_path TEXT,
            tags TEXT DEFAULT '[]',
            parent_prompts TEXT DEFAULT '[]',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            usage_count INTEGER DEFAULT 0,
            tokens INTEGER,
            hash TEXT
        )
    """)
    
    # Table for tracking prompt usage
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usage_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt_name TEXT NOT NULL,
            prompt_type TEXT NOT NULL,  -- 'default', 'custom', 'file'
            used_at TEXT NOT NULL,
            tokens INTEGER
        )
    """)
    
    conn.commit()
    conn.close()

def estimate_tokens(text: str) -> int:
    """Estimate token count from text."""
    return int(len(text) * TOKEN_RATIO)

def get_default_prompt(name: str) -> Optional[Dict]:
    """Load a default prompt from our curated library."""
    # Map of default prompt names to their file paths
    default_prompts = {
        # Core methodologies
        "ask_plan_act": "prompts/axioms/CORE.md",
        "quality_axioms": "prompts/axioms/QUALITY.md", 
        "patterns": "prompts/axioms/PATTERNS.md",
        
        # Specific patterns
        "safe_coding": "prompts/patterns/safe_coding.md",
        "context_economy": "prompts/patterns/context_economy.md",
        "echo_emoji": "prompts/patterns/echo_emoji.md",
        "debugging_methodology": "prompts/patterns/debugging_methodology.md",
        "code_review": "prompts/patterns/code_review.md",
        "documentation": "prompts/patterns/documentation.md",
        "testing_strategy": "prompts/patterns/testing_strategy.md",
        
        # Meta prompts
        "implementation_guide": "prompts/meta/implementation-plan.md",
        "design_rationale": "prompts/meta/design-rationale.md"
    }
    
    if name not in default_prompts:
        return None
    
    file_path = Path(default_prompts[name])
    if not file_path.exists():
        return None
    
    content = file_path.read_text()
    return {
        "name": name,
        "content": content,
        "type": "default",
        "path": str(file_path),
        "tokens": estimate_tokens(content)
    }

@mcp.tool()
def get_prompt(name: str) -> dict:
    """
    Load a single prompt by name from the registry.
    
    Args:
        name: Prompt name (can be default prompt or custom saved prompt)
    
    Returns:
        dict: Prompt data including content, tokens, and metadata
    """
    init_db()
    
    # First check default prompts
    default = get_default_prompt(name)
    if default:
        # Log usage
        log_usage(name, "default", default["tokens"])
        return default
    
    # Then check custom prompts
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT name, content, file_path, tags, parent_prompts, 
               created_at, updated_at, tokens, hash
        FROM custom_prompts
        WHERE name = ?
    """, (name,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return {"error": f"Prompt '{name}' not found in registry"}
    
    name, content, file_path, tags_json, parents_json, created, updated, tokens, hash_val = row
    
    # If it's a file reference, load from file
    if file_path and not content:
        try:
            content = Path(file_path).read_text()
            tokens = estimate_tokens(content)
        except Exception as e:
            return {"error": f"Failed to load file '{file_path}': {str(e)}"}
    
    # Log usage
    log_usage(name, "custom", tokens)
    
    return {
        "name": name,
        "content": content,
        "type": "custom",
        "file_path": file_path,
        "tags": json.loads(tags_json),
        "parent_prompts": json.loads(parents_json),
        "created_at": created,
        "updated_at": updated,
        "tokens": tokens
    }

@mcp.tool()
def save_prompt(
    name: str,
    content: Optional[str] = None,
    file_path: Optional[str] = None,
    tags: Optional[List[str]] = None,
    parent_prompts: Optional[List[str]] = None
) -> dict:
    """
    Save a custom prompt to the registry.
    
    Args:
        name: Unique name for the prompt
        content: Prompt content (mutually exclusive with file_path)
        file_path: Path to file containing prompt (mutually exclusive with content)
        tags: List of tags for categorization
        parent_prompts: List of parent prompt names this was derived from
    
    Returns:
        dict: Confirmation with prompt metadata
    """
    init_db()
    
    if not content and not file_path:
        return {"error": "Must provide either content or file_path"}
    
    if content and file_path:
        return {"error": "Cannot provide both content and file_path"}
    
    # Calculate tokens and hash
    if content:
        tokens = estimate_tokens(content)
        hash_val = hashlib.sha256(content.encode()).hexdigest()[:16]
    else:
        # For file references, we'll calculate on load
        tokens = None
        hash_val = None
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    try:
        cursor.execute("""
            INSERT INTO custom_prompts 
            (id, name, content, file_path, tags, parent_prompts, 
             created_at, updated_at, tokens, hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name.lower().replace(" ", "_"),
            name,
            content,
            file_path,
            json.dumps(tags or []),
            json.dumps(parent_prompts or []),
            now,
            now,
            tokens,
            hash_val
        ))
        
        conn.commit()
        conn.close()
        
        return {
            "saved": True,
            "name": name,
            "type": "content" if content else "file_reference",
            "tokens": tokens,
            "tags": tags or [],
            "parent_prompts": parent_prompts or []
        }
        
    except sqlite3.IntegrityError:
        conn.close()
        return {"error": f"Prompt with name '{name}' already exists"}

@mcp.tool()
def load_prompts(prompt_refs: List[str]) -> dict:
    """
    Load multiple prompts at once from various sources.
    
    Args:
        prompt_refs: List of prompt references in format:
            - "prompt_name" - Load from registry (default or custom)
            - "file:path/to/file.md" - Load from file path
            - "shippopotamus:name" - Explicitly load default prompt
            - "custom:name" - Explicitly load custom prompt
    
    Returns:
        dict: Loaded prompts with metadata and combined token count
    """
    init_db()
    
    loaded = []
    errors = []
    total_tokens = 0
    
    for ref in prompt_refs:
        if ref.startswith("file:"):
            # Load from file
            file_path = ref[5:]  # Remove "file:" prefix
            try:
                content = Path(file_path).read_text()
                tokens = estimate_tokens(content)
                loaded.append({
                    "ref": ref,
                    "content": content,
                    "type": "file",
                    "path": file_path,
                    "tokens": tokens
                })
                total_tokens += tokens
                log_usage(file_path, "file", tokens)
            except Exception as e:
                errors.append({
                    "ref": ref,
                    "error": str(e)
                })
                
        elif ref.startswith("shippopotamus:"):
            # Explicitly load default prompt
            name = ref[14:]  # Remove prefix
            prompt = get_default_prompt(name)
            if prompt:
                loaded.append({
                    "ref": ref,
                    **prompt
                })
                total_tokens += prompt["tokens"]
                log_usage(name, "default", prompt["tokens"])
            else:
                errors.append({
                    "ref": ref,
                    "error": f"Default prompt '{name}' not found"
                })
                
        elif ref.startswith("custom:"):
            # Explicitly load custom prompt
            name = ref[7:]  # Remove prefix
            result = get_prompt(name)
            if "error" not in result:
                loaded.append({
                    "ref": ref,
                    **result
                })
                total_tokens += result["tokens"]
            else:
                errors.append({
                    "ref": ref,
                    "error": result["error"]
                })
                
        else:
            # Try registry (default first, then custom)
            result = get_prompt(ref)
            if "error" not in result:
                loaded.append({
                    "ref": ref,
                    **result
                })
                total_tokens += result["tokens"]
            else:
                errors.append({
                    "ref": ref,
                    "error": result["error"]
                })
    
    return {
        "loaded": loaded,
        "errors": errors,
        "total_prompts": len(loaded),
        "total_tokens": total_tokens,
        "success_rate": f"{len(loaded)}/{len(prompt_refs)}"
    }

def log_usage(name: str, prompt_type: str, tokens: int):
    """Log prompt usage for analytics."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO usage_log (prompt_name, prompt_type, used_at, tokens)
        VALUES (?, ?, ?, ?)
    """, (name, prompt_type, datetime.now().isoformat(), tokens))
    
    # Update usage count for custom prompts
    if prompt_type == "custom":
        cursor.execute("""
            UPDATE custom_prompts 
            SET usage_count = usage_count + 1
            WHERE name = ?
        """, (name,))
    
    conn.commit()
    conn.close()