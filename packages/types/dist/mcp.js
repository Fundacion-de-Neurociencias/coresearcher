import { z } from 'zod';
// === MCP Protocol Types ===
export const MCPVersion = z.literal('2025-03-26');
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
//# sourceMappingURL=mcp.js.map