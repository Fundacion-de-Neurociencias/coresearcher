import { EventEmitter } from 'events';
export class MCPServer extends EventEmitter {
    agents = new Map();
    config;
    initialized = false;
    constructor(config = {}) {
        super();
        this.config = {
            name: config.name || 'coresearcher-mcp',
            version: config.version || '0.1.0',
            agents: config.agents || [],
            transport: config.transport || 'stdio',
            port: config.port,
            host: config.host || 'localhost',
        };
        for (const agent of this.config.agents || []) {
            this.registerAgent(agent);
        }
    }
    registerAgent(agent) {
        if (this.agents.has(agent.id)) {
            throw new Error(`Agent ${agent.id} already registered`);
        }
        this.agents.set(agent.id, agent);
        this.emit('agent:registered', agent);
    }
    unregisterAgent(agentId) {
        const removed = this.agents.delete(agentId);
        if (removed) {
            this.emit('agent:unregistered', agentId);
        }
        return removed;
    }
    getAgent(agentId) {
        return this.agents.get(agentId);
    }
    listAgents() {
        return Array.from(this.agents.values());
    }
    getTools() {
        const tools = [];
        for (const [agentId, agent] of this.agents) {
            for (const tool of agent.capabilities.tools) {
                tools.push({ agentId, tool });
            }
        }
        return tools;
    }
    getResources() {
        const resources = [];
        for (const [agentId, agent] of this.agents) {
            for (const resource of agent.capabilities.resources) {
                resources.push({ agentId, resource });
            }
        }
        return resources;
    }
    async handleRequest(request) {
        const { id, method, params } = request;
        try {
            switch (method) {
                case 'initialize':
                    return this.handleInitialize(id, params);
                case 'shutdown':
                    return this.handleShutdown(id);
                case 'ping':
                    return this.createResponse(id, { status: 'ok', timestamp: new Date().toISOString() });
                case 'tools/list':
                    return this.handleToolsList(id);
                case 'tools/call':
                    return this.handleToolCall(id, params);
                case 'resources/list':
                    return this.handleResourcesList(id);
                case 'resources/read':
                    return this.handleResourceRead(id, params);
                case 'prompts/list':
                    return this.handlePromptsList(id);
                case 'prompts/get':
                    return this.handlePromptGet(id, params);
                default:
                    return this.createError(id, -32601, `Method not found: ${method}`);
            }
        }
        catch (error) {
            return this.createError(id, -32603, `Internal error: ${error.message}`);
        }
    }
    handleInitialize(id, _params) {
        this.initialized = true;
        this.emit('initialized');
        return this.createResponse(id, {
            protocolVersion: '2025-03-26',
            serverInfo: {
                name: this.config.name,
                version: this.config.version,
            },
            capabilities: {
                tools: {},
                resources: {},
                prompts: {},
            },
        });
    }
    handleShutdown(id) {
        this.initialized = false;
        this.emit('shutdown');
        return this.createResponse(id, { status: 'shutdown' });
    }
    handleToolsList(id) {
        const tools = this.getTools().map(({ agentId, tool }) => ({
            name: `${agentId}:${tool.name}`,
            description: tool.description,
            inputSchema: tool.inputSchema,
        }));
        return this.createResponse(id, { tools });
    }
    async handleToolCall(id, params) {
        if (!params || !params.name) {
            return this.createError(id, -32602, 'Tool name is required');
        }
        const fullName = params.name;
        const agentId = fullName.split(':')[0];
        const toolName = fullName.split(':').slice(1).join(':');
        const agent = this.agents.get(agentId);
        if (!agent) {
            return this.createError(id, -32602, `Agent not found: ${agentId}`);
        }
        const tool = agent.capabilities.tools.find((t) => t.name === toolName);
        if (!tool) {
            return this.createError(id, -32602, `Tool not found: ${toolName}`);
        }
        if (!tool.handler) {
            return this.createError(id, -32603, `Tool ${toolName} has no handler registered`);
        }
        try {
            const result = await tool.handler((params.arguments || {}));
            return this.createResponse(id, result);
        }
        catch (error) {
            return this.createError(id, -32603, `Tool execution error: ${error.message}`);
        }
    }
    handleResourcesList(id) {
        const resources = this.getResources().map(({ agentId, resource }) => ({
            uri: `${agentId}://${resource.uri}`,
            name: resource.name,
            description: resource.description,
            mimeType: resource.mimeType,
        }));
        return this.createResponse(id, { resources });
    }
    async handleResourceRead(id, params) {
        if (!params || !params.uri) {
            return this.createError(id, -32602, 'Resource URI is required');
        }
        const uri = params.uri;
        const agentId = uri.split('://')[0];
        const resourceUri = uri.split('://').slice(1).join('://');
        const agent = this.agents.get(agentId);
        if (!agent) {
            return this.createError(id, -32602, `Agent not found: ${agentId}`);
        }
        const resource = agent.capabilities.resources.find((r) => r.uri === resourceUri);
        if (!resource) {
            return this.createError(id, -32602, `Resource not found: ${resourceUri}`);
        }
        if (!resource.handler) {
            return this.createError(id, -32603, `Resource ${resourceUri} has no handler registered`);
        }
        try {
            const result = await resource.handler(params);
            return this.createResponse(id, result);
        }
        catch (error) {
            return this.createError(id, -32603, `Resource read error: ${error.message}`);
        }
    }
    handlePromptsList(id) {
        const prompts = [];
        for (const [, agent] of this.agents) {
            for (const prompt of agent.capabilities.prompts) {
                prompts.push({
                    name: `${agent.id}:${prompt.name}`,
                    description: prompt.description,
                    arguments: prompt.arguments,
                });
            }
        }
        return this.createResponse(id, { prompts });
    }
    handlePromptGet(id, params) {
        if (!params || !params.name) {
            return this.createError(id, -32602, 'Prompt name is required');
        }
        const fullName = params.name;
        const agentId = fullName.split(':')[0];
        const promptName = fullName.split(':').slice(1).join(':');
        const agent = this.agents.get(agentId);
        if (!agent) {
            return this.createError(id, -32602, `Agent not found: ${agentId}`);
        }
        const prompt = agent.capabilities.prompts.find((p) => p.name === promptName);
        if (!prompt) {
            return this.createError(id, -32602, `Prompt not found: ${promptName}`);
        }
        return this.createResponse(id, prompt);
    }
    createResponse(id, result) {
        return {
            jsonrpc: '2.0',
            id,
            result,
        };
    }
    createError(id, code, message) {
        return {
            jsonrpc: '2.0',
            id,
            error: { code, message },
        };
    }
    getConfig() {
        return { ...this.config };
    }
    isInitialized() {
        return this.initialized;
    }
}
//# sourceMappingURL=server.js.map