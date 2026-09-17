# Constraint Stability Report — SPRINT 61

**Fecha**: 2026-08-01
**Sprint**: SPRINT 61 — Constraint Reconstruction Validation
**Veredicto global**: 🔴 RED — H7 FALSIFICADA en su implementación actual

---

## 1. Resumen

Este reporte sintetiza los resultados de 5 fases de validación científica
diseñadas para **intentar falsar H7** (Constraint Reconstruction).

H7 no sobrevivió el intento de falsación.

---

## 2. Métricas clave

| Métrica | Valor | Criterio | Estado |
|---------|-------|----------|--------|
| Convergencias reales | 100% | ≥80% | ✅ |
| Cohen kappa (is_real) | -0.030 | ≥0.7 | 🔴 |
| Cohen kappa (hypothesis) | -0.067 | ≥0.7 | 🔴 |
| False positive rate (synthetic) | 70% | <20% | 🔴 |
| False positive rate (noise) | 35% | <20% | 🔴 |
| Repositorios analizados | 1 | ≥10 | ⚪ |
| Hipótesis competidoras por convergencia | 3 | ≥3 | ✅ |
| Definición operacional | 100% | 100% | ✅ |
| Criterios de falsación | 100% | 100% | ✅ |

---

## 3. Distribución de tipos de restricción

| Tipo | Frecuencia total | Como principal |
|------|------------------|----------------|
| tecnica | 5 | 0 |
| conceptual | 3 | 3 |
| historica | 3 | 1 |
| matematica | 1 | 0 |
| ontologica | 0 | 0 |

**Patrón**: Las restricciones conceptuales dominan como hipótesis principales
(3 de 4). Las técnicas aparecen como competidoras frecuentes pero nunca
como principales. Esto sugiere que las barreras reales son más conceptuales
que técnicas, pero el sample size (4) es insuficiente.

---

## 4. Hallazgo crítico: Hallucinated Constraints

El experimento de falsación (FASE 5) reveló que el detector de convergencias
produce **hallucinated constraints**: detecta "convergencias" en datos
sintéticos y de ruido con una tasa de falsos positivos del 70%.

### Causa raíz

El detector usa Jaccard similarity de títulos para agrupar decisiones.
Cualquier conjunto de nodos con títulos similares (incluso sintéticos)
es detectado como convergencia. No hay validación de:
- Si los actores son humanos reales
- Si los PRs tienen discusión real
- Si el tema es semánticamente coherente
- Si hay evidencia de código más allá del título

### Implicación

Las 4 convergencias detectadas en langgraph pueden ser reales (FASE 1
las clasificó como reales con 100%), pero el detector no puede
distinguirías de artefactos. Se necesita un mecanismo de validación
más robusto.

---

## 5. Estado epistemológico

### H7 (implementación actual)
```
Estado: FALSIFIED
Razón: 70% false positive rate en convergencias sintéticas
Kappa: -0.030 (poor agreement entre revisores)
```

### H7 (concepto / teoría)
```
Estado: UNDETERMINED
Razón: La teoría no ha sido realmente sometida a prueba porque nunca
       llegamos a observar restricciones. Solo observamos convergencias.
       El mecanismo que conecta convergencia → restricción ha resultado
       poco fiable. No podemos decir "el concepto es válido" — solo
       podemos decir "no sabemos".
Necesario: definición operacional de "restricción" (SPRINT 62)
```

### Restricciones como variables latentes
```
Estado: UNDETERMINED (no "validadas")
Razón: Nunca observamos restricciones directamente.
       Solo observamos convergencias.
       La conexión convergencia → restricción no está validada.
```

### Restricciones individuales
```
CONV-000001: UNDETERMINED (3 hipótesis activas)
CONV-000002: UNDETERMINED (3 hipótesis activas)
CONV-000003: UNDETERMINED (3 hipótesis activas)
CONV-000004: UNDETERMINED (3 hipótesis activas)
```

Ninguna restricción ha sido promovida a hecho.
El sistema responde honestamente: "no sabemos".

---

## 6. Lo que funciona

1. **Protocolo epistemológico**: hipótesis competidoras + definición operacional + falsación
2. **Estados epistemológicos**: OBSERVED/DERIVED/HYPOTHESIZED/FALSIFIED/UNDETERMINED
3. **Prohibición de wishful mnemonic**: "restricción detectada" → "hipótesis de restricción"
4. **Honestidad epistemológica**: el sistema detectó su propia limitación

## 7. Lo que no funciona

1. **Detector de convergencias**: vulnerable a hallucinated constraints (70% FPR)
2. **Acuerdo entre revisores**: κ = -0.030 (worse than chance)
3. **Generalización**: solo 1 repositorio analizado

---

## 8. Recomendaciones

### Inmediato
1. Mejorar detector: validar actores humanos, discusión real, coherencia semántica
2. Repetir FASE 2 con revisores humanos reales
3. Ejecutar pipeline en 10+ repositorios

### Si el detector mejora
1. Repetir FASE 5
2. Si FPR < 20% → H7 gana credibilidad provisional
3. Si κ ≥ 0.7 → GREEN

### Si el detector no mejora
1. H7 queda FALSIFIED
2. Replantear detección de convergencias
3. Considerar análisis semántico más profundo

---

## 9. Conclusión

> Una teoría falsa es peor que admitir que todavía no tenemos teoría.

H7 fue falsada en su implementación actual. Eso es progreso científico.

El sistema detectó su propia limitación. Eso es honestidad epistemológica.

El concepto de restricciones como variables latentes está UNDETERMINED.
No podemos decir "el concepto es válido" — solo podemos decir "no sabemos".
Lo que falla es el detector. Pero la teoría tampoco ha sido probada.

---

*SPRINT 61 produjo datos experimentales reales.*
*H7 fue falsada. El sistema aprendió algo sobre sí mismo.*
*Eso es exactamente lo que debe hacer la ciencia.*