# Sprint 43 — Failure Pattern Analysis

## Hipótesis a examinar

- Knowledge ≠ Insight
- Information ≠ Comprehension  
- Artifact ≠ Understanding

---

## Falsación 1: Sprint 27 — GitHub Activity ≠ Scientific Activity

### 1. Hipótesis original
GitHub activity (commits, issues, PRs) puede reconstruir actividad científica real de un proyecto.

### 2. Qué se observó
Reconstrucción extrajo solo metadatos de desarrollo (issues/PRs), no evidencia científica. Los commits eran inaccesibles por limitaciones de paginación. Los scientific artifacts no se vincularon.

### 3. Por qué fue falsada
- **Evidencia faltante**: No hay acceso a commits del repositorio
- **Vínculo DOI ausente**: No se conectó Zenodo/OpenAlex/Crossref
- **Sólo superficie**: El ledger contiene issues/PRs, no papers/artículos científicos

### 4. Qué información faltaba
- Acceso completo al historial de commits
- Metadatos de DOIs (publicaciones, datasets, software)
- Conectores adecuados para Zenodo/OpenAlex/Crossref

### 5. Qué tipo de comprensión se perdió
Comprensión científica sustancial: las preguntas sobre "qué hacen estos artefactos científicamente" no pueden responderse con metadatos de desarrollo. Los artefactos sin contexto de evidencia científica son solo ruido.

---

## Falsación 2: Sprint 30 — Artifact Similarity ≠ Program Membership

### 1. Hipótesis original
La similitud entre artefactos permite inferir pertenencia a programas científicos coherentes.

### 2. Qué se observó
61 artefactos produjeron 57 programas distintos. Muchos programas son duplicados con IDs diferentes. Los "comprehension summaries" son incoherentes:

- program-0: "spanning 0 repositories" pero con 1 dataset
- programas con años de actividad imposibles (1985, 1994, etc.)
- Muchos programas apuntan a papers irrelevantes ("Realized Variance and Market Microstructure Noise" en bids-examples)

### 3. Por qué fue falsada
- **No hay ground truth real**: No hay relación causa-efecto verificable
- **Duplicación masiva**: El mismo repositorio aparece múltiples veces con diferentes IDs
- **Contaminación de datos**: Papers no relacionados aparecen como parte del programa
- **Sin verificación humana**: Precision/recall nunca fueron medidos

### 4. Qué información faltaba
- Validación manual por expertos
- Ground truth independiente
- Conocimiento real de los programas científicos

### 5. Qué tipo de comprensión se perdió
Comprensión del propósito científico: la agrupación por similitud produce clusters que el experto no reconocería como programas coherentes. Un programa científico requiere más que artefactos similares.

---

## Falsación 3: Sprint 31 — Network Similarity ≠ Program Membership

### 1. Hipótesis original
La red de contribución entre repositorios puede agruparlos en programas científicos coherentes.

### 2. Qué se observó
808 nodos y 1011 edges produjeron 12 programas. Los mismos problemas que Sprint 30 persisten:

- bids-examples asociado a papers de "Combinatorial Auctions"
- "Bid/no-bid decision-making – a fuzzy linguistic approach" en lugar de neurociencia
- Fechas de actividad absurdas (1985-2026 para el mismo programa)

### 3. Por qué fue falsada
- **Falla de Sprint 30 persiste**: El problema no era el algoritmo, sino la ausencia de verdad fundamental
- **Sin dirección arquitectónica**: La red captura colaboraciones técnicas, no propósito científico
- **La hipótesis original era falsa**: Las redes técnicas reflejan trabajo de ingeniería, no programas científicos

### 4. Qué información faltaba
- Definición operativa de "programa científico"
- Ground truth validado por humanos
- Separación entre coordinación técnica y programa científico

### 5. Qué tipo de comprensión se perdió
Comprensión del programa científico: el resolver de red identifica clusters técnicos pero no responde "¿qué pregunta científica está abordando este proyecto?".

---

## Falsación 4: Sprint 39B — Information Retrieval ≠ Project Comprehension

### 1. Hipótesis original
El tiempo de recuperación de información del ledger vs búsqueda en crudo mide "costo de comprensión".

### 2. Qué se observó
- Raw context: 11547 caracteres, 30% precisión, 0.000179s promedio
- Ledger: 20 observaciones curadas, 100% precisión, ~0s (dict lookup)
- Ratio de compresión: 896x

### 3. Por qué fue falsada
**Construct Validity CRITICAL**: El experimento mide "tiempo de búsqueda en diccionario vs tiempo de búsqueda en texto", no comprensión:

- Ledger = "leer la clave de respuestas"
- Raw = "buscar texto en README"
- Un humano necesita minutos para comprender, no microsegundos

**Internal Validity CRITICAL**: Ground truth copiado directamente al ledger. El ledger valida contra sí mismo.

**External Validity HIGH**: Solo MNE-Python fue testeado (proyecto bien documentado).

### 4. Qué información faltaba
- Ground truth independiente (expertos, no experimentador)
- Medidas en escala humana (minutos, no microsegundos)
- Preguntas que requieren síntesis, no recuperación directa
- Proyectos con diferente nivel de documentación

### 5. Qué tipo de comprensión se perdió
Comprensión real del proyecto: el ledger contiene respuestas listas, no razonamiento. La habilidad de "recordar" no equivale a "comprender".

---

## Falsación 5: Sprint 40 — Decision → Total Coordination
 
### 1. Hipótesis original
Las decisiones explícitas en issues son la unidad fundamental de coordinación en proyectos científicos.
 
### 2. Qué se observó
6/11 casos tienen "Resolved Trade-off" (decisiones explícitas). 5/11 casos no tienen decisión explícita pero tienen patrones observables de coordinación:
 
- Iterative Implementation Discussion
- Technical Q&A / Knowledge Exchange
- Bug Investigation Coordination
- Status / Progress Update
- Implementation Detail Negotiation
 
### 3. Por qué fue falsada
- **Hipótesis demasiado fuerte**: Las decisiones explícitas (trade-offs) son **una forma** de coordinación, no su definición exhaustiva
- **Patrones no capturados**: 5 casos significativos (45%) no tienen "trade-off" pero son actividades reales
- **La coordinación es multiparadigma**: diseño, estado, conocimiento, implementación
 
### 4. Qué información faltaba
- Observabilidad de patrones no-decisionales
- Reconocimiento de coordinación implícita
- Tipos de unidad más amplios que trade-offs
 
### 5. Qué tipo de comprensión se perdió
Comprensión del proceso de coordinación: reducir la coordinación a decisiones pierde 5/11 de las interacciones reales. Las decisiones son coordinación, pero no agotan toda la coordinación.
 
---
 
## Patrón transversal: Correlation ≠ Explanation
 
### Forma repetida de fracaso
 
| Sprint | Estructura observable | Explicación buscada | Resultado |
|--------|----------------------|---------------------|-----------|
| 30 | Artefactos similares | Programa científico | ❌ No explica coherencia científica |
| 31 | Red similar | Programa científico | ❌ No explica propósito científico |
| 39B | Información accesible | Comprensión | ❌ No explica significado |
| 40 | Decisiones observables | Coordinación total | ❌ No explica toda la coordinación |
 
### Observación clave
 
> **Correlation ≠ Explanation**
 > **Structure ≠ Meaning**
 
 Las propiedades observables (similitud, red, accesibilidad, decisiones) no tienen la capacidad intrínseca de explicar el significado que se les atribuye.
 
 ---
 
## Afirmación precisa
 
Las falsaciones ocurren al intentar que propiedades observables (Data, Artifact, Network, Information, Decision) produzcan explicaciones (Scientific Activity, Program, Comprehension, Total Coordination) que no están garantizadas por esas propiedades.
