import { z } from 'zod';
// === Neo4j Knowledge Graph Schema ===
// === Node Labels ===
export const NodeLabel = z.enum([
    'Paper',
    'Author',
    'Institution',
    'Concept',
    'Claim',
    'Hypothesis',
    'Experiment',
    'Dataset',
    'Method',
    'Tool',
    'Code',
    'Figure',
    'Table',
]);
// === Relationship Types ===
export const RelationshipType = z.enum([
    'CITES',
    'SUPPORTS',
    'CONTRADICTS',
    'DERIVES_FROM',
    'TESTS',
    'AUTHORED_BY',
    'AFFILIATED_WITH',
    'MENTIONS',
    'USES',
    'PRODUCES',
    'REFERENCES',
    'BUILDS_UPON',
    'VALIDATES',
    'INVALIDATES',
]);
// === Node Properties ===
export const PaperNode = z.object({
    id: z.string(),
    title: z.string(),
    abstract: z.string().optional(),
    doi: z.string().optional(),
    pmid: z.string().optional(),
    arxivId: z.string().optional(),
    year: z.number().int().optional(),
    journal: z.string().optional(),
    volume: z.string().optional(),
    issue: z.string().optional(),
    pages: z.string().optional(),
    url: z.string().url().optional(),
    pdfUrl: z.string().url().optional(),
    citations: z.number().int().optional(),
    keywords: z.array(z.string()).default([]),
    fields: z.array(z.string()).default([]),
    language: z.string().default('en'),
    processedAt: z.string().datetime(),
    embedding: z.array(z.number()).optional(),
});
export const AuthorNode = z.object({
    id: z.string(),
    name: z.string(),
    orcid: z.string().optional(),
    email: z.string().optional(),
    hIndex: z.number().int().optional(),
    affiliations: z.array(z.string()).default([]),
    fields: z.array(z.string()).default([]),
    paperCount: z.number().int().optional(),
});
export const InstitutionNode = z.object({
    id: z.string(),
    name: z.string(),
    ror: z.string().optional(),
    country: z.string().optional(),
    type: z.enum(['university', 'research_center', 'hospital', 'company', 'other']).optional(),
    fields: z.array(z.string()).default([]),
});
export const ConceptNode = z.object({
    id: z.string(),
    name: z.string(),
    description: z.string().optional(),
    ontology: z.string().optional(),
    ontologyId: z.string().optional(),
    synonyms: z.array(z.string()).default([]),
    category: z.string().optional(),
    embedding: z.array(z.number()).optional(),
});
export const ClaimNode = z.object({
    id: z.string(),
    text: z.string(),
    confidence: z.number().min(0).max(1).default(0.5),
    evidence: z.string().optional(),
    evidenceType: z.enum(['statistical', 'experimental', 'observational', 'theoretical', 'computational']).optional(),
    status: z.enum(['proposed', 'supported', 'contradicted', 'unverified', 'accepted', 'rejected']).default('proposed'),
    extractedFrom: z.string().optional(),
    extractionMethod: z.string().optional(),
    tags: z.array(z.string()).default([]),
    embedding: z.array(z.number()).optional(),
});
export const HypothesisNode = z.object({
    id: z.string(),
    text: z.string(),
    status: z.enum(['formulated', 'testing', 'supported', 'contradicted', 'refined', 'abandoned']).default('formulated'),
    confidence: z.number().min(0).max(1).default(0.3),
    generatedBy: z.string().optional(),
    testedBy: z.array(z.string()).default([]),
    tags: z.array(z.string()).default([]),
});
export const ExperimentNode = z.object({
    id: z.string(),
    name: z.string(),
    description: z.string(),
    design: z.record(z.unknown()).optional(),
    results: z.record(z.unknown()).optional(),
    conclusion: z.string().optional(),
    status: z.enum(['designed', 'running', 'completed', 'failed', 'replicated', 'invalidated']).default('designed'),
    reproducibility: z.number().min(0).max(1).optional(),
    tags: z.array(z.string()).default([]),
});
// === Relationship Properties ===
export const CitationRelation = z.object({
    type: z.literal('CITES'),
    context: z.string().optional(),
    citationCount: z.number().int().optional(),
    citationIntent: z.enum(['supports', 'contradicts', 'discusses', 'extends', 'reviews']).optional(),
});
export const SupportRelation = z.object({
    type: z.literal('SUPPORTS'),
    strength: z.number().min(0).max(1).default(0.5),
    evidence: z.string().optional(),
    method: z.string().optional(),
});
export const ContradictionRelation = z.object({
    type: z.literal('CONTRADICTS'),
    strength: z.number().min(0).max(1).default(0.5),
    evidence: z.string().optional(),
    resolved: z.boolean().default(false),
});
// === Graph Query Types ===
export const GraphQuery = z.object({
    nodes: z.array(z.object({
        label: NodeLabel,
        properties: z.record(z.unknown()).optional(),
    })).optional(),
    relationships: z.array(z.object({
        type: RelationshipType,
        direction: z.enum(['outgoing', 'incoming', 'both']).default('outgoing'),
    })).optional(),
    limit: z.number().int().positive().default(100),
    offset: z.number().int().min(0).default(0),
});
export const GraphPath = z.object({
    startNode: z.string(),
    endNode: z.string(),
    maxDepth: z.number().int().positive().default(3),
    relationshipTypes: z.array(RelationshipType).optional(),
});
//# sourceMappingURL=knowledge-graph.js.map