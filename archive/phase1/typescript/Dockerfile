# CoResearcher OS - Multi-stage Docker Build

# === Stage 1: Build TypeScript ===
FROM node:20-alpine AS builder
WORKDIR /app

# Install build dependencies
RUN apk add --no-cache python3 make g++

# Copy package files
COPY package.json tsconfig.json ./
COPY packages/types/package.json packages/types/
COPY packages/mcp-server/package.json packages/mcp-server/
COPY packages/provenance/package.json packages/provenance/
COPY agents/reviewer/package.json agents/reviewer/
COPY agents/co-scientist/package.json agents/co-scientist/
COPY agents/autoscientist/package.json agents/autoscientist/
COPY agents/neurodiagnoses/package.json agents/neurodiagnoses/

# Install dependencies
RUN npm install

# Copy source files
COPY packages/types/src packages/types/src/
COPY packages/mcp-server/src packages/mcp-server/src/
COPY packages/provenance/src packages/provenance/src/
COPY agents/reviewer/src agents/reviewer/src/
COPY agents/co-scientist/src agents/co-scientist/src/
COPY agents/autoscientist/src agents/autoscientist/src/
COPY agents/neurodiagnoses/src agents/neurodiagnoses/src/

# Build all packages
RUN npm run build

# === Stage 2: MCP Server Runtime ===
FROM node:20-alpine AS mcp-server
WORKDIR /app

# Copy built artifacts
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/packages/types/dist ./packages/types/dist
COPY --from=builder /app/packages/types/package.json ./packages/types/
COPY --from=builder /app/packages/mcp-server/dist ./packages/mcp-server/dist
COPY --from=builder /app/packages/mcp-server/package.json ./packages/mcp-server/
COPY --from=builder /app/packages/provenance/dist ./packages/provenance/dist
COPY --from=builder /app/packages/provenance/package.json ./packages/provenance/
COPY --from=builder /app/agents/reviewer/dist ./agents/reviewer/dist
COPY --from=builder /app/agents/reviewer/package.json ./agents/reviewer/
COPY --from=builder /app/agents/co-scientist/dist ./agents/co-scientist/dist
COPY --from=builder /app/agents/co-scientist/package.json ./agents/co-scientist/
COPY --from=builder /app/agents/autoscientist/dist ./agents/autoscientist/dist
COPY --from=builder /app/agents/autoscientist/package.json ./agents/autoscientist/
COPY --from=builder /app/agents/neurodiagnoses/dist ./agents/neurodiagnoses/dist
COPY --from=builder /app/agents/neurodiagnoses/package.json ./agents/neurodiagnoses/
COPY --from=builder /app/package.json ./

# Copy MCP config
COPY mcp.config.json ./

EXPOSE 3100

CMD ["node", "packages/mcp-server/dist/index.js", "mcp.config.json"]

# === Stage 3: Python Scientific Agents ===
FROM python:3.12-slim AS python-agents
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements
COPY python/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python agent code
COPY python/ ./python/

CMD ["python", "-m", "python.agents"]