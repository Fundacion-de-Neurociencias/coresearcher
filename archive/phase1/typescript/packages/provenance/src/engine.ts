import { v4 as uuidv4 } from 'uuid';
import { createHash } from 'crypto';
import type {
  Artifact,
  ArtifactType,
  Execution,
  Experiment,
  ProvenanceRecord,
  ProvenanceSource,
  ProvenanceQuery,
} from '@coresearcher/types';

export class ProvenanceEngine {
  private records: Map<string, ProvenanceRecord> = new Map();
  private executions: Map<string, Execution> = new Map();
  private experiments: Map<string, Experiment> = new Map();
  private artifacts: Map<string, Artifact> = new Map();

  constructor() {
    this.records = new Map();
    this.executions = new Map();
    this.experiments = new Map();
    this.artifacts = new Map();
  }

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
  }): Artifact {
    const id = uuidv4();
    const contentHash = this.hashContent(params.content);

    const artifact: Artifact = {
      id,
      type: params.type,
      name: params.name,
      content: params.content,
      contentHash,
      createdAt: new Date().toISOString(),
      createdBy: params.createdBy,
      description: params.description,
      sources: params.sources || [],
      parentId: params.parentId,
      tags: params.tags || [],
      version: params.version || '1.0.0',
    };

    this.artifacts.set(id, artifact);
    this.createProvenanceRecord(artifact);

    return artifact;
  }

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
  }): Execution {
    const id = uuidv4();
    const startedAt = new Date().toISOString();

    const execution: Execution = {
      id,
      agentId: params.agentId,
      action: params.action,
      input: params.input,
      output: params.output,
      modelUsed: params.modelUsed,
      promptsUsed: params.promptsUsed,
      toolsUsed: params.toolsUsed,
      codeExecuted: params.codeExecuted,
      datasetsUsed: params.datasetsUsed,
      sources: params.sources,
      startedAt,
      status: 'completed',
      completedAt: new Date().toISOString(),
      artifacts: params.artifacts || [],
      tags: params.tags || [],
    };

    const start = new Date(startedAt).getTime();
    const end = new Date(execution.completedAt!).getTime();
    execution.duration = end - start;

    this.executions.set(id, execution);

    const execArtifact = this.registerArtifact({
      type: 'execution',
      name: `${params.action}-${params.agentId}`,
      content: JSON.stringify({ input: params.input, output: params.output }),
      createdBy: params.agentId,
      sources: params.sources,
      tags: ['execution', ...(params.tags || [])],
    });

    execution.artifacts.push(execArtifact.id);

    return execution;
  }

  createExperiment(params: {
    name: string;
    description: string;
    hypothesis?: string;
    design: Record<string, unknown>;
    variables?: Record<string, unknown>;
    tags?: string[];
  }): Experiment {
    const id = uuidv4();
    const now = new Date().toISOString();

    const experiment: Experiment = {
      id,
      name: params.name,
      description: params.description,
      hypothesis: params.hypothesis,
      design: params.design,
      variables: params.variables,
      executions: [],
      artifacts: [],
      status: 'designed',
      tags: params.tags || [],
      createdAt: now,
      updatedAt: now,
    };

    this.experiments.set(id, experiment);

    this.registerArtifact({
      type: 'experiment',
      name: params.name,
      content: JSON.stringify(params.design),
      createdBy: 'system',
      description: params.description,
      tags: ['experiment', ...(params.tags || [])],
    });

    return experiment;
  }

  linkExecutionToExperiment(executionId: string, experimentId: string): void {
    const experiment = this.experiments.get(experimentId);
    if (!experiment) {
      throw new Error(`Experiment not found: ${experimentId}`);
    }

    if (!experiment.executions.includes(executionId)) {
      experiment.executions.push(executionId);
      experiment.updatedAt = new Date().toISOString();
    }
  }

  getProvenanceLineage(artifactId: string): ProvenanceRecord[] {
    const record = this.records.get(artifactId);
    if (!record) {
      return [];
    }

    const lineage: ProvenanceRecord[] = [record];

    let currentArtifact = record.artifact;
    while (currentArtifact.parentId) {
      const parentRecord = this.records.get(currentArtifact.parentId);
      if (parentRecord) {
        lineage.unshift(parentRecord);
        currentArtifact = parentRecord.artifact;
      } else {
        break;
      }
    }

    return lineage;
  }

  queryProvenance(query: ProvenanceQuery): ProvenanceRecord[] {
    let results = Array.from(this.records.values());

    if (query.artifactId) {
      results = results.filter(r => r.artifact.id === query.artifactId);
    }

    if (query.agentId) {
      results = results.filter(r => 
        r.execution && r.execution.agentId === query.agentId
      );
    }

    if (query.type) {
      results = results.filter(r => r.artifact.type === query.type);
    }

    if (query.fromDate) {
      const from = new Date(query.fromDate).getTime();
      results = results.filter(r => new Date(r.timestamp).getTime() >= from);
    }

    if (query.toDate) {
      const to = new Date(query.toDate).getTime();
      results = results.filter(r => new Date(r.timestamp).getTime() <= to);
    }

    if (query.tags && query.tags.length > 0) {
      results = results.filter(r =>
        query.tags!.some(tag => r.artifact.tags.includes(tag))
      );
    }

    results.sort((a, b) => 
      new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );

    const start = query.offset || 0;
    const end = start + (query.limit || 50);

    return results.slice(start, end);
  }

  getArtifact(id: string): Artifact | undefined {
    return this.artifacts.get(id);
  }

  getExecution(id: string): Execution | undefined {
    return this.executions.get(id);
  }

  getExperiment(id: string): Experiment | undefined {
    return this.experiments.get(id);
  }

  listExperiments(): Experiment[] {
    return Array.from(this.experiments.values());
  }

  getExperimentExecutions(experimentId: string): Execution[] {
    const experiment = this.experiments.get(experimentId);
    if (!experiment) {
      return [];
    }
    return experiment.executions
      .map((id: string) => this.executions.get(id))
      .filter((e: Execution | undefined): e is Execution => e !== undefined);
  }

  generateReport(artifactId: string): string {
    const lineage = this.getProvenanceLineage(artifactId);
    if (lineage.length === 0) {
      return 'No provenance data found';
    }

    const artifact = lineage[lineage.length - 1].artifact;
    let report = `=== Provenance Report ===\n\n`;
    report += `Artifact: ${artifact.name} (${artifact.type})\n`;
    report += `ID: ${artifact.id}\n`;
    report += `Version: ${artifact.version}\n`;
    report += `Created: ${artifact.createdAt}\n`;
    report += `Created By: ${artifact.createdBy}\n`;
    report += `Content Hash: ${artifact.contentHash}\n\n`;

    if (artifact.sources && artifact.sources.length > 0) {
      report += `Sources:\n`;
      for (const source of artifact.sources) {
        report += `  - ${source.type}: ${source.identifier}${source.version ? ` v${source.version}` : ''}\n`;
        if (source.uri) report += `    URI: ${source.uri}\n`;
        if (source.hash) report += `    Hash: ${source.hash}\n`;
      }
      report += '\n';
    }

    report += `Lineage (${lineage.length} generations):\n`;
    for (let i = 0; i < lineage.length; i++) {
      const gen = lineage[i];
      report += `  [${i + 1}] ${gen.artifact.name} (${gen.artifact.type})`;
      if (gen.execution) {
        report += ` via ${gen.execution.action}`;
      }
      report += '\n';
    }

    return report;
  }

  private createProvenanceRecord(artifact: Artifact): ProvenanceRecord {
    const record: ProvenanceRecord = {
      id: uuidv4(),
      artifact,
      timestamp: new Date().toISOString(),
      lineage: this.buildLineage(artifact.id),
    };

    this.records.set(artifact.id, record);
    return record;
  }

  private buildLineage(artifactId: string): string[] {
    const lineage: string[] = [];
    let current = this.artifacts.get(artifactId);

    while (current && current.parentId) {
      lineage.push(current.parentId);
      current = this.artifacts.get(current.parentId);
    }

    return lineage;
  }

  private hashContent(content: string): string {
    return createHash('sha256').update(content).digest('hex');
  }
}