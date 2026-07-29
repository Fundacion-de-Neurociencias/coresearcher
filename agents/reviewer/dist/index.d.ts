import type { MCPAgent } from '@coresearcher/types/mcp';
import { ProvenanceEngine } from '@coresearcher/provenance';
/**
 * Scientific Reviewer Agent
 * Validates citations, DOIs, PMIDs, statistical results, and marks confidence levels.
 * No final responses allowed without review.
 */
export declare class ReviewerAgent {
    private provenance;
    private confidenceThresholds;
    constructor(provenance?: ProvenanceEngine);
    /**
     * Validate a DOI (Digital Object Identifier)
     */
    validateDOI(doi: string): Promise<{
        valid: boolean;
        confidence: number;
        metadata?: Record<string, unknown>;
        errors?: string[];
    }>;
    /**
     * Validate a PMID (PubMed Identifier)
     */
    validatePMID(pmid: string): Promise<{
        valid: boolean;
        confidence: number;
        metadata?: Record<string, unknown>;
        errors?: string[];
    }>;
    /**
     * Validate a citation (automatic DOI detection + validation)
     */
    validateCitation(citation: string): Promise<{
        validated: boolean;
        confidence: number;
        doi?: string;
        pmid?: string;
        details: string[];
        warnings: string[];
    }>;
    /**
     * Check if content needs review
     */
    needsReview(content: string): {
        needs: boolean;
        reason: string;
    };
    /**
     * Generate a review report for a piece of scientific content
     */
    review(params: {
        content: string;
        citations: string[];
        statisticalResults?: Array<{
            type: string;
            value: string;
        }>;
    }): Promise<{
        reviewed: boolean;
        overallConfidence: number;
        citationResults: Array<{
            citation: string;
            validated: boolean;
            confidence: number;
            errors: string[];
        }>;
        warnings: string[];
        suggestions: string[];
    }>;
    /**
     * Register this agent with the MCP server
     */
    getMCPRegistration(): MCPAgent;
}
//# sourceMappingURL=index.d.ts.map