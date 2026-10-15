# CoResearcher REST API.
# The earlier multi-stage image (TypeScript MCP server and phase-1 Python agents) is in archive/phase1/typescript/.
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ ./api/
COPY python/ ./python/
COPY schemas/ ./schemas/

# Secrets (CORESEARCHER_API_KEY, webhook secret) come from the runtime environment, never from the image.
RUN useradd --create-home appuser
USER appuser

ENV PORT=8080
EXPOSE 8080
CMD ["sh", "-c", "python -m python.cli.main serve --host 0.0.0.0 --port ${PORT}"]
