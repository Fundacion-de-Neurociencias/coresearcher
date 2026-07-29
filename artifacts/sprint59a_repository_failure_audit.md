# Sprint 59A — Repository Failure Audit

## Caso 1: LlamaIndex 404

### Evidencia observable

```json
{
  "requested_repo": "run-llama/LlamaIndex",
  "github_response": "HTTP Error 404: Not Found",
  "classification": "REPOSITORY_IDENTIFIER_ERROR"
}
```

### Diagnóstico

El repositorio solicitado devolvió 404 en todos los endpoints probados:

- `/repos/run-llama/LlamaIndex` → 404
- `/repos/run-llama/LlamaIndex/issues` → 404
- `/repos/run-llama/LlamaIndex/pulls` → 404

### Hipótesis (no confirmada)

El repositorio público de LlamaIndex puede haber sido renombrado.
El nombre correcto podría ser:

```text
run-llama/llama_index
```

### Acción

Intentar automáticamente el identificador alternativo.

---

## Caso 2: Reintento con identificador alternativo

### Evidencia observable

```json
{
  "retry_repo": "run-llama/llama_index",
  "status": "PENDIENTE"
}
```

---

## Métrica global: repository_resolution_rate

```text
repositorios válidos encontrados
/
repositorios solicitados
```

### Estado actual

```text
3 / 4 = 0.75
```

- langchain-ai/langgraph → OK
- langchain-ai/langchain → OK
- run-llama/LlamaIndex → FAIL (404)
- deepset-ai/haystack → OK

### Umbral de aceptación

```text
repository_resolution_rate >= 0.90
```

Si el reintento con `run-llama/llama_index` funciona:

```text
4 / 4 = 1.0
```

---

## Conclusión preliminar

La frontera empírica actual de Coresearcher:

```text
Funciona en repositorios con:
- issues abundantes
- PRs abundantes
- comunidad activa
- historial público rico
```

No se ha demostrado generalización fuera de esta familia.
