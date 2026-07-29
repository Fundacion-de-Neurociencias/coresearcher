# Plan de Onboarding de Accesos e Inventario Físico Real (NEUROOS ACCESS ONBOARDING)

**Versión:** 1.1.0  
**Gobernanza:** Plan de Ejecución Físico y Censo de Accesos  
**Estados Permitidos:** `NOT_DISCOVERED` | `DISCOVERED` | `INVENTORIED` | `MIGRATED` | `VALIDATED`  

---

## 1. Hoja de Ruta de Onboarding Físico (5 Fases)

```text
┌────────────────────────┐    ┌────────────────────────┐    ┌────────────────────────┐
│ FASE 1: BLINDAJE       │───>│ FASE 2: BÓVEDA VAULT   │───>│ FASE 3: INVENTARIO REAL│
│ MFA + Sin Circularidad │    │ Bitwarden Colecciones  │    │ 50 Servicios Primero   │
└────────────────────────┘    └────────────────────────┘    └───────────┬────────────┘
                                                                        │
┌────────────────────────┐    ┌────────────────────────┐                │
│ FASE 5: BOTS TÉCNICOS  │<───│ FASE 4: DELEGACIÓN     │<───────────────┘
│ Cuentas Específicas    │    │ Gradual (Grupos A-D)   │
└────────────────────────┘    └────────────────────────┘
```

### Fase 1 — Blindaje de la Cuenta Operativa (`manuelmdezglez@gmail.com`)
1. **MFA Obligatoria:** Activar verificación en dos pasos (Google Authenticator / YubiKey).
2. **Códigos de Recuperación:** Almacenados fuera de línea en papel/soporte ignífugo.
3. **Email de Recuperación:** Configurado en cuenta personal secundaria sin circularidad hacia `manuelmenendez@gmail.com`.
4. **Prohibición:** Prohibido convertir esta cuenta en email de recuperación del pasaporte digital soberano.

### Fase 2 — Bóveda de Contraseñas (Bitwarden / Vaultwarden)
Organización: `NeuroOS`  
Colecciones Físicas:
- `Development` (GitHub, Vercel, OpenRouter, Render)
- `University` (Universidad de Oviedo SSO, Campus Virtual)
- `Foundation` (Fundación de Neurociencias, Stripe, Web)
- `ISPA` (Investigación ISPA/FINBA)
- `Travel` (Booking, Renfe, Aerolíneas)
- `Finance` (Exclusivo Manuel - Sin delegación)

### Fase 3 — Inventario Real de los 50 Primeros Servicios
Priorizar la migración del censo de los primeros 50 servicios reales en lugar de 500 teóricos.

---

## 2. Matriz Física de Onboarding y Estado de Delegación

| Servicio / Plataforma | Usuario / Identidad | Categoría | Nivel de Riesgo | MFA Activo | En Vault | Permisos (`discover`, `read`, `act`) | Estado Actual |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **GitHub Operations** | `manuelmdezglez@gmail.com` | Desarrollo | `AUTOMATION` | Sí | Sí | `discover: true, read: true, act: true` | **MIGRATED** |
| **Vercel Deployments** | `manuelmdezglez@gmail.com` | Hosting / Dev | `AUTOMATION` | Sí | Sí | `discover: true, read: true, act: true` | **MIGRATED** |
| **Medicalia Repo** | `automation@medicalia.org` | Proyecto | `AUTOMATION` | Sí | Sí | `discover: true, read: true, act: true` | **INVENTORIED** |
| **CoResearcher Repo** | `github-bot@coresearcher` | Proyecto | `AUTOMATION` | Sí | Sí | `discover: true, read: true, act: true` | **INVENTORIED** |
| **GeneForge Repo** | `github-bot@geneforge` | Proyecto | `AUTOMATION` | Sí | Sí | `discover: true, read: true, act: true` | **INVENTORIED** |
| **Neurodiagnoses Repo** | `github-bot@neurodiagnoses` | Proyecto | `AUTOMATION` | Sí | Sí | `discover: true, read: true, act: true` | **INVENTORIED** |
| **Universidad de Oviedo** | `manuel.menendez@uniovi.es` | Universidad | `OPERATIONAL` | Sí | Pendiente | `discover: true, read: true, act: false` | **INVENTORIED** |
| **Fundación de Neurociencias** | `fundacion@neurociencias.org` | Fundación | `OPERATIONAL` | Sí | Pendiente | `discover: true, read: true, act: false` | **INVENTORIED** |
| **ISPA / FINBA** | `ispa_researcher` | Investigación | `OPERATIONAL` | Sí | Pendiente | `discover: true, read: true, act: false` | **DISCOVERED** |
| **Gmail Fundación** | `fundacion@neurociencias.org` | Correo Ops | `OPERATIONAL` | Sí | Pendiente | `discover: true, read: true, act: false` | **INVENTORIED** |
| **Gmail Uniovi** | `manuel.menendez@uniovi.es` | Correo Ops | `OPERATIONAL` | Sí | Pendiente | `discover: true, read: true, act: false` | **INVENTORIED** |
| **HUCA Neurología Ops** | `huca_clinical_ops` | Sanitario | `CRITICAL_OPERATIONAL` | Sí | No | `discover: true, read: false, act: false` | **INVENTORIED** |
| **Gmail Personal Principal** | `manuelmenendez@gmail.com` | Soberano | `SOVEREIGN` | Sí | No | `discover: false, read: false, act: false` | **INVENTORIED** |

---

## 3. Protocolo de Transición de Estados
Cualquier activo de NeuroOS solo transiciona mediante validación física:
$$\text{NOT\_DISCOVERED} \longrightarrow \text{DISCOVERED} \longrightarrow \text{INVENTORIED} \longrightarrow \text{MIGRATED} \longrightarrow \text{VALIDATED}$$
