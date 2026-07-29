# Plan de Validación Empírica (ARQ-001 → ARQ-003)

**Propósito:** Validar empíricamente la utilidad, escalabilidad, mantenibilidad y auditabilidad de CoResearcher **sin modificar ni extender la arquitectura congelada**.

---

## 1. Validación de Utilidad (Utility Benchmark)

* **Hipótesis a probar:** Un tercero independiente puede reconstruir la cadena de conocimiento completa usando únicamente el `EvidenceGraph` sin pérdida de significado.
* **Diseño del Experimento (Double-Blind Metric Evaluation):**
  1. Extraer 50 papers biomédicos reales (OpenAccess / PubMed).
  2. Generar grafos de evidencia para 200 Claims clave.
  3. Ocultar el texto fuente original.
  4. Entregar el `EvidenceGraph` a 3 LLMs distintos (Claude 3.5 Sonnet, GPT-4o, Llama 3 70B) y a 2 evaluadores humanos expertos.
  5. **Métrica de Éxito:** Precision ≥ 0.90 y Recall ≥ 0.85 en la reconstrucción semántica del Claim original sin alucinación.

---

## 2. Validación de Escalabilidad (Scalability & Performance Benchmark)

* **Hipótesis a probar:** El sistema soporta 100.000 nodos sin colapsar el tiempo de validación constitucional ni degradar el almacenamiento.
* **Diseño del Experimento:**
  1. Desarrollar un generador de grafos masivos cumpliendo estrictamente `constitution_rules.yaml`.
  2. Evaluar el tiempo de validación con el validador en memoria actual frente a una persistencia en SQLite / GraphDB indexado.
  3. **Puntos de Corte:**
     - 1.000 nodos: < 100 ms.
     - 10.000 nodos: < 1.000 ms.
     - 100.000 nodos: < 5.000 ms.
  4. **Métrica de Éxito:** La validación constitucional no debe ser el cuello de botella del runtime.

---

## 3. Validación de Auditabilidad por Terceros (Adversarial Auditability Test)

* **Hipótesis a probar:** Dado solo el `DecisionGraph` y el `MissionGraph`, un auditor externo puede explicar la secuencia de acciones y descartar derivas no autorizadas.
* **Diseño del Experimento:**
  1. Simular 10 trazas complejas de investigación distribuida con 5 subagentes.
  2. Inyectar 2 anomalías arbitrarias (ej. un agente ejecutando una acción no spawneada por ninguna `Mission`).
  3. Ejecutar el validador automático de gobernanza.
  4. **Métrica de Éxito:** 100% de detección de acciones no autorizadas y 0% falsos positivos en trazas legítimas.

---

## 4. Validación de Mantenibilidad (Cognitive Load & Developer Ergonomics)

* **Hipótesis a probar:** La separación tri-grafo reduce la complejidad de depuración cuando ocurre un error en producción.
* **Diseño del Experimento:**
  1. Presentar 5 fallos de producción simulados a desarrolladores/agentes que no participaron en el diseño.
  2. Medir el tiempo medio de localización del error (Mean Time To Diagnose - MTTD) comparando el enfoque Tri-Grafo de CoResearcher contra una traza de logs lineal tradicional.
  3. **Métrica de Éxito:** Reducción del MTTD de al menos un 40%.
