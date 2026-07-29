# Sprint 54 — Explanatory Gain per Mechanism

## Pregunta

> ¿Cuánta capacidad explicativa aporta cada mecanismo de selección?

## Método

Para cada uno de los 6 mecanismos identificados en Sprint 53, evaluar:

1. **Frecuencia**: en cuántos casos aparece
2. **Ganancia explicativa media**: cuánto añade respecto al estado aislado (usando la escala de Sprint 49: Sí / No / Indeterminado)
3. **Densidad explicativa**: cuánta información adicional aporta por aparición

La pregunta central de CoResearcher no es "¿qué ocurre más?" sino "¿qué explica más?".

## Evaluación por mecanismo

### Mecanismo A: Eliminación por redundancia
**Casos donde aparece**: 1
**Ganancia explicativa**: Alta. Saber que dos funciones hacían lo mismo explica por qué se eliminó una. Sin este mecanismo, la eliminación parece arbitraria.
**Densidad**: Alta. Una sola frase ("parece que si eliminamos regress, ya convergemos") contiene toda la justificación.

### Mecanismo B: Reducción por capacidad limitada
**Casos donde aparece**: 2
**Ganancia explicativa**: Alta. Saber que el PR completo era demasiado grande para revisarlo explica por qué el resultado es un módulo pequeño.
**Densidad**: Alta. Una frase ("too much to bite off in one PR") contiene la justificación completa.

### Mecanismo C: Separación por restricción arquitectónica
**Casos donde aparece**: 3
**Ganancia explicativa**: Alta. Saber que matplotlib no debía estar en el núcleo explica la dirección del cambio arquitectónico.
**Densidad**: Media. La justificación está distribuida en la discusión, no en una frase única.

### Mecanismo D: Sustitución por evidencia cuantitativa
**Casos donde aparece**: 4
**Ganancia explicativa**: Alta. La métrica objetiva (12MB vs 15KB) es la justificación más sólida de todos los casos.
**Densidad**: Alta. Los datos hablan por sí mismos.

### Mecanismo E: Selección por trade-off explícito
**Casos donde aparece**: 5
**Ganancia explicativa**: Alta. Es el caso con más alternativas documentadas y criterios explícitos.
**Densidad**: Alta. Múltiples alternativas + criterios + decisión documentada.

### Mecanismo F: Internalización por control de dependencias
**Casos donde aparece**: 6
**Ganancia explicativa**: Media-Alta. El criterio ("control de roadmap") es cualitativo y no verificable desde el registro público.
**Densidad**: Media. La justificación existe pero es menos sólida que en otros casos.

## Tabla de ganancia explicativa por mecanismo

| Mecanismo | Casos | Frecuencia | Ganancia | Densidad |
|-----------|:----:|:----------:|:--------:|:--------:|
| A: Redundancia | 1 | 1/6 | Alta | Alta |
| B: Capacidad | 2 | 1/6 | Alta | Alta |
| C: Arquitectura | 3 | 1/6 | Alta | Media |
| D: Evidencia cuantitativa | 4 | 1/6 | Alta | Alta |
| E: Trade-off explícito | 5 | 1/6 | Alta | Alta |
| F: Control dependencias | 6 | 1/6 | Media-Alta | Media |

### Observaciones

1. **Todos los mecanismos tienen ganancia alta o media-alta**. No hay ningún mecanismo con ganancia baja en esta muestra. Esto sugiere que el tipo de mecanismo importa menos que el hecho de que haya un mecanismo documentado.

2. **La frecuencia es idéntica (1/6) para todos**. Cada mecanismo aparece exactamente una vez. No es posible determinar si algún mecanismo es dominante porque la muestra es demasiado pequeña.

3. **La densidad varía**: los mecanismos con justificación concentrada en una frase (A, B, D, E) tienen densidad alta; los que requieren inferencia de la discusión (C, F) tienen densidad media.

4. **El mecanismo D (evidencia cuantitativa) es el único con evidencia reproducible**. Los demás dependen de juicios de expertos no verificables desde el registro público.

## Lo que esto sugiere

La pregunta relevante no es "¿qué mecanismo es más frecuente?" sino "¿qué hace que un mecanismo tenga alta densidad explicativa?".

Los mecanismos con alta densidad comparten una propiedad: **la justificación está contenida en una frase o dato específico, no distribuida en la discusión**. Esto sugiere que la densidad explicativa depende más de la claridad de la documentación que del tipo de mecanismo.

## Pregunta abierta para Sprint 55

```
¿La ganancia explicativa depende del tipo de mecanismo
o del hecho de que haya algún mecanismo documentado?
```

Para responder, habría que encontrar casos donde:
- Hay mecanismo documentado → medir ganancia
- No hay mecanismo documentado → medir ganancia
- Comparar

Si la ganancia es similar independientemente del mecanismo, entonces lo que importa es la presencia de justificación, no su tipo. Si la ganancia varía significativamente por mecanismo, entonces el tipo importa.