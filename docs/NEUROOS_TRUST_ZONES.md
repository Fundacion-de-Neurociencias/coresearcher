# Zonas de Confianza y Límites de Autonomía de NeuroOS (NEUROOS TRUST ZONES)

**Versión:** 1.0.0  
**Gobernanza:** Clasificación por Nivel de Confianza y Autonomía  
**Estado:** Canónico - Directiva de Seguridad y Ejecución  

---

## 1. Principio Fundamental de Autonomía

NeuroOS no se gobierna por dominios estáticos, sino por **Niveles de Confianza Requeridos (Trust Zones)**. 

La pregunta no es *"¿Qué agente hace qué?"*, sino:  
> **"¿Qué agente está autorizado a ejecutar o modificar qué activo?"**

---

## 2. Matriz General de Zonas de Confianza

| Zona | Nivel de Sensibilidad | Ejecuta | Aprueba | Arquitectura de Ejecución |
| :--- | :--- | :--- | :--- | :--- |
| **Zona Negra / Nivel D** | **Prohibido a Antigravity** | **Solo ManuEl** | **Solo ManuEl** | Aislamiento total. Antigravity nunca ejecuta acciones. |
| **Zona Roja / Nivel A** | **Máxima Sensibilidad** | **Solo ManuEl** | **Solo ManuEl** | Antigravity prepara borrador; ManuEl + IA Local ejecuta. |
| **Zona Naranja / Nivel B** | **Sensibilidad Media** | **Antigravity** | **ManuEl** | Antigravity propone → ManuEl aprueba → Antigravity ejecuta. |
| **Zona Verde / Nivel C** | **Baja Sensibilidad** | **Antigravity** | **Antigravity** | Autonomía total (CTO Distribuido). |

---

## 3. Desglose Operativo por Zonas

### 🔴 Zona Negra / Nivel D: Activos Prohibidos (Sin Acceso Ejecutivo para Antigravity)
Queda strictly prohibido a Antigravity ejecutar cualquier tipo de acción, transacción o modificación sobre estos activos.

```yaml
protected_repositories:
  - UQG

protected_services:
  - AgenciaTributaria
  - SeguridadSocial
  - Clave
  - BancoSantander
  - BBVA
  - OpenBank

protected_credentials:
  - certificados_digitales
  - api_keys_privadas_produccion
  - seed_phrases_crypto
```

---

### 🚨 Zona Roja / Nivel A: Máxima Sensibilidad (Preparación por Antigravity, Ejecución por ManuEl + IA Local)
Antigravity únicamente puede preparar borradores o procesar datos. La firma, presentación o transacción la ejecuta **ManuEl** desde su entorno local con IA local.

* **Servicios/Trámites:** Declaraciones IRPF/impuestos, firma de contratos legales privados, información médica personal/familiar, transacciones bancarias o de inversión, cambios de credenciales.
* **Patrón de Ejecución:**
  $$\text{Antigravity (Prepara Borrador)} \longrightarrow \text{ManuEl + IA Local (Revisa)} \longrightarrow \text{ManuEl (Firma/Presenta)}$$

---

### 🟠 Zona Naranja / Nivel B: Sensibilidad Media (Propuesta de Antigravity, Aprobación de ManuEl)
Antigravity analiza el contexto, consulta herramientas y genera una propuesta completa. No se ejecuta nada irreversible hasta la aprobación explícita de ManuEl.

* **Operaciones Incluidas:**
  - Reservas de viaje (vuelos, hoteles, trenes).
  - Compras y adquisiciones.
  - Gestión de agenda y reestructuración de calendarios.
  - Envíos de correo electrónico a terceros.
  - Solicitudes de subvenciones y contratos de proyectos.
  - Gestión operativa de la Fundación de Neurociencias y Medicalia.
* **Patrón de Ejecución:**
  $$\text{Antigravity (Propuesta)} \longrightarrow \text{ManuEl (Aprobación/Feedback)} \longrightarrow \text{Antigravity (Ejecución)}$$

---

### 🟢 Zona Verde / Nivel C: Baja Sensibilidad (Autonomía Total - CTO Distribuido)
Antigravity opera de forma autónoma. Puede crear issues, refactorizar código, actualizar dependencias, generar documentación, ejecutar tests, abrir PRs y coordinar subagentes.

* **Repositorios y Activos Habilitados:**
  - `Medicalia`
  - `CoResearcher`
  - `Editxt`
  - `GeneForge` / `GeneForgeLang Ecosystem`
  - `Neurodiagnoses` / `Neurodiagnoses Ecosystem`
  - `PharmaOracle`
  - `Vadimecum`
  - `BrainBridge`
  - `DataBrain`
  - `Neurotech`
  - Documentación de proyectos, páginas web, MCPs, skills, pipelines CI/CD.

---

## 4. Regla Constitucional de Seguridad y Límites

1. **Principio de Mínimo Privilegio:** Ningún subagente o herramienta MCP heredará permisos de Nivel A o D.
2. **Trazabilidad de Firma:** Toda acción en Zona Naranja o Roja debe guardar la traza de aprobación explícita de ManuEl en la memoria del kernel de NeuroOS.
