# Plan de Ejecución Real de NeuroOS (NEUROOS EXECUTION PLAN)

**Versión:** 1.0.0  
**Directiva:** ANTIGRAVITY-003  
**Modo:** DEMOSTRACIÓN EMPÍRICA EN TIEMPO REAL  

Este plan define el caso de prueba único y ejecutable para validar la interoperabilidad real entre los subsistemas de NeuroOS en el entorno local (`C:\Users\usuario`).

---

## 1. Caso de Prueba Seleccionado

**"Flujo Multidisciplinar Real: Biomarcadores de Alzheimer (p-tau217) y Trayectoria Biológica"**

```text
[ Documento Fuente (PMID:32722172) ]
                 │
                 ▼
     [ Step 1: CoResearcher ]  ──> Valida evidencia inmutable (validate_constitution.py)
                 │
                 ▼
       [ Step 2: EditXT ]     ──> Audita el contrato e interfaz del grafo
                 │
                 ▼
     [ Step 3: GeneForge ]    ──> Ejecuta motor de trayectoria biológica (main.py)
                 │
                 ▼
  [ Step 4: Neurodiagnoses ]  ──> Procesa módulo de reporte clínico (gf.clinical)
```

---

## 2. Definición de Pasos y Comandos Reales

1. **Step 1 (CoResearcher):** Generar e ingestar un `EvidenceGraph` real (`scratch/alzheimer_evidence_graph.json`) y validar las 8 reglas constitucionales ejecutando `python scripts/validate_constitution.py`.
2. **Step 2 (EditXT):** Verificar el estado físico del repositorio EditXT (`C:\Users\usuario\Editxt`) y la compatibilidad del grafo.
3. **Step 3 (GeneForge):** Ejecutar la trayectoria dinámica de control biológico ejecutando `python main.py` en `GeneForge Ecosystem\GeneForge`.
4. **Step 4 (Neurodiagnoses / Clinical):** Cargar e importar el parser de reportes neuroclínicos mediante `PYTHONPATH="C:\Users\usuario\GeneForge Ecosystem\GeneForge" python -c "import gf.clinical.report_parser"`.

---

## 3. Criterio de Aprobación
- Cada paso debe ejecutarse en la consola local.
- No se aceptan datos sintéticos ni mocks simulados.
- Todo fallo o bloqueo debe ser capturado inmediatamente en el `NEUROOS_FAILURE_REPORT.md`.
