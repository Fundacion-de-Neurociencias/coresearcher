# Sprint 58A — Evidence Anchoring Audit

## Contexto

Sprint 58 reveló: `precision_observable = 0.0`

Todas las 33 afirmaciones del Trajectory Report son clasificadas como "inferred".

Esto significa que el reporte actual genera hipótesis plausibles, no trazabilidad recuperable.

## Objetivo

Determinar cuántas afirmaciones sobreviven si eliminamos toda inferencia.

Responder:

> ¿Cuánta información es realmente recuperable desde evidencia pública?

## Prohibición absoluta

```text
claim without evidence
```

Si no existe evidencia rastreable (Issue, PR, Commit, Release, Zenodo Record):

```text
classification = inferred
```

automáticamente.

---

## Paso 1: Auditoría de cada afirmación

Tomar las 33 afirmaciones del Trajectory Report.

Para cada una:

```json
{
  "claim": "...",
  "source_issue": "...",
  "source_pr": "...",
  "source_commit": "...",
  "source_release": "...",
  "classification": "observable|derivable|inferred|unknown"
}
```

### Reglas de clasificación

**Observable**: La afirmación aparece literalmente en un Issue, PR, Commit, Release o Zenodo Record.

**Derivable**: La afirmación puede calcularse mediante un algoritmo explícito sobre datos observables (ej: "hay 15 releases", "el PR #456 fue mergeado el 2024-01-15").

**Inferido**: La afirmación es una interpretación razonable pero no aparece literalmente (ej: "el equipo decidió priorizar escalabilidad").

**Desconocido**: La información no está disponible públicamente.

---

## Paso 2: Métricas

### observable_ratio

```text
observable
/
total
```

### evidence_coverage

```text
claims_with_sources
/
total_claims
```

### inference_ratio

```text
inferred
/
total
```

---

## Paso 3: Resultado esperado

### Escenario A (bueno)

Las afirmaciones están presentes en los datos crudos, pero el reporte no las conserva como anchors.

Solución: añadir evidence anchors a cada claim.

```text
Claim: "The team chose architecture X"
Evidence: Issue #123, PR #456, Commit abc123
Classification: observable
```

### Escenario B (malo)

Las afirmaciones son generadas por heurísticas sin evidencia rastreable.

```text
Claim: "The team chose architecture X for scalability"
Evidence: none
Classification: inferred
```

En este caso, Coresearcher no está reconstruyendo trazabilidad. Está generando hipótesis plausibles.

---

## Paso 4: Producto resultante

Independientemente del escenario, el producto debe evolucionar a:

```text
Evidence-Anchored Trajectory Report
```

donde cada frase tenga detrás:

```text
Issue
PR
Commit
Release
Zenodo Record
```

o admita explícitamente:

```text
No recuperable desde evidencia pública
```

---

## Script

Crear:

```text
scripts/audit_evidence_anchoring.py
```

Entrada:

```text
artifacts/langgraph_trajectory_report_v0.md
data/langgraph_raw.json
```

Salida:

```json
{
  "total_claims": 0,
  "observable": 0,
  "derivable": 0,
  "inferred": 0,
  "unknown": 0,
  "observable_ratio": 0.0,
  "evidence_coverage": 0.0,
  "inference_ratio": 0.0,
  "anchored_claims": [],
  "unanchored_claims": []
}
```

---

## Criterio de éxito

Todo claim debe tener:

1. Una clasificación epistemológica explícita.
2. Al menos una fuente rastreable (Issue, PR, Commit, Release, Zenodo).

Si no cumple: `classification = inferred`.

---

## Próximo paso

Si `observable_ratio < 0.3`:

- El reporte actual genera más inferencias que evidencia.
- Necesario reescribir el extractor para incluir evidence anchors.
- El producto debe ser "Evidence-Anchored Trajectory Report".

Si `observable_ratio >= 0.5`:

- El reporte contiene trazabilidad real.
- Necesario mejorar la presentación para hacer los anchors visibles.
- El producto puede escalar.
