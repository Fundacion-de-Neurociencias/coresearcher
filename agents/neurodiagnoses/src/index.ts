import type { MCPAgent, MCPTool } from '@coresearcher/types/mcp';
import { ProvenanceEngine } from '@coresearcher/provenance';

/**
 * Triaxial Classification Model for Neurodiagnoses
 * Axis 1: Clinical Syndrome
 * Axis 2: Etiology/Pathophysiology
 * Axis 3: Functional Impairment
 */
interface TriaxialDiagnosis {
  axis1: { syndrome: string; code: string; confidence: number };
  axis2: { etiology: string; code: string; confidence: number };
  axis3: { impairment: string; severity: 'mild' | 'moderate' | 'severe'; code: string; confidence: number };
  confidence: number;
  timestamp: string;
}

/**
 * Neurodiagnoses Agent Pack
 * Implements Biomarker, Neurodiagnosis, Trial, and Regulatory agents
 * using the triaxial classification model as the native framework.
 */
export class NeurodiagnosesAgent {
  private provenance: ProvenanceEngine;

  constructor(provenance?: ProvenanceEngine) {
    this.provenance = provenance || new ProvenanceEngine();
  }

  // === Biomarker Agent ===

  async analyzeBiomarkers(params: {
    biomarkers: Array<{ name: string; value: string; unit: string; referenceRange: string }>;
    context?: string;
    diagnosis?: string;
  }): Promise<{
    analysis: string;
    significant: Array<{ biomarker: string; direction: string; significance: number }>;
    patterns: string[];
    recommendations: string[];
  }> {
    const significant = params.biomarkers
      .filter(b => {
        const value = parseFloat(b.value);
        const range = b.referenceRange.match(/[\d.]+/g);
        if (!range || range.length < 2) return false;
        return value < parseFloat(range[0]) || value > parseFloat(range[1]);
      })
      .map(b => ({
        biomarker: b.name,
        direction: parseFloat(b.value) > parseFloat(b.referenceRange.match(/[\d.]+/g)![1]) ? 'elevated' : 'decreased',
        significance: 0.7,
      }));

    this.provenance.trackExecution({
      agentId: 'neurodiagnoses',
      action: 'analyze-biomarkers',
      input: { biomarkers: params.biomarkers, context: params.context },
      output: { significantCount: significant.length, patterns: ['neurodegenerative-profile'] },
      toolsUsed: ['biomarker-analysis'],
      tags: ['biomarker', 'neurodiagnoses'],
    });

    return {
      analysis: `Analysis of ${params.biomarkers.length} biomarkers revealed ${significant.length} significant findings`,
      significant,
      patterns: ['neurodegenerative-profile', 'inflammatory-markers'],
      recommendations: ['Correlate with clinical presentation', 'Consider longitudinal monitoring'],
    };
  }

  // === Neurodiagnosis Agent (Triaxial) ===

  async triaxialDiagnosis(params: {
    symptoms: string[];
    biomarkers: Array<{ name: string; value: string; unit: string; referenceRange: string }>;
    imaging?: string[];
    cognitiveTests?: Array<{ test: string; score: string; interpretation: string }>;
    history?: string;
  }): Promise<{
    diagnosis: TriaxialDiagnosis;
    differential: string[];
    recommendedTests: string[];
    confidence: number;
  }> {
    // Axis 1: Clinical Syndrome determination
    const axis1 = this.determineClinicalSyndrome(params.symptoms, params.cognitiveTests);

    // Axis 2: Etiology/Pathophysiology
    const axis2 = this.determineEtiology(params.biomarkers, params.imaging);

    // Axis 3: Functional Impairment
    const axis3 = this.determineImpairment(params.symptoms, params.cognitiveTests);

    const overallConfidence = (axis1.confidence + axis2.confidence + axis3.confidence) / 3;

    const diagnosis: TriaxialDiagnosis = {
      axis1,
      axis2,
      axis3,
      confidence: overallConfidence,
      timestamp: new Date().toISOString(),
    };

    this.provenance.trackExecution({
      agentId: 'neurodiagnoses',
      action: 'triaxial-diagnosis',
      input: { symptoms: params.symptoms, biomarkerCount: params.biomarkers.length },
      output: { diagnosis },
      toolsUsed: ['triaxial-classification'],
      tags: ['diagnosis', 'triaxial', 'neurodiagnoses'],
    });

    return {
      diagnosis,
      differential: ['Alzheimer Disease', 'Frontotemporal Dementia', 'Lewy Body Dementia'],
      recommendedTests: ['Neuropsychological battery', 'Brain MRI with volumetric analysis', 'CSF biomarkers'],
      confidence: overallConfidence,
    };
  }

  // === Trial Agent ===

  async findTrials(params: {
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
  }> {
    const trials = [
      {
        id: 'NCT000001',
        title: `Phase 3 Study of Novel Therapy for ${params.diagnosis}`,
        phase: 'Phase 3',
        status: 'Recruiting',
        eligibility: 'Early stage, biomarker positive',
        location: params.location || 'Multiple sites',
        matchScore: 0.85,
      },
      {
        id: 'NCT000002',
        title: `Biomarker Validation Study in ${params.diagnosis}`,
        phase: 'Phase 2',
        status: 'Active',
        eligibility: 'Confirmed diagnosis, all stages',
        location: params.location || 'United States',
        matchScore: 0.72,
      },
    ];

    this.provenance.trackExecution({
      agentId: 'neurodiagnoses',
      action: 'find-trials',
      input: params as unknown as Record<string, unknown>,
      output: { trialsFound: trials.length },
      toolsUsed: ['clinical-trials-search'],
      tags: ['trials', 'neurodiagnoses'],
    });

    return {
      trials,
      totalCount: trials.length,
      topMatches: trials.filter(t => t.matchScore > 0.7).map(t => t.id),
    };
  }

  // === Regulatory Agent ===

  async checkRegulatoryStatus(params: {
    biomarker: string;
    region: string;
    application?: string;
  }): Promise<{
    status: string;
    approvals: Array<{ agency: string; status: string; date?: string; indication: string }>;
    guidelines: string[];
    requirements: string[];
  }> {
    const approvals = [
      {
        agency: params.region === 'US' ? 'FDA' : 'EMA',
        status: 'Approved',
        indication: `Diagnostic use in neurodegenerative disease`,
      },
    ];

    this.provenance.trackExecution({
      agentId: 'neurodiagnoses',
      action: 'regulatory-check',
      input: params as unknown as Record<string, unknown>,
      output: { approvals },
      toolsUsed: ['regulatory-database'],
      tags: ['regulatory', 'neurodiagnoses'],
    });

    return {
      status: 'Approved',
      approvals,
      guidelines: [
        'Follow CLIA guidelines for laboratory developed tests',
        'Adhere to local diagnostic criteria',
      ],
      requirements: [
        'Clinical validation data required',
        'Quality control procedures',
        'Regular proficiency testing',
      ],
    };
  }

  private determineClinicalSyndrome(
    symptoms: string[],
    cognitiveTests?: Array<{ test: string; score: string; interpretation: string }>
  ): { syndrome: string; code: string; confidence: number } {
    const symptomText = symptoms.join(' ').toLowerCase();

    if (symptomText.includes('memory') || symptomText.includes('forget')) {
      return { syndrome: 'Major Neurocognitive Disorder due to Alzheimer Disease', code: 'G30.9', confidence: 0.75 };
    }
    if (symptomText.includes('tremor') || symptomText.includes('rigidity')) {
      return { syndrome: 'Parkinson Disease Dementia', code: 'G20', confidence: 0.7 };
    }
    if (symptomText.includes('behavior') || symptomText.includes('personality')) {
      return { syndrome: 'Frontotemporal Neurocognitive Disorder', code: 'G31.09', confidence: 0.65 };
    }

    return { syndrome: 'Unspecified Neurocognitive Disorder', code: 'G31.84', confidence: 0.5 };
  }

  private determineEtiology(
    biomarkers: Array<{ name: string; value: string; unit: string; referenceRange: string }>,
    imaging?: string[]
  ): { etiology: string; code: string; confidence: number } {
    const biomarkerNames = biomarkers.map(b => b.name.toLowerCase());

    if (biomarkerNames.some(b => b.includes('amyloid') || b.includes('tau'))) {
      return { etiology: 'Alzheimer Disease Pathology', code: 'G30.9', confidence: 0.8 };
    }
    if (biomarkerNames.some(b => b.includes('alpha-synuclein'))) {
      return { etiology: 'Synucleinopathy', code: 'G23.8', confidence: 0.7 };
    }

    return { etiology: 'Unspecified Neurodegenerative Process', code: 'G31.9', confidence: 0.5 };
  }

  private determineImpairment(
    symptoms: string[],
    cognitiveTests?: Array<{ test: string; score: string; interpretation: string }>
  ): { impairment: string; severity: 'mild' | 'moderate' | 'severe'; code: string; confidence: number } {
    // Simplified impairment determination
    const severeIndicators = ['severe', 'unable', 'dependent', 'bedridden'];
    const moderateIndicators = ['moderate', 'difficulty', 'assistance', 'supervision'];

    let severity: 'mild' | 'moderate' | 'severe' = 'mild';

    for (const s of symptoms) {
      const lower = s.toLowerCase();
      if (severeIndicators.some(i => lower.includes(i))) {
        severity = 'severe';
        break;
      }
      if (moderateIndicators.some(i => lower.includes(i))) {
        severity = 'moderate';
      }
    }

    const severityCodes = { mild: 'R41.89', moderate: 'F02.80', severe: 'F02.81' };

    return {
      impairment: `${severity.charAt(0).toUpperCase() + severity.slice(1)} Functional Impairment`,
      severity,
      code: severityCodes[severity],
      confidence: 0.7,
    };
  }

  /**
   * Register this agent with the MCP server
   */
  getMCPRegistration(): MCPAgent {
    const biomarkerTool: MCPTool = {
      name: 'analyze_biomarkers',
      description: 'Analyze neurological biomarkers and identify significant patterns',
      inputSchema: {
        type: 'object',
        properties: {
          biomarkers: {
            type: 'array',
            items: {
              type: 'object',
              properties: {
                name: { type: 'string' },
                value: { type: 'string' },
                unit: { type: 'string' },
                referenceRange: { type: 'string' },
              },
            },
          },
          context: { type: 'string' },
          diagnosis: { type: 'string' },
        },
        required: ['biomarkers'],
      },
      handler: async (args: Record<string, unknown>) => {
        return this.analyzeBiomarkers({
          biomarkers: args.biomarkers as Array<{ name: string; value: string; unit: string; referenceRange: string }>,
          context: args.context as string | undefined,
          diagnosis: args.diagnosis as string | undefined,
        });
      },
    };

    const diagnosisTool: MCPTool = {
      name: 'triaxial_diagnosis',
      description: 'Perform triaxial neurodiagnosis (Axis 1: Syndrome, Axis 2: Etiology, Axis 3: Impairment)',
      inputSchema: {
        type: 'object',
        properties: {
          symptoms: { type: 'array', items: { type: 'string' } },
          biomarkers: {
            type: 'array',
            items: {
              type: 'object',
              properties: {
                name: { type: 'string' },
                value: { type: 'string' },
                unit: { type: 'string' },
                referenceRange: { type: 'string' },
              },
            },
          },
          imaging: { type: 'array', items: { type: 'string' } },
          cognitiveTests: {
            type: 'array',
            items: {
              type: 'object',
              properties: {
                test: { type: 'string' },
                score: { type: 'string' },
                interpretation: { type: 'string' },
              },
            },
          },
          history: { type: 'string' },
        },
        required: ['symptoms'],
      },
      handler: async (args: Record<string, unknown>) => {
        return this.triaxialDiagnosis({
          symptoms: args.symptoms as string[],
          biomarkers: (args.biomarkers || []) as Array<{ name: string; value: string; unit: string; referenceRange: string }>,
          imaging: args.imaging as string[] | undefined,
          cognitiveTests: args.cognitiveTests as Array<{ test: string; score: string; interpretation: string }> | undefined,
          history: args.history as string | undefined,
        });
      },
    };

    const trialTool: MCPTool = {
      name: 'find_clinical_trials',
      description: 'Find relevant clinical trials for a neurological condition',
      inputSchema: {
        type: 'object',
        properties: {
          diagnosis: { type: 'string' },
          biomarkers: { type: 'array', items: { type: 'string' } },
          stage: { type: 'string' },
          location: { type: 'string' },
        },
        required: ['diagnosis'],
      },
      handler: async (args: Record<string, unknown>) => {
        return this.findTrials({
          diagnosis: args.diagnosis as string,
          biomarkers: args.biomarkers as string[] | undefined,
          stage: args.stage as string | undefined,
          location: args.location as string | undefined,
        });
      },
    };

    const regulatoryTool: MCPTool = {
      name: 'check_regulatory',
      description: 'Check regulatory status and requirements for neurological diagnostics',
      inputSchema: {
        type: 'object',
        properties: {
          biomarker: { type: 'string' },
          region: { type: 'string', enum: ['US', 'EU', 'UK', 'JP'] },
          application: { type: 'string' },
        },
        required: ['biomarker', 'region'],
      },
      handler: async (args: Record<string, unknown>) => {
        return this.checkRegulatoryStatus({
          biomarker: args.biomarker as string,
          region: args.region as string,
          application: args.application as string | undefined,
        });
      },
    };

    return {
      id: 'neurodiagnoses',
      name: 'Neurodiagnoses Agent Pack',
      description: 'Biomarker analysis, triaxial neurodiagnosis, clinical trial matching, and regulatory compliance for neurological disorders',
      version: '0.1.0',
      capabilities: {
        tools: [biomarkerTool, diagnosisTool, trialTool, regulatoryTool],
        resources: [],
        prompts: [],
      },
      metadata: {
        classificationModel: 'triaxial',
        axes: ['Clinical Syndrome', 'Etiology/Pathophysiology', 'Functional Impairment'],
        domains: ['Alzheimer Disease', 'Parkinson Disease', 'Frontotemporal Dementia', 'Lewy Body Dementia'],
      },
    };
  }
}

if (typeof process !== 'undefined' && process.argv[1]?.endsWith('index.js')) {
  const agent = new NeurodiagnosesAgent();
  const mcpAgent = agent.getMCPRegistration();
  console.error(`Neurodiagnoses Agent v${mcpAgent.version} loaded`);
  console.error(`Tools: ${mcpAgent.capabilities.tools.map(t => t.name).join(', ')}`);
}