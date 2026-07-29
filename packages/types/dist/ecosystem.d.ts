import { z } from 'zod';
export declare const DomainPack: z.ZodObject<{
    id: z.ZodString;
    name: z.ZodString;
    version: z.ZodString;
    entities: z.ZodArray<z.ZodObject<{
        type: z.ZodString;
        label: z.ZodString;
        description: z.ZodOptional<z.ZodString>;
        properties: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodString>>;
    }, "strip", z.ZodTypeAny, {
        type: string;
        label: string;
        description?: string | undefined;
        properties?: Record<string, string> | undefined;
    }, {
        type: string;
        label: string;
        description?: string | undefined;
        properties?: Record<string, string> | undefined;
    }>, "many">;
    relationships: z.ZodArray<z.ZodObject<{
        type: z.ZodString;
        from: z.ZodString;
        to: z.ZodString;
        description: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        type: string;
        from: string;
        to: string;
        description?: string | undefined;
    }, {
        type: string;
        from: string;
        to: string;
        description?: string | undefined;
    }>, "many">;
    workflows: z.ZodArray<z.ZodObject<{
        id: z.ZodString;
        name: z.ZodString;
        description: z.ZodOptional<z.ZodString>;
        entrypoint: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        id: string;
        name: string;
        entrypoint: string;
        description?: string | undefined;
    }, {
        id: string;
        name: string;
        entrypoint: string;
        description?: string | undefined;
    }>, "many">;
    connectors: z.ZodOptional<z.ZodArray<z.ZodObject<{
        id: z.ZodString;
        name: z.ZodString;
        type: z.ZodEnum<["api", "database", "tool", "mcp"]>;
        config: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodUnknown>>;
    }, "strip", z.ZodTypeAny, {
        id: string;
        type: "api" | "database" | "tool" | "mcp";
        name: string;
        config?: Record<string, unknown> | undefined;
    }, {
        id: string;
        type: "api" | "database" | "tool" | "mcp";
        name: string;
        config?: Record<string, unknown> | undefined;
    }>, "many">>;
    prompts: z.ZodArray<z.ZodObject<{
        id: z.ZodString;
        name: z.ZodString;
        description: z.ZodOptional<z.ZodString>;
        template: z.ZodString;
        variables: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
    }, "strip", z.ZodTypeAny, {
        id: string;
        name: string;
        template: string;
        description?: string | undefined;
        variables?: string[] | undefined;
    }, {
        id: string;
        name: string;
        template: string;
        description?: string | undefined;
        variables?: string[] | undefined;
    }>, "many">;
    extends: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    id: string;
    name: string;
    version: string;
    entities: {
        type: string;
        label: string;
        description?: string | undefined;
        properties?: Record<string, string> | undefined;
    }[];
    relationships: {
        type: string;
        from: string;
        to: string;
        description?: string | undefined;
    }[];
    workflows: {
        id: string;
        name: string;
        entrypoint: string;
        description?: string | undefined;
    }[];
    prompts: {
        id: string;
        name: string;
        template: string;
        description?: string | undefined;
        variables?: string[] | undefined;
    }[];
    connectors?: {
        id: string;
        type: "api" | "database" | "tool" | "mcp";
        name: string;
        config?: Record<string, unknown> | undefined;
    }[] | undefined;
    extends?: string | undefined;
}, {
    id: string;
    name: string;
    version: string;
    entities: {
        type: string;
        label: string;
        description?: string | undefined;
        properties?: Record<string, string> | undefined;
    }[];
    relationships: {
        type: string;
        from: string;
        to: string;
        description?: string | undefined;
    }[];
    workflows: {
        id: string;
        name: string;
        entrypoint: string;
        description?: string | undefined;
    }[];
    prompts: {
        id: string;
        name: string;
        template: string;
        description?: string | undefined;
        variables?: string[] | undefined;
    }[];
    connectors?: {
        id: string;
        type: "api" | "database" | "tool" | "mcp";
        name: string;
        config?: Record<string, unknown> | undefined;
    }[] | undefined;
    extends?: string | undefined;
}>;
export type DomainPack = z.infer<typeof DomainPack>;
export declare const Capability: z.ZodEnum<["Discovery", "LiteratureReview", "GrantWriting", "ClinicalEvidence", "DrugDiscovery", "BiomarkerDiscovery", "GenomicsAnalysis", "ProteinAnalysis", "RegulatoryAnalysis"]>;
export type Capability = z.infer<typeof Capability>;
export declare const CapabilityRegistration: z.ZodObject<{
    capability: z.ZodEnum<["Discovery", "LiteratureReview", "GrantWriting", "ClinicalEvidence", "DrugDiscovery", "BiomarkerDiscovery", "GenomicsAnalysis", "ProteinAnalysis", "RegulatoryAnalysis"]>;
    packId: z.ZodString;
    workflowIds: z.ZodArray<z.ZodString, "many">;
    agentIds: z.ZodArray<z.ZodString, "many">;
    priority: z.ZodDefault<z.ZodNumber>;
    config: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodUnknown>>;
}, "strip", z.ZodTypeAny, {
    capability: "Discovery" | "LiteratureReview" | "GrantWriting" | "ClinicalEvidence" | "DrugDiscovery" | "BiomarkerDiscovery" | "GenomicsAnalysis" | "ProteinAnalysis" | "RegulatoryAnalysis";
    packId: string;
    workflowIds: string[];
    agentIds: string[];
    priority: number;
    config?: Record<string, unknown> | undefined;
}, {
    capability: "Discovery" | "LiteratureReview" | "GrantWriting" | "ClinicalEvidence" | "DrugDiscovery" | "BiomarkerDiscovery" | "GenomicsAnalysis" | "ProteinAnalysis" | "RegulatoryAnalysis";
    packId: string;
    workflowIds: string[];
    agentIds: string[];
    config?: Record<string, unknown> | undefined;
    priority?: number | undefined;
}>;
export type CapabilityRegistration = z.infer<typeof CapabilityRegistration>;
export declare const PackDependency: z.ZodObject<{
    packId: z.ZodString;
    dependsOn: z.ZodArray<z.ZodString, "many">;
    optionalDependencies: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
}, "strip", z.ZodTypeAny, {
    packId: string;
    dependsOn: string[];
    optionalDependencies?: string[] | undefined;
}, {
    packId: string;
    dependsOn: string[];
    optionalDependencies?: string[] | undefined;
}>;
export type PackDependency = z.infer<typeof PackDependency>;
export declare const DependencyGraph: z.ZodObject<{
    nodes: z.ZodArray<z.ZodString, "many">;
    edges: z.ZodArray<z.ZodObject<{
        from: z.ZodString;
        to: z.ZodString;
        type: z.ZodEnum<["requires", "extends", "recommends"]>;
    }, "strip", z.ZodTypeAny, {
        type: "extends" | "requires" | "recommends";
        from: string;
        to: string;
    }, {
        type: "extends" | "requires" | "recommends";
        from: string;
        to: string;
    }>, "many">;
    resolved: z.ZodDefault<z.ZodBoolean>;
}, "strip", z.ZodTypeAny, {
    nodes: string[];
    edges: {
        type: "extends" | "requires" | "recommends";
        from: string;
        to: string;
    }[];
    resolved: boolean;
}, {
    nodes: string[];
    edges: {
        type: "extends" | "requires" | "recommends";
        from: string;
        to: string;
    }[];
    resolved?: boolean | undefined;
}>;
export type DependencyGraph = z.infer<typeof DependencyGraph>;
export declare const ProvenanceFlowStep: z.ZodObject<{
    step: z.ZodEnum<["paper", "claim", "evidence", "hypothesis", "critic_review", "tournament_rank", "grant_section"]>;
    artifactId: z.ZodString;
    timestamp: z.ZodString;
    model: z.ZodOptional<z.ZodString>;
    confidence: z.ZodOptional<z.ZodNumber>;
    evidenceScore: z.ZodOptional<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    step: "paper" | "claim" | "evidence" | "hypothesis" | "critic_review" | "tournament_rank" | "grant_section";
    artifactId: string;
    timestamp: string;
    confidence?: number | undefined;
    model?: string | undefined;
    evidenceScore?: number | undefined;
}, {
    step: "paper" | "claim" | "evidence" | "hypothesis" | "critic_review" | "tournament_rank" | "grant_section";
    artifactId: string;
    timestamp: string;
    confidence?: number | undefined;
    model?: string | undefined;
    evidenceScore?: number | undefined;
}>;
export type ProvenanceFlowStep = z.infer<typeof ProvenanceFlowStep>;
export declare const ProvenanceFlow: z.ZodObject<{
    id: z.ZodString;
    projectId: z.ZodOptional<z.ZodString>;
    steps: z.ZodArray<z.ZodObject<{
        step: z.ZodEnum<["paper", "claim", "evidence", "hypothesis", "critic_review", "tournament_rank", "grant_section"]>;
        artifactId: z.ZodString;
        timestamp: z.ZodString;
        model: z.ZodOptional<z.ZodString>;
        confidence: z.ZodOptional<z.ZodNumber>;
        evidenceScore: z.ZodOptional<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        step: "paper" | "claim" | "evidence" | "hypothesis" | "critic_review" | "tournament_rank" | "grant_section";
        artifactId: string;
        timestamp: string;
        confidence?: number | undefined;
        model?: string | undefined;
        evidenceScore?: number | undefined;
    }, {
        step: "paper" | "claim" | "evidence" | "hypothesis" | "critic_review" | "tournament_rank" | "grant_section";
        artifactId: string;
        timestamp: string;
        confidence?: number | undefined;
        model?: string | undefined;
        evidenceScore?: number | undefined;
    }>, "many">;
    currentStep: z.ZodString;
    createdAt: z.ZodString;
    updatedAt: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    id: string;
    createdAt: string;
    steps: {
        step: "paper" | "claim" | "evidence" | "hypothesis" | "critic_review" | "tournament_rank" | "grant_section";
        artifactId: string;
        timestamp: string;
        confidence?: number | undefined;
        model?: string | undefined;
        evidenceScore?: number | undefined;
    }[];
    currentStep: string;
    updatedAt?: string | undefined;
    projectId?: string | undefined;
}, {
    id: string;
    createdAt: string;
    steps: {
        step: "paper" | "claim" | "evidence" | "hypothesis" | "critic_review" | "tournament_rank" | "grant_section";
        artifactId: string;
        timestamp: string;
        confidence?: number | undefined;
        model?: string | undefined;
        evidenceScore?: number | undefined;
    }[];
    currentStep: string;
    updatedAt?: string | undefined;
    projectId?: string | undefined;
}>;
export type ProvenanceFlow = z.infer<typeof ProvenanceFlow>;
export declare const ModelConfig: z.ZodObject<{
    id: z.ZodString;
    purpose: z.ZodString;
    model: z.ZodString;
    provider: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    id: string;
    model: string;
    purpose: string;
    provider?: string | undefined;
}, {
    id: string;
    model: string;
    purpose: string;
    provider?: string | undefined;
}>;
export type ModelConfig = z.infer<typeof ModelConfig>;
export declare const ProjectWorkflow: z.ZodObject<{
    id: z.ZodString;
    packId: z.ZodString;
    config: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodUnknown>>;
}, "strip", z.ZodTypeAny, {
    id: string;
    packId: string;
    config?: Record<string, unknown> | undefined;
}, {
    id: string;
    packId: string;
    config?: Record<string, unknown> | undefined;
}>;
export type ProjectWorkflow = z.infer<typeof ProjectWorkflow>;
export declare const ResearchProject: z.ZodObject<{
    name: z.ZodString;
    description: z.ZodOptional<z.ZodString>;
    packs: z.ZodArray<z.ZodString, "many">;
    workflows: z.ZodArray<z.ZodObject<{
        id: z.ZodString;
        packId: z.ZodString;
        config: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodUnknown>>;
    }, "strip", z.ZodTypeAny, {
        id: string;
        packId: string;
        config?: Record<string, unknown> | undefined;
    }, {
        id: string;
        packId: string;
        config?: Record<string, unknown> | undefined;
    }>, "many">;
    models: z.ZodArray<z.ZodObject<{
        id: z.ZodString;
        purpose: z.ZodString;
        model: z.ZodString;
        provider: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        id: string;
        model: string;
        purpose: string;
        provider?: string | undefined;
    }, {
        id: string;
        model: string;
        purpose: string;
        provider?: string | undefined;
    }>, "many">;
    createdAt: z.ZodOptional<z.ZodString>;
    updatedAt: z.ZodOptional<z.ZodString>;
    status: z.ZodDefault<z.ZodEnum<["created", "running", "completed", "archived"]>>;
}, "strip", z.ZodTypeAny, {
    status: "created" | "running" | "completed" | "archived";
    name: string;
    workflows: {
        id: string;
        packId: string;
        config?: Record<string, unknown> | undefined;
    }[];
    packs: string[];
    models: {
        id: string;
        model: string;
        purpose: string;
        provider?: string | undefined;
    }[];
    createdAt?: string | undefined;
    updatedAt?: string | undefined;
    description?: string | undefined;
}, {
    name: string;
    workflows: {
        id: string;
        packId: string;
        config?: Record<string, unknown> | undefined;
    }[];
    packs: string[];
    models: {
        id: string;
        model: string;
        purpose: string;
        provider?: string | undefined;
    }[];
    status?: "created" | "running" | "completed" | "archived" | undefined;
    createdAt?: string | undefined;
    updatedAt?: string | undefined;
    description?: string | undefined;
}>;
export type ResearchProject = z.infer<typeof ResearchProject>;
export interface DomainPackRegistryInterface {
    register(pack: DomainPack): void;
    unregister(packId: string): void;
    get(packId: string): DomainPack | undefined;
    list(): DomainPack[];
    listByCapability(capability: Capability): DomainPack[];
    resolveDependencies(packId: string): DomainPack[];
}
export interface CapabilityRegistryInterface {
    register(registration: CapabilityRegistration): void;
    unregister(capability: Capability, packId: string): void;
    get(capability: Capability): CapabilityRegistration[];
    list(): Capability[];
    getBestPack(capability: Capability): string | undefined;
}
export interface DependencyEngineInterface {
    addDependency(packId: string, dependsOn: string[]): void;
    resolve(): DependencyGraph;
    getTransitiveDependencies(packId: string): string[];
    validate(): boolean;
}
//# sourceMappingURL=ecosystem.d.ts.map