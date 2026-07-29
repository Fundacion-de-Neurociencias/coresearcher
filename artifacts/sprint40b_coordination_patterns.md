# Sprint 40B — Coordination Patterns in Q1=NO Cases

## Scope

Análisis de los 5 casos sin decisión explícita (Q1=NO) observados manualmente.

**Dataset**: 5 casos exclusivamente
**Método**: Categorización basada ÚNICAMENTE en patrones observables, sin inferencia.

---

## Patrón 1: Iterative Implementation Discussion

### Caso: MNE-Python #2154 — Concatenated epoch plot

**Patrón observable**:
- Lista de TODOs pendientes (bugs, features, testing)
- Comentarios de revisión técnica
- Preguntas de implementación ("how do we handle X?")
- Sin alternativas de diseño explícitas

**Categoría emergente**: Iterative Implementation Discussion

---

## Patrón 2: Technical Q&A / Knowledge Exchange

### Caso: Nilearn #1016 — Surface plotting

**Patrón observable**:
- Preguntas técnicas sobre implementación
- "Would some version of that be an option?" ("¿Alguna versión de eso sería una opción?")
- Sugerencias sin evaluación de alternativas
- Discusión de cómo resolver problemas técnicos específicos

**Categoría emergente**: Technical Q&A / Knowledge Exchange

---

## Patrón 3: Bug Investigation Coordination

### Caso: PyBIDS #451 — List metadata

**Patrón observable**:
- Reporte de error observable ("TypeError: unhashable type")
- Comentarios sobre workarounds y soluciones
- Discusión de implementación de fix
- Sin evaluación de alternativas de diseño arquitectónico

**Categoría emergente**: Bug Investigation Coordination

---

## Patrón 4: Status / Progress Update

### Caso: MNE-Python #766 — Trans GUI

**Patrón observable**:
- Actualizaciones de estado ("still aiming for 0.7")
- Preguntas sobre timeline
- Discusión de testing
- Sin alternativas explícitas de diseño

**Categoría emergente**: Status / Progress Update

---

## Patrón 5: Implementation Detail Negotiation

### Caso: MNE-Python #2676 — EEGLAB reader

**Patrón observable**:
- Preguntas sobre detalles de implementación
- "Wdyt?" ("What do you think?")
- Discusión de cómo manejar casos particulares
- Sin trade-offs de diseño explícitos

**Categoría emergente**: Implementation Detail Negotiation

---

## Análisis de patrones emergentes

Los 5 casos Q1=NO no contienen "Resolved Trade-off", pero contienen patrones observables de coordinación:

1. **Iterative Implementation Discussion** (feature/bug workflow)
2. **Technical Q&A / Knowledge Exchange** (how-to questions)
3. **Bug Investigation Coordination** (error diagnosis)
4. **Status / Progress Update** (timeline negotiation)
5. **Implementation Detail Negotiation** (technical details)

---

## Comparación con casos Q1=YES

| Característica | Q1=YES (6 casos) | Q1=NO (5 casos) |
|----------------|-----------------|-----------------|
| Trade-offs explícitos | YES | NO |
| Evidencia utilizada | YES | VARIABLE |
| Justificación de elección | YES | NO |
| Recuperable | YES | N/A |
| Tipo: Coordinación de proyecto | SÍ | SÍ (diferente forma) |

---

## Implicación preliminar

Los casos sin "Resolved Trade-off" tampoco son "ruido". Representan formas diferentes de coordinación:

- **Status exchange** (qué se ha hecho, qué falta)
- **Knowledge exchange** (cómo resolver problemas técnicos)
- **Implementation negotiation** (detalles técnicos)

Esto sugiere que la coordinación en proyectos científicos es **multiparadigma**, no monocausal.

---

## Interpretive Assessment (non-validated)

La hipótesis "Resolved Trade-off = unidad mínima" puede ser demasiado estrecha.

Los 11 casos observados sugieren un espectro de coordinación:

1. Diseño (trade-offs resueltos)
2. Estado (progreso, timeline)
3. Conocimiento (resolución técnica)
4. Implementación (negociación de detalles)

Para CoResearcher, esto significa que la comprensión del proyecto podría requerir más que solo trade-offs.
</tool_call>