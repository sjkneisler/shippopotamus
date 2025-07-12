"""
id: progress_queue
tag: progress_tracking

FIFO queue for tracking progress across sessions with importance levels.
Items with importance > 0 are sticky and won't be pruned automatically.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastmcp import FastMCP

mcp = FastMCP()

def init_db():
    """Initialize the progress queue database"""
    db_path = Path("tmp/progress.db")
    db_path.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            importance INTEGER DEFAULT 0,
            tags TEXT DEFAULT '[]',
            created_at TEXT NOT NULL,
            completed_at TEXT
        )
    """)
    
    conn.commit()
    conn.close()

@mcp.tool()
def progress_push(
    content: str,
    importance: int = 0,
    tags: Optional[List[str]] = None
) -> dict:
    """
    Add an item to the progress queue
    
    Args:
        content: The task or progress item to track
        importance: 0 = normal (can be pruned), >0 = sticky
        tags: Optional list of tags for categorization
    
    Returns:
        dict: {"id": N, "position": M, "queue_size": Q}
    """
    init_db()
    
    conn = sqlite3.connect("tmp/progress.db")
    cursor = conn.cursor()
    
    tags_json = json.dumps(tags or [])
    created_at = datetime.now().isoformat()
    
    cursor.execute("""
        INSERT INTO progress_queue (content, importance, tags, created_at)
        VALUES (?, ?, ?, ?)
    """, (content, importance, tags_json, created_at))
    
    item_id = cursor.lastrowid
    
    # Get position in queue (count of incomplete items before this one)
    cursor.execute("""
        SELECT COUNT(*) FROM progress_queue 
        WHERE completed_at IS NULL AND id < ?
    """, (item_id,))
    position = cursor.fetchone()[0]
    
    # Get total queue size
    cursor.execute("SELECT COUNT(*) FROM progress_queue WHERE completed_at IS NULL")
    queue_size = cursor.fetchone()[0]
    
    conn.commit()
    conn.close()
    
    return {
        "id": item_id,
        "position": position,
        "queue_size": queue_size
    }

@mcp.tool()
def progress_pop() -> dict:
    """
    Remove and return the oldest non-sticky item from the queue
    
    Returns:
        dict: The popped item or {"error": "empty"} if no items available
    """
    init_db()
    
    conn = sqlite3.connect("tmp/progress.db")
    cursor = conn.cursor()
    
    # Get oldest non-sticky, incomplete item
    cursor.execute("""
        SELECT id, content, importance, tags, created_at
        FROM progress_queue
        WHERE completed_at IS NULL AND importance = 0
        ORDER BY id
        LIMIT 1
    """)
    
    row = cursor.fetchone()
    if not row:
        conn.close()
        return {"error": "empty"}
    
    item_id, content, importance, tags_json, created_at = row
    
    # Mark as completed
    completed_at = datetime.now().isoformat()
    cursor.execute("""
        UPDATE progress_queue SET completed_at = ?
        WHERE id = ?
    """, (completed_at, item_id))
    
    conn.commit()
    conn.close()
    
    return {
        "id": item_id,
        "content": content,
        "importance": importance,
        "tags": json.loads(tags_json),
        "created_at": created_at,
        "completed_at": completed_at
    }

@mcp.tool()
def progress_list(
    limit: int = 10,
    include_completed: bool = False,
    tag_filter: Optional[str] = None
) -> dict:
    """
    List items in the progress queue
    
    Args:
        limit: Maximum number of items to return
        include_completed: Whether to include completed items
        tag_filter: Filter by tag (if specified)
    
    Returns:
        dict: {"items": [...], "total": N, "sticky_count": M}
    """
    init_db()
    
    conn = sqlite3.connect("tmp/progress.db")
    cursor = conn.cursor()
    
    # Build query
    conditions = []
    params = []
    
    if not include_completed:
        conditions.append("completed_at IS NULL")
    
    if tag_filter:
        conditions.append("tags LIKE ?")
        params.append(f'%"{tag_filter}"%')
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    # Get items
    query = f"""
        SELECT id, content, importance, tags, created_at, completed_at
        FROM progress_queue
        WHERE {where_clause}
        ORDER BY 
            CASE WHEN completed_at IS NULL THEN 0 ELSE 1 END,
            importance DESC,
            id
        LIMIT ?
    """
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    items = []
    for row in rows:
        item_id, content, importance, tags_json, created_at, completed_at = row
        items.append({
            "id": item_id,
            "content": content,
            "importance": importance,
            "tags": json.loads(tags_json),
            "created_at": created_at,
            "completed_at": completed_at
        })
    
    # Get total count
    cursor.execute(f"SELECT COUNT(*) FROM progress_queue WHERE {where_clause}", params[:-1])
    total = cursor.fetchone()[0]
    
    # Get sticky count
    cursor.execute("SELECT COUNT(*) FROM progress_queue WHERE completed_at IS NULL AND importance > 0")
    sticky_count = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "items": items,
        "total": total,
        "sticky_count": sticky_count
    }

@mcp.tool()
def progress_complete(item_id: int) -> dict:
    """
    Mark a specific item as completed
    
    Args:
        item_id: The ID of the item to complete
    
    Returns:
        dict: {"status": "success"} or {"error": "not_found"}
    """
    init_db()
    
    conn = sqlite3.connect("tmp/progress.db")
    cursor = conn.cursor()
    
    # Check if item exists and is not already completed
    cursor.execute("SELECT completed_at FROM progress_queue WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return {"error": "not_found"}
    
    if row[0]:  # Already completed
        conn.close()
        return {"error": "already_completed"}
    
    # Mark as completed
    completed_at = datetime.now().isoformat()
    cursor.execute("""
        UPDATE progress_queue SET completed_at = ?
        WHERE id = ?
    """, (completed_at, item_id))
    
    conn.commit()
    conn.close()
    
    return {"status": "success", "completed_at": completed_at}