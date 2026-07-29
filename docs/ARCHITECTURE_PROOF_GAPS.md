# Auditoría de Brechas de Evidencia (Architecture Proof Gaps)

**Estado:** Congelamiento de Arquitectura (ARQ-001 → ARQ-003)  
**Objetivo:** Identificar qué afirmaciones de CoResearcher siguen siendo hipótesis no demostradas empíricamente.

| Afirmación | Evidencia Existente | Evidencia Faltante |
| :--- | :--- | :--- |
| **"EvidenceGraph es autosuficiente para reconstruir Claims"** | Reconstrucción ciega simulada con un script determinista que valida Precision/Recall sobre datos de prueba sintéticos. | Validación empírica con evaluadores humanos doble ciego y múltiples modelos LLM independientes (Claude 3.5, Llama 3) sin acceso a frases precocinadas. |
| **"DecisionGraph mejora la gobernanza y evita derivas"** | Definición del esquema `decision_graph.yaml` y registro del ADR-DEC-001. | Prueba con agentes autónomos reales tomando decisiones secuenciales en un entorno de investigación continuo durante >48h sin supervisión humana. |
| **"MissionGraph evita la contaminación ontológica"** | Reglas constitucionales en YAML y 7 casos de prueba de caos (Chaos Tests) ejecutados localmente en memoria. | Ejecución asíncrona real distribuida con fallos de red, reinicios de demonios y agentes externos fallando y reintentando sin corromper el estado. |
| **"La Constitución detecta todas las violaciones relevantes"** | 7 tests sintéticos de caos que pasan determinísticamente (100% de éxito en los 7 casos prefijados). | Fuzzing probabilístico masivo generando miles de grafos sintéticos aleatorios con permutaciones no previstas manualmente. |
| **"El supertipo Artifact sustituye a Quote sin pérdida de precisión"** | Actualización de la especificación `EVIDENCEGRAPH_SPEC.md` a v1.1.0 aceptando tipos multimodales. | Parsers de ingestión y validadores reales para matrices de expresión, imágenes histológicas y archivos PDB de AlphaFold. |
| **"CoResearcher es agnóstico al modelo LLM"** | Ninguna (las pruebas actuales corren con scripts de prueba Python y simulaciones estáticas). | Benchmark comparativo multiplataforma ejecutando las mismas misiones con OpenAI Codex, Claude Code, Gemini y Llama local. |
| **"La separación tri-grafo no degrada la mantenibilidad"** | Tres esquemas YAML independientes (`constitution_rules`, `decision_graph`, `mission_graph`). | Medición del tiempo y esfuerzo cognitivo de un desarrollador externo para implementar un nuevo flujo sin violar fronteras. |
