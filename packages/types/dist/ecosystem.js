import { z } from 'zod';
// =============================================================================
// Sprint 6: Ecosystem Architecture Layer
// =============================================================================
// === Domain Pack Registry ===
export const DomainPack = z.object({
    id: z.string(),
    name: z.string(),
    version: z.string(),
    // Domain entities and relationships
    entities: z.array(z.object({
        type: z.string(),
        label: z.string(),
        description: z.string().optional(),
        properties: z.record(z.string()).optional(),
    })),
    relationships: z.array(z.object({
        type: z.string(),
        from: z.string(),
        to: z.string(),
        description: z.string().optional(),
    })),
    // Workflows provided by this pack
    workflows: z.array(z.object({
        id: z.string(),
        name: z.string(),
        description: z.string().optional(),
        entrypoint: z.string(),
    })),
    // Connectors for external integrations
    connectors: z.array(z.object({
        id: z.string(),
        name: z.string(),
        type: z.enum(['api', 'database', 'tool', 'mcp']),
        config: z.record(z.unknown()).optional(),
    })).optional(),
    // Prompts provided by this pack
    prompts: z.array(z.object({
        id: z.string(),
        name: z.string(),
        description: z.string().optional(),
        template: z.string(),
        variables: z.array(z.string()).optional(),
    })),
    // Optional: extends another pack
    extends: z.string().optional(),
});
// === Capability Registry ===
export const Capability = z.enum([
    'Discovery',
    'LiteratureReview',
    'GrantWriting',
    'ClinicalEvidence',
    'DrugDiscovery',
    'BiomarkerDiscovery',
    'GenomicsAnalysis',
    'ProteinAnalysis',
    'RegulatoryAnalysis',
]);
export const CapabilityRegistration = z.object({
    capability: Capability,
    packId: z.string(),
    workflowIds: z.array(z.string()),
    agentIds: z.array(z.string()),
    priority: z.number().int().min(0).max(100).default(50),
    config: z.record(z.unknown()).optional(),
});
// === Cross-Pack Dependency Engine ===
export const PackDependency = z.object({
    packId: z.string(),
    dependsOn: z.array(z.string()),
    optionalDependencies: z.array(z.string()).optional(),
});
// Dependency graph for the ecosystem
export const DependencyGraph = z.object({
    nodes: z.array(z.string()),
    edges: z.array(z.object({
        from: z.string(),
        to: z.string(),
        type: z.enum(['requires', 'extends', 'recommends']),
    })),
    resolved: z.boolean().default(false),
});
// === Provenance Dashboard Types ===
export const ProvenanceFlowStep = z.object({
    step: z.enum([
        'paper',
        'claim',
        'evidence',
        'hypothesis',
        'critic_review',
        'tournament_rank',
        'grant_section'
    ]),
    artifactId: z.string().uuid(),
    timestamp: z.string().datetime(),
    model: z.string().optional(),
    confidence: z.number().min(0).max(1).optional(),
    evidenceScore: z.number().min(0).max(1).optional(),
});
export const ProvenanceFlow = z.object({
    id: z.string().uuid(),
    projectId: z.string().uuid().optional(),
    steps: z.array(ProvenanceFlowStep),
    currentStep: z.string(),
    createdAt: z.string().datetime(),
    updatedAt: z.string().datetime().optional(),
});
// === Research Project Container ===
export const ModelConfig = z.object({
    id: z.string(),
    purpose: z.string(), // critique, ranking, extraction, etc.
    model: z.string(), // e.g., claude, gpt, qwen
    provider: z.string().optional(), // anthropic, openai, local
});
export const ProjectWorkflow = z.object({
    id: z.string(),
    packId: z.string(),
    config: z.record(z.unknown()).optional(),
});
export const ResearchProject = z.object({
    name: z.string(),
    description: z.string().optional(),
    packs: z.array(z.string()),
    workflows: z.array(ProjectWorkflow),
    models: z.array(ModelConfig),
    createdAt: z.string().datetime().optional(),
    updatedAt: z.string().datetime().optional(),
    status: z.enum(['created', 'running', 'completed', 'archived']).default('created'),
});
//# sourceMappingURL=ecosystem.js.map