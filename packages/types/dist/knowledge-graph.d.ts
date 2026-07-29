import { z } from 'zod';
export declare const NodeLabel: z.ZodEnum<["Paper", "Author", "Institution", "Concept", "Claim", "Hypothesis", "Experiment", "Dataset", "Method", "Tool", "Code", "Figure", "Table"]>;
export type NodeLabel = z.infer<typeof NodeLabel>;
export declare const RelationshipType: z.ZodEnum<["CITES", "SUPPORTS", "CONTRADICTS", "DERIVES_FROM", "TESTS", "AUTHORED_BY", "AFFILIATED_WITH", "MENTIONS", "USES", "PRODUCES", "REFERENCES", "BUILDS_UPON", "VALIDATES", "INVALIDATES"]>;
export type RelationshipType = z.infer<typeof RelationshipType>;
export declare const PaperNode: z.ZodObject<{
    id: z.ZodString;
    title: z.ZodString;
    abstract: z.ZodOptional<z.ZodString>;
    doi: z.ZodOptional<z.ZodString>;
    pmid: z.ZodOptional<z.ZodString>;
    arxivId: z.ZodOptional<z.ZodString>;
    year: z.ZodOptional<z.ZodNumber>;
    journal: z.ZodOptional<z.ZodString>;
    volume: z.ZodOptional<z.ZodString>;
    issue: z.ZodOptional<z.ZodString>;
    pages: z.ZodOptional<z.ZodString>;
    url: z.ZodOptional<z.ZodString>;
    pdfUrl: z.ZodOptional<z.ZodString>;
    citations: z.ZodOptional<z.ZodNumber>;
    keywords: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    fields: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    language: z.ZodDefault<z.ZodString>;
    processedAt: z.ZodString;
    embedding: z.ZodOptional<z.ZodArray<z.ZodNumber, "many">>;
}, "strip", z.ZodTypeAny, {
    id: string;
    title: string;
    keywords: string[];
    fields: string[];
    language: string;
    processedAt: string;
    doi?: string | undefined;
    pmid?: string | undefined;
    journal?: string | undefined;
    year?: number | undefined;
    abstract?: string | undefined;
    arxivId?: string | undefined;
    volume?: string | undefined;
    issue?: string | undefined;
    pages?: string | undefined;
    url?: string | undefined;
    pdfUrl?: string | undefined;
    citations?: number | undefined;
    embedding?: number[] | undefined;
}, {
    id: string;
    title: string;
    processedAt: string;
    doi?: string | undefined;
    pmid?: string | undefined;
    journal?: string | undefined;
    year?: number | undefined;
    abstract?: string | undefined;
    arxivId?: string | undefined;
    volume?: string | undefined;
    issue?: string | undefined;
    pages?: string | undefined;
    url?: string | undefined;
    pdfUrl?: string | undefined;
    citations?: number | undefined;
    keywords?: string[] | undefined;
    fields?: string[] | undefined;
    language?: string | undefined;
    embedding?: number[] | undefined;
}>;
export type PaperNode = z.infer<typeof PaperNode>;
export declare const AuthorNode: z.ZodObject<{
    id: z.ZodString;
    name: z.ZodString;
    orcid: z.ZodOptional<z.ZodString>;
    email: z.ZodOptional<z.ZodString>;
    hIndex: z.ZodOptional<z.ZodNumber>;
    affiliations: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    fields: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    paperCount: z.ZodOptional<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    id: string;
    name: string;
    fields: string[];
    affiliations: string[];
    orcid?: string | undefined;
    email?: string | undefined;
    hIndex?: number | undefined;
    paperCount?: number | undefined;
}, {
    id: string;
    name: string;
    fields?: string[] | undefined;
    orcid?: string | undefined;
    email?: string | undefined;
    hIndex?: number | undefined;
    affiliations?: string[] | undefined;
    paperCount?: number | undefined;
}>;
export type AuthorNode = z.infer<typeof AuthorNode>;
export declare const InstitutionNode: z.ZodObject<{
    id: z.ZodString;
    name: z.ZodString;
    ror: z.ZodOptional<z.ZodString>;
    country: z.ZodOptional<z.ZodString>;
    type: z.ZodOptional<z.ZodEnum<["university", "research_center", "hospital", "company", "other"]>>;
    fields: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
}, "strip", z.ZodTypeAny, {
    id: string;
    name: string;
    fields: string[];
    type?: "university" | "research_center" | "hospital" | "company" | "other" | undefined;
    ror?: string | undefined;
    country?: string | undefined;
}, {
    id: string;
    name: string;
    type?: "university" | "research_center" | "hospital" | "company" | "other" | undefined;
    fields?: string[] | undefined;
    ror?: string | undefined;
    country?: string | undefined;
}>;
export type InstitutionNode = z.infer<typeof InstitutionNode>;
export declare const ConceptNode: z.ZodObject<{
    id: z.ZodString;
    name: z.ZodString;
    description: z.ZodOptional<z.ZodString>;
    ontology: z.ZodOptional<z.ZodString>;
    ontologyId: z.ZodOptional<z.ZodString>;
    synonyms: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    category: z.ZodOptional<z.ZodString>;
    embedding: z.ZodOptional<z.ZodArray<z.ZodNumber, "many">>;
}, "strip", z.ZodTypeAny, {
    id: string;
    name: string;
    synonyms: string[];
    description?: string | undefined;
    embedding?: number[] | undefined;
    ontology?: string | undefined;
    ontologyId?: string | undefined;
    category?: string | undefined;
}, {
    id: string;
    name: string;
    description?: string | undefined;
    embedding?: number[] | undefined;
    ontology?: string | undefined;
    ontologyId?: string | undefined;
    synonyms?: string[] | undefined;
    category?: string | undefined;
}>;
export type ConceptNode = z.infer<typeof ConceptNode>;
export declare const ClaimNode: z.ZodObject<{
    id: z.ZodString;
    text: z.ZodString;
    confidence: z.ZodDefault<z.ZodNumber>;
    evidence: z.ZodOptional<z.ZodString>;
    evidenceType: z.ZodOptional<z.ZodEnum<["statistical", "experimental", "observational", "theoretical", "computational"]>>;
    status: z.ZodDefault<z.ZodEnum<["proposed", "supported", "contradicted", "unverified", "accepted", "rejected"]>>;
    extractedFrom: z.ZodOptional<z.ZodString>;
    extractionMethod: z.ZodOptional<z.ZodString>;
    tags: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    embedding: z.ZodOptional<z.ZodArray<z.ZodNumber, "many">>;
}, "strip", z.ZodTypeAny, {
    status: "proposed" | "supported" | "contradicted" | "unverified" | "accepted" | "rejected";
    id: string;
    tags: string[];
    text: string;
    confidence: number;
    embedding?: number[] | undefined;
    evidence?: string | undefined;
    evidenceType?: "statistical" | "experimental" | "observational" | "theoretical" | "computational" | undefined;
    extractedFrom?: string | undefined;
    extractionMethod?: string | undefined;
}, {
    id: string;
    text: string;
    status?: "proposed" | "supported" | "contradicted" | "unverified" | "accepted" | "rejected" | undefined;
    tags?: string[] | undefined;
    embedding?: number[] | undefined;
    confidence?: number | undefined;
    evidence?: string | undefined;
    evidenceType?: "statistical" | "experimental" | "observational" | "theoretical" | "computational" | undefined;
    extractedFrom?: string | undefined;
    extractionMethod?: string | undefined;
}>;
export type ClaimNode = z.infer<typeof ClaimNode>;
export declare const HypothesisNode: z.ZodObject<{
    id: z.ZodString;
    text: z.ZodString;
    status: z.ZodDefault<z.ZodEnum<["formulated", "testing", "supported", "contradicted", "refined", "abandoned"]>>;
    confidence: z.ZodDefault<z.ZodNumber>;
    generatedBy: z.ZodOptional<z.ZodString>;
    testedBy: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    tags: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
}, "strip", z.ZodTypeAny, {
    status: "supported" | "contradicted" | "formulated" | "testing" | "refined" | "abandoned";
    id: string;
    tags: string[];
    text: string;
    confidence: number;
    testedBy: string[];
    generatedBy?: string | undefined;
}, {
    id: string;
    text: string;
    status?: "supported" | "contradicted" | "formulated" | "testing" | "refined" | "abandoned" | undefined;
    tags?: string[] | undefined;
    confidence?: number | undefined;
    generatedBy?: string | undefined;
    testedBy?: string[] | undefined;
}>;
export type HypothesisNode = z.infer<typeof HypothesisNode>;
export declare const ExperimentNode: z.ZodObject<{
    id: z.ZodString;
    name: z.ZodString;
    description: z.ZodString;
    design: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodUnknown>>;
    results: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodUnknown>>;
    conclusion: z.ZodOptional<z.ZodString>;
    status: z.ZodDefault<z.ZodEnum<["designed", "running", "completed", "failed", "replicated", "invalidated"]>>;
    reproducibility: z.ZodOptional<z.ZodNumber>;
    tags: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
}, "strip", z.ZodTypeAny, {
    status: "running" | "completed" | "failed" | "designed" | "replicated" | "invalidated";
    id: string;
    name: string;
    description: string;
    tags: string[];
    design?: Record<string, unknown> | undefined;
    results?: Record<string, unknown> | undefined;
    conclusion?: string | undefined;
    reproducibility?: number | undefined;
}, {
    id: string;
    name: string;
    description: string;
    status?: "running" | "completed" | "failed" | "designed" | "replicated" | "invalidated" | undefined;
    tags?: string[] | undefined;
    design?: Record<string, unknown> | undefined;
    results?: Record<string, unknown> | undefined;
    conclusion?: string | undefined;
    reproducibility?: number | undefined;
}>;
export type ExperimentNode = z.infer<typeof ExperimentNode>;
export declare const CitationRelation: z.ZodObject<{
    type: z.ZodLiteral<"CITES">;
    context: z.ZodOptional<z.ZodString>;
    citationCount: z.ZodOptional<z.ZodNumber>;
    citationIntent: z.ZodOptional<z.ZodEnum<["supports", "contradicts", "discusses", "extends", "reviews"]>>;
}, "strip", z.ZodTypeAny, {
    type: "CITES";
    context?: string | undefined;
    citationCount?: number | undefined;
    citationIntent?: "supports" | "contradicts" | "discusses" | "extends" | "reviews" | undefined;
}, {
    type: "CITES";
    context?: string | undefined;
    citationCount?: number | undefined;
    citationIntent?: "supports" | "contradicts" | "discusses" | "extends" | "reviews" | undefined;
}>;
export type CitationRelation = z.infer<typeof CitationRelation>;
export declare const SupportRelation: z.ZodObject<{
    type: z.ZodLiteral<"SUPPORTS">;
    strength: z.ZodDefault<z.ZodNumber>;
    evidence: z.ZodOptional<z.ZodString>;
    method: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    type: "SUPPORTS";
    strength: number;
    method?: string | undefined;
    evidence?: string | undefined;
}, {
    type: "SUPPORTS";
    method?: string | undefined;
    evidence?: string | undefined;
    strength?: number | undefined;
}>;
export type SupportRelation = z.infer<typeof SupportRelation>;
export declare const ContradictionRelation: z.ZodObject<{
    type: z.ZodLiteral<"CONTRADICTS">;
    strength: z.ZodDefault<z.ZodNumber>;
    evidence: z.ZodOptional<z.ZodString>;
    resolved: z.ZodDefault<z.ZodBoolean>;
}, "strip", z.ZodTypeAny, {
    type: "CONTRADICTS";
    strength: number;
    resolved: boolean;
    evidence?: string | undefined;
}, {
    type: "CONTRADICTS";
    evidence?: string | undefined;
    strength?: number | undefined;
    resolved?: boolean | undefined;
}>;
export type ContradictionRelation = z.infer<typeof ContradictionRelation>;
export declare const GraphQuery: z.ZodObject<{
    nodes: z.ZodOptional<z.ZodArray<z.ZodObject<{
        label: z.ZodEnum<["Paper", "Author", "Institution", "Concept", "Claim", "Hypothesis", "Experiment", "Dataset", "Method", "Tool", "Code", "Figure", "Table"]>;
        properties: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodUnknown>>;
    }, "strip", z.ZodTypeAny, {
        label: "Paper" | "Author" | "Institution" | "Concept" | "Claim" | "Hypothesis" | "Experiment" | "Dataset" | "Method" | "Tool" | "Code" | "Figure" | "Table";
        properties?: Record<string, unknown> | undefined;
    }, {
        label: "Paper" | "Author" | "Institution" | "Concept" | "Claim" | "Hypothesis" | "Experiment" | "Dataset" | "Method" | "Tool" | "Code" | "Figure" | "Table";
        properties?: Record<string, unknown> | undefined;
    }>, "many">>;
    relationships: z.ZodOptional<z.ZodArray<z.ZodObject<{
        type: z.ZodEnum<["CITES", "SUPPORTS", "CONTRADICTS", "DERIVES_FROM", "TESTS", "AUTHORED_BY", "AFFILIATED_WITH", "MENTIONS", "USES", "PRODUCES", "REFERENCES", "BUILDS_UPON", "VALIDATES", "INVALIDATES"]>;
        direction: z.ZodDefault<z.ZodEnum<["outgoing", "incoming", "both"]>>;
    }, "strip", z.ZodTypeAny, {
        type: "CITES" | "SUPPORTS" | "CONTRADICTS" | "DERIVES_FROM" | "TESTS" | "AUTHORED_BY" | "AFFILIATED_WITH" | "MENTIONS" | "USES" | "PRODUCES" | "REFERENCES" | "BUILDS_UPON" | "VALIDATES" | "INVALIDATES";
        direction: "outgoing" | "incoming" | "both";
    }, {
        type: "CITES" | "SUPPORTS" | "CONTRADICTS" | "DERIVES_FROM" | "TESTS" | "AUTHORED_BY" | "AFFILIATED_WITH" | "MENTIONS" | "USES" | "PRODUCES" | "REFERENCES" | "BUILDS_UPON" | "VALIDATES" | "INVALIDATES";
        direction?: "outgoing" | "incoming" | "both" | undefined;
    }>, "many">>;
    limit: z.ZodDefault<z.ZodNumber>;
    offset: z.ZodDefault<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    limit: number;
    offset: number;
    nodes?: {
        label: "Paper" | "Author" | "Institution" | "Concept" | "Claim" | "Hypothesis" | "Experiment" | "Dataset" | "Method" | "Tool" | "Code" | "Figure" | "Table";
        properties?: Record<string, unknown> | undefined;
    }[] | undefined;
    relationships?: {
        type: "CITES" | "SUPPORTS" | "CONTRADICTS" | "DERIVES_FROM" | "TESTS" | "AUTHORED_BY" | "AFFILIATED_WITH" | "MENTIONS" | "USES" | "PRODUCES" | "REFERENCES" | "BUILDS_UPON" | "VALIDATES" | "INVALIDATES";
        direction: "outgoing" | "incoming" | "both";
    }[] | undefined;
}, {
    limit?: number | undefined;
    offset?: number | undefined;
    nodes?: {
        label: "Paper" | "Author" | "Institution" | "Concept" | "Claim" | "Hypothesis" | "Experiment" | "Dataset" | "Method" | "Tool" | "Code" | "Figure" | "Table";
        properties?: Record<string, unknown> | undefined;
    }[] | undefined;
    relationships?: {
        type: "CITES" | "SUPPORTS" | "CONTRADICTS" | "DERIVES_FROM" | "TESTS" | "AUTHORED_BY" | "AFFILIATED_WITH" | "MENTIONS" | "USES" | "PRODUCES" | "REFERENCES" | "BUILDS_UPON" | "VALIDATES" | "INVALIDATES";
        direction?: "outgoing" | "incoming" | "both" | undefined;
    }[] | undefined;
}>;
export type GraphQuery = z.infer<typeof GraphQuery>;
export declare const GraphPath: z.ZodObject<{
    startNode: z.ZodString;
    endNode: z.ZodString;
    maxDepth: z.ZodDefault<z.ZodNumber>;
    relationshipTypes: z.ZodOptional<z.ZodArray<z.ZodEnum<["CITES", "SUPPORTS", "CONTRADICTS", "DERIVES_FROM", "TESTS", "AUTHORED_BY", "AFFILIATED_WITH", "MENTIONS", "USES", "PRODUCES", "REFERENCES", "BUILDS_UPON", "VALIDATES", "INVALIDATES"]>, "many">>;
}, "strip", z.ZodTypeAny, {
    startNode: string;
    endNode: string;
    maxDepth: number;
    relationshipTypes?: ("CITES" | "SUPPORTS" | "CONTRADICTS" | "DERIVES_FROM" | "TESTS" | "AUTHORED_BY" | "AFFILIATED_WITH" | "MENTIONS" | "USES" | "PRODUCES" | "REFERENCES" | "BUILDS_UPON" | "VALIDATES" | "INVALIDATES")[] | undefined;
}, {
    startNode: string;
    endNode: string;
    maxDepth?: number | undefined;
    relationshipTypes?: ("CITES" | "SUPPORTS" | "CONTRADICTS" | "DERIVES_FROM" | "TESTS" | "AUTHORED_BY" | "AFFILIATED_WITH" | "MENTIONS" | "USES" | "PRODUCES" | "REFERENCES" | "BUILDS_UPON" | "VALIDATES" | "INVALIDATES")[] | undefined;
}>;
export type GraphPath = z.infer<typeof GraphPath>;
//# sourceMappingURL=knowledge-graph.d.ts.map