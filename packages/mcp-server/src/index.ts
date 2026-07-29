#!/usr/bin/env node

import { MCPServer } from './server.js';

// Read config path from command line args
const configPath = process.argv[2] || './mcp.config.json';

async function startServer() {
  let config: Record<string, unknown> = {};

  try {
    const fs = await import('fs');
    if (fs.existsSync(configPath)) {
      const raw = fs.readFileSync(configPath, 'utf-8');
      config = JSON.parse(raw);
    }
  } catch {
    // No config file, use defaults
  }

  const server = new MCPServer({
    name: (config.name as string) || 'coresearcher-mcp',
    version: (config.version as string) || '0.1.0',
    transport: (config.transport as 'stdio' | 'sse' | 'websocket') || 'stdio',
    port: config.port as number | undefined,
  });

  // Handle stdin/stdout transport
  if (server.getConfig().transport === 'stdio') {
    process.stdin.setEncoding('utf-8');
    let buffer = '';

    process.stdin.on('data', (chunk: string) => {
      buffer += chunk;
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.trim()) {
          try {
            const request = JSON.parse(line);
            server.handleRequest(request).then(response => {
              process.stdout.write(JSON.stringify(response) + '\n');
            });
          } catch (err) {
            const errorResponse = {
              jsonrpc: '2.0',
              id: null,
              error: {
                code: -32700,
                message: 'Parse error',
              },
            };
            process.stdout.write(JSON.stringify(errorResponse) + '\n');
          }
        }
      }
    });

    process.stdin.on('end', () => {
      process.exit(0);
    });
  }

  console.error(`MCP Server "${server.getConfig().name}" v${server.getConfig().version} started`);
  console.error(`Transport: ${server.getConfig().transport}`);
  console.error(`Agents registered: ${server.listAgents().length}`);
}

startServer().catch(err => {
  console.error('Failed to start MCP Server:', err);
  process.exit(1);
});