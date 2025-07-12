#!/bin/bash
# Publishing script for Shippopotamus

echo "🚢🦛 Preparing to publish Shippopotamus..."

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Run from project root."
    exit 1
fi

# Clean and rebuild
echo "🧹 Cleaning old build..."
rm -rf dist/

echo "📦 Installing dependencies..."
npm install

echo "🔨 Building TypeScript..."
npm run build

echo "🧪 Running Python tests..."
npm test

if [ $? -ne 0 ]; then
    echo "❌ Tests failed! Fix before publishing."
    exit 1
fi

echo "✅ All checks passed!"
echo ""
echo "To publish to npm:"
echo "  1. Make sure you're logged in: npm login"
echo "  2. Run: npm publish"
echo ""
echo "For local testing:"
echo "  1. Run: npm link"
echo "  2. In another project: npm link shippopotamus"