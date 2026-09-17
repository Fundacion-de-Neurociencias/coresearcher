# SCIENTIFIC INSTRUMENTABILITY MATRIX — SPRINT 66

**Generated**: 2026-08-01T15:48:39.555345+00:00
**Report ID**: INST66-20260801154839

## Scientific Question

> ¿Qué observaciones permitirían distinguir entre explicaciones competidoras?

## Methodology

| Dimension | Question |
|-----------|----------|
| Observable | ¿Existe evidencia directa? |
| Inferible | ¿Puede reconstruirse desde evidencia indirecta? |
| Instrumentable | ¿Al menos una observación capaz de discriminar hipótesis competidoras? |
| Falsable | ¿Puede formularse una condición observacional incompatible? |
| Replicable | ¿Dos investigadores independientes alcanzan conclusiones compatibles? |

## Instrumentability Index

- Escala: 0.0 (no investigable) → 1.0 (plenamente investigable)
- Cálculo: promedio de 5 dimensiones booleanas

## Matrix

| Entity | Observable | Inferible | Instrumentable | Falsable | Replicable | Index | Status |
|--------|------------|-----------|----------------|----------|------------|-------|--------|
| DecisionNode | Yes | Yes | Yes | Yes | Yes | 1.00 | FULLY_INVESTIGABLE |
| Trajectory | No | Yes | Yes | Yes | PARTIAL | 0.80 | FULLY_INVESTIGABLE |
| Convergence | No | Yes | Yes | Yes | PARTIAL | 0.80 | FULLY_INVESTIGABLE |
| Restriction | No | No | Yes | Yes | PARTIAL | 0.60 | INVESTIGABLE_CON_RESTRICCIONES |
| Mechanism | No | No | Yes | Yes | PARTIAL | 0.60 | INVESTIGABLE_CON_RESTRICCIONES |
| Explanation | No | No | Yes | Yes | PARTIAL | 0.60 | INVESTIGABLE_CON_RESTRICCIONES |
| Hypothesis | No | No | Yes | Yes | PARTIAL | 0.60 | INVESTIGABLE_CON_RESTRICCIONES |
| Theory | No | No | Yes | Yes | PARTIAL | 0.60 | INVESTIGABLE_CON_RESTRICCIONES |
| Paradigm | No | No | Yes | Yes | UNKNOWN | 0.40 | INVESTIGABLE_CON_ALTA_RESTRICCION |

## Distribution

| Status | Count |
|--------|-------|
| FULLY_INVESTIGABLE | 3 |
| INVESTIGABLE_CON_RESTRICCIONES | 5 |
| INVESTIGABLE_CON_ALTA_RESTRICCION | 1 |
| INVESTIGABLE_CON_MUY_ALTA_RESTRICCION | 0 |
| NON_INIVESTIGABLE | 0 |

## Mandatory Experiment: Hypothesis, Theory, Restriction

### Hypothesis

- **Observable**: False
- **Inferible**: False
- **Instrumentable**: True
- **Falsable**: True
- **Replicable**: PARTIAL
- **Status**: INVESTIGABLE_CON_RESTRICCIONES

**Conclusion**: NON-INSTRUMENTABLE por observabilidad, pero SÍ instrumentable por falsabilidad. No requiere observación directa. Requiere definir métrica de falsabilidad y novedad.

### Theory

- **Observable**: False
- **Inferible**: False
- **Instrumentable**: True
- **Falsable**: True
- **Replicable**: PARTIAL
- **Status**: INVESTIGABLE_CON_RESTRICCIONES

**Conclusion**: NON-INSTRUMENTABLE por observabilidad, pero SÍ instrumentable por falsabilidad. La teoría de la evolución no es observable pero es investigable por sus predicciones.

### Restriction

- **Observable**: False
- **Inferible**: False
- **Instrumentable**: True
- **Falsable**: True
- **Replicable**: PARTIAL
- **Status**: INVESTIGABLE_CON_RESTRICCIONES

**Conclusion**: NON-INSTRUMENTABLE por observabilidad, pero SÍ instrumentable por manipulación. Si eliminamos la restricción y el comportamiento cambia, estaba ahí. Como el gen en 1850.

## Key Finding

> Todas las entidades analizadas son al menos INVESTIGABLE_CON_ALTA_RESTRICCION. Ninguna es NON_INVESTIGABLE. Esto significa que, con instrumentación adecuada, todas pueden ser estudiadas científicamente.

## Paradigm Shift

> El problema no es generar explicaciones. El problema es diseñar observaciones capaces de decidir entre ellas.

---

*Este sprint es exclusivamente metodológico. No genera hipótesis, no reactiva EHG, no modifica arquitectura.*
*Ver: docs/EPISTEMIC_GAP_CONCEPT.md*
