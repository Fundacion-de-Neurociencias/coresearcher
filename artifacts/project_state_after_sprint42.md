# Project State After Sprint 42

## Línea temporal de falsaciones (Sprint 27 → Sprint 42)

### Sprint 27
- **Hipótesis:** GitHub Activity = Scientific Activity
- **Resultado:** FALSADA
- **Evidencia:** Actividad de código no corresponde necesariamente a actividad científica

### Sprint 28
- **Hipótesis:** Artifact Similarity = Program Membership
- **Resultado:** FALSADA
- **Evidencia:** Artefactos similares pueden pertenecer a programas diferentes

### Sprint 29-31
- **Hipótesis:** Network Similarity = Program Membership
- **Resultado:** FALSADA
- **Evidencia:** Redes de contribución no garantizan programas científicos comunes

### Sprint 38
- **Hipótesis:** Information Retrieval = Comprehension
- **Resultado:** FALSADA
- **Evidencia:** Recuperar información no implica comprender el razonamiento

### Sprint 39
- **Hipótesis:** Decisions = Total Coordination
- **Resultado:** FALSADA
- **Evidencia:** La coordinación incluye más que decisiones explícitas (presión, incertidumbre, alternativas)

---

## Hipótesis validadas

1. **Artefact extraction**: El proyecto puede extraer evidencia desde múltiples fuentes (GitHub issues, discussions)

2. **Artifact resolution**: Los artefactos pueden resolverse y estructurarse

3. **Scientific Activity Ledger**: El ledger puede generarse con datos empíricos

4. **Artefact limitations**: Los artefactos por sí solos no explican un proyecto

5. **Metadata limitations**: Los metadatos por sí solos no explican un proyecto

6. **Artifact similarity limitation**: Similitud de artefactos no explica programas

7. **Network similarity limitation**: Redes de contribución no explican programas

8. **Decision observability**: Las decisiones son observables en issues

9. **Coordination complexity**: La coordinación contiene más elementos que decisiones

---

## Hipótesis falsadas

- GitHub Activity = Scientific Activity ❌
- Artifact Similarity = Program Membership ❌
- Network Similarity = Program Membership ❌
- Information Retrieval = Comprehension ❌
- Decisions = Total Coordination ❌

---

## Hipótesis abiertas

1. **Restriction observability**: ¿Las restricciones son observables de forma reproducible?

2. **Uncertainty observability**: ¿Las incertidumbres son observables de forma reproducible?

3. **Alternative observability**: ¿Las alternativas descartadas son observables de forma reproducible?

4. **Context + Restrictions + Uncertainties + Alternatives + Decisions = Comprehension**: ¿Esta ecuación es correcta?

5. **Understanding = Reasoning reconstruction**: ¿Comprender es lo mismo que reconstruir el razonamiento?

---

## Inventario de artefactos activos

### Observables
- sprint42c_observations.json - 11 casos con 5 dimensiones

### Protocolos
- sprint42c_observation_protocol.md - Protocolo de extracción de observaciones

### Sprint 42D (Preparados)
- sprint42d_atomic_observation_schema.md - Formato atómico para observaciones
- sprint42d_controlled_vocabulary.md - 13+17+14 categorías
- sprint42d_observer_b_protocol.md - Protocolo para observador independiente
- sprint42d_reliability_scoring.md - Métricas definidas
- sprint42d_threats_to_reliability.md - Amenazas identificadas
- sprint42d_experiment_package.md - Paquete entregable
- sprint42d_reproducibility_audit.md - Audición intra-procedimiento

---

## Artefactos archivados

| Archivo | Motivo de archivado |
|---------|-------------------|
| sprint42d_execution_blocked.md | No hay observador B independiente disponible |
| sprint42e_blocked.md | Repositorio externo no disponible |

---

## Pregunta científica principal abierta

`	ext
¿Dos observadores independientes identifican las mismas:
- restricciones
- incertidumbres
- alternativas descartadas

a partir del mismo material fuente?
`

**Subpregunta:** Si la respuesta es no, ¿qué unidad observacional sí es estable?

---

## Riesgos metodológicos pendientes

1. **Observer independence in hybrid systems**: Sin un Observador B auténticamente independiente, no se puede validar la fiabilidad inter-observador

2. **Vocabulary completeness**: El vocabulario controlado está incompleto - faltan categorías para frases observadas

3. **Epistemological bottleneck**: No se ha demostrado que "restricciones + incertidumbres + alternativas" sea la unidad fundamental de comprensión

4. **Reasoning reconstruction validity**: No se ha verificado que reconstruir razonamiento equivalga a comprensión verdadera

---

## Evidencia requerida para Sprint 43

Para considerar Sprint 43 (modelado de comprensión):

1. **Validación de observabilidad**: Demostrar que restricciones/incertidumbres/alternativas son observables (>80% concordancia)

2. **Evidencia empírica**: Que las categorías aportan comprensión verificable, no interpretativa

3. **Reproducibilidad confirmada**: Que el mismo procedimiento conduce al mismo resultado

4. **Claridad metodológica**: Qué unidad observacional usar como base para el modelo

---

## Estado actual del proyecto

**READY_FOR_INTER_RATER_VALIDATION** (blocked)

El proyecto está en un estado metodológicamente sano:

- Limitado a observación, no interpretación
- Protocolos definidos pero no ejecutados
- Vocabulario basado en evidencia observada
- Falsaciones acumuladas documentadas
- Cuello de botella identificado: independencia observacional
