# CoResearcher Protocol vs Einstein Discovery Suite

## La separación constitucional

> **CoResearcher coordina actividad científica.**
> **Einstein genera inteligencia científica.**

---

## Capa 1: CoResearcher Protocol (gratuito)

Equivalente a Git, GitHub, ORCID, DOI, OpenAlex, OSF.

**Función:** Coordinar actividad científica verificable.

### Objetos abiertos:

| Objeto | Descripción | Uso en protocolo |
|--------|-------------|------------------|
| **QUESTION** | Norte estratégico | Orientación de investigación |
| **ACTION** | Ejecución verificable | Actividad registrada |
| **REVIEW** | Validación externa | Calidad y confianza |
| **CLAIM** | Observación atómica | Producción verificable |
| **PROGRAM** | Compromiso intelectual | Organización acumulativa |
| **PROVENANCE** | Trazabilidad total | Reproducibilidad |

### Características:

- **Open** - Estructura pública sin restricciones
- **GitHub-based** - Repositorios estándar
- **MCP-first** - Protocolo abierto para agentes
- **Agent-compatible** - Integración con herramientas externas
- **Coste cero** - Sin dependencias propietarias
- **Sin IA obligatoria** - Operación sin LLMs

### Valor del protocolo:

```text
Coordinar
    ↓
Versionar
    ↓
Verificar
    ↓
Trazar
    ↓
Transferir
```

**No incluye:** Descubrimiento, generación de hipótesis, razonamiento científico avanzado.

---

## Capa 2: Einstein Discovery Suite (de pago)

**Función:** Generar inteligencia científica.

### Componentes propietarios:

| Componente | Descripción | Valor económico |
|------------|-------------|-----------------|
| **Mechanism Graph** | Base de conocimiento estructurado | IP acumulativa |
| **NoveltyDetector** | Detección de unusualness | Diferenciación |
| **Hypothesis Generator** | Generación de hipótesis | Sorpresa controlada |
| **Prioritization Engine** | Priorización de investigración | Ahorro de recursos |
| **Benchmark Suite** | Evaluación de descubrimientos | Calidad garantizada |
| **Discovery Evaluation** | Métricas de impacto | Decisión informada |

### Producto SaaS:

```text
"¿Qué hipótesis debería investigar?"

"¿Qué papers contradicen este mecanismo?"

"¿Qué experimentos tienen mayor valor esperado?"

"¿Qué claim es más novedoso?"

"¿Qué programa merece financiación?"
```

---

## La analogía correcta

| Infraestructura | Producto comercial |
|-----------------|-------------------|
| Git | GitHub Enterprise |
| Linux | Red Hat |
| Web | Google |
| **CoResearcher Protocol** | **Einstein Discovery Suite** |

El protocolo debe poder sobrevivir aunque Einstein desaparezca.
Einstein debe poder operar aunque existan otros protocolos.

---

## Separación estructural

### CoResearcher Protocol (infraestructura)

```text
python/ontology/
python/actions/
python/reviews/
python/questions/
python/provenance/
python/mcp/
```

### Einstein Discovery Suite (inteligencia)

```text
discovery/
├── novelty_detector.py      # Detección de unusualness
├── mechanism_engine.py        # Motor de mecanismos
├── hypothesis_generator.py    # Generación de hipótesis
├── prioritization_engine.py   # Priorización de investigración
├── benchmark_suite.py         # Evaluación de descubrimientos
└── discovery_evaluation.py    # Métricas especializadas
```

---

## Dependencias arquitectónicas

### Protocolo (independiente)

```
QUESTION ──┐
CLAIM   ───┤
ACTION  ───┼──> Registry
REVIEW  ──┤
PROGRAM ──┘
```

### Discovery Suite (opcional)

```
Protocol Objects ──> Discovery Suite ──> Intelligence Layer
                     ↑
              MCP Integration
```

**Ningún componente de descubrimiento es dependencia obligatoria del protocolo.**

---

## Consecuencias estratégicas

### Si se separa correctamente:

✓ Protocolo abierto con adopción masiva posible
✓ Suite de descubrimiento como diferenciador premium
✓ Competidores pueden usar el protocolo sin usar Einstein
✓ Innovación en discovery stack sin romper el protocolo
✓ Comunidad puede contribuir sin complejidad comercial

### Si se mezcla:

✗ Nadie adopta el protocolo (siente "funnel comercial")
✗ Dificultad para contribuir al código abierto
✗ Bloqueo de innovación externa
✗ Confusión sobre qué es gratuito vs propietario
✗ Riesgo de fragmentación prematura

---

## Instrucción constitucional

> **CoResearcher Protocol coordina actividad científica verificable.**
>
> **Einstein Discovery Suite genera inteligencia científica.**
>
> **El protocolo debe poder sobrevivir aunque Einstein desaparezca.**
>
> **Einstein debe poder operar aunque existan otros protocolos.**
>
> **Ningún componente de descubrimiento será dependencia obligatoria del protocolo.**

---

## Roadmap evolutivo

### Sprint 24-25: Consolidación del Protocolo

- [ ] Documentar interfaces públicas estables
- [ ] Separar discovery/ del core
- [ ] Crear MCP independiente de discovery
- [ ] Validar con investigadores reales

### Sprint 26+: Einstein Discovery Suite

- [ ] Commercializar NoveltyDetector
- [ ] Monetizar priorización de hipótesis
- [ ] Integrar con servicios de pago (PubMed, Semantic Scholar)
- [ ] Construir benchmarks propietarios