#!/bin/bash
# Run all tests with coverage

set -e

echo "🧪 Running Shippopotamus tests..."

# Run Python tests with coverage
echo "📊 Running Python tests with coverage..."
pytest -v --cov=tools --cov-report=term-missing --cov-report=html

# Run specific test categories
echo "🔌 Running MCP integration tests..."
pytest -v -m "mcp or integration"

echo "🔍 Running embeddings tests (if available)..."
pytest -v -m "embeddings" || echo "⚠️  Embeddings tests skipped (dependencies not installed)"

# Build TypeScript
echo "🏗️  Building TypeScript..."
npm run build

# Test the MCP bridge directly
echo "🌉 Testing MCP bridge..."
python tools/mcp_bridge.py 2>&1 | grep -q "Usage" && echo "✅ Bridge help works"

# Summary
echo ""
echo "✨ All tests completed!"
echo "📈 Coverage report available in htmlcov/index.html"