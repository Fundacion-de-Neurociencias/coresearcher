import type { MCPAgent } from '@coresearcher/types/mcp';
import { ProvenanceEngine } from '@coresearcher/provenance';
/**
 * Triaxial Classification Model for Neurodiagnoses
 * Axis 1: Clinical Syndrome
 * Axis 2: Etiology/Pathophysiology
 * Axis 3: Functional Impairment
 */
interface TriaxialDiagnosis {
    axis1: {
        syndrome: string;
        code: string;
        confidence: number;
    };
    axis2: {
        etiology: string;
        code: string;
        confidence: number;
    };
    axis3: {
        impairment: string;
        severity: 'mild' | 'moderate' | 'severe';
        code: string;
        confidence: number;
    };
    confidence: number;
    timestamp: string;
}
/**
 * Neurodiagnoses Agent Pack
 * Implements Biomarker, Neurodiagnosis, Trial, and Regulatory agents
 * using the triaxial classification model as the native framework.
 */
export declare class NeurodiagnosesAgent {
    private provenance;
    constructor(provenance?: ProvenanceEngine);
    analyzeBiomarkers(params: {
        biomarkers: Array<{
            name: string;
            value: string;
            unit: string;
            referenceRange: string;
        }>;
        context?: string;
        diagnosis?: string;
    }): Promise<{
        analysis: string;
        significant: Array<{
            biomarker: string;
            direction: string;
            significance: number;
        }>;
        patterns: string[];
        recommendations: string[];
    }>;
    triaxialDiagnosis(params: {
        symptoms: string[];
        biomarkers: Array<{
            name: string;
            value: string;
            unit: string;
            referenceRange: string;
        }>;
        imaging?: string[];
        cognitiveTests?: Array<{
            test: string;
            score: string;
            interpretation: string;
        }>;
        history?: string;
    }): Promise<{
        diagnosis: TriaxialDiagnosis;
        differential: string[];
        recommendedTests: string[];
        confidence: number;
    }>;
    findTrials(params: {
        diagnosis: string;
        biomarkers?: string[];
        stage?: string;
        location?: string;
    }): Promise<{
        trials: Array<{
            id: string;
            title: string;
            phase: string;
            status: string;
            eligibility: string;
            location: string;
            matchScore: number;
        }>;
        totalCount: number;
        topMatches: string[];
    }>;
    checkRegulatoryStatus(params: {
        biomarker: string;
        region: string;
        application?: string;
    }): Promise<{
        status: string;
        approvals: Array<{
            agency: string;
            status: string;
            date?: string;
            indication: string;
        }>;
        guidelines: string[];
        requirements: string[];
    }>;
    private determineClinicalSyndrome;
    private determineEtiology;
    private determineImpairment;
    /**
     * Register this agent with the MCP server
     */
    getMCPRegistration(): MCPAgent;
}
export {};
//# sourceMappingURL=index.d.ts.map