import type { MCPAgent } from '@coresearcher/types/mcp';
import { ProvenanceEngine } from '@coresearcher/provenance';
/**
 * AutoScientist Agent
 * Orchestrates long-running research cycles with persistent memory,
 * agent forums, and autonomous investigation capabilities.
 */
export declare class AutoScientistAgent {
    private provenance;
    private researchCycles;
    private knowledgeBase;
    constructor(provenance?: ProvenanceEngine);
    /**
     * Start a new autonomous research cycle
     */
    startResearchCycle(params: {
        goal: string;
        context?: string;
        maxSteps?: number;
        tags?: string[];
    }): Promise<{
        cycleId: string;
        plan: string[];
        estimatedDuration: string;
    }>;
    /**
     * Store knowledge in persistent memory
     */
    storeKnowledge(params: {
        key: string;
        value: unknown;
        confidence: number;
        source?: string;
    }): void;
    /**
     * Retrieve knowledge from persistent memory
     */
    retrieveKnowledge(key: string): {
        value: unknown;
        confidence: number;
        timestamp: string;
    } | null;
    /**
     * Search knowledge base by semantic similarity (keyword-based for now)
     */
    searchKnowledge(query: string): Array<{
        key: string;
        value: unknown;
        confidence: number;
        relevance: number;
    }>;
    /**
     * Get research cycle status
     */
    getCycleStatus(cycleId: string): {
        status: string;
        hypothesesGenerated: number;
        experimentsCompleted: number;
        findingsMade: number;
        lastActive: string;
    } | null;
    getMCPRegistration(): MCPAgent;
}
//# sourceMappingURL=index.d.ts.map