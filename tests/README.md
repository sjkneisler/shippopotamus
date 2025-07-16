# Shippopotamus Test Suite

This directory contains comprehensive tests for all Shippopotamus MCP tools.

## Test Structure

### Test Files

- **`test_prompt_ops.py`** - Core prompt operations
  - Registry functionality (save, load, get)
  - Batch loading
  - Prompt composition
  - Utility functions
  - Bootstrap session
  - Edge cases and error handling

- **`test_embeddings_manager.py`** - Semantic search and discovery
  - Embeddings generation
  - Similarity search
  - Prompt discovery
  - Smart composition
  - Auto-indexing

- **`test_mcp_integration.py`** - MCP tool integration
  - Tool registration
  - MCP bridge functionality
  - Integration between tools
  - Error handling across tools
  - Token management

### Fixtures (in `conftest.py`)

- `temp_workspace` - Temporary directory for test isolation
- `initialized_db` - Database setup
- `sample_prompts` - Pre-created test prompts
- `mock_embeddings_model` - Mocked ML model for consistent tests
- `prompt_files` - Temporary prompt files
- `mock_default_prompts` - Mocked default prompt mappings

## Running Tests

### Basic Usage

```bash
# Run all tests
python -m pytest tests/

# Run with verbose output
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_prompt_ops.py

# Run specific test
python -m pytest tests/test_prompt_ops.py::TestPromptRegistry::test_save_and_get_custom_prompt
```

### Using the Test Script

```bash
# Run all tests
./scripts/test.sh

# Run with coverage
./scripts/test.sh --coverage

# Run specific test file
./scripts/test.sh -t test_embeddings_manager.py

# Run tests with specific marker
./scripts/test.sh -m unit
```

### Coverage Reports

```bash
# Generate coverage report
pytest --cov=tools --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Test Categories (Markers)

Tests are categorized with markers for selective execution:

- `@pytest.mark.unit` - Unit tests for individual functions
- `@pytest.mark.integration` - Integration tests for tool interactions
- `@pytest.mark.mcp` - Tests specific to MCP tool registration
- `@pytest.mark.slow` - Tests that take longer to run
- `@pytest.mark.requires_model` - Tests requiring ML models

Run tests by marker:
```bash
pytest -m unit          # Only unit tests
pytest -m "not slow"    # Skip slow tests
```

## CI/CD Integration

Tests run automatically on:
- Push to main/develop branches
- Pull requests to main
- Multiple Python versions (3.8-3.11)
- Coverage reports uploaded to Codecov

See `.github/workflows/test.yml` for CI configuration.

## Writing New Tests

### Test Structure Template

```python
class TestNewFeature:
    """Test description"""
    
    def setup_method(self):
        """Setup for each test"""
        # Use fixtures or manual setup
    
    @pytest.mark.unit
    def test_specific_behavior(self, initialized_db):
        """Test specific behavior"""
        # Arrange
        # Act
        # Assert
    
    def test_error_handling(self):
        """Test error scenarios"""
        # Test expected failures
```

### Best Practices

1. **Isolation**: Each test should be independent
2. **Fixtures**: Use fixtures for common setup
3. **Mocking**: Mock external dependencies
4. **Coverage**: Aim for >80% code coverage
5. **Edge Cases**: Test boundaries and error conditions
6. **Documentation**: Clear test names and docstrings

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're in the project root
2. **Database Errors**: Tests create temp databases automatically
3. **Model Dependencies**: Tests mock ML models by default
4. **File Paths**: Tests use temporary directories for isolation

### Debug Mode

Run tests with debugging:
```bash
pytest -vv --tb=short  # Verbose with short traceback
pytest --pdb          # Drop into debugger on failure
```

## Test Coverage Goals

Current coverage targets:
- Overall: >80%
- Core tools: >90%
- Error handling: 100%
- Integration points: >75%

Missing coverage areas are tracked in test files with TODO comments.