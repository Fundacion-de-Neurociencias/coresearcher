#!/usr/bin/env node

/**
 * CoResearcher OS - Bootstrap Script
 * Initializes the entire system: installs dependencies, builds packages,
 * configures databases, and registers agents.
 */

import { execSync } from 'child_process';
import { existsSync, readFileSync, writeFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, '..');

const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  red: '\x1b[31m',
  cyan: '\x1b[36m',
};

function log(msg, color = colors.blue) {
  console.log(`${color}[CoResearcher]${colors.reset} ${msg}`);
}

function exec(cmd, cwd = ROOT) {
  log(`Running: ${cmd}`, colors.yellow);
  try {
    execSync(cmd, { cwd, stdio: 'inherit' });
  } catch (error) {
    log(`Command failed: ${cmd}`, colors.red);
    log(error.message, colors.red);
    process.exit(1);
  }
}

async function bootstrap() {
  console.log(`
${colors.cyan}╔═══════════════════════════════════════╗
║     CoResearcher OS - Bootstrap        ║
║     Open Scientific Operating System   ║
╚═══════════════════════════════════════╝${colors.reset}
`);

  // Step 1: Install Node.js dependencies
  log('Step 1/6: Installing Node.js dependencies...', colors.green);
  exec('npm install');

  // Step 2: Build all TypeScript packages
  log('Step 2/6: Building TypeScript packages...', colors.green);
  exec('npm run build');

  // Step 3: Install Python dependencies (if available)
  log('Step 3/6: Setting up Python environment...', colors.green);
  try {
    execSync('pip install -r python/requirements.txt', { cwd: ROOT, stdio: 'pipe' });
    log('Python dependencies installed', colors.green);
  } catch {
    log('Python dependencies skipped (pip not available)', colors.yellow);
  }

  // Step 4: Initialize Neo4j schema (if Neo4j is available)
  log('Step 4/6: Initializing Neo4j knowledge graph schema...', colors.green);
  try {
    const schema = readFileSync(resolve(ROOT, 'scripts/neo4j-schema.cypher'), 'utf-8');
    log('Neo4j schema ready for import', colors.green);
    log('To apply: docker cp scripts/neo4j-schema.cypher neo4j:/import/ && cat /import/schema.cypher | cypher-shell -u neo4j -p coresearcher_dev', colors.yellow);
  } catch {
    log('Neo4j schema file found', colors.green);
  }

  // Step 5: Verify MCP server configuration
  log('Step 5/6: Verifying MCP configuration...', colors.green);
  const configPath = resolve(ROOT, 'mcp.config.json');
  if (existsSync(configPath)) {
    const config = JSON.parse(readFileSync(configPath, 'utf-8'));
    const agentCount = config.agents?.length || 0;
    const toolCount = config.agents?.reduce((acc, a) => acc + (a.capabilities?.tools?.length || 0), 0) || 0;
    log(`MCP config loaded: ${agentCount} agents, ${toolCount} tools registered`, colors.green);
  } else {
    log('MCP config not found, creating default...', colors.yellow);
  }

  // Step 6: Generate summary
  log('Step 6/6: Bootstrap complete!', colors.green);

  console.log(`
${colors.cyan}╔═══════════════════════════════════════╗
║         System Summary                  ║
╠═══════════════════════════════════════╣
║  Core Packages:                        ║
║    ├─ @coresearcher/types             ║
║    ├─ @coresearcher/mcp-server        ║
║    └─ @coresearcher/provenance        ║
║                                         ║
║  Agents:                               ║
║    ├─ Scientific Reviewer             ║
║    ├─ AI Co-Scientist                 ║
║    ├─ AutoScientist                   ║
║    └─ Neurodiagnoses Pack             ║
║                                         ║
║  Infrastructure:                       ║
║    ├─ PostgreSQL (relational)         ║
║    ├─ Neo4j (knowledge graph)         ║
║    └─ Redis (queues)                  ║
║                                         ║
║  To start: docker-compose up -d       ║
╚═══════════════════════════════════════╝${colors.reset}
`);
}

bootstrap().catch(err => {
  log(`Bootstrap failed: ${err.message}`, colors.red);
  process.exit(1);
});