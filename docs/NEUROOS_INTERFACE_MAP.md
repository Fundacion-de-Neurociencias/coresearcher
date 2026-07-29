# Mapa de Interfaces de NeuroOS (NEUROOS INTERFACE MAP)

**Versión:** 1.0.0  
**Directiva:** ANTIGRAVITY-002  
**Estado:** Activo - Especificación de Contratos Inter-Sistema

Este documento especifica cómo se comunican entre sí los subsistemas especializados de NeuroOS, los contratos formales que rigen el intercambio de datos y los formatos de mensaje.

---

## 1. Diagrama de Flujo de Interfaces

```text
[NeuroOS Kernel] ──(1. Brief JSON)──> [ManuEl Runtime]
                                             │
                                   (2. Artifact / Evidence)
                                             ▼
[EditXT] <──(3. EvidenceGraph v1.1)── [CoResearcher]
   │                                         ▲
(4. ReviewGraph)                             │
   ▼                                (5. Verified Evidence)
[AI Scientists / World Model] ───────────────┘
   │
(6. Hypothesis Payload)
   ▼
[GeneForge Ecosystem] ──(7. BioDSL AST)──> [PharmaOracle / Neurodiagnoses]
```

---

## 2. Definición Detallada de Contratos de Interfaz

### Interfaz 1: `Kernel Dispatch Interface` (NeuroOS Kernel → ManuEl Runtime)
* **Contrato:** `schemas/mission_graph.yaml` (Nodo `Brief`).
* **Formato:** JSON determinista.
* **Payload:** Contexto, herramientas autorizadas, criterio de éxito inmutable.
* **Garantía:** El runtime de agentes no puede alterar el `Brief`.

### Interfaz 2: `Evidence Ingestion Interface` (ManuEl Runtime → CoResearcher)
* **Contrato:** `EVIDENCEGRAPH_SPEC.md` v1.1.0.
* **Formato:** JSON (`Claim` + `Artifact` + `Source`).
* **Payload:** Resultados empíricos obtenidos por la ejecución de herramientas.
* **Garantía:** CoResearcher rechaza cualquier nodo que contenga calificaciones de calidad o intenciones de trabajo.

### Interfaz 3: `Audit Export Interface` (CoResearcher → EditXT)
* **Contrato:** `BOUNDARY_WITH_EDITXT.md` & `constitution_rules.yaml`.
* **Formato:** Grafo JSON (DAG 100% acíclico).
* **Payload:** `EvidenceGraph` completo para revisión crítica.
* **Garantía:** EditXT lee el grafo de forma strictly de solo lectura.

### Interfaz 4: `Quality Feedback Interface` (EditXT → AI Scientists / World Model)
* **Contrato:** `ReviewGraph Schema`.
* **Formato:** JSON (`ReviewFinding`, `SeverityScore`, `RefactoringTarget`).
* **Payload:** Veredictos de inconsistencia o lagunas de conocimiento detectadas en la literatura.
* **Garantía:** Los veredictos de EditXT jamás ingresan al `EvidenceGraph` de CoResearcher.

### Interfaz 5: `Hypothesis Pipeline Interface` (AI Scientists / World Model → GeneForge Ecosystem)
* **Contrato:** `BOUNDARY_WITH_AI_SCIENTISTS.md`.
* **Formato:** JSON / Event Payload (`HypothesisTarget`).
* **Payload:** Parámetros de dianas genómicas o mecanismos de empalme a diseñar in silico.
* **Garantía:** Una hipótesis no es un hecho; debe compilarse y validarse experimentalmente.

### Interfaz 6: `BioDSL Compilation Interface` (GeneForge Ecosystem → PharmaOracle / Neurodiagnoses)
* **Contrato:** Especificación GFL (Sintaxis 2-space indentation, `gf/parser.py`).
* **Formato:** Código GFL / AST Compilado.
* **Payload:** Estructura genómica o variantes para validación clínica/farmacológica.
* **Garantía:** Validación sintáctica estricta antes del análisis biológico empírico.

### Interfaz 7: `Clinical Validation Interface` (Neurodiagnoses → CoResearcher)
* **Contrato:** Directiva de Rigor Científico & EBRAINS REST API.
* **Formato:** JSON (`Source` vinculada a PMID/DOIs reales y datos de pacientes anonimizados).
* **Payload:** Criterios clínicos validados (ej. McKeith 2017 para DLB) y marcadores biofísicos.
* **Garantía:** Queda prohibida la simulación/stubbing de respuestas diagnósticas.
