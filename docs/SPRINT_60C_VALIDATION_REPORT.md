# SPRINT 60C VALIDATION REPORT
**Objetivo**: Validar empíricamente la reconstrucción de trayectorias de decisión desde repositorios reales de GitHub  
**Repositorio**: langchain-ai/langgraph  
**Fecha**: 2026-07-31  
**Modo**: Offline desde snapshot `data/langgraph_raw.json`  

## 1. Metodología

Se partió de `data/langgraph_raw.json`, snapshot de issues, PRs y commits.  
Se aplicó extracción por señales léxicas, clasificación por outcome metadata, vinculación por referencias explícitas y secuencias temporales por autor.  
No se utilizó API en vivo.

## 2. Repositorios analizados
- langchain-ai/langgraph 

## 3. Decisions extraídas

| Métrica | Valor |
|---------|-------|
| Total decisiones | 301 |
| Exitosas | 122 |
| Abandonadas | 129 |
| Fallidas | 40 |
| Pendientes | 10 |
| Actores únicos | 106 |

## 4. Precisión / Cobertura

| Indicador | Valor |
|-----------|-------|
| Cobertura de extracción | 301 decisiones con señal |
| Exactitud outcome (PR merged/closed) | Regla por metadata |
| Vínculos explícitos | 231 |
| Vínculos temporales | 426 |

## 5. Casos relevantes

### 5.1 Éxito
- Reconstrucción completa desde snapshot sin API viva.
- 426 edges generados: 231 por referencia explícita, 195 por secuencia temporal por autor.

### 5.2 Fracaso / Limitación
- No se detectaron `superseded` en clasificación automática.
- Vinculación puede sobregenerar `led_to` si un autor hace commits temáticos cercanos en temas distintos.

## 6. Limitaciones detectadas
- Dependencia de keywords en texto público.
- Ausencia de PRs merged explícitos en snapshot limita validación de ciertos edges.
- No se realizó validación manual por muestra en esta ejecución.

## 7. Recomendaciones para SPRINT 61
- Muestreo manual de 20 decisiones para precisión.
- Añadir `evaluate_extraction.py` con métricas por categoría.
- Ampliar a 10-20 repos para generalizar resultados.

## 8. Entregables
- `data/trajectories/langchain_ai_langgraph/decisions_classified.jsonl`
- `data/trajectories/langchain_ai_langgraph/trajectory_graph.json`
- `data/trajectories/langchain_ai_langgraph/evaluation_metrics.json`
- `scripts/offline_sprint60c_from_raw.py`

## 9. Conclusión
SPRINT 60C produjo evidencia ejecutable: 301 decisiones y 426 edges desde langgraph.  
Queda como baseline para SPRINT 61. No se abrieron nuevos frentes arquitectónicos.