import { z } from 'zod';

// =============================================================================
// Scientific Core Schema (SKOS Foundation)
// Universal primitives for any scientific domain
// =============================================================================

// === Universal Node Labels ===
export const UniversalNodeLabel = z.enum([
  'Paper',
  'Author',
  'Institution',
  'Concept',
  'Entity',           // Universal scientific entity (Gene, Protein are domain packs)
  'Claim',
  'Evidence',         // Universal evidence
  'Hypothesis',
  'Experiment',
  'Dataset',
  'Method',
  'Tool',
  'Code',
  'Figure',
  'Table',
  'Result',
  'Analysis',
  'Manuscript',
]);

export type UniversalNodeLabel = z.infer<typeof UniversalNodeLabel>;

// === Universal Relationship Types ===
export const UniversalRelationshipType = z.enum([
  // Paper → Knowledge
  'PRODUCES',         // Paper → Claim
  'MENTIONS',         // Paper → Entity/Concept
  
  // Knowledge relationships
  'SUPPORTED_BY',     // Claim → Evidence
  'CONTRADICTS',      // Claim → Claim
  'DERIVES_FROM',     // Claim → Claim
  'TESTS',            // Experiment/Hypothesis → Claim
  
  // Citation relationships
  'CITES',
  'REFERENCES',
  'BUILDS_UPON',
  
  // Validation
  'VALIDATES',
  'INVALIDATES',
  
  // Entity relationships
  'RELATED_TO',
  'ASSOCIATED_WITH',
  
  // Authorship
  'AUTHORED_BY',
  'AFFILIATED_WITH',
  
  // Lineage (knowledge evolution)
  'UPDATED_BY',       // Claim → Claim
]);

export type UniversalRelationshipType = z.infer<typeof UniversalRelationshipType>;

// === Universal Evidence Types ===
export const EvidenceType = z.enum([
  'statistical',
  'experimental',
  'observational',
  'theoretical',
  'computational',
  'meta_analysis',
  'systematic_review',
  'clinical_trial',
  'animal_study',
  'in_vitro',
]);

export type EvidenceType = z.infer<typeof EvidenceType>;

// === Universal Evidence Node (all scientific fields) ===
export const EvidenceNode = z.object({
  id: z.string(),
  value: z.string(),
  evidenceType: EvidenceType.optional(),
  qualityScore: z.number().min(0).max(1).default(0.5),
  sampleSize: z.number().int().optional(),
  pValue: z.number().optional(),
  effectSize: z.number().optional(),
  followupMonths: z.number().optional(),
  hasStatisticalEvidence: z.boolean().default(false),
  extractedFrom: z.string().optional(),
});

export type EvidenceNode = z.infer<typeof EvidenceNode>;

// === Universal Entity Node ===
export const EntityNode = z.object({
  id: z.string(),
  name: z.string(),
  canonicalName: z.string().optional(),
  entityType: z.string(),  // Domain pack defines specific types (Gene, Protein, etc)
  aliases: z.array(z.string()).default([]),
  domain: z.string().optional(),
  confidence: z.number().min(0).max(1).default(0.8),
});

export type EntityNode = z.infer<typeof EntityNode>;

// === Universal Claim Node ===
export const UniversalClaimNode = z.object({
  id: z.string(),
  text: z.string(),
  confidence: z.number().min(0).max(1).default(0.5),
  domain: z.string().optional(),  // e.g., "neurodegeneration", "oncology"
  claimType: z.string().optional(), // Domain pack defines: "biomarker", "mechanism", etc
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime().optional(),
  evidenceCount: z.number().int().default(0),
  supportCount: z.number().int().default(0),
  contradictionCount: z.number().int().default(0),
  extractedFrom: z.string().optional(),
  extractionMethod: z.string().optional(),
  tags: z.array(z.string()).default([]),
});

export type UniversalClaimNode = z.infer<typeof UniversalClaimNode>;

// === Domain Pack Contract ===
export const DomainPackManifest = z.object({
  id: z.string(),
  name: z.string(),
  version: z.string(),
  nodeTypes: z.array(z.string()),
  relationshipTypes: z.array(z.string()),
  entityResolvers: z.record(z.string()),
  evidenceWeights: z.record(z.number()).optional(),
  queries: z.array(z.string()).optional(),
});

export type DomainPackManifest = z.infer<typeof DomainPackManifest>;

// All types are already exported inline above
