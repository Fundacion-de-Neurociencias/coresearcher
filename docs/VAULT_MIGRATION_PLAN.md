# Plan de Migración a Bóveda Central (VAULT MIGRATION PLAN)

**Versión:** 1.0.0  
**Gobernanza:** Plan de Descubrimiento e Inventario Físico de Accesos  
**Estados Permitidos:** `NOT_DISCOVERED` | `DISCOVERED` | `INVENTORIED` | `MIGRATED` | `VALIDATED`  

---

## 1. Fases del Plan de Migración a Bitwarden / Vault Central

```text
[ NOT_DISCOVERED ] ──> [ DISCOVERED ] ──> [ INVENTORIED ] ──> [ MIGRATED ] ──> [ VALIDATED ]
```

1. **Fase 1: Descubrimiento y Censo en Navegadores y Gestores:**  
   Exportar el mapa de logins guardados en Chrome/Edge/Dispositivos hacia el inventario unificado.
2. **Fase 2: Creación de Colecciones en Bitwarden:**  
   - `Development` (Fase A)
   - `University` (Fase B)
   - `Foundation` (Fase B)
   - `ISPA` (Fase B)
   - `Travel` (Fase B)
   - `Finance` (Exclusivo Manuel - Sin delegación)
3. **Fase 3: Migración Físicamente Validada (MIGRATED):**  
   Transferir claves, configurar MFA en la bóveda e ingresar URIs de referencia (`vault_ref`).
4. **Fase 4: Prueba de Ejecución Real (VALIDATED):**  
   Demostración de login y emisión de lease efímero con auditoría registrada.

---

## 2. Matriz de Capacidades Operativas (`discover`, `read`, `act`)

| Identidad / Servicio | Permiso `discover` | Permiso `read` | Permiso `act` | Estado Actual |
| :--- | :---: | :---: | :---: | :---: |
| **GitHub Operations** | **true** | **true** | **true** | **MIGRATED** |
| **Vercel Deployments** | **true** | **true** | **true** | **MIGRATED** |
| **Medicalia Repo** | **true** | **true** | **true** | **INVENTORIED** |
| **Universidad de Oviedo** | **true** | **true** | **false** | **INVENTORIED** |
| **Fundación de Neurociencias** | **true** | **true** | **false** | **INVENTORIED** |
| **HUCA Neurología Ops** | **true** | **false** | **false** | **INVENTORIED** |
| **Gmail Personal Soberano** | **false** | **false** | **false** | **INVENTORIED** |
