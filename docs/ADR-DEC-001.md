# ADR-DEC-001: Decision ≠ Action (El DecisionGraph)

**Version 1.0.0** - Architecture Decision Record  
**Status**: Canonical Reference - Gobernanza Ontológica

## 1. Contexto

Hasta la versión ARQ-001, CoResearcher operaba como un *Traceability Engine* puro. El sistema modelaba eficientemente el "Qué" (a través de `ACTION-XXXXXX`) y el "Dónde" (a través del `EvidenceGraph` y `CLAIM-XXXXXX`).
Sin embargo, el sistema padecía de un vacío fundamental en su modelo de gobernanza: **era ciego a la intencionalidad**. 

Podíamos auditar que el agente X extrajo el claim Y de la fuente Z, pero no podíamos auditar por qué el agente X decidió investigar esa fuente Z descartando la fuente W. A medida que el sistema escala, esta omisión impide gobernar las estrategias de investigación y el retorno de inversión (ROI) de los recursos algorítmicos asignados.

## 2. Decisión

Formalizamos la **Decisión** como una primitiva ontológica de primer orden, estrictamente diferenciada de la **Acción**.
- **Action (`ACTION-XXXXXX`)**: Es mecanicista. Es la ejecución física de una tarea (ej. leer un PDF, invocar una API, procesar un texto).
- **Decision (`DECISION-XXXXXX`)**: Es teleológica y direccional. Es un acto de gobernanza que asigna recursos, descarta alternativas y provee una justificación racional basada en un estado de evidencia existente.

Para soportar esta primitiva, se introduce el **DecisionGraph**.

## 3. Relación Estructural

El `DecisionGraph` no reemplaza al `EvidenceGraph`; lo envuelve.

1. Un nodo `DECISION` se ancla a un estado de evidencia en el tiempo (`based_on`: [EG-0001, EG-0002]).
2. Un nodo `DECISION` produce directivas de investigación o prioridades, que desencadenan misiones (`directed_towards`: [CLAIM-XXXXXX]).
3. Crucialmente, un nodo `DECISION` documenta permanentemente las ramas no exploradas (`alternatives_discarded`), habilitando la trazabilidad contrafactual.

## 4. Consecuencias

### Positivas
- CoResearcher transiciona exitosamente de ser un *traceability engine* a un *governance engine* maduro.
- La responsabilidad algorítmica pasa a ser medible. Podemos auditar la calidad del "decididor" comparando el ratio de éxito de sus decisiones históricas.
- Provee un *log* de entrenamiento de alto valor ("Decision History Value") para futuros modelos de toma de decisiones estratégicas.

### Negativas / Riesgos
- Añade complejidad estructural a la capa de registro.
- Requiere que los agentes ejecutores sean capaces de verbalizar su *rationale* antes de bifurcar flujos de ejecución costosos, lo que aumenta el consumo de tokens y la latencia en nodos de orquestación.

## 5. Implementación Referencial
El esquema de datos que soporta esta decisión queda formalizado en `schemas/decision_graph.yaml`.
