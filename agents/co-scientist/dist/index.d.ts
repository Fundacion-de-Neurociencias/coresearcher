import type { MCPAgent } from '@coresearcher/types/mcp';
import { ProvenanceEngine } from '@coresearcher/provenance';
/**
 * AI Co-Scientist Agent
 * Adapts the open-source AI Co-Scientist architecture to MCP and OpenScience.
 * Generates hypotheses, designs experiments, and collaborates on research.
 */
export declare class CoScientistAgent {
    private provenance;
    private hypotheses;
    constructor(provenance?: ProvenanceEngine);
    /**
     * Generate a new hypothesis based on a research question
     */
    generateHypothesis(params: {
        researchQuestion: string;
        context?: string;
        domain?: string;
        constraints?: string[];
        tags?: string[];
    }): Promise<{
        id: string;
        hypothesis: string;
        confidence: number;
        reasoning: string;
        suggestedExperiments: string[];
    }>;
    /**
     * Design an experiment to test a hypothesis
     */
    designExperiment(params: {
        hypothesisId: string;
        approach?: string;
        variables?: Record<string, unknown>;
        constraints?: string[];
    }): Promise<{
        experimentId: string;
        design: Record<string, unknown>;
        predictedOutcomes: string[];
        requiredResources: string[];
    }>;
    /**
     * Analyze experimental results
     */
    analyzeResults(params: {
        experimentId: string;
        results: Record<string, unknown>;
        hypothesisId: string;
    }): Promise<{
        supportsHypothesis: boolean;
        confidence: number;
        insights: string[];
        recommendations: string[];
    }>;
    /**
     * Get the current research status
     */
    getResearchStatus(): {
        totalHypotheses: number;
        activeHypotheses: number;
        supportedHypotheses: number;
        contradictedHypotheses: number;
        experimentsDesigned: number;
    };
    private structuredHypothesisGeneration;
    /**
     * Register this agent with the MCP server
     */
    getMCPRegistration(): MCPAgent;
}
//# sourceMappingURL=index.d.ts.map