# Sprint 42D — Atomic Observation Schema

## Purpose

Transform narrative observations into atomic, machine-readable observations for inter-rater reliability validation.

## Atomic Observation Format

Each observation MUST be represented as a JSON object with exactly one key: the category identifier.

### Constraints (dimension_3)

**Narrative to Atomic Transformation:**

| Narrative | Atomic |
|-----------|--------|
| "backward compatibility con API existente" | {"constraint": "backwards_compatibility"} |
| "consistencia con enfoque pandas-query" | {"constraint": "api_consistency"} |
| "complejidad técnica del encoding model general" | {"constraint": "technical_complexity"} |
| "capacidad de revisión del PR (tamaño manejable)" | {"constraint": "pr_review_capacity"} |
| "dependencia de matplotlib en el núcleo" | {"constraint": "dependency_constraint"} |
| "tamaño de notebooks (12MB con papaya)" | {"constraint": "resource_constraint"} |
| "dependencias JavaScript de papaya" | {"constraint": "dependency_constraint"} |
| "cumplir con el estándar BIDS" | {"constraint": "standard_compliance"} |
| "no exponer parámetros complejos al usuario" | {"constraint": "api_simplicity"} |
| "dependencia externa grabbit" | {"constraint": "external_dependency"} |
| "compatibilidad con fitlins y neuroscout" | {"constraint": "ecosystem_compatibility"} |
| "recursos de desarrollo limitados" | {"constraint": "resource_constraint"} |
| "integración con arquitectura existente" | {"constraint": "architectural_integrity"} |
| "formato EEGLAB complejo y variable" | {"constraint": "format_complexity"} |
| "limitaciones de la librería de plotting 3D" | {"constraint": "library_limitation"} |
| "compatibilidad con diferentes backends" | {"constraint": "backend_compatibility"} |
| "comportamiento correcto según spec BIDS" | {"constraint": "standard_compliance"} |

### Uncertainties (dimension_4)

**Narrative to Atomic Transformation:**

| Narrative | Atomic |
|-----------|--------|
| "impacto en usuarios existentes que usaban regress" | {"uncertainty": "user_impact_unknown"} |
| "si el enfoque general será adoptado en el futuro" | {"uncertainty": "adoption_unknown"} |
| "si el módulo receptive field será suficiente a largo plazo" | {"uncertainty": "long_term_sufficiency_unknown"} |
| "adopción de la nueva API de reporting" | {"uncertainty": "adoption_unknown"} |
| "complejidad adicional de subpaquete separado" | {"uncertainty": "complexity_impact_unknown"} |
| "si brainsprite ofrecería todas las features de papaya" | {"uncertainty": "feature_coverage_unknown"} |
| "compatibilidad con diferentes navegadores" | {"uncertainty": "compatibility_unknown"} |
| "si el ajuste automático cubriría todos los casos de uso" | {"uncertainty": "edge_case_coverage_unknown"} |
| "rendimiento con diferentes tasas de oversampling" | {"uncertainty": "performance_unknown"} |
| "esfuerzo requerido para portar toda la funcionalidad" | {"uncertainty": "effort_estimate_unknown"} |
| "mantenimiento a largo plazo de la funcionalidad portada" | {"uncertainty": "maintenance_feasibility_unknown"} |
| "si la feature sería útil para suficientes usuarios" | {"uncertainty": "user_impact_unknown"} |
| "cómo manejar diferentes casos de uso" | {"uncertainty": "implementation_feasibility_unknown"} |
| "demanda real de la feature" | {"uncertainty": "demand_unknown"} |
| "prioridad en el roadmap" | {"uncertainty": "priority_unknown"} |
| "cobertura completa de formatos EEGLAB" | {"uncertainty": "format_coverage_unknown"} |
| "mantenimiento futuro" | {"uncertainty": "maintenance_feasibility_unknown"} |
| "mejor enfoque técnico para surface plotting" | {"uncertainty": "technical_approach_unknown"} |
| "recursos disponibles" | {"uncertainty": "resource_feasibility_unknown"} |
| "alcance del bug" | {"uncertainty": "bug_scope_unknown"} |
| "impacto en usuarios" | {"uncertainty": "user_impact_unknown"} |

### Rejected Alternatives (dimension_5)

**Narrative to Atomic Transformation:**

| Narrative | Atomic |
|-----------|--------|
| "mantener ambas funciones (regress y pandas-query) a costa de complejidad" | {"alternative": "keep_both_functions"} |
| "modificar regress para que trabaje con pandas-query" | {"alternative": "modify_existing_function"} |
| "implementar encoding model completo en un solo PR" | {"alternative": "large_pr"} |
| "dividir en múltiples PRs parciales" | {"alternative": "multiple_prs"} |
| "mantener HTMLDocument dentro de nilearn.plotting" | {"alternative": "keep_api_location"} |
| "eliminar funcionalidad de reporting completamente" | {"alternative": "remove_api"} |
| "mantener papaya a costa de tamaño de notebooks" | {"alternative": "keep_library"} |
| "optimizar papaya internamente" | {"alternative": "optimize_existing"} |
| "usar otra alternativa diferente" | {"alternative": "alternative_library"} |
| "usuario llama ToDense manualmente antes de Convolve" | {"alternative": "manual_workaround"} |
| "exponer el parámetro de oversampling en la API" | {"alternative": "expose_parameter"} |
| "mantener grabbit como dependencia externa" | {"alternative": "keep_dependency"} |
| "actualizar grabbit en lugar de portar" | {"alternative": "update_dependency"} |
| "N/A - no se discutieron alternativas explícitas" | {"alternative": "no_alternative_discussed"} |
