# Registro de Deuda Técnica (Technical Debt Register)

**Estado:** Congelamiento de Arquitectura (ARQ-001 → ARQ-003)  
**Objetivo:** Consolidar y priorizar por riesgo todas las advertencias, limitaciones e ineficiencias identificadas en el sistema.

---

## Prioridad 1: Riesgo Crítico (Impacta Escalabilidad y Producción)

### `DEBT-001`: Validación Lenta en Memoria para Grafos Grandes
- **Descripción:** El validador `validate_constitution.py` procesa listas JSON en memoria mediante iteración secuencial. En pruebas sintéticas, 10.000 nodos requirieron ~53 segundos. A 100.000 nodos el proceso falla por timeout/memoria.
- **Riesgo:** Cuello de botella severo que impide el uso del sistema a escala industrial.
- **Mitigación Planificada:** Migrar la ejecución de validación a un motor indexado (SQLite / DuckDB / Graph engine) sin cambiar las reglas del esquema.

---

## Prioridad 2: Riesgo Alto (Impacta Rigor y Fidelidad)

### `DEBT-002`: Reconstrucción Ciega Basada en Simulaciones Deterministas
- **Descripción:** Las pruebas de `advanced_claim_reconstruction.py` utilizan prompts simulados y frases estáticas prefijadas para validar Precision/Recall.
- **Riesgo:** Falso sentido de seguridad. No se ha probado si un LLM real no determinista alucina cuando recibe el grafo aislado de texto.
- **Mitigación Planificada:** Reemplazar el mock del script por llamadas reales en modo ciego a APIs de LLM en la suite de validación empírica.

### `DEBT-003`: Multimodalidad de `Artifact` No Implementada en Parsers
- **Descripción:** Aunque `EVIDENCEGRAPH_SPEC.md` v1.1.0 define el supertipo `Artifact` para soportar imágenes, tablas y estructuras 3D (PDB), actualmente no existen parsers ni convertidores reales de este tipo de objetos en el código.
- **Riesgo:** El soporte multimodal es solo teórico en la especificación y fallará si se ingesta un binario real.
- **Mitigación Planificada:** Construir parsers de prueba para artefactos biomédicos (e.g. archivos PDB de AlphaFold).

---

## Prioridad 3: Riesgo Medio (Impacta Cobertura y Ergonómia)

### `DEBT-004`: Fuzzing Constitucional Inexistente
- **Descripción:** Los Chaos Tests constan de 7 casos de prueba estáticos escritos manualmente.
- **Riesgo:** Un caso borde no anticipado (e.g., combinación de ciclos con nodos no estándar) podría eludir la validación constitucional.
- **Mitigación Planificada:** Implementar un generador estocástico de grafos (fuzzer) para someter el validador a 10.000 permutaciones aleatorias.

### `DEBT-005`: Inexistencia de Cola de Persistencia para `MissionGraph`
- **Descripción:** El `MissionGraph` está especificado conceptualmente y en esquema YAML (`mission_graph.yaml`), pero no existe una cola de tareas persistente (ej. SQLite / Redis / Daemon) que gestione el ciclo de vida de los *Briefs*.
- **Riesgo:** Si el orquestador se reinicia, las misiones en curso se pierden.
- **Mitigación Planificada:** Implementar un almacenamiento de estado liviano para la capa de ejecución.

---

## Prioridad 4: Riesgo Bajo (Higiene y Compatibilidad)

### `DEBT-006`: Dependencia de Codificación `cp1252` en Windows
- **Descripción:** Scripts que imprimen por consola (como el benchmark de escalabilidad o el CLI de `skillspector`) fallan al renderizar caracteres UTF-8/emojis si no se fuerza `$env:PYTHONUTF8=1`.
- **Riesgo:** Errores molestos en la ejecución CLI en entornos Windows sin UTF-8 por defecto.
- **Mitigación Planificada:** Forzar el manejo explícito de codificación `utf-8` en todas las salidas por stream/console.
