import { ProvenanceEngine } from '@coresearcher/provenance';
/**
 * Scientific Reviewer Agent
 * Validates citations, DOIs, PMIDs, statistical results, and marks confidence levels.
 * No final responses allowed without review.
 */
export class ReviewerAgent {
    provenance;
    confidenceThresholds = {
        high: 0.9,
        medium: 0.7,
        low: 0.5,
    };
    constructor(provenance) {
        this.provenance = provenance || new ProvenanceEngine();
    }
    /**
     * Validate a DOI (Digital Object Identifier)
     */
    async validateDOI(doi) {
        const errors = [];
        // Basic format validation
        const doiPattern = /^10\.\d{4,}\/[\w\-\.;()\/:]+$/i;
        if (!doiPattern.test(doi)) {
            errors.push('Invalid DOI format');
            return { valid: false, confidence: 0, errors };
        }
        // Try to resolve DOI via doi.org
        try {
            const response = await fetch(`https://doi.org/api/handles/${doi}`, {
                method: 'GET',
                headers: { Accept: 'application/json' },
                signal: AbortSignal.timeout(5000),
            });
            if (!response.ok) {
                errors.push(`DOI resolution failed: HTTP ${response.status}`);
                return { valid: false, confidence: 0.3, errors };
            }
            const data = await response.json();
            const metadata = data;
            // Track this validation in provenance
            this.provenance.trackExecution({
                agentId: 'reviewer',
                action: 'validate-doi',
                input: { doi },
                output: { valid: true, metadata },
                modelUsed: 'none',
                toolsUsed: ['doi.org-api'],
            });
            return {
                valid: true,
                confidence: 0.95,
                metadata,
                errors: [],
            };
        }
        catch (error) {
            // If DOI API fails, still accept valid format with lower confidence
            errors.push(`DOI resolution error: ${error.message}`);
            return { valid: true, confidence: 0.6, errors };
        }
    }
    /**
     * Validate a PMID (PubMed Identifier)
     */
    async validatePMID(pmid) {
        const errors = [];
        // Basic format validation
        if (!/^\d+$/.test(pmid)) {
            errors.push('Invalid PMID format: must be numeric');
            return { valid: false, confidence: 0, errors };
        }
        // Try to fetch from PubMed API
        try {
            const response = await fetch(`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=${pmid}&retmode=json`, { signal: AbortSignal.timeout(5000) });
            if (!response.ok) {
                errors.push(`PMID resolution failed: HTTP ${response.status}`);
                return { valid: false, confidence: 0.3, errors };
            }
            const data = await response.json();
            const result = data?.result?.[pmid];
            if (!result) {
                errors.push('PMID not found in PubMed');
                return { valid: false, confidence: 0.2, errors };
            }
            const metadata = {
                title: result.title,
                authors: result.authors?.map((a) => a.name),
                journal: result.source,
                year: result.pubdate,
                uid: pmid,
            };
            this.provenance.trackExecution({
                agentId: 'reviewer',
                action: 'validate-pmid',
                input: { pmid },
                output: { valid: true, metadata },
                toolsUsed: ['pubmed-api'],
            });
            return { valid: true, confidence: 0.95, metadata, errors: [] };
        }
        catch (error) {
            errors.push(`PMID validation error: ${error.message}`);
            return { valid: true, confidence: 0.5, errors };
        }
    }
    /**
     * Validate a citation (automatic DOI detection + validation)
     */
    async validateCitation(citation) {
        const details = [];
        const warnings = [];
        let confidence = 0.5;
        // Extract DOI if present
        const doiMatch = citation.match(/10\.\d{4,}\/[\w\-\.;()\/:]+/i);
        let doiValid = false;
        let pmidValid = false;
        if (doiMatch) {
            const doi = doiMatch[0];
            const result = await this.validateDOI(doi);
            doiValid = result.valid;
            if (result.valid) {
                confidence = Math.max(confidence, result.confidence);
                details.push(`DOI ${doi} validated (confidence: ${result.confidence})`);
            }
            else {
                warnings.push(...(result.errors || []));
            }
        }
        // Extract PMID if present
        const pmidMatch = citation.match(/PMID:\s*(\d+)/i);
        if (pmidMatch) {
            const pmid = pmidMatch[1];
            const result = await this.validatePMID(pmid);
            pmidValid = result.valid;
            if (result.valid) {
                confidence = Math.max(confidence, result.confidence);
                details.push(`PMID ${pmid} validated (confidence: ${result.confidence})`);
            }
            else {
                warnings.push(...(result.errors || []));
            }
        }
        // If no identifier found, do basic validation
        if (!doiMatch && !pmidMatch) {
            warnings.push('No DOI or PMID found in citation text');
            confidence = 0.3;
        }
        return {
            validated: doiValid || pmidValid,
            confidence: Math.min(confidence, 1.0),
            doi: doiMatch?.[0],
            pmid: pmidMatch?.[1],
            details,
            warnings,
        };
    }
    /**
     * Check if content needs review
     */
    needsReview(content) {
        // Check for claims without citations
        const claimPatterns = [
            /we (show|demonstrate|find|prove|conclude)/i,
            /our (results|findings|analysis) (show|suggest|indicate|demonstrate)/i,
            /this (study|work|paper) (shows|demonstrates|proves)/i,
            /significant(ly)? (effect|difference|correlation|increase|decrease)/i,
            /p\s*[<≤]\s*0\.\d+/i,
        ];
        for (const pattern of claimPatterns) {
            if (pattern.test(content)) {
                return { needs: true, reason: 'Contains scientific claims requiring citation validation' };
            }
        }
        // Check for statistical results
        if (/[χχ²χ2]|t[\s-]test|p[\s-]value|confidence interval|CI:|OR:|HR:|RR:/i.test(content)) {
            return { needs: true, reason: 'Contains statistical results requiring validation' };
        }
        return { needs: false, reason: 'No review triggers detected' };
    }
    /**
     * Generate a review report for a piece of scientific content
     */
    async review(params) {
        const warnings = [];
        const suggestions = [];
        let overallConfidence = 1.0;
        // Validate all citations
        const citationResults = await Promise.all(params.citations.map(async (citation) => {
            const result = await this.validateCitation(citation);
            return {
                citation,
                validated: result.validated,
                confidence: result.confidence,
                errors: result.warnings,
            };
        }));
        // Calculate overall confidence
        const validCitations = citationResults.filter(c => c.validated).length;
        const totalCitations = citationResults.length;
        if (totalCitations > 0) {
            const citationConfidence = validCitations / totalCitations;
            overallConfidence = Math.min(overallConfidence, citationConfidence);
        }
        // Check for unvalidated citations
        const unvalidated = citationResults.filter(c => !c.validated);
        if (unvalidated.length > 0) {
            warnings.push(`${unvalidated.length} citation(s) could not be validated`);
            suggestions.push('Provide DOIs or PMIDs for all citations');
        }
        // Validate statistical results if provided
        if (params.statisticalResults && params.statisticalResults.length > 0) {
            for (const stat of params.statisticalResults) {
                if (stat.type === 'p-value') {
                    const pValue = parseFloat(stat.value.replace(/[<≤>≥p=]/gi, ''));
                    if (isNaN(pValue)) {
                        warnings.push(`Invalid p-value format: ${stat.value}`);
                    }
                    else if (pValue < 0 || pValue > 1) {
                        suggestions.push(`p-value ${stat.value} appears invalid (must be between 0 and 1)`);
                        overallConfidence = Math.min(overallConfidence, 0.5);
                    }
                }
            }
        }
        // Track review in provenance
        this.provenance.trackExecution({
            agentId: 'reviewer',
            action: 'scientific-review',
            input: params,
            output: {
                reviewed: true,
                overallConfidence,
                citationsValidated: validCitations,
                totalCitations,
            },
            toolsUsed: ['doi-validation', 'pmid-validation'],
            tags: ['review', 'validation'],
        });
        return {
            reviewed: true,
            overallConfidence,
            citationResults,
            warnings,
            suggestions,
        };
    }
    /**
     * Register this agent with the MCP server
     */
    getMCPRegistration() {
        const validateDOITool = {
            name: 'validate_doi',
            description: 'Validate a Digital Object Identifier (DOI)',
            inputSchema: {
                type: 'object',
                properties: {
                    doi: { type: 'string', description: 'The DOI to validate' },
                },
                required: ['doi'],
            },
            handler: async (args) => {
                return this.validateDOI(args.doi);
            },
        };
        const validatePMIDTool = {
            name: 'validate_pmid',
            description: 'Validate a PubMed Identifier (PMID)',
            inputSchema: {
                type: 'object',
                properties: {
                    pmid: { type: 'string', description: 'The PMID to validate' },
                },
                required: ['pmid'],
            },
            handler: async (args) => {
                return this.validatePMID(args.pmid);
            },
        };
        const validateCitationTool = {
            name: 'validate_citation',
            description: 'Validate a scientific citation',
            inputSchema: {
                type: 'object',
                properties: {
                    citation: { type: 'string', description: 'The citation text to validate' },
                },
                required: ['citation'],
            },
            handler: async (args) => {
                return this.validateCitation(args.citation);
            },
        };
        const reviewTool = {
            name: 'review_content',
            description: 'Review scientific content for citation and statistical validity',
            inputSchema: {
                type: 'object',
                properties: {
                    content: { type: 'string', description: 'The scientific content to review' },
                    citations: { type: 'array', items: { type: 'string' }, description: 'Array of citation strings' },
                    statisticalResults: {
                        type: 'array',
                        items: {
                            type: 'object',
                            properties: {
                                type: { type: 'string' },
                                value: { type: 'string' },
                            },
                        },
                        description: 'Statistical results to validate',
                    },
                },
                required: ['content', 'citations'],
            },
            handler: async (args) => {
                return this.review({
                    content: args.content,
                    citations: args.citations,
                    statisticalResults: args.statisticalResults,
                });
            },
        };
        const needsReviewTool = {
            name: 'needs_review',
            description: 'Check if content requires scientific review',
            inputSchema: {
                type: 'object',
                properties: {
                    content: { type: 'string', description: 'The content to check' },
                },
                required: ['content'],
            },
            handler: async (args) => {
                return this.needsReview(args.content);
            },
        };
        return {
            id: 'reviewer',
            name: 'Scientific Reviewer',
            description: 'Validates citations, DOIs, PMIDs, statistical results, and marks confidence levels',
            version: '0.1.0',
            capabilities: {
                tools: [validateDOITool, validatePMIDTool, validateCitationTool, reviewTool, needsReviewTool],
                resources: [],
                prompts: [],
            },
            metadata: {
                confidenceThresholds: this.confidenceThresholds,
            },
        };
    }
}
// Standalone execution
if (typeof process !== 'undefined' && process.argv[1]?.endsWith('index.js')) {
    const agent = new ReviewerAgent();
    const mcpAgent = agent.getMCPRegistration();
    console.error(`Reviewer Agent v${mcpAgent.version} loaded`);
    console.error(`Tools: ${mcpAgent.capabilities.tools.map(t => t.name).join(', ')}`);
}
//# sourceMappingURL=index.js.map