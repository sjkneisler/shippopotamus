"""
Tests for embeddings-based prompt discovery tools.
"""

import pytest
import json
import tempfile
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Add the tools directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from embeddings_manager import (
    EmbeddingsManager, search_prompts, discover_prompts, 
    compose_smart, _extract_description
)


class TestEmbeddingsManager:
    """Test the EmbeddingsManager class."""
    
    @pytest.fixture
    def mock_db_path(self, tmp_path):
        """Create a temporary database path."""
        db_path = tmp_path / "test_prompts.db"
        with patch('embeddings_manager.DB_PATH', str(db_path)):
            yield str(db_path)
    
    @pytest.fixture
    def manager(self, mock_db_path):
        """Create an EmbeddingsManager instance with mocked model."""
        with patch('embeddings_manager.HAS_SENTENCE_TRANSFORMERS', False):
            manager = EmbeddingsManager()
            return manager
    
    def test_init_creates_tables(self, manager, mock_db_path):
        """Test that initialization creates the embeddings table."""
        import sqlite3
        conn = sqlite3.connect(mock_db_path)
        cursor = conn.cursor()
        
        # Check table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='prompt_embeddings'
        """)
        assert cursor.fetchone() is not None
        conn.close()
    
    def test_fallback_embedding(self, manager):
        """Test fallback embedding generation when sentence-transformers unavailable."""
        text = "Test prompt content"
        embedding = manager.generate_embedding(text)
        
        assert isinstance(embedding, list)
        assert len(embedding) == 384  # Expected dimension
        assert all(isinstance(x, float) for x in embedding)
        assert all(-0.5 <= x <= 0.5 for x in embedding)
    
    def test_store_and_retrieve_embedding(self, manager):
        """Test storing and retrieving embeddings."""
        prompt_id = "test_prompt"
        prompt_type = "default"
        embedding = [0.1, 0.2, 0.3] * 128  # 384 dimensions
        content_hash = "test_hash"
        
        # Store embedding
        manager.store_embedding(prompt_id, prompt_type, embedding, content_hash)
        
        # Retrieve embedding
        retrieved = manager.get_embedding(prompt_id, prompt_type)
        assert retrieved == embedding
    
    def test_cosine_similarity(self, manager):
        """Test cosine similarity calculation."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        vec3 = [0.0, 1.0, 0.0]
        vec4 = [-1.0, 0.0, 0.0]
        
        # Same vectors = 1.0
        assert abs(manager.cosine_similarity(vec1, vec2) - 1.0) < 0.001
        
        # Orthogonal vectors = 0.0
        assert abs(manager.cosine_similarity(vec1, vec3)) < 0.001
        
        # Opposite vectors = -1.0
        assert abs(manager.cosine_similarity(vec1, vec4) - (-1.0)) < 0.001
    
    def test_auto_indexing_on_first_search(self, manager, mock_db_path):
        """Test that find_similar triggers auto-indexing on first use."""
        # Mock the default prompts
        with patch('embeddings_manager.default_prompts', {
            'test_prompt': 'path/to/test.md'
        }):
            with patch('embeddings_manager.get_default_prompt') as mock_get:
                mock_get.return_value = {
                    'content': 'Test content',
                    'name': 'test_prompt'
                }
                
                # First search should trigger indexing
                query_embedding = [0.1] * 384
                results = manager.find_similar(query_embedding)
                
                # Verify indexing happened
                assert manager._auto_indexed
                
                # Check embedding was stored
                import sqlite3
                conn = sqlite3.connect(mock_db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM prompt_embeddings")
                count = cursor.fetchone()[0]
                assert count > 0
                conn.close()


class TestSearchPrompts:
    """Test the search_prompts tool."""
    
    @pytest.fixture
    def mock_manager(self):
        """Mock the embeddings manager."""
        with patch('embeddings_manager.get_embeddings_manager') as mock_get:
            manager = Mock()
            manager.generate_embedding.return_value = [0.1] * 384
            manager.find_similar.return_value = [
                {'prompt_id': 'safe_coding', 'prompt_type': 'default', 'similarity': 0.85},
                {'prompt_id': 'testing_strategy', 'prompt_type': 'default', 'similarity': 0.72}
            ]
            mock_get.return_value = manager
            yield manager
    
    def test_search_prompts_success(self, mock_manager):
        """Test successful prompt search."""
        with patch('embeddings_manager.get_prompt') as mock_get_prompt:
            mock_get_prompt.side_effect = [
                {
                    'content': '<!-- type:principle -->\nSafe coding practices...',
                    'type': 'principle',
                    'tokens': 100
                },
                {
                    'content': '<!-- type:principle -->\nTesting best practices...',
                    'type': 'principle', 
                    'tokens': 150
                }
            ]
            
            result = search_prompts("secure coding practices", top_k=5, min_similarity=0.3)
            
            assert result['query'] == "secure coding practices"
            assert len(result['results']) == 2
            assert result['results'][0]['name'] == 'safe_coding'
            assert result['results'][0]['similarity'] == 0.85
            assert 'suggested_principles' in result
            assert 'tip' in result
    
    def test_search_prompts_no_results(self, mock_manager):
        """Test search with no similar prompts found."""
        mock_manager.find_similar.return_value = []
        
        result = search_prompts("completely unrelated query")
        
        assert result['results'] == []
        assert 'No similar prompts found' in result['message']
    
    def test_search_prompts_embedding_failure(self, mock_manager):
        """Test search when embedding generation fails."""
        mock_manager.generate_embedding.return_value = None
        
        result = search_prompts("test query")
        
        assert 'error' in result
        assert 'fallback' in result


class TestDiscoverPrompts:
    """Test the discover_prompts tool."""
    
    @patch('embeddings_manager.search_prompts')
    def test_discover_prompts_mixed_results(self, mock_search):
        """Test discovery with both principles and workflows."""
        mock_search.return_value = {
            'results': [
                {
                    'name': 'quality_axioms',
                    'similarity': 0.8,
                    'type': 'principle',
                    'description': 'Quality best practices for robust code'
                },
                {
                    'name': 'update_docs',
                    'similarity': 0.75,
                    'type': 'workflow',
                    'description': 'Update documentation after changes'
                },
                {
                    'name': 'safe_coding',
                    'similarity': 0.6,
                    'type': 'principle',
                    'description': 'Security practices'
                }
            ]
        }
        
        result = discover_prompts("update documentation with quality standards")
        
        assert len(result['recommended_principles']) == 2
        assert len(result['recommended_workflows']) == 1
        assert result['recommended_principles'][0]['name'] == 'quality_axioms'
        assert result['recommended_workflows'][0]['name'] == 'update_docs'
        assert 'command' in result
        assert 'insight' in result
    
    @patch('embeddings_manager.search_prompts')
    def test_discover_prompts_no_workflows(self, mock_search):
        """Test discovery with only principles found."""
        mock_search.return_value = {
            'results': [
                {
                    'name': 'quality_axioms',
                    'similarity': 0.8,
                    'type': 'principle',
                    'description': 'Quality best practices'
                }
            ]
        }
        
        result = discover_prompts("code quality")
        
        assert len(result['recommended_principles']) == 1
        assert len(result['recommended_workflows']) == 0
        assert 'You might want to create a workflow' in result['insight']


class TestComposeSmart:
    """Test the compose_smart tool."""
    
    @patch('embeddings_manager.discover_prompts')
    @patch('embeddings_manager.compose_prompts')
    def test_compose_smart_success(self, mock_compose, mock_discover):
        """Test smart composition with principles and workflows."""
        mock_discover.return_value = {
            'recommended_principles': [
                {'name': 'quality_axioms', 'relevance': 0.85, 'why': 'Quality...'},
                {'name': 'safe_coding', 'relevance': 0.7, 'why': 'Security...'}
            ],
            'recommended_workflows': [
                {'name': 'update_docs', 'relevance': 0.8, 'what': 'Documentation...'}
            ]
        }
        
        mock_compose.return_value = {
            'content': 'Combined prompt content...',
            'tokens': 500,
            'sources': []
        }
        
        result = compose_smart(
            "update documentation with security considerations",
            max_tokens=1000,
            include_principles=True,
            include_workflows=True
        )
        
        assert 'smart_metadata' in result
        assert result['smart_metadata']['task'] == "update documentation with security considerations"
        assert len(result['smart_metadata']['selected_components']['principles']) == 2
        assert len(result['smart_metadata']['selected_components']['workflows']) == 1
        assert 'usage_tip' in result
        assert result['smart_metadata']['average_relevance'] > 0.7
    
    @patch('embeddings_manager.discover_prompts')
    def test_compose_smart_no_relevant_prompts(self, mock_discover):
        """Test smart composition when no relevant prompts found."""
        mock_discover.return_value = {
            'recommended_principles': [],
            'recommended_workflows': []
        }
        
        result = compose_smart("completely unrelated task")
        
        assert 'error' in result
        assert result['task'] == "completely unrelated task"
        assert 'suggestion' in result
    
    @patch('embeddings_manager.discover_prompts')
    @patch('embeddings_manager.compose_prompts')
    def test_compose_smart_principles_only(self, mock_compose, mock_discover):
        """Test smart composition with principles only."""
        mock_discover.return_value = {
            'recommended_principles': [
                {'name': 'quality_axioms', 'relevance': 0.9, 'why': 'Quality...'}
            ],
            'recommended_workflows': []
        }
        
        mock_compose.return_value = {
            'content': 'Principles content...',
            'tokens': 300,
            'sources': []
        }
        
        result = compose_smart("establish coding standards", include_workflows=False)
        
        assert len(result['smart_metadata']['selected_components']['principles']) == 1
        assert len(result['smart_metadata']['selected_components']['workflows']) == 0
        assert 'Consider your specific implementation' in result['usage_tip']


class TestHelperFunctions:
    """Test helper functions."""
    
    def test_extract_description(self):
        """Test description extraction from prompt content."""
        content = """<!-- id:test emoji:🧪 -->
# Test Prompt

This is a test prompt for unit testing.
It has multiple lines of content.
"""
        
        description = _extract_description(content)
        assert description == "This is a test prompt for unit testing."
        
        # Test with long content
        long_content = "# Header\n\n" + "x" * 200
        description = _extract_description(long_content, max_length=50)
        assert description.endswith("...")
        assert len(description) == 53  # 50 + "..."
        
        # Test with no content
        empty_content = "# Header\n<!--comment-->\n"
        description = _extract_description(empty_content)
        assert description == "No description available"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])