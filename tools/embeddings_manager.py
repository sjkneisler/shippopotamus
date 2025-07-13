"""
Embeddings manager for semantic prompt discovery.
Handles embedding generation, storage, and similarity search.
"""

import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import numpy as np
from collections import defaultdict

# For now, we'll use a simple TF-IDF approach as a fallback
# In production, you'd use sentence-transformers or OpenAI embeddings
try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

from fastmcp import FastMCP
try:
    from .prompt_registry import DB_PATH, init_db, get_default_prompt
    from .prompt_composer import compose_prompts
except ImportError:
    from prompt_registry import DB_PATH, init_db, get_default_prompt
    from prompt_composer import compose_prompts

mcp = FastMCP()

# Constants
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Small, fast, good for semantic similarity
EMBEDDING_DIM = 384  # Dimension for all-MiniLM-L6-v2

class EmbeddingsManager:
    """Manages embeddings for prompt discovery."""
    
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        self.model_name = model_name
        self.model = None
        self._init_model()
        self._init_embeddings_table()
        self._auto_indexed = False  # Track if we've auto-indexed
    
    def _init_model(self):
        """Initialize the embedding model."""
        if HAS_SENTENCE_TRANSFORMERS:
            try:
                self.model = SentenceTransformer(self.model_name)
            except Exception as e:
                print(f"Failed to load embedding model: {e}")
                self.model = None
    
    def _init_embeddings_table(self):
        """Create embeddings table if it doesn't exist."""
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create embeddings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prompt_embeddings (
                prompt_id TEXT PRIMARY KEY,
                prompt_type TEXT NOT NULL,  -- 'default' or 'custom'
                embedding_json TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                model_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_embeddings_type 
            ON prompt_embeddings(prompt_type)
        """)
        
        conn.commit()
        conn.close()
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text."""
        if self.model is None:
            # Fallback: simple character-based hash embedding
            # This is just for demonstration - in production, use proper embeddings
            return self._fallback_embedding(text)
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return self._fallback_embedding(text)
    
    def _fallback_embedding(self, text: str) -> List[float]:
        """Simple fallback embedding based on text statistics."""
        # This is a very basic approach - just for testing without dependencies
        import hashlib
        
        # Create a deterministic pseudo-embedding
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        
        # Convert hash to numbers
        embedding = []
        for i in range(0, len(text_hash), 2):
            value = int(text_hash[i:i+2], 16) / 255.0 - 0.5
            embedding.append(value)
        
        # Pad or truncate to match expected dimension
        if len(embedding) < EMBEDDING_DIM:
            embedding.extend([0.0] * (EMBEDDING_DIM - len(embedding)))
        else:
            embedding = embedding[:EMBEDDING_DIM]
        
        return embedding
    
    def store_embedding(self, prompt_id: str, prompt_type: str, 
                       embedding: List[float], content_hash: str):
        """Store embedding in database."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO prompt_embeddings 
            (prompt_id, prompt_type, embedding_json, content_hash, model_name)
            VALUES (?, ?, ?, ?, ?)
        """, (prompt_id, prompt_type, json.dumps(embedding), 
              content_hash, self.model_name))
        
        conn.commit()
        conn.close()
    
    def get_embedding(self, prompt_id: str, prompt_type: str) -> Optional[List[float]]:
        """Retrieve embedding from database."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT embedding_json FROM prompt_embeddings
            WHERE prompt_id = ? AND prompt_type = ?
        """, (prompt_id, prompt_type))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        return None
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def find_similar(self, query_embedding: List[float], 
                    top_k: int = 5, 
                    min_similarity: float = 0.3) -> List[Dict]:
        """Find similar prompts based on embedding similarity."""
        # Auto-index if we haven't already
        self._ensure_indexed()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get all embeddings
        cursor.execute("""
            SELECT prompt_id, prompt_type, embedding_json 
            FROM prompt_embeddings
        """)
        
        results = []
        for prompt_id, prompt_type, embedding_json in cursor.fetchall():
            embedding = json.loads(embedding_json)
            similarity = self.cosine_similarity(query_embedding, embedding)
            
            if similarity >= min_similarity:
                results.append({
                    'prompt_id': prompt_id,
                    'prompt_type': prompt_type,
                    'similarity': similarity
                })
        
        conn.close()
        
        # Sort by similarity and return top_k
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]
    
    def _ensure_indexed(self):
        """Ensure all prompts are indexed before searching."""
        if self._auto_indexed:
            return
        
        # Check if we have any embeddings
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM prompt_embeddings")
        count = cursor.fetchone()[0]
        conn.close()
        
        # If no embeddings exist, do initial indexing
        if count == 0:
            self._do_index()
        
        self._auto_indexed = True
    
    def _do_index(self):
        """Internal method to index all prompts."""
        from prompt_registry import default_prompts
        import hashlib
        
        # Index default prompts
        for prompt_name, prompt_path in default_prompts.items():
            try:
                prompt_data = get_default_prompt(prompt_name)
                if prompt_data:
                    content = prompt_data['content']
                    content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
                    
                    # Generate and store embedding
                    embedding = self.generate_embedding(content)
                    if embedding:
                        self.store_embedding(prompt_name, 'default', embedding, content_hash)
            except Exception:
                pass  # Silent fail on auto-index
        
        # Index custom prompts
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT name, content FROM custom_prompts")
            for name, content in cursor.fetchall():
                try:
                    content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
                    embedding = self.generate_embedding(content)
                    if embedding:
                        self.store_embedding(name, 'custom', embedding, content_hash)
                except Exception:
                    pass  # Silent fail on auto-index
        except Exception:
            pass  # Table might not exist yet
        
        conn.close()


# Global instance
_embeddings_manager = None

def get_embeddings_manager() -> EmbeddingsManager:
    """Get or create the global embeddings manager."""
    global _embeddings_manager
    if _embeddings_manager is None:
        _embeddings_manager = EmbeddingsManager()
    return _embeddings_manager


@mcp.tool()
def search_prompts(query: str, top_k: int = 5, min_similarity: float = 0.3) -> dict:
    """
    Search for prompts using semantic similarity.
    
    Args:
        query: Natural language description of what you want to do
        top_k: Number of results to return (default: 5)
        min_similarity: Minimum similarity threshold (0-1, default: 0.3)
    
    Returns:
        dict: Search results with relevant prompts and similarity scores
    """
    manager = get_embeddings_manager()
    
    # Generate embedding for query
    query_embedding = manager.generate_embedding(query)
    if not query_embedding:
        return {
            "error": "Failed to generate query embedding",
            "fallback": "Use list_available() to browse prompts manually"
        }
    
    # Find similar prompts
    similar = manager.find_similar(query_embedding, top_k, min_similarity)
    
    if not similar:
        return {
            "results": [],
            "message": "No similar prompts found. Try a different query or use list_available()"
        }
    
    # Enrich results with prompt details
    from prompt_registry import get_prompt
    
    results = []
    principles = []
    workflows = []
    
    for match in similar:
        prompt_data = get_prompt(match['prompt_id'])
        if prompt_data:
            result = {
                "name": match['prompt_id'],
                "similarity": round(match['similarity'], 3),
                "type": prompt_data.get('type', 'unknown'),
                "description": _extract_description(prompt_data['content']),
                "tokens": prompt_data.get('tokens', 0)
            }
            results.append(result)
            
            # Categorize by type
            if 'principle' in prompt_data.get('content', ''):
                principles.append(match['prompt_id'])
            elif 'workflow' in prompt_data.get('content', ''):
                workflows.append(match['prompt_id'])
    
    return {
        "query": query,
        "results": results,
        "suggested_principles": principles[:3],
        "suggested_workflows": workflows[:2],
        "tip": f"Load these with: load_prompts({[r['name'] for r in results[:3]]})"
    }


@mcp.tool()
def discover_prompts(task_description: str) -> dict:
    """
    Discover relevant prompts for a specific task.
    
    This tool analyzes your task description and recommends:
    - Principles to guide HOW you work
    - Workflows that match WHAT you want to do
    
    Args:
        task_description: Description of the task you want to accomplish
    
    Returns:
        dict: Recommended prompts categorized by type
    """
    # Search for relevant prompts
    search_results = search_prompts(task_description, top_k=10, min_similarity=0.2)
    
    if "error" in search_results:
        return search_results
    
    # Analyze and categorize results
    principles = []
    workflows = []
    
    for result in search_results.get("results", []):
        if result["similarity"] > 0.4:  # Higher threshold for recommendations
            if "principle" in result.get("type", ""):
                principles.append({
                    "name": result["name"],
                    "relevance": result["similarity"],
                    "why": result["description"][:100] + "..."
                })
            elif "workflow" in result.get("type", ""):
                workflows.append({
                    "name": result["name"],
                    "relevance": result["similarity"],
                    "what": result["description"][:100] + "..."
                })
    
    # Generate recommendations
    recommendations = {
        "task": task_description,
        "recommended_principles": principles[:3],
        "recommended_workflows": workflows[:2],
        "suggested_bootstrap": []
    }
    
    # Build bootstrap command
    if principles:
        bootstrap_prompts = [p["name"] for p in principles[:2]]
        if workflows:
            bootstrap_prompts.append(workflows[0]["name"])
        recommendations["suggested_bootstrap"] = bootstrap_prompts
        recommendations["command"] = f"compose_prompts({bootstrap_prompts})"
    
    # Add insights
    if not principles and not workflows:
        recommendations["insight"] = "No highly relevant prompts found. Consider saving a custom prompt for this task type."
    elif principles and not workflows:
        recommendations["insight"] = "Found guiding principles but no specific workflows. You might want to create a workflow for this task."
    elif workflows and not principles:
        recommendations["insight"] = "Found workflows but consider loading principles first for best practices."
    else:
        recommendations["insight"] = "Found both principles and workflows. Use the suggested command to load them together."
    
    return recommendations


def _extract_description(content: str, max_length: int = 150) -> str:
    """Extract a description from prompt content."""
    lines = content.strip().split('\n')
    
    # Skip headers and metadata
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('<!--'):
            # Found first content line
            if len(line) > max_length:
                return line[:max_length] + "..."
            return line
    
    return "No description available"




@mcp.tool()
def compose_smart(
    task_description: str,
    max_tokens: Optional[int] = None,
    include_principles: bool = True,
    include_workflows: bool = True
) -> dict:
    """
    Intelligently compose prompts based on task description.
    
    This tool:
    1. Discovers relevant prompts for your task
    2. Automatically selects the best combination
    3. Composes them with proper deduplication
    4. Respects token budget constraints
    
    Args:
        task_description: What you want to accomplish
        max_tokens: Maximum token budget (optional)
        include_principles: Include guiding principles (default: True)
        include_workflows: Include task workflows (default: True)
    
    Returns:
        dict: Composed prompt with selected components and metadata
    """
    # Discover relevant prompts
    discovery = discover_prompts(task_description)
    
    if "error" in discovery:
        return discovery
    
    # Build prompt list based on relevance
    prompts_to_load = []
    selected_components = {
        "principles": [],
        "workflows": [],
        "relevance_scores": {}
    }
    
    # Add principles
    if include_principles:
        for principle in discovery.get("recommended_principles", [])[:2]:
            prompts_to_load.append(principle["name"])
            selected_components["principles"].append(principle["name"])
            selected_components["relevance_scores"][principle["name"]] = principle["relevance"]
    
    # Add workflows
    if include_workflows:
        for workflow in discovery.get("recommended_workflows", [])[:1]:
            prompts_to_load.append(workflow["name"])
            selected_components["workflows"].append(workflow["name"])
            selected_components["relevance_scores"][workflow["name"]] = workflow["relevance"]
    
    if not prompts_to_load:
        return {
            "error": "No relevant prompts found for task",
            "task": task_description,
            "suggestion": "Try a more specific task description or browse with list_available()"
        }
    
    # Compose the prompts
    composition_result = compose_prompts(
        prompt_refs=prompts_to_load,
        deduplicate=True,
        max_tokens=max_tokens
    )
    
    # Add smart composition metadata
    if "error" not in composition_result:
        composition_result["smart_metadata"] = {
            "task": task_description,
            "selected_components": selected_components,
            "selection_reasoning": _explain_selection(selected_components),
            "average_relevance": sum(selected_components["relevance_scores"].values()) / len(selected_components["relevance_scores"])
        }
        
        # Add usage recommendation
        if selected_components["principles"] and selected_components["workflows"]:
            composition_result["usage_tip"] = "Loaded both principles and workflows. The principles will guide your approach while the workflow provides specific steps."
        elif selected_components["principles"]:
            composition_result["usage_tip"] = "Loaded guiding principles. Consider your specific implementation approach for this task."
        elif selected_components["workflows"]:
            composition_result["usage_tip"] = "Loaded task workflow. Follow the steps while keeping best practices in mind."
    
    return composition_result


def _explain_selection(components: dict) -> str:
    """Generate explanation for why specific prompts were selected."""
    explanations = []
    
    if components["principles"]:
        explanations.append(f"Selected {len(components['principles'])} principles for best practices and methodology")
    
    if components["workflows"]:
        explanations.append(f"Selected {len(components['workflows'])} workflow(s) for task-specific guidance")
    
    # Mention high relevance scores
    high_relevance = [name for name, score in components["relevance_scores"].items() if score > 0.7]
    if high_relevance:
        explanations.append(f"Particularly relevant: {', '.join(high_relevance)}")
    
    return ". ".join(explanations) if explanations else "Selected based on relevance to task"