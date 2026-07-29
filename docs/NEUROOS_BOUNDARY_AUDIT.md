# Auditoría de Solapamientos y Fronteras de NeuroOS (NEUROOS BOUNDARY AUDIT)

**Versión:** 1.0.0  
**Directiva:** ANTIGRAVITY-002  
**Estado:** Activo - Diagnóstico de Invasiones Ontológicas

Este documento responde a la pregunta clave: **¿Hay dos sistemas haciendo lo mismo dentro de NeuroOS?** Se analizan los solapamientos potenciales, las violaciones históricas y las salvaguardas constitucionales para eliminarlos.

---

## 1. Matriz de Solapamientos Identificados y Resolución

| Zona de Fricción | Sistemas en Conflicto | Descripción del Solapamiento | Estado de Resolución | Salvaguarda Aplicada |
| :--- | :--- | :--- | :--- | :--- |
| **Evaluación de Calidad de Evidencia** | **CoResearcher** vs **EditXT** | CoResearcher intentaba calcular `trust_score` o `confidence`, invadiendo la función de evaluación de EditXT. | **RESUELTO (ARQ-003)** | Purgado el *Trust Engine* de CoResearcher. Toda evaluación de calidad ahora reside exclusivamente en EditXT (`ReviewGraph`). |
| **Generación de Hipótesis y Descubrimiento** | **CoResearcher** vs **AI Scientists / World Model** | CoResearcher corría el riesgo de inferir nuevos claims no demostrados, actuando como generador científico. | **RESUELTO (ARQ-001)** | Regla `ARQ-BD-002`: Prohibido inyectar nodos `Hypothesis`, `Experiment` o `Discovery` en el `EvidenceGraph`. |
| **Generación de Código Biológico** | **AI Scientists** vs **GeneForge Ecosystem** | AI Scientists generaba secuencias y construcciones directas sin pasar por el compilador sintáctico. | **RESUELTO (ANTIGRAVITY-002)** | Delimitación: AI Scientists produce la especificación de la hipótesis; GeneForge es el único facultado para parsear y compilar sintaxis BioDSL (`gf/parser.py`). |
| **Diagnóstico Clínico vs Farmacogenómica** | **Neurodiagnoses** vs **PharmaOracle** | Solapamiento potencial en la evaluación de biomarcadores en enfermedades neurodegenerativas (ej. p-tau217 en Alzheimer). | **RESUELTO (ANTIGRAVITY-002)** | Delimitación: Neurodiagnoses evalúa criterios clínicos diagnósticos (EBRAINS / McKeith). PharmaOracle se limita al docking y binding fármaco-diana. |
| **Gestión de Misiones y Trabajo en Curso** | **ManuEl Runtime** vs **NeuroOS Kernel** | Agentes en runtime intentaban modificar sus propias intenciones y redefinir misiones sobre la marcha. | **RESUELTO (ARQ-003)** | Regla `ARQ-BD-003`: El trabajo en curso vive en `MissionGraph` bajo el patrón `Brief` inmutable dispatched desde el Kernel de NeuroOS. |

---

## 2. Reglas Constitucionales de Inviolabilidad de Frontera

1. **Regla de la Verdad Factual (CoResearcher Boundary):** CoResearcher registra lo que se sabe. Nunca evalúa lo que se sabe ni decide lo que se debe hacer.
2. **Regla de la Crítica (EditXT Boundary):** EditXT juzga la calidad. Nunca inyecta evidencia nueva ni modifica los datos de origen.
3. **Regla de la Especulación (AI Scientists Boundary):** AI Scientists propone hipótesis. Ninguna hipótesis se convierte en evidencia sin pasar por una misión de validación empírica.
4. **Regla de la Sintaxis Biológica (GeneForge Boundary):** Todo código GFL debe compilar mediante `gf/parser.py` cumpliendo la indentación de 2 espacios. Ningún otro módulo puede emitir ASTs biológicos.
5. **Regla del Rigor Clínico (Neurodiagnoses Boundary):** Prohibición absoluta de usar respuestas falsas o datos simulados (mocking/stubbing) en diagnósticos neuroclínicos.
