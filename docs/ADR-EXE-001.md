# ADR-EXE-001: Ejecución Distribuida Auditable (MissionGraph)

**Version 1.0.0** - Architecture Decision Record  
**Status**: Canonical Reference - Ejecución Distribuida

## 1. Contexto

La arquitectura ARQ-001 resolvió la trazabilidad retrospectiva (Qué sabemos) con el `EvidenceGraph`.
La arquitectura ARQ-002 resolvió la gobernanza direccional (Por qué investigamos) con el `DecisionGraph`.

Sin embargo, para cerrar el ciclo, carecíamos de una estructura formal para el "Cómo lo hacemos" en un entorno de orquestación multi-agente (NeuroOS). La ausencia de esta estructura forzaba al `EvidenceGraph` a intentar registrar el estado del "trabajo en curso", generando paradojas temporales (Claims huérfanos).

## 2. Decisión

Formalizamos la ontología de **Ejecución Distribuida Auditable** bajo el patrón `Mission → Brief → Execution`, consolidada en el **MissionGraph**.

1. **Mission (`MISSION-XXXXXX`)**: Un objetivo acotado y rastreable derivado directamente de una `DECISION`. Ejemplo: "Extraer claims de la literatura reciente sobre p-tau217".
2. **Brief (`BRIEF-XXXXXX`)**: Un paquete contextual autocontenido, determinista e inmutable que se entrega al agente ejecutor. Especifica instrucciones, herramientas permitidas, y el criterio de éxito explícito. Esto permite que el agente opere de manera desconectada (stateless) respecto al orquestador central.
3. **Execution (`EXEC-XXXXXX` o `ACTION-XXXXXX`)**: La traza física (logs, tool calls, retries) del agente intentando cumplir el Brief. Esta traza resultará en la creación de nuevos componentes del `EvidenceGraph` (como Claims y Artifacts) si es exitosa.

## 3. Consecuencias

### Positivas
- **Desacoplamiento Estricto:** Protege al `EvidenceGraph` de cualquier estado incompleto, especulativo o en curso.
- **Escalabilidad Masiva:** Permite encolar, distribuir y paralelizar miles de `Briefs` a través de múltiples agentes sin bloqueos, posibilitando una arquitectura asíncrona real.
- **Trazabilidad de Ejecución:** Si un subagente falla, la falla se registra en el `Execution` node asociado al `Brief`, permitiendo una analítica de "Agent Reliability" sin afectar el conocimiento científico demostrado.

### Negativas
- Añade una tercera capa ontológica al sistema (Evidence, Decision, Mission), aumentando la carga cognitiva para desarrolladores e integradores externos.

## 4. Implementación Referencial
El modelo de datos y validaciones queda instanciado en el archivo `schemas/mission_graph.yaml`.
