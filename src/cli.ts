#!/usr/bin/env node
import { fileURLToPath } from 'url';
import path from 'path';

// Simple CLI that starts the MCP server
console.log('🚢🦛 Shippopotamus MCP Server');
console.log('Starting prompt management tools...\n');

// Import and run the server
import('./index.js').catch(console.error);