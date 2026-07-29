# Scientific Infrastructure Patterns - Sprint 38A.5

**¿Qué caracteriza una infraestructura científica que permanece relevante durante más de una década?**

---

## Pattern: Longitudinality + Standardization + Quality Control

Los activos que sobreviven >10 años comparten esta combinación:

### ADNI (20+ años)
- Longitudinality: Sí (5-10 años follow-up)
- Standardization: Sí (MRI protocol idéntico en 60+ sitios)
- QC: Sí (phantom mensual, central review)

### UK Biobank (15+ años)
- Longitudinality: Sí (multiple assessment waves)
- Standardization: Sí (protocolos fijos para 500,000 participantes)
- QC: Sí (samples procesados en laboratorios acreditados)

### MIMIC-IV (15+ años)
- Longitudinality: Parcial (solo durante hospitalización)
- Standardization: Parcial (datos heterogéneos de ICU)
- QC: Sí (validación de datos clínicos)

---

## Pattern: Governance + Multi-modal Integration

Los activos con gobernanza formal y datos multimodal:

### ADNI
- Governance: DUA + NIH approval
- Modalities: MRI, PET, CSF, plasma, genetics, cognition

### UK Biobank
- Governance: Aprobación de investigación + datos anonimizados
- Modalities: Imaging, blood, genetics, lifestyle, cognition

Los activos sin gobernanza formal tienden a ser más nuevos o más técnicos.

---

## Pattern: Versioning OR Ontology

Los activos duraderos desarrollan algún mecanismo de control de cambios:

### Con Versioning (software/infraestructura)
- OpenNeuro (datasets versionados)
- MONAI (versiones de código)
- OHDSI (versiones de Common Data Model)
- FHIR (versiones de estándares)

### Con Ontologías (datos clínicos)
- OHDSI (OMOP CDM)
- FHIR (recursos clínicos)
- SNOMED-CT (terminología)

---

## Pattern: Decoupled Architecture

Los activos estructuralmente separan:

1. **Datos** (UK Biobank, ADNI) - estructura de cohorte
2. **Métodos** (MONAI, OHDSI) - estandarización de procesamiento
3. **Interoperabilidad** (FHIR, OHDSI) - APIs y mappings
4. **Terminología** (SNOMED-CT, OHDSI) - ontologies

Esta separación permite evolución independiente de cada capa.

---

## No-Infraestructuras (sin supervivencia demostrada)

Activos que carecen de estos patrones tienden a:
1. Tener propósito muy específico (ej: estudio puntual)
2. Carecer de mecanismo de sostenibilidad (financiamiento/ausencia)
3. No tener cómo integrarse con otros activos

---

## Principio emergente

Una infraestructura científica duradera requiere al menos:

**3 de 4**: Longitudinality, Standardization, Quality Control, Governance

Sin esto, la evidencia producida es:
- De corta duración
- De difícil replicación
- De limitada generalización

---

## Métricas finales

```text
Activos analizados: 9
Patrones identificados: 8
Comparaciones realizadas: 5
Combinaciones exitosas: 2 (ADNI, UK Biobank)