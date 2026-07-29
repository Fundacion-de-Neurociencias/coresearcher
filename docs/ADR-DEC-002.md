# ADR-DEC-002: Evidence Never Contains Intent

**Version 1.0.0** - Architecture Decision Record  
**Status**: Canonical Reference - Gobernanza Ontológica

## 1. Contexto

Durante la revisión adversarial de la fase ARQ-002, se detectó una vulnerabilidad semántica grave al enlazar el `DecisionGraph` con el `EvidenceGraph`. Al permitir que las decisiones ruteen la investigación futura hacia aserciones potenciales, existía el riesgo de que el `EvidenceGraph` comenzara a absorber metadatos de intención (e.g., `selected_because`, `priority`, `target`).

El `EvidenceGraph` fue diseñado estrictamente como un registro inmutable retrospectivo (lo que se sabe empíricamente y su procedencia). Mezclar trabajo en curso (intención) con conocimiento demostrado (evidencia) erosiona la pureza ontológica del sistema y lo degrada a un simple gestor de tareas.

## 2. Decisión

Formalizamos la regla constitucional fundamental: **La evidencia nunca contiene intención.**

1. Un nodo `Claim` o `Artifact` dentro del `EvidenceGraph` existe única y exclusivamente para describir el estado del conocimiento y su anclaje empírico.
2. Queda estrictamente prohibido incluir campos como `priority`, `intent`, `hypothesis`, `selected_because`, o `target_date` dentro de cualquier nodo del `EvidenceGraph`.
3. Cualquier representación de trabajo futuro, intención direccional, o gobernanza residirá exclusivamente en el `DecisionGraph` o en el `MissionGraph`.

## 3. Consecuencias

### Positivas
- Preserva la inmutabilidad y la pureza del `EvidenceGraph` como una estructura de datos apta para auditoría científica pura.
- Evita la fuga semántica donde la "urgencia" o la "dirección estratégica" de un programa de investigación corrompe la interpretación algorítmica de la evidencia misma.

### Negativas / Restricciones
- Aumenta la complejidad del motor de consultas. Para responder a la pregunta *"¿Qué evidencia validamos la semana pasada a causa de la decisión estratégica X?"*, el sistema de base de datos deberá realizar un *join* transversal entre el `DecisionGraph` y el `EvidenceGraph`, en lugar de simplemente filtrar atributos directamente sobre los claims.

## 4. Implementación Referencial
La regla queda enlazada a las políticas constitucionales a través de `schemas/constitution_rules.yaml`. Cualquier grafo de evidencia que contenga campos de intención será automáticamente rechazado.
