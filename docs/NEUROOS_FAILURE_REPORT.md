# Reporte de Fallos e Incompatibilidades de NeuroOS (NEUROOS FAILURE REPORT)

**Directiva:** ANTIGRAVITY-003  
**Estado:** Diagnóstico de Ejecución Empírica  
**Principio:** *"Los fallos reales son más valiosos que los documentos"*

Este documento registra de forma transparente y honesta todas las incompatibilidades, dependencias faltantes y fallos de código descubiertos durante la ejecución real de los subsistemas en la máquina local.

---

## 1. Registro de Fallos Detectados en Ejecución Real

### `FAIL-001`: Repositorio EditXT sin Código Ejecutable
* **Sistema Afectado:** EditXT (`C:\Users\usuario\Editxt`).
* **Síntoma Físico:** El directorio `C:\Users\usuario\Editxt` solo contiene la carpeta oculta `.codebase-graph`. No existen scripts `.py` ni módulos de auditoría `ReviewGraph` instalados en esa ruta física.
* **Causa Raíz:** El código de EditXT se encuentra en otro repositorio o no fue clonado en la raíz `C:\Users\usuario\Editxt`.
* **Impacto:** Bloqueo parcial de la fase 2 del flujo End-to-End. EditXT no puede ejecutar revisiones dinámicas en código local actualmente.

---

### `FAIL-002`: Error de Importación de Módulo `ModuleNotFoundError: No module named 'gf'`
* **Sistema Afectado:** GeneForge / Clinical (`C:\Users\usuario\GeneForge Ecosystem\GeneForge\gf\clinical\report_parser.py`).
* **Síntoma Físico:** Al ejecutar `python report_parser.py` directamente, se lanza una excepción de runtime:
  ```text
  ModuleNotFoundError: No module named 'gf'
  ```
* **Causa Raíz:** El paquete `gf` no está instalado en modo editable (`pip install -e .`) ni agregado automáticamente al `sys.path`.
* **Impacto:** Fallo inmediato si un agente o script invoca los módulos de `gf` sin inyectar explícitamente `PYTHONPATH`.
* **Solución de Runtime:** Requerir `$env:PYTHONPATH="C:\Users\usuario\GeneForge Ecosystem\GeneForge"` en los scripts de invocación.

---

### `FAIL-003`: `validate_constitution.py` Invocado Sin Argumentos
* **Sistema Afectado:** CoResearcher (`C:\Users\usuario\coresearcher\scripts\validate_constitution.py`).
* **Síntoma Físico:** Si el script se ejecuta sin parámetros (`python validate_constitution.py`), aborta silenciosamente con un mensaje de uso: `Usage: python validate_constitution.py <graph_json>` y código de salida 1.
* **Causa Raíz:** Ausencia de un JSON por defecto para tests rápidos de sanidad.
* **Impacto:** Si un subagente invoca el validador sin especificar el path exacto del grafo, el proceso falla inmediatamente.

---

### `FAIL-004`: UnicodeEncodeError en Windows CLI (cp1252)
* **Sistema Afectado:** CLI de `skillspector` y scripts Python de benchmarks.
* **Síntoma Físico:** Excepción al imprimir caracteres especiales/emojis en consolas Windows cp1252:
  ```text
  UnicodeEncodeError: 'charmap' codec can't encode characters in position 0-78
  ```
* **Causa Raíz:** La consola por defecto de Windows no utiliza UTF-8 para flujos de salida de Python.
* **Impacto:** Interrupción imprevista de scripts de prueba.
* **Solución de Runtime:** Forzar `$env:PYTHONUTF8=1` antes de la ejecución.

---

## 2. Acción Requerida (Detención de Expansión)

En cumplimiento de la **DIRECTIVA ANTIGRAVITY-003**, se detiene cualquier extensión arquitectónica hasta que se resuelvan los fallos `FAIL-001` (repositorio EditXT) y `FAIL-002` (instalación del paquete `gf`).
