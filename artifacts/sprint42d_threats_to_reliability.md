# Sprint 42D — Threats to Reliability

Identificación explícita de amenazas potenciales a la fiabilidad del protocolo de observación.

## Observer Bias

**Definición:** Tendencia del observador a interpretar información basado en creencias previas.

**Posibles fuentes en este estudio:**
- Conocimiento previo del proyecto neuroinformatics
- Preferencias personales por ciertos tipos de soluciones (simplicity vs complexity)
- Experiencia con herramientas similares (pandas, BIDS, etc.)

**Mitigación:**
- Protocolo estricto de solo leer issues originales
- Vocabulario controlado limita interpretaciones
- Justificación documentada obligatoria

## Project Familiarity Bias

**Definición:** Ventaja o desventaja basada en conocimiento previo del proyecto.

**Posibles fuentes:**
- Familiaridad con arquitectura de mne-python, nilearn, pybids
- Conocimiento del roadmap o historia del proyecto
- Experiencia como usuario de las herramientas

**Mitigación:**
- Observador B debe ser independiente
- Solo acceso a issues, no a documentación adicional
- Preguntas de clarificación deben basarse en texto del issue, no en conocimiento externo

## Vocabulary Ambiguity

**Definición:** Ambigüedad en la definición de categorías del vocabulario controlado.

**Posibles ambigüedades identificadas:**
- "user_impact_unknown" vs "adoption_unknown" - ¿diferencia clara?
- "dependency_constraint" vs "external_dependency" - ¿cuándo aplicar cada una?
- "resource_constraint" - ¿qué tipos de recursos? (tiempo, memoria, desarrollo)

**Mitigación:**
- Definiciones explícitas con ejemplos
- Documentar casos límite durante observación
- Revisión de categorías ambiguas por ambos observadores

## Selection Bias

**Definición:** Tendencia sistemática a seleccionar ciertos tipos de observaciones.

**Posibles fuentes:**
- Enfocarse en discusiones técnicas vs discusiones de producto
- Preferencia por alternativas que "parecen lógicas"
- Ignorar alternativas mencionadas brevemente

**Mitigación:**
- Revisar TODO el issue, no solo los comentarios principales
- Incluir alternativas aunque estén descartadas rápidamente
- Documentar qué partes del issue se consideraron

## Confirmation Bias

**Definición:** Tendencia a buscar evidencia que confirme expectativas previas.

**Posibles manifestaciones:**
- Buscar frases que confirmen categorías esperadas
- Descartar información que contradiga el patrón conocido
- Inferir restricciones no explícitas

**Mitigación:**
- Cada categoría requiere evidencia textual explícita
- Prohibido inferir información no visible en el issue
- Regla: "Solo lo que está escrito"

## Temporal Bias

**Definición:** Efecto del orden de observación en los resultados.

**Posibles fuentes:**
- Primeros casos pueden influir en interpretación de siguientes
- Aprendizaje durante el proceso puede cambiar criterios

**Mitigación:**
- Observador B debe trabajar de forma independiente
- No comparar resultados hasta completar todos los casos
- Analizar consistencia interna de cada observador

## Categorization Threshold Bias

**Definición:** Diferente umbral para considerar algo como categoría válida.

**Posibles variaciones:**
- ¿Mención casual o mención enfática?
- ¿Requisito explícito o implicado?
- ¿Impacto directo o impacto potencial?

**Mitigación:**
- Criterio: "El issue menciona explícita o implícitamente"
- Justificación obligatoria para cada selección
- Documentar nivel de evidencia (explícito/implícito)

## Resumen de Amenazas Críticas

| Amenaza | Nivel de Riesgo | Acción Correctiva |
|---------|-----------------|-------------------|
| Observer Bias | ALTO | Protocolo estricto + Independent B |
| Vocabulary Ambiguity | ALTO | Definiciones claras + revisiones |
| Confirmation Bias | ALTO | Evidencia textual obligatoria |
| Selection Bias | MEDIO | Revisión completa de issues |
| Project Familiarity | MEDIO | Acceso limitado a fuentes |
| Temporal Bias | BAJO | Observación independiente |
| Threshold Bias | ALTO | Criterios explícitos |
