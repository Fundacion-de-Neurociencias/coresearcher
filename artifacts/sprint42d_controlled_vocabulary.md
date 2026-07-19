# Sprint 42D — Controlled Vocabulary

Extracción de todas las categorías observadas realmente en los 11 casos de sprint42c_observations.json.

## Constraints (dimension_3)

Categorías observadas en orden de aparición:

1. **backwards_compatibility** - backward compatibility con API existente
2. **api_consistency** - consistencia con enfoque pandas-query
3. **technical_complexity** - complejidad técnica del encoding model general
4. **pr_review_capacity** - capacidad de revisión del PR (tamaño manejable)
5. **dependency_constraint** - dependencia de matplotlib en el núcleo / dependencias JavaScript de papaya / dependencia externa grabbit
6. **standard_compliance** - cumplir con el estándar BIDS / comportamiento correcto según spec BIDS
7. **api_simplicity** - no exponer parámetros complejos al usuario
8. **ecosystem_compatibility** - compatibilidad con fitlins y neuroscout
9. **resource_constraint** - tamaño de notebooks (12MB con papaya) / recursos de desarrollo limitados
10. **architectural_integrity** - integración con arquitectura existente
11. **format_complexity** - formato EEGLAB complejo y variable
12. **library_limitation** - limitaciones de la librería de plotting 3D
13. **backend_compatibility** - compatibilidad con diferentes backends

## Uncertainties (dimension_4)

Categorías observadas en orden de aparición:

1. **user_impact_unknown** - impacto en usuarios existentes que usaban regress / impacto en usuarios
2. **adoption_unknown** - si el enfoque general será adoptado en el futuro / adopción de la nueva API de reporting
3. **long_term_sufficiency_unknown** - si el módulo receptive field será suficiente a largo plazo
4. **complexity_impact_unknown** - complejidad adicional de subpaquete separado
5. **feature_coverage_unknown** - si brainsprite ofrecería todas las features de papaya
6. **compatibility_unknown** - compatibilidad con diferentes navegadores
7. **edge_case_coverage_unknown** - si el ajuste automático cubriría todos los casos de uso
8. **performance_unknown** - rendimiento con diferentes tasas de oversampling
9. **effort_estimate_unknown** - esfuerzo requerido para portar toda la funcionalidad
10. **maintenance_feasibility_unknown** - mantenimiento a largo plazo de la funcionalidad portada / mantenimiento futuro
11. **implementation_feasibility_unknown** - cómo manejar diferentes casos de uso
12. **demand_unknown** - demanda real de la feature
13. **priority_unknown** - prioridad en el roadmap
14. **format_coverage_unknown** - cobertura completa de formatos EEGLAB
15. **technical_approach_unknown** - mejor enfoque técnico para surface plotting
16. **resource_feasibility_unknown** - recursos disponibles
17. **bug_scope_unknown** - alcance del bug

## Alternatives (dimension_5)

Categorías observadas en orden de aparición:

1. **keep_both_functions** - mantener ambas funciones (regress y pandas-query) a costa de complejidad
2. **modify_existing_function** - modificar regress para que trabaje con pandas-query
3. **large_pr** - implementar encoding model completo en un solo PR
4. **multiple_prs** - dividir en múltiples PRs parciales
5. **keep_api_location** - mantener HTMLDocument dentro de nilearn.plotting
6. **remove_api** - eliminar funcionalidad de reporting completamente
7. **keep_library** - mantener papaya a costa de tamaño de notebooks
8. **optimize_existing** - optimizar papaya internamente
9. **alternative_library** - usar otra alternativa diferente
10. **manual_workaround** - usuario llama ToDense manualmente antes de Convolve
11. **expose_parameter** - exponer el parámetro de oversampling en la API
12. **keep_dependency** - mantener grabbit como dependencia externa
13. **update_dependency** - actualizar grabbit en lugar de portar
14. **no_alternative_discussed** - N/A - no se discutieron alternativas explícitas
