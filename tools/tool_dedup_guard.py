"""
id: tool_dedup_guard
tag: safety

Deduplication guard to prevent duplicate tool calls and enforce safe-write rule.
Must be called before any tool invocation to check if it's safe to proceed.
"""

import hashlib
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

from fastmcp import FastMCP

mcp = FastMCP()

def init_db():
    """Initialize the deduplication database"""
    db_path = Path("tmp/dedup.db")
    db_path.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dedup_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tool_name TEXT NOT NULL,
            params_hash TEXT NOT NULL,
            params_json TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            session_id TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS write_safety (
            file_path TEXT PRIMARY KEY,
            last_read TEXT NOT NULL,
            last_write TEXT
        )
    """)
    
    conn.commit()
    conn.close()

def compute_hash(tool_name: str, params: Dict[str, Any]) -> str:
    """Compute a hash for tool + params combination"""
    # Sort params for consistent hashing
    params_str = json.dumps(params, sort_keys=True)
    content = f"{tool_name}:{params_str}"
    return hashlib.sha256(content.encode()).hexdigest()

@mcp.tool()
def tool_dedup_guard(
    tool_name: str,
    params: Dict[str, Any],
    session_id: Optional[str] = None,
    ttl_seconds: int = 300
) -> dict:
    """
    Check if a tool call is safe to execute (not a duplicate)
    
    Args:
        tool_name: Name of the tool to be called
        params: Parameters for the tool call
        session_id: Optional session identifier
        ttl_seconds: Time-to-live for dedup entries (default: 5 minutes)
    
    Returns:
        dict: {"safe": bool, "reason": str, "last_called": timestamp}
    """
    init_db()
    
    params_hash = compute_hash(tool_name, params)
    
    conn = sqlite3.connect("tmp/dedup.db")
    cursor = conn.cursor()
    
    # Check for recent duplicate
    cutoff_time = (datetime.now() - timedelta(seconds=ttl_seconds)).isoformat()
    
    cursor.execute("""
        SELECT timestamp FROM dedup_log
        WHERE tool_name = ? AND params_hash = ? AND timestamp > ?
        ORDER BY timestamp DESC
        LIMIT 1
    """, (tool_name, params_hash, cutoff_time))
    
    row = cursor.fetchone()
    
    if row:
        conn.close()
        return {
            "safe": False,
            "reason": f"Duplicate call detected (last called: {row[0]})",
            "last_called": row[0]
        }
    
    # Special handling for write_file
    if tool_name == "write_file" and "file_path" in params:
        file_path = params["file_path"]
        
        # Check if file was read in this session
        cursor.execute("""
            SELECT last_read FROM write_safety
            WHERE file_path = ?
        """, (file_path,))
        
        read_row = cursor.fetchone()
        if not read_row:
            conn.close()
            return {
                "safe": False,
                "reason": "Safe-write rule violation: file must be read before writing",
                "last_called": None
            }
    
    # Log this call
    timestamp = datetime.now().isoformat()
    params_json = json.dumps(params, sort_keys=True)
    
    cursor.execute("""
        INSERT INTO dedup_log (tool_name, params_hash, params_json, timestamp, session_id)
        VALUES (?, ?, ?, ?, ?)
    """, (tool_name, params_hash, params_json, timestamp, session_id))
    
    conn.commit()
    conn.close()
    
    return {
        "safe": True,
        "reason": "No duplicate detected",
        "last_called": None
    }

@mcp.tool()
def register_file_read(file_path: str) -> dict:
    """
    Register that a file has been read (for safe-write rule)
    
    Args:
        file_path: Path of the file that was read
    
    Returns:
        dict: {"status": "success"}
    """
    init_db()
    
    conn = sqlite3.connect("tmp/dedup.db")
    cursor = conn.cursor()
    
    timestamp = datetime.now().isoformat()
    
    cursor.execute("""
        INSERT OR REPLACE INTO write_safety (file_path, last_read)
        VALUES (?, ?)
    """, (file_path, timestamp))
    
    conn.commit()
    conn.close()
    
    return {"status": "success", "timestamp": timestamp}

@mcp.tool()
def clear_dedup_log(older_than_seconds: int = 3600) -> dict:
    """
    Clear old entries from deduplication log
    
    Args:
        older_than_seconds: Remove entries older than this (default: 1 hour)
    
    Returns:
        dict: {"deleted": N, "remaining": M}
    """
    init_db()
    
    conn = sqlite3.connect("tmp/dedup.db")
    cursor = conn.cursor()
    
    cutoff_time = (datetime.now() - timedelta(seconds=older_than_seconds)).isoformat()
    
    # Get count before deletion
    cursor.execute("SELECT COUNT(*) FROM dedup_log")
    total_before = cursor.fetchone()[0]
    
    # Delete old entries
    cursor.execute("DELETE FROM dedup_log WHERE timestamp < ?", (cutoff_time,))
    deleted = cursor.rowcount
    
    # Get remaining count
    cursor.execute("SELECT COUNT(*) FROM dedup_log")
    remaining = cursor.fetchone()[0]
    
    conn.commit()
    conn.close()
    
    return {
        "deleted": deleted,
        "remaining": remaining
    }