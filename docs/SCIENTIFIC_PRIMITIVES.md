# Scientific Primitives Audit
## Universalidad vs Especificidad

---

## Regla de Oro

> "**Si no existe en física, química, biología, matemáticas, economía e ingeniería, NO es core.**"

Cada primitiva debe pasar este filtro de universalidad.

---

## Tabla de Primitivas - AUDITORÍA AGRESIVA

| Primitiva | Universal | Core Status | Justificación |
|-----------|-----------|-------------|---------------|
| **Question** | ✅ Sí | ✅ CORE | ¿Por qué? existente en toda ciencia |
| **Observation** | ✅ Sí | ✅ CORE | Observación directa es universal |
| **Measurement** | ✅ Sí | ✅ CORE | Medición es actividad científica básica |
| **Evidence** | ✅ Sí | ✅ CORE | Evidencia apoya afirmaciones |
| **Claim** | ✅ Sí | ✅ CORE | Afirmación atómica: existente en toda ciencia |
| **Finding** | ❌ No | 📦 DOMAIN PACK | En matemáticas/teórica no existe - es synthesis |
| **Mechanism** | ✅ Sí | ✅ CORE | Explicación causal universal |
| **Model** | ✅ Sí | ✅ CORE | Modelo integrador existente |
| **Theory** | ✅ Sí | ✅ CORE | Marco explicativo universal |
| **Researcher** | ✅ Sí | ✅ CORE | Científico/a investigador/a existe en todas partes |
| **Biomarker** | ❌ No | 📦 DOMAIN PACK | Específico de biología/medicina |
| **Gene** | ❌ No | 📦 DOMAIN PACK | Específico de genética |
| **Drug** | ❌ No | 📦 DOMAIN PACK | Específico de farmacología |
| **Patient** | ❌ No | 📦 DOMAIN PACK | Específico de medicina clínica |
| **Trial** | ❌ No | 📦 DOMAIN PACK | Específico de investigación clínica |

---

## Primitivas Core (Universales)

### Question
- Física: "¿Por qué la luz se curva?"
- Química: "¿Por qué esta reacción es exotérmica?"
- Biología: "¿Por qué APOE4 causa AD?"
- Matemáticas: "¿Existe un patrón aquí?"
- Economía: "¿Por qué la inflación sube?"
- Ingeniería: "¿Por qué falló este material?"

### Observation
- Física: "La luz se curva 1.75 en el eclipse"
- Química: "El pH disminuyó a 3.2"
- Biología: "APOE4 homocigóticos tienen más placas"
- Matemáticas: "Esta serie converge a π"
- Economía: "El desempleo subió a 8%"
- Ingeniería: "La temperatura llegó a 150°C"

### Measurement
- Física: "masa = 9.11e-31 kg"
- Química: "pH = 7.4"
- Biología: "pTau217 = 23.5 pg/mL"
- Matemáticas: "error < 0.05"
- Economía: "PIB = 1.2 billones"
- Ingeniería: "tensión = 250 MPa"

### Evidence
- Física: "3 experimentos independientes coinciden"
- Química: "espectro muestra pico a 340nm"
- Biología: "p < 0.001 en 5 cohortes"
- Matemáticas: "teorema demostrado por 3 métodos"
- Economía: "correlación r = -0.78"
- Ingeniería: "fatiga confirmada en ciclo 10000"

### Claim
- Física: "masa → curvatura espacio → órbita"
- Química: "pH → velocidad reacción → producto"
- Biología: "APOE4 → amiloide → deterioro"
- Matemáticas: "n → serie → convergencia"
- Economía: "tipos → capital → inversión"
- Ingeniería: "temperatura → fatiga → fallo"

### Finding
- Física: "relación masa-órbita (r²=0.99)"
- Química: "relación pH-producto (k=0.45)"
- Biología: "relación APOE4-placas (OR=3.2)"
- Matemáticas: "serie converge a π/4"
- Economía: "relación tipos-inversión (β=-0.3)"
- Ingeniería: "relación temperatura-fallo (N=5000)"

**Nota**: Finding parece universal como "patrón distilado". Revisar con más ejemplos.

### Mechanism
- Física: "masa → curvatura → trayectoria geodésica"
- Química: "pH → concentración → velocidad"
- Biología: "estrés → pTau217 → amiloide"
- Matemáticas: "derivada → integral → función"
- Economía: "tipos → capital → inversión → empleo"
- Ingeniería: "temperatura → microfissuras → fallo"

### Model
- Física: "Modelo de relatividad + gravitación"
- Química: "Modelo cinético + termodinámico"
- Biología: "Modelo amiloide + neuroinflamación"
- Matemáticas: "Modelo estadístico + serie"
- Economía: "Modelo IS-LM + crecimiento"
- Ingeniería: "Modelo de fatiga + fluencia"

### Theory
- Física: "Relatividad general + teoría de campos"
- Química: "Química cuántica + cinética"
- Biología: "Teoría proteostasis + neurodegeneración"
- Matemáticas: "Teoría números + teoría grupos"
- Economía: "Teoría macro + teoría micro"
- Ingeniería: "Teoría materiales + teoría estructuras"

---

## Primitivas Domain Pack (Específicas)

### Biomarker
- Solo medicina/biología
- Usa: Observation + Claim universal

### Gene
- Solo genética
- Usa: Entity + Claim universal

### Drug
- Solo farmacología
- Usa: Entity + Claim universal

### Patient
- Solo medicina clínica
- Usa: Entity + Observation

---

## API Core (Simplificada) - Finding movido a Domain Pack

```python
# Universal scientific objects (CORE)
QUESTION.create(text, domain)
OBSERVATION.record(entities, values, units)
MEASUREMENT.capture(entity, value, uncertainty)
EVIDENCE.record(source_claims, replication_count)
CLAIM.assert(subject, predicate, object, evidence_refs)
MECHANISM.propose(entities, arrows, type)
MODEL.integrate(mechanisms)
THEORY.unify(models)
RESEARCHER.register(name, institution, expertise)

# Participation actions
SUPPORT(object_id, researcher_id, evidence=None)
CHALLENGE(object_id, researcher_id, reasoning)
REPLICATE(object_id, researcher_id, method)
CONFIRM(object_id, researcher_id, data)
REJECT(object_id, researcher_id, counterevidence)
FORK(object_id, variants)
```

### Domain Pack API (específico)

```python
# Para biología/medicina
Finding.distill_claims(claims) → Finding
Biomarker.register(name, associated_conditions)
Gene.link_to_phenotype(gene, phenotype)
```

---

## Implementación Recomendada

1. **Sprint 23A**: Scientific Semantic Compiler (traduce lenguaje humano a objetos)
2. **Sprint 23B**: Universal Object Registry (solo las primitivas core)
3. **Sprint 24**: Domain Pack Framework (para biomarcadores, genes, fármacos)
4. **Sprint 25**: Einstein v2 (opera sobre mechanisms reales)

---

## La Identidad Final

CoResearcher no es:
- Un motor de IA
- Un sistema de papers
- Un knowledge graph

CoResearcher es:
- **La Scientific Interaction Layer**
- **El Scientific State Machine**
- **El Global Scientific Ledger**

Donde el conocimiento científico vive con su historia de participación.