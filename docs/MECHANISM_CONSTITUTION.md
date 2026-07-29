# Mechanism Constitution
## CoResearcher Theory of Scientific Mechanisms

## Pregunta 1: ¿Qué es un mecanismo?

Un **mecanismo** es una secuencia explicativa causal que conecta observaciones con fenómenos, representando **cómo** algo ocurre, no solo **que** ocurre.

### Definición Formal

```
Un mecanismo es un conjunto estructurado de relaciones causales
que explica el vínculo entre variables observables y fenómenos complejos,
y que puede ser puesto a prueba mediante predicciones empíricas.
```

### Propiedades Fundamentales

1. **Causalidad explícita** - Las relaciones son orientadas y explicativas
2. **Testabilidad** - Genera predicciones verificables
3. **Modularidad** - Puede combinarse con otros mecanismos
4. **Evolución** - Puede modificarse con nueva evidencia

---

## Pregunta 2: ¿Qué diferencia hay entre?

### Claim vs Finding vs Mechanism vs Model vs Theory

| Nivel | Qué | Ejemplo | Mutabilidad |
|-------|-----|---------|-------------|
| **Claim** | Observación atómica | "pTau217 predicts AD (r=0.78)" | Baja - es un hecho reportado |
| **Finding** | Distilación estructurada | "pTau217 → amyloid pathway (effect=0.78)" | Media - puede re-evaluarse con nueva evidencia |
| **Mechanism** | Explicación causal | "pTau217 mediates stress response that triggers amyloid aggregation via MECH-X" | Alta - se refinan con evidencia |
| **Model** | Conjunto de mecanismos | "Amyloid cascade + Tau propagation + Inflammation" | Media - se reemplaza si falla |
| **Theory** | Marco explicativo amplio | "Proteostasis failure in neurodegeneration" | Muy alta - paradigma científico |

---

## Pregunta 3: ¿Puede existir un mecanismo falso?

**Sí.** Un mecanismo puede ser:
- Incorrecto (predicciones refutadas)
- Incompleto (faltan pasos intermedios)
- Superficial (el mecanismo real es diferente)

### Atributos de Validación

```yaml
mechanism:
  id: MECH-000001
  name: "Neuronal Stress-Mediated Amyloid Deposition"
  support:  # Evidencia a favor
    - CLAIM-00123
    - FIND-00456
    - REPLICATION-007
  contradictions:  # Evidencia en contra
    - CHALLENGE-008
  confidence: 0.3  # Basado en apoyo/refutación
  replications: 0
  challenges: 0
  institution_count: 0
  trust_score: 0.5  # Dinámico, de Participation Layer
```

---

## Pregunta 4: ¿Cómo nace un mecanismo?

### Bottom-up (Inductivo)

```
Finding A    Finding B    Finding C
    ↓            ↓            ↓
   [ENTITY-X] → [ENTITY-Y] → [ENTITY-Z]
         ↓
   "Hay una relación causal oculta"
         ↓
      MECHANISM (hipótesis)
```

### Top-down (Deductivo)

```
Hypothesis: "pTau217 is protective response"
    ↓
What mechanism would explain this?
    ↓
MECH-X: stress → pTau217 upregulation → amyloid sequestration
    ↓
Predictions para test
    ↓
Predicciones refutadas → mecanismo rechazado
Predictions confirmadas → mecanismo reforzado
```

---

## Pregunta 5: ¿Cómo muere un mecanismo?

Los mecanismos siguen un ciclo de vida científico:

```
NACIMIENTO (birth)
    ↓
CREACIÓN → {support, confidence=0.1}
    ↓
CRECIMIENTO (growth) → CONFIRMACIONES, REPLICACIONES
    ↓
CONVERGENCIA → confianza alta, múltiples apoyos
    ↓
REFUTACIÓN o degradación progresiva
    ↓
MUERTE (death) → challenges > support, confidence → 0
```

### Operaciones sobre Mecanismos

| Operación | Qué hace | Resultado |
|-----------|----------|-----------|
| **CONFIRM** | Evidencia apoya el mecanismo | +confidence, +trust_score |
| **REJECT** | Evidencia refuta el mecanismo | -confidence, -trust_score |
| **FORK** | Crear variante del mecanismo | MECH-fork (nueva ruta) |
| **MERGE** | Combinar dos mecanismos | MECH-combined (más general) |
| **SPLIT** | Dividir mecanismo complejo | MECH-A, MECH-B (más específicos) |

---

## Primitivas Participation para Mecanismos

```
MECH-000001
├── support (CLAIM/FINDING que lo respaldan)
├── contradict (CLAIM/FINDING que lo refutan)
├── replicate (evidencia de replicación)
├── challenge (análisis crítico)
├── fork (mecanismo derivado)
└── merge_request (propuesta de combinación)
```

---

## Conclusión

Los mecanismos son el **núcleo del descubrimiento científico compartido**. 

No los claims. No los papers. 

**Los mecanismos son las explicaciones que los científicos discuten, defienden, refutan y evolucionan colectivamente.**

Este es el activo que generará el verdadero moat de CoResearcher: una red acumulativa de mecanismos con su historia de participación científica.