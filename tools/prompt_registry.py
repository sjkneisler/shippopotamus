"""
id: prompt_registry
tag: prompt_ops

Registry for tracking loaded prompts and computing context costs.
Works in tandem with prompt_loader to provide context economy insights.
"""

from typing import Dict, List
from datetime import datetime

from fastmcp import FastMCP

mcp = FastMCP()

# In-memory registry for this session
_registry: Dict[str, List[Dict]] = {
    "sessions": [],
    "current_session": None
}

def _get_or_create_session() -> Dict:
    """Get current session or create a new one."""
    if not _registry["current_session"]:
        session = {
            "id": datetime.now().isoformat(),
            "started_at": datetime.now().isoformat(),
            "prompts_loaded": [],
            "total_tokens": 0,
            "loads_count": 0
        }
        _registry["sessions"].append(session)
        _registry["current_session"] = session
    return _registry["current_session"]

@mcp.tool()
def register_prompt_load(
    prompt_id: str,
    emoji: str,
    tokens: int,
    source_path: str,
    echo_confirmed: bool = False
) -> dict:
    """
    Register that a prompt was loaded (called by agents after loading).
    
    Args:
        prompt_id: The ID of the loaded prompt
        emoji: The emoji that should be echoed
        tokens: Estimated token count
        source_path: Path to the prompt file
        echo_confirmed: Whether the echo-emoji contract was fulfilled
    
    Returns:
        dict: Registration confirmation with session stats
    """
    session = _get_or_create_session()
    
    load_record = {
        "prompt_id": prompt_id,
        "emoji": emoji,
        "tokens": tokens,
        "source_path": source_path,
        "loaded_at": datetime.now().isoformat(),
        "echo_confirmed": echo_confirmed,
        "load_number": session["loads_count"] + 1
    }
    
    session["prompts_loaded"].append(load_record)
    session["total_tokens"] += tokens
    session["loads_count"] += 1
    
    return {
        "registered": True,
        "load_number": load_record["load_number"],
        "session_total_tokens": session["total_tokens"],
        "session_prompts_count": len(set(p["prompt_id"] for p in session["prompts_loaded"])),
        "echo_contract": "fulfilled" if echo_confirmed else "pending"
    }

@mcp.tool()
def get_session_report() -> dict:
    """
    Get a detailed report of the current session's prompt usage.
    
    Returns:
        dict: Comprehensive session statistics and insights
    """
    session = _get_or_create_session()
    
    # Calculate unique prompts
    unique_prompts = {}
    for load in session["prompts_loaded"]:
        pid = load["prompt_id"]
        if pid not in unique_prompts:
            unique_prompts[pid] = {
                "emoji": load["emoji"],
                "load_count": 0,
                "total_tokens": 0,
                "echo_confirmed_count": 0
            }
        unique_prompts[pid]["load_count"] += 1
        unique_prompts[pid]["total_tokens"] += load["tokens"]
        if load["echo_confirmed"]:
            unique_prompts[pid]["echo_confirmed_count"] += 1
    
    # Find most loaded prompts
    most_loaded = sorted(
        unique_prompts.items(),
        key=lambda x: x[1]["load_count"],
        reverse=True
    )[:5]
    
    # Calculate echo contract compliance
    total_loads = len(session["prompts_loaded"])
    echo_confirmed = sum(1 for load in session["prompts_loaded"] if load["echo_confirmed"])
    compliance_rate = (echo_confirmed / total_loads * 100) if total_loads > 0 else 0
    
    return {
        "session_id": session["id"],
        "started_at": session["started_at"],
        "duration_minutes": _calculate_duration_minutes(session["started_at"]),
        "total_loads": total_loads,
        "unique_prompts": len(unique_prompts),
        "total_tokens": session["total_tokens"],
        "average_tokens_per_load": session["total_tokens"] // total_loads if total_loads > 0 else 0,
        "echo_contract_compliance": f"{compliance_rate:.1f}%",
        "most_loaded_prompts": [
            {
                "id": pid,
                "emoji": data["emoji"],
                "loads": data["load_count"],
                "tokens": data["total_tokens"]
            }
            for pid, data in most_loaded
        ],
        "prompts_by_category": _categorize_prompts(unique_prompts)
    }

def _calculate_duration_minutes(start_time: str) -> float:
    """Calculate duration in minutes from start time."""
    start = datetime.fromisoformat(start_time)
    duration = datetime.now() - start
    return round(duration.total_seconds() / 60, 1)

def _categorize_prompts(unique_prompts: Dict) -> Dict:
    """Categorize prompts based on their IDs."""
    categories = {
        "axioms": [],
        "meta": [],
        "other": []
    }
    
    for prompt_id in unique_prompts:
        if prompt_id in ["CORE", "QUALITY", "PATTERNS"]:
            categories["axioms"].append(prompt_id)
        elif prompt_id in ["backlog", "design-rationale", "implementation-plan"]:
            categories["meta"].append(prompt_id)
        else:
            categories["other"].append(prompt_id)
    
    return {k: v for k, v in categories.items() if v}

@mcp.tool()
def estimate_context_usage(
    prompt_ids: List[str]
) -> dict:
    """
    Estimate the context usage for loading a set of prompts.
    
    Args:
        prompt_ids: List of prompt IDs to estimate
    
    Returns:
        dict: Token estimates and recommendations
    """
    # Import prompt_loader to get actual file info
    import prompt_loader
    
    estimates = []
    total_tokens = 0
    missing_prompts = []
    
    for prompt_id in prompt_ids:
        # Try to get prompt info without loading it
        all_prompts = prompt_loader.list_prompts()
        prompt_info = next((p for p in all_prompts["prompts"] if p["id"] == prompt_id), None)
        
        if prompt_info:
            estimates.append({
                "id": prompt_id,
                "emoji": prompt_info["emoji"],
                "tokens": prompt_info["tokens"],
                "category": prompt_info["category"]
            })
            total_tokens += prompt_info["tokens"]
        else:
            missing_prompts.append(prompt_id)
    
    # Recommendations based on token count
    recommendations = []
    if total_tokens > 10000:
        recommendations.append("Consider loading prompts incrementally rather than all at once")
    if total_tokens > 20000:
        recommendations.append("This will use significant context - ensure it's necessary")
    
    # Check for redundancy
    if "CORE" in prompt_ids and "PATTERNS" in prompt_ids:
        recommendations.append("CORE and PATTERNS have some overlap - consider loading only one")
    
    return {
        "requested_prompts": len(prompt_ids),
        "found_prompts": len(estimates),
        "missing_prompts": missing_prompts,
        "total_estimated_tokens": total_tokens,
        "estimates": estimates,
        "recommendations": recommendations,
        "context_percentage": f"{(total_tokens / 200000 * 100):.1f}%"  # Assuming ~200k context
    }

@mcp.tool()
def new_session() -> dict:
    """
    Start a new prompt loading session.
    
    Returns:
        dict: New session information
    """
    # Save current session if exists
    if _registry["current_session"]:
        _registry["current_session"]["ended_at"] = datetime.now().isoformat()
    
    # Create new session
    session = {
        "id": datetime.now().isoformat(),
        "started_at": datetime.now().isoformat(),
        "prompts_loaded": [],
        "total_tokens": 0,
        "loads_count": 0
    }
    _registry["sessions"].append(session)
    _registry["current_session"] = session
    
    return {
        "new_session_id": session["id"],
        "previous_sessions": len(_registry["sessions"]) - 1,
        "status": "Session started"
    }

@mcp.tool()
def get_all_sessions_summary() -> dict:
    """
    Get a summary of all prompt loading sessions.
    
    Returns:
        dict: Summary statistics across all sessions
    """
    if not _registry["sessions"]:
        return {"message": "No sessions recorded yet"}
    
    total_tokens_all = sum(s["total_tokens"] for s in _registry["sessions"])
    total_loads_all = sum(s["loads_count"] for s in _registry["sessions"])
    
    sessions_summary = []
    for session in _registry["sessions"]:
        duration = _calculate_duration_minutes(session["started_at"])
        is_current = session == _registry["current_session"]
        
        sessions_summary.append({
            "session_id": session["id"],
            "duration_minutes": duration,
            "loads": session["loads_count"],
            "tokens": session["total_tokens"],
            "is_current": is_current
        })
    
    return {
        "total_sessions": len(_registry["sessions"]),
        "total_tokens_all_time": total_tokens_all,
        "total_loads_all_time": total_loads_all,
        "average_tokens_per_session": total_tokens_all // len(_registry["sessions"]),
        "sessions": sessions_summary
    }

def _reset_registry():
    """Reset the registry for testing purposes."""
    global _registry
    _registry = {
        "sessions": [],
        "current_session": None
    }