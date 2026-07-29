import type { Artifact, ArtifactType, Execution, Experiment, ProvenanceRecord, ProvenanceSource, ProvenanceQuery } from '@coresearcher/types';
export declare class ProvenanceEngine {
    private records;
    private executions;
    private experiments;
    private artifacts;
    constructor();
    registerArtifact(params: {
        type: ArtifactType;
        name: string;
        content: string;
        createdBy: string;
        description?: string;
        sources?: ProvenanceSource[];
        parentId?: string;
        tags?: string[];
        version?: string;
    }): Artifact;
    trackExecution(params: {
        agentId: string;
        action: string;
        input: Record<string, unknown>;
        output: Record<string, unknown>;
        modelUsed?: string;
        promptsUsed?: string[];
        toolsUsed?: string[];
        codeExecuted?: string[];
        datasetsUsed?: string[];
        sources?: ProvenanceSource[];
        artifacts?: string[];
        tags?: string[];
    }): Execution;
    createExperiment(params: {
        name: string;
        description: string;
        hypothesis?: string;
        design: Record<string, unknown>;
        variables?: Record<string, unknown>;
        tags?: string[];
    }): Experiment;
    linkExecutionToExperiment(executionId: string, experimentId: string): void;
    getProvenanceLineage(artifactId: string): ProvenanceRecord[];
    queryProvenance(query: ProvenanceQuery): ProvenanceRecord[];
    getArtifact(id: string): Artifact | undefined;
    getExecution(id: string): Execution | undefined;
    getExperiment(id: string): Experiment | undefined;
    listExperiments(): Experiment[];
    getExperimentExecutions(experimentId: string): Execution[];
    generateReport(artifactId: string): string;
    private createProvenanceRecord;
    private buildLineage;
    private hashContent;
}
//# sourceMappingURL=engine.d.ts.map