import { z } from 'zod';

// === MCP Protocol Types ===

export const MCPVersion = z.literal('2025-03-26');
export type MCPVersion = z.infer<typeof MCPVersion>;

export const MCPMethod = z.enum([
  'initialize',
  'shutdown',
  'ping',
  'resources/list',
  'resources/read',
  'tools/list',
  'tools/call',
  'prompts/list',
  'prompts/get',
  'notifications/initialized',
  'notifications/cancelled',
  'notifications/progress',
  'notifications/resources/list_changed',
  'notifications/tools/list_changed',
]);

export type MCPMethod = z.infer<typeof MCPMethod>;

// === JSON-RPC Message ===

export interface MCPRequest {
  jsonrpc: '2.0';
  id: string | number;
  method: MCPMethod;
  params?: Record<string, unknown>;
}

export interface MCPResponse {
  jsonrpc: '2.0';
  id: string | number | null;
  result?: unknown;
  error?: {
    code: number;
    message: string;
    data?: unknown;
  };
}

// === Tool Definition ===

export interface MCPToolInputSchema {
  type: 'object';
  properties?: Record<string, unknown>;
  required?: string[];
}

export interface MCPTool {
  name: string;
  description?: string;
  inputSchema: MCPToolInputSchema;
  handler?: (args: Record<string, unknown>) => Promise<unknown> | unknown;
}

export interface MCPResource {
  uri: string;
  name: string;
  description?: string;
  mimeType?: string;
  handler?: (params: Record<string, unknown>) => Promise<unknown> | unknown;
}

export interface MCPPrompt {
  name: string;
  description?: string;
  arguments?: Array<{
    name: string;
    description?: string;
    required?: boolean;
  }>;
}

export interface MCPAgentCapabilities {
  tools: MCPTool[];
  resources: MCPResource[];
  prompts: MCPPrompt[];
}

export interface MCPAgent {
  id: string;
  name: string;
  description: string;
  version: string;
  capabilities: MCPAgentCapabilities;
  metadata?: Record<string, unknown>;
}

export interface MCPServerConfig {
  name: string;
  version: string;
  agents?: MCPAgent[];
  transport: 'stdio' | 'sse' | 'websocket';
  port?: number;
  host?: string;
}