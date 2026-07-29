# Comparativa Competitiva y Ventaja Diferencial (Competitor Baseline)

**Objetivo:** Comparar conceptual y empíricamente a CoResearcher frente a los paradigmas existentes de recuperación y gestión de conocimiento en agentes de IA, separando las ventajas **demostradas** de las **teóricas**.

---

## 1. Matriz Comparativa

| Enfoque | Trazabilidad Computable | Separación Ontológica (Conocimiento / Gobernanza / Ejecución) | Auditoría Constitucional Inmutable | Coste e Infraestructura | Ventaja Real Demostrada | Ventaja Teórica (No Proada) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Traditional RAG** | ❌ No (Basado en similitud de embeddings, caja negra). | ❌ No (Mezcla fragmentos de texto con prompt context). | ❌ No. | Bajo (VectorDB). | Facilidad de implementación rápida. | Alta precisión en respuestas cortas. |
| **Microsoft GraphRAG** | ⚠️ Parcial (Grafo de entidades y comunidades). | ❌ No (Mezcla conocimiento extraído con resúmenes LLM). | ❌ No. | Muy Alto (Múltiples pasadas LLM para construir resúmenes). | Excelente para resúmenes globales temáticos. | Robustez ante consultas complejas de nivel macro. |
| **OpenAI / Google Deep Research** | ⚠️ Parcial (Citas textuales simples en formato markdown). | ❌ No (La trayectoria vive en la ventana de contexto del agente). | ❌ No. | Alto (Múltiples llamadas a APIs propietarias). | Gran capacidad de redacción y síntesis fluida. | Exhaustividad en la cobertura de búsqueda. |
| **Claude Code / Codex Workflows** | ❌ No (Logs de herramientas y bash execution). | ❌ No (Tool calling directo). | ❌ No. | Medio (Ejecución local CLI). | Gran capacidad de refactorización y navegación de código. | Coordinación entre subagentes de desarrollo. |
| **Evidence-based KGs (Hetionet, BioCypher)** | ---------------+ Alta (Estructura formal). | ⚠️ Parcial (Solo representa conocimiento estático). | ❌ No (Esquemas fijos, sin gobernanza ejecutiva). | Medio (Bases de datos de grafos como Neo4j). | Rigor absoluto en dominios biofarmacéuticos. | Escalabilidad a millones de relaciones curadas. |
| **CoResearcher (ARQ-001→003)** | ✅ **100% Determinista (DAG)**. | ✅ **Sí (Tri-Grafo: Evidence, Decision, Mission)**. | ✅ **Sí (Constitution-as-Code & Chaos Tests)**. | **Muy Bajo (Zero-Infra, JSON/YAML)**. | **Garantía absoluta de no-evaluación y detección de violaciones fronterizas en tiempo real.** | **Inmunidad total a la deriva ontológica en tareas de investigación autónomas de >48h.** |

---

## 2. Ventajas Diferenciales Reales vs Teóricas

### Ventajas Reales (Demostradas por Código y Chaos Tests)
1. **Verificabilidad Constitucional Automática:** Ningún otro framework de agentes valida en tiempo real si el resultado viola leyes de frontera (ej. intentar emitir calidad o generar hipótesis sin permiso) mediante Chaos Testing determinista.
2. **Ausencia de Puntuación Falsa (Sin Trust Scores ficticios):** A diferencia de RAG o GraphRAG que intentan calcular distancias de similitud o confianzas simuladas, CoResearcher ofrece solo *Evidence Descriptors* estructurales purios.

### Ventajas Teóricas (Pendientes de Validación Empírica)
1. **Superioridad en Investigaciones Científicas Complejas:** Aún no se ha probado que un agente usando CoResearcher descubra o sintetice mejor evidencia científica que un flujo de Deep Research tradicional.
2. **Escalabilidad de la Ejecución Distribuida:** La triada `Mission → Brief → Execution` promete que N agentes pueden trabajar asíncronamente sin desincronizarse, pero falta demostrarlo en un entorno de producción masivo.
