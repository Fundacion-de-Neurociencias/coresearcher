# Operationalization Framework — SPRINT 64R

**Fecha**: 2026-08-01
**Origen**: Corrección al salto inferencial detectado en SPRINT 64
**Objetivo**: Formalizar la distinción entre ontología, operacionalización, observabilidad y medición

---

## La pregunta científica

> ¿Estamos midiendo la realidad de los constructos?
> o
> ¿Estamos midiendo únicamente nuestra capacidad actual para operacionalizarlos?

---

## 1. Ontological Status

**Pregunta**: ¿La entidad podría existir independientemente de nuestra capacidad de medirla?

| Estado | Significado |
|--------|-------------|
| ESTABLISHED | Existencia aceptada por la comunidad científica |
| PLAUSIBLE | Existencia debatida pero argumentable |
| UNKNOWN | No sabemos si existe independientemente de nuestra medición |
| QUESTIONED | Evidencia sugiere que podría no existir como entidad |

**Ejemplos**:
- Gen (1850): UNKNOWN → ESTABLISHED (con DNA)
- Campo gravitatorio: ESTABLISHED
- Inteligencia: PLAUSIBLE (debate sobre qué es)
- Éter luminífero: QUESTIONED → falsado

---

## 2. Operational Status

**Pregunta**: ¿CoResearcher dispone actualmente de un procedimiento reproducible para identificarla?

| Estado | Significado |
|--------|-------------|
| OPERATIONAL | Procedimiento reproducible validado |
| PARTIALLY_OPERATIONAL | Algunas dimensiones funcionan |
| NOT_YET_OPERATIONAL | Requiere formalización |
| UNOPERATIONALIZED | Sin procedimiento |

**CRÍTICO**: Este estado mide la capacidad de CoResearcher, NO la existencia de la entidad.

---

## 3. Observability

**Pregunta**: ¿Existe una observación directa o indirecta?

| Estado | Significado |
|--------|-------------|
| DIRECT | Observable sin inferencia |
| INDIRECT | Observable via inferencia desde observables |
| NONE | No observable con tecnología actual |

**CRÍTICO**: Observabilidad baja ≠ inexistencia. Ver contraejemplos (gen, microbio, neutrino).

---

## 4. Measurement

**Pregunta**: ¿Existe una métrica reproducible?

| Estado | Significado |
|--------|-------------|
| YES | Métrica reproducible validada |
| PARTIAL | Métrica parcial o no validada |
| NO | Sin métrica |

---

## 5. Regla fundamental

> NUNCA inferir inexistencia ontológica desde baja operacionalización.
> NUNCA inferir inexistencia ontológica desde baja observabilidad.
> NUNCA inferir inexistencia ontológica desde falta de medición.

Una entidad puede ser:
- Ontológicamente ESTABLISHED pero operacionalmente UNOPERATIONALIZED
- Ejemplo: "Theory" es ontológicamente establecida pero CoResearcher no sabe operacionalizarla

---

## 6. False Negative Risk

Una entidad tiene `false_negative_risk = True` cuando:
- Su baja puntuación en operacionalización/observabilidad podría llevar a descartarla
- Pero su estatus ontológico es ESTABLISHED o PLAUSIBLE
- Y existen contraejemplos históricos de entidades similares que resultaron ser reales

**Acción**: Las entidades con false_negative_risk deben tratarse como "requieren mejor instrumentación", no como "no existen".

---

*Este framework existe para que el error de SPRINT 64 no se repita.*
*Confundir operacionalización con ontología es el mismo error que confundir Chain of Thought con razonamiento.*
