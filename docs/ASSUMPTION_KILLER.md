# Sprint 24: Assumption Killer

## Identificar las 10 hipótesis estratégicas cuya falsedad destruiría CoResearcher

---

## Las 10 Hipótesis Críticas

### H1: Investigadores aceptarán revisión Agent→Agent

**Descripción:**
Los investigadores aceptarán revisión automática si tiene trazabilidad ORCID

**Impacto si falsa:**
Verification Layer sin adopción

**Evidencia actual:**
???

**Experimento de validación:**
Entrevista: "¿Aceptarías revisión Agent→Agent con ORCID responsable?"

**Coste de validación:**
Bajo - entrevistas

**Prioridad:**
🔴 CRÍTICA

---

### H2: Investigadores querrán registrar actividad científica

**Descripción:**
Los investigadores verán valor en registrar SUPPORT/CHALLENGE/REPLICATE

**Impacto si falsa:**
Scientific Activity Graph sin nodos

**Evidencia actual:**
???

**Experimento de validación:**
"¿Qué actividad científica registra hoy? ¿Por qué?"

**Coste de validación:**
Medio - observación

**Prioridad:**
🔴 CRÍTICA

---

### H3: ORCID aceptará coexistir con identidades de agentes

**Descripción:**
ORCID no bloqueará identidades de agentes con ORCID respaldando

**Impacto si falsa:**
Identidades fragmentadas, sin interoperabilidad

**Evidencia actual:**
???

**Experimento de validación:**
Contacto con ORCID team

**Coste de validación:**
Medio

**Prioridad:**
🔴 CRÍTICA

---

### H4: Agentes externos consumirán CoResearcher MCP

**Descripción:**
Claude Research, Gemini Research, Codex adoptarán CoResearcher como fuente

**Impacto si falsa:**
Ecosistema sin agentes, solo humanos

**Evidencia actual:**
???

**Experimento de validación:**
API test con agentes actuales

**Coste de validación:**
Bajo

**Prioridad:**
🔴 CRÍTICA

---

### H5: La comunidad percibe valor en Scientific Actions

**Descripción:**
ACTION-XXXXXX tiene valor percibido como identificador

**Impacto si falsa:**
Identificadores irrelevantes, sin adopción

**Evidencia actual:**
???

**Experimento de validación:**
"¿Qué importa más: tu paper o tu historia de contribución?"

**Coste de validación:**
Bajo

**Prioridad:**
🔴 CRÍTICA

---

### H6: Reputación basada en actividad importa

**Descripción:**
trust_score derivado de acciones supera al impact factor

**Impacto si falsa:**
Trust como feature decorativa

**Evidencia actual:**
???

**Experimento de validación:**
Comparar adopción vs sistemas tradicionales

**Coste de validación:**
Alto

**Prioridad:**
🟡 ALTA

---

### H7: Revisión híbrida reduce costes

**Descripción:**
Agent review + human escalation es más barato que review puro

**Impacto si falsa:**
No hay ventaja económica

**Evidencia actual:**
???

**Experimento de validación:**
Modelado de costes

**Coste de validación:**
Medio

**Prioridad:**
🟡 ALTA

---

### H8: Coordinación > Descubrimiento

**Descripción:**
Coordinación científica es un problema más grande que descubrimiento

**Impacto si falsa:**
Enfoque incorrecto - debería ser Discovery Engine

**Evidencia actual:**
Bibliotecas de papers existen, coordinación no

**Experimento de validación:**
"¿Cuántas veces perdiste datos importantes por falta de coordinación?"

**Coste de validación:**
Bajo

**Prioridad:**
🟡 ALTA

---

### H9: Equipos híbridos humano+agente serán dominante

**Descripción:**
La unidad operativa será TEAM-XXXXXX (humano + múltiples agentes)

**Impacto si falsa:**
Research Program como abstracción inútil

**Evidencia actual:**
Investigadores ya usan múltiples herramientas IA

**Experimento de validación:**
Mapear "agent stack" de investigadores actuales

**Coste de validación:**
Bajo

**Prioridad:**
🔴 CRÍTICA

---

### H10: Actividad verificable genera network effects

**Descripción:**
500M acciones verificables > 10M papers sin historia

**Impacto si falsa:**
Knowledge Graph > Activity Graph como estrategia

**Evidencia actual:**
GitHub valió más por actividad que código

**Experimento de validación:**
Analogía con sistemas existentes

**Coste de validación:**
Bajo

**Prioridad:**
🟢 MEDIA

---

## Prioridad de Validación

### Inmediata (esta semana)
- H1, H2, H4, H9: Entrevistas con investigadores y tests de agentes

### Corto plazo (2 semanas)
- H3, H5: Contacto con ORCID, tests de percepción

### Mediano plazo (1 mes)
- H6, H7, H8: Modelado y estudios de adopción

---

## Regla de oro

> **Si la hipótesis está en 🔴 CRÍTICA y es falsa, NO implementar Sprint 23A.**

> **Detenerse antes de construir.**