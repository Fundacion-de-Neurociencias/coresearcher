import { z } from 'zod';
import { DomainPackManifest, UniversalNodeLabel, UniversalRelationshipType } from './scientific-core.js';
import { MCPAgent } from './mcp.js';

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

export type DomainPack = z.infer<typeof DomainPack>;

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

export type Capability = z.infer<typeof Capability>;

export const CapabilityRegistration = z.object({
  capability: Capability,
  packId: z.string(),
  workflowIds: z.array(z.string()),
  agentIds: z.array(z.string()),
  priority: z.number().int().min(0).max(100).default(50),
  config: z.record(z.unknown()).optional(),
});

export type CapabilityRegistration = z.infer<typeof CapabilityRegistration>;

// === Cross-Pack Dependency Engine ===

export const PackDependency = z.object({
  packId: z.string(),
  dependsOn: z.array(z.string()),
  optionalDependencies: z.array(z.string()).optional(),
});

export type PackDependency = z.infer<typeof PackDependency>;

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

export type DependencyGraph = z.infer<typeof DependencyGraph>;

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

export type ProvenanceFlowStep = z.infer<typeof ProvenanceFlowStep>;

export const ProvenanceFlow = z.object({
  id: z.string().uuid(),
  projectId: z.string().uuid().optional(),
  steps: z.array(ProvenanceFlowStep),
  currentStep: z.string(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime().optional(),
});

export type ProvenanceFlow = z.infer<typeof ProvenanceFlow>;

// === Research Project Container ===

export const ModelConfig = z.object({
  id: z.string(),
  purpose: z.string(), // critique, ranking, extraction, etc.
  model: z.string(), // e.g., claude, gpt, qwen
  provider: z.string().optional(), // anthropic, openai, local
});

export type ModelConfig = z.infer<typeof ModelConfig>;

export const ProjectWorkflow = z.object({
  id: z.string(),
  packId: z.string(),
  config: z.record(z.unknown()).optional(),
});

export type ProjectWorkflow = z.infer<typeof ProjectWorkflow>;

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

export type ResearchProject = z.infer<typeof ResearchProject>;

// === Registry Interfaces ===

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