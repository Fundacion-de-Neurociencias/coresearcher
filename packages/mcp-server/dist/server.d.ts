import { EventEmitter } from 'events';
import type { MCPAgent, MCPTool, MCPResource, MCPRequest, MCPResponse, MCPServerConfig } from '@coresearcher/types';
export declare class MCPServer extends EventEmitter {
    private agents;
    private config;
    private initialized;
    constructor(config?: Partial<MCPServerConfig>);
    registerAgent(agent: MCPAgent): void;
    unregisterAgent(agentId: string): boolean;
    getAgent(agentId: string): MCPAgent | undefined;
    listAgents(): MCPAgent[];
    getTools(): Array<{
        agentId: string;
        tool: MCPTool;
    }>;
    getResources(): Array<{
        agentId: string;
        resource: MCPResource;
    }>;
    handleRequest(request: MCPRequest): Promise<MCPResponse>;
    private handleInitialize;
    private handleShutdown;
    private handleToolsList;
    private handleToolCall;
    private handleResourcesList;
    private handleResourceRead;
    private handlePromptsList;
    private handlePromptGet;
    private createResponse;
    private createError;
    getConfig(): MCPServerConfig;
    isInitialized(): boolean;
}
//# sourceMappingURL=server.d.ts.map