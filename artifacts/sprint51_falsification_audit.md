# Sprint 51 — Falsification Audit

## Pregunta

> ¿Existen transformaciones que reduzcan drásticamente el espacio de posibilidades y aun así no aporten capacidad explicativa?

## Hipótesis a falsar

```
Reduction of possibility space → Explanatory gain
```

Si se encuentra al menos un caso donde una transformación reduce drásticamente el espacio de posibilidades pero no aporta capacidad explicativa, la hipótesis queda falsada y "reduction of possibility space" no puede tratarse como principio general.

## Método

Buscar contraejemplos en los 11 casos existentes y, si es necesario, ampliar la muestra a otros proyectos.

### Candidatos a contraejemplo

#### 1. Filtros arbitrarios
Una transformación que elimina opciones por razones no explicativas (ej. "lo decidió la persona que tenía más tiempo libre").

**¿Aparece en los 11 casos?** No explícitamente. Pero en los Casos 7-11 (sin merge), la ausencia de decisión podría ser un filtro arbitrario: no se eligió activamente, simplemente no ocurrió. La reducción de espacio (de "implementar o no implementar" a "no implementar") ocurrió sin que haya una razón documentada.

**¿Aporta capacidad explicativa?** Parcialmente. Saber que "no se implementó porque nadie lo hizo" es información, pero no explica por qué no se implementó en términos de restricciones del proyecto.

#### 2. Restricciones administrativas
Una decisión tomada por política organizativa, no por razones técnicas.

**¿Aparece en los 11 casos?** No directamente. Pero el Caso 6 (grabbit removal) tiene un componente de control de roadmap que es parcialmente administrativo.

**¿Aporta capacidad explicativa?** Sí, pero la restricción es cualitativa y no verificable desde el registro público.

#### 3. Decisiones accidentales
Una alternativa se elige por error, azar, o falta de información.

**¿Aparece en los 11 casos?** No hay evidencia de decisiones accidentales en la muestra. Todas las decisiones documentadas tienen una razón (aunque sea parcial).

**¿Dónde buscar?** Proyectos con documentación mínima, issues sin discusión, PRs mergeados sin revisión.

#### 4. Elecciones aleatorias
Cuando hay múltiples opciones equivalentes y se elige una sin criterio.

**¿Aparece en los 11 casos?** No. En todos los casos con merge, la solución elegida tiene una razón documentada (redundancia, capacidad de revisión, métrica objetiva, etc.).

**¿Dónde buscar?** Proyectos donde haya "bike-shedding" (discusiones largas sobre decisiones triviales) o donde se documente explícitamente que "cualquiera vale".

## Resultado preliminar

En la muestra actual de 11 casos, **no se encuentra un contraejemplo claro**. Todas las transformaciones que reducen el espacio de posibilidades (T1, T2, T3, T5, T7, T9) añaden capacidad explicativa.

Esto no falsa la hipótesis, pero tampoco la confirma. La muestra es pequeña (11 casos, 3 proyectos) y puede estar sesgada hacia proyectos bien documentados.

## Próximo paso

Ampliar la muestra a proyectos con documentación mínima o decisiones explícitamente arbitrarias para buscar el contraejemplo que falsaría la hipótesis.