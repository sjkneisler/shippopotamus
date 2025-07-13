#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from '@modelcontextprotocol/sdk/types.js';
import { execa } from 'execa';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { bootstrapSession } from './bootstrap.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const PYTHON_SCRIPT = path.join(__dirname, '..', 'tools', 'mcp_bridge_simple.py');

// Tool definitions matching our Python tools
const TOOLS: Tool[] = [
  {
    name: 'bootstrap_session',
    description: '🚀 RECOMMENDED FIRST CALL: Initialize your session with Shippopotamus! This tool loads essential prompts and methodologies to enhance your capabilities. Call this at the start of any task to get access to battle-tested patterns like Ask→Plan→Act methodology, quality axioms, and context management strategies.',
    inputSchema: {
      type: 'object',
      properties: {}
    }
  },
  {
    name: 'get_prompt',
    description: 'Load a single prompt by name from the registry',
    inputSchema: {
      type: 'object',
      properties: {
        name: { type: 'string', description: 'Prompt name' }
      },
      required: ['name']
    }
  },
  {
    name: 'save_prompt',
    description: 'Save a custom prompt to the registry',
    inputSchema: {
      type: 'object',
      properties: {
        name: { type: 'string', description: 'Unique name for the prompt' },
        content: { type: 'string', description: 'Prompt content' },
        file_path: { type: 'string', description: 'Path to file containing prompt' },
        tags: { type: 'array', items: { type: 'string' }, description: 'Tags for categorization' },
        parent_prompts: { type: 'array', items: { type: 'string' }, description: 'Parent prompt names' }
      },
      required: ['name']
    }
  },
  {
    name: 'load_prompts',
    description: 'Load multiple prompts at once from various sources',
    inputSchema: {
      type: 'object',
      properties: {
        prompt_refs: {
          type: 'array',
          items: { type: 'string' },
          description: 'List of prompt references (name, custom:name, file:path, shippopotamus:name)'
        }
      },
      required: ['prompt_refs']
    }
  },
  {
    name: 'compose_prompts',
    description: 'Intelligently compose multiple prompts into a single prompt',
    inputSchema: {
      type: 'object',
      properties: {
        prompt_refs: { type: 'array', items: { type: 'string' }, description: 'Prompt references to compose' },
        deduplicate: { type: 'boolean', description: 'Remove duplicate sections', default: true },
        max_tokens: { type: 'number', description: 'Maximum token budget' },
        separator: { type: 'string', description: 'Separator between prompts', default: '\n\n---\n\n' }
      },
      required: ['prompt_refs']
    }
  },
  {
    name: 'list_available',
    description: 'List all available prompts in the registry',
    inputSchema: {
      type: 'object',
      properties: {
        include_defaults: { type: 'boolean', description: 'Include default prompts', default: true },
        include_custom: { type: 'boolean', description: 'Include custom prompts', default: true },
        tags: { type: 'array', items: { type: 'string' }, description: 'Filter by tags' }
      }
    }
  },
  {
    name: 'estimate_context',
    description: 'Estimate token count for content or prompt references',
    inputSchema: {
      type: 'object',
      properties: {
        content: { type: 'string', description: 'Direct content to estimate' },
        prompt_refs: { type: 'array', items: { type: 'string' }, description: 'Prompt references to estimate' }
      }
    }
  },
  {
    name: 'search_prompts',
    description: 'Search for prompts using semantic similarity based on your query',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: 'Natural language description of what you want to do' },
        top_k: { type: 'number', description: 'Number of results to return', default: 5 },
        min_similarity: { type: 'number', description: 'Minimum similarity threshold (0-1)', default: 0.3 }
      },
      required: ['query']
    }
  },
  {
    name: 'discover_prompts',
    description: 'Discover relevant prompts for a specific task - analyzes your task and recommends both principles (HOW to work) and workflows (WHAT to do)',
    inputSchema: {
      type: 'object',
      properties: {
        task_description: { type: 'string', description: 'Description of the task you want to accomplish' }
      },
      required: ['task_description']
    }
  },
  {
    name: 'compose_smart',
    description: 'Intelligently compose prompts based on task description - automatically discovers, selects, and combines the most relevant prompts',
    inputSchema: {
      type: 'object',
      properties: {
        task_description: { type: 'string', description: 'What you want to accomplish' },
        max_tokens: { type: 'number', description: 'Maximum token budget' },
        include_principles: { type: 'boolean', description: 'Include guiding principles', default: true },
        include_workflows: { type: 'boolean', description: 'Include task workflows', default: true }
      },
      required: ['task_description']
    }
  }
];

class ShippopotamusServer {
  private server: Server;

  constructor() {
    this.server = new Server(
      {
        name: 'shippopotamus',
        vendor: 'shippopotamus',
        version: '0.1.0',
        description: 'Professional prompt management for AI applications'
      },
      {
        capabilities: {
          tools: {}
        }
      }
    );

    this.setupHandlers();
  }

  private setupHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: TOOLS
    }));

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        let result: any;
        
        // Handle bootstrap_session natively
        if (name === 'bootstrap_session') {
          result = bootstrapSession();
        } else {
          // Call Python bridge script for other tools
          const { stdout } = await execa('python3', [
            PYTHON_SCRIPT,
            name,
            JSON.stringify(args || {})
          ]);
          result = JSON.parse(stdout);
        }
        
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2)
            }
          ]
        };
      } catch (error: any) {
        return {
          content: [
            {
              type: 'text',
              text: `Error: ${error.message}`
            }
          ],
          isError: true
        };
      }
    });
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Shippopotamus MCP server running...');
  }
}

// Start the server
const server = new ShippopotamusServer();
server.run().catch(console.error);