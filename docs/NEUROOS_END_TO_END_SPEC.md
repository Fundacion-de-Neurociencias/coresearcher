# Especificación de la Prueba End-to-End de NeuroOS (NEUROOS END-TO-END SPEC)

**Versión:** 1.0.0  
**Directiva:** ANTIGRAVITY-002  
**Caso de Uso Canónico:** Flujo Multidisciplinar de Investigación y Diagnóstico en Alzheimer / Tauopatías

---

## 1. El Objetivo de la Prueba

Demostrar empíricamente que NeuroOS puede coordinar un flujo de trabajo científico completo a través de **6 sistemas independientes**, sin que ningún sistema invada el dominio de otro y garantizando la trazabilidad auditable de origen a fin.

---

## 2. Diagrama de la Prueba End-to-End

```text
[ Paper Científico (Alzheimer / p-tau217) ]
                    │
                    ▼
          (1) CoResearcher
                    │  Ingesta evidencia inmutable
                    ▼
             [ EvidenceGraph ]
                    │
                    ▼
            (2) EditXT
                    │  Audita consistencia y vacíos
                    ▼
              [ ReviewGraph ]
                    │
                    ▼
       (3) AI Scientists / World Model
                    │  Formula hipótesis de modulación de empalme
                    ▼
           [ Hypothesis Spec ]
                    │
                    ▼
            (4) GeneForge
                    │  Compila secuencia GFL (gf/parser.py)
                    ▼
         [ BioDSL AST / Candidate ]
                    │
                    ▼
            (5) PharmaOracle
                    │  Simula binding fármaco-diana
                    ▼
           [ Binding Report ]
                    │
                    ▼
            (6) Neurodiagnoses
                    │  Valida contra criterios clínicos (EBRAINS)
                    ▼
    [Clinical Interpretation & Report ]
```

---

## 3. Desglose Paso a Paso del Flujo

### Paso 1: Ingesta de Evidencia (CoResearcher)
* **Acción:** Ingesta de literatura reciente sobre biomarcadores plasmáticos de p-tau217 en Alzheimer.
* **Salida:** `EvidenceGraph` (v1.1.0) conteniendo `Claims` anclados a `Artifacts` de fuente primaria (PMIDs/DOIs).
* **Validación de Frontera:** Sin calificaciones de calidad ni `trust_scores`.

### Paso 2: Auditoría Crítica de Calidad (EditXT)
* **Acción:** EditXT analiza el `EvidenceGraph` y detecta una laguna de conocimiento: la fosforilación de T217 está vinculada a patología Tau, pero falta evidencia sobre la modulación del empalme alternativo del exon 10 en MAPT.
* **Salida:** `ReviewGraph` registrando la brecha de evidencia (`ReviewFinding`).

### Paso 3: Formulación de Hipótesis (AI Scientists / World Model)
* **Acción:** AI Scientists consume el `ReviewGraph` y el `EvidenceGraph` y propone la hipótesis de que modular el exon 10 mediante oligonucleótidos sintéticos reducirá la agregación patológica.
* **Salida:** `Hypothesis Target Payload`.

### Paso 4: Compilación Biológica (GeneForge)
* **Acción:** GeneForge recibe la diana y compila la secuencia biológica correspondiente escribiendo y parseando código GFL mediante `gf/parser.py`.
* **Salida:** AST válido en sintaxis GFL (2-space indentation).

### Paso 5: Binding y Farmacogenómica (PharmaOracle)
* **Acción:** PharmaOracle simula la afinidad de unión de la molécula diseñada contra la diana de Tau.
* **Salida:** `Binding Affinity Report`.

### Paso 6: Verificación Neuroclínica (Neurodiagnoses)
* **Acción:** Neurodiagnoses contrasta los resultados con la plataforma EBRAINS y los criterios de diagnóstico neuroclínico (McKeith et al. para diferenciación frente a Lewy Body Dementia).
* **Salida:** Reporte Clínico Integrado para publicación/decisión médica.

---

## 4. Criterios Estrictos de Aprobación de la Prueba E2E

1. **Cero Violaciones de Frontera:** Ningún sistema genera objetos pertenecientes al dominio de otro (e.g. CoResearcher no genera `ReviewFindings`, GeneForge no evalúa pacientes).
2. **Trazabilidad 100% Retrospectiva:** Desde el Reporte Clínico de Neurodiagnoses se puede navegar hacia atrás en el grafo hasta llegar al `Claim` original ingestada por CoResearcher.
3. **Ejecución Asíncrona sin Bloqueos:** El Kernel de NeuroOS coordina los saltos entre sistemas sin interrupciones ni pérdida de estado.
