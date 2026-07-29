# Cadena de Autoridad y Jurisdicción de NeuroOS (CHAIN OF AUTHORITY)

**Versión:** 2.0.0  
**Gobernanza:** Directiva Constitucional Canónica  
**Estado:** Inviolable  

---

## 1. Las Tres Cadenas Independientes

Para evitar cuellos de botella operativos y duplicación de datos, NeuroOS diferencia explícitamente tres cadenas:

### 1.1 Cadena de Autoridad (Inmutable)
Responde a: *¿Quién puede autorizar, revocar o delegar?*
```text
Manuel (Nivel 0) ──> ManuEl (Nivel 1) ──> Antigravity (Nivel 2) ──> Subagentes (Nivel 3)
```

### 1.2 Cadena de Ejecución (Variable / Directa)
Una vez que la autorización o lease es válida, la ejecución es directa sin intermediarios innecesarios.
```text
Subagente ───────> GitHub / Tool / File API (Directo)
Antigravity ────> Gmail / Workspace API (Directo tras aprobación)
ManuEl ─────────> Filesystem Local (Directo)
```

### 1.3 Cadena de Evidencia (Independiente)
Toda acción ejecutada escribe su evento de forma directa e inmutable en la bitácora de auditoría.
```text
Ejecutor (Subagente / Antigravity / ManuEl) ──> Audit Trail (audit_trail.jsonl)
```

---

## 2. Axioma Fundamental de Separación de Funciones

> **Manuel tiene la Autoridad.** (Soberano Único).  
> **ManuEl tiene la Jurisdicción.** (Policy Engine / Leases / Audit en Lenovo).  
> **Antigravity tiene la Iniciativa.** (Planificación / Orquestación / Desarrollo en Mac Studio).  
> **Los Subagentes tienen la Ejecución.** (Tareas específicas).  

---

## 3. Failure Modes and Jurisdiction Availability (Modo Degradado)

### Paradoja de Disponibilidad
Si el nodo local de Lenovo (ManuEl / IA Local) está apagado o no disponible, NeuroOS entra automáticamente en **Modo Degradado de Alta Disponibilidad** para evitar el bloqueo del desarrollo.

```text
Lenovo / ManuEl ONLINE  ──> Policy Engine Normal (Zonas: BLACK, CRITICAL, CONTROLLED, AUTONOMOUS)
Lenovo / ManuEl OFFLINE ──> Modo Degradado Activado (Solo Zonas AUTONOMOUS permitidas)
```

### Matriz de Disponibilidad en Modo Degradado (Lenovo Offline)

| Zona de Riesgo | Estado con ManuEl Offline | Razón y Comportamiento |
| :--- | :---: | :--- |
| **🟢 AUTONOMOUS** | **PERMITIDO** | Antigravity continúa trabajando de forma autónoma en repositorios de código, desarrollo, tests, CI/CD y documentación (`Medicalia`, `CoResearcher`, `Editxt`, `GeneForge`, `Neurodiagnoses`, etc.). |
| **🟠 CONTROLLED_LOW** | **BLOQUEADO** | Requiere evaluación de jurisdicción; se suspende hasta recuperar conexión con ManuEl. |
| **🟠 CONTROLLED_HIGH**| **BLOQUEADO** | Requiere aprobación explícita humana de Manuel/ManuEl. |
| **🔴 CRITICAL** | **BLOQUEADO** | Requiere ejecución exclusiva en ManuEl + IA Local. |
| **⚫ BLACK** | **BLOQUEADO** | Acceso inalcanzable. |
