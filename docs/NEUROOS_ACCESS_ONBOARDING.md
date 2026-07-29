# Plan de Onboarding de Accesos e Inventario Físico Real (NEUROOS ACCESS ONBOARDING)

**Versión:** 1.0.0  
**Gobernanza:** Plan de Ejecución Físico y Delegación Gradual  
**Estado:** Activo - Onboarding de Servicios Reales  

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
Priorizar la migración de los primeros 50 servicios reales en lugar de 500 teóricos.

---

## 2. Matriz Física de Onboarding y Estado de Delegación

| Servicio / Plataforma | Usuario / Identidad | Categoría | Nivel de Riesgo | MFA Activo | En Vault | Estado de Delegación |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **GitHub Operations** | `manuelmdezglez@gmail.com` | Desarrollo | `AUTOMATION` | Sí | Sí | **Grupo A (Completado)** |
| **Vercel Deployments** | `manuelmdezglez@gmail.com` | Hosting / Dev | `AUTOMATION` | Sí | Sí | **Grupo A (Completado)** |
| **Medicalia Repo** | `automation@medicalia.org` | Proyecto | `AUTOMATION` | Sí | Sí | **Grupo A (Completado)** |
| **CoResearcher Repo** | `github-bot@coresearcher` | Proyecto | `AUTOMATION` | Sí | Sí | **Grupo A (Completado)** |
| **GeneForge Repo** | `github-bot@geneforge` | Proyecto | `AUTOMATION` | Sí | Sí | **Grupo A (Completado)** |
| **Neurodiagnoses Repo** | `github-bot@neurodiagnoses` | Proyecto | `AUTOMATION` | Sí | Sí | **Grupo A (Completado)** |
| **Universidad de Oviedo** | `manuel.menendez@uniovi.es` | Universidad | `OPERATIONAL` | Sí | Pendiente | **Grupo B (Pendiente)** |
| **Fundación de Neurociencias** | `fundacion@neurociencias.org` | Fundación | `OPERATIONAL` | Sí | Pendiente | **Grupo B (Pendiente)** |
| **ISPA / FINBA** | `ispa_researcher` | Investigación | `OPERATIONAL` | Sí | Pendiente | **Grupo B (Pendiente)** |
| **Gmail Fundación** | `fundacion@neurociencias.org` | Correo Ops | `OPERATIONAL` | Sí | Pendiente | **Grupo C (Restringido)** |
| **Gmail Uniovi** | `manuel.menendez@uniovi.es` | Correo Ops | `OPERATIONAL` | Sí | Pendiente | **Grupo C (Restringido)** |
| **HUCA Neurología Ops** | `huca_clinical_ops` | Sanitario | `CRITICAL_OPERATIONAL` | Sí | No | **Grupo C (Sin LLM Nube)** |
| **Gmail Personal Principal** | `manuelmenendez@gmail.com` | Soberano | `SOVEREIGN` | Sí | No | **Grupo D (NUNCA)** |

---

## 3. Fase 4 — Protocolo de Delegación Gradual por Grupos

- **Grupo A (Impacto Bajo - Desarrollo y Código):** GitHub, Vercel, Medicalia, GeneForge, Neurodiagnoses. Delegación autónoma a Antigravity completada.
- **Grupo B (Impacto Medio - Institucional y Proyectos):** Fundación, ISPA, Uniovi. Delegación mediante Leases y Puertas de Aprobación de ManuEl.
- **Grupo C (Impacto Delicado - Correos Corporativos):** Gmail Fundación, Gmail Uniovi. Requiere aprobación humana expresa por cada mensaje externo redactado.
- **Grupo D (NUNCA):** Identidad Soberana Personal. Acceso agencial strictly prohibido.

---

## 4. Fase 5 — Descomposición en Cuentas Técnicas Específicas

Para evitar convertir a `manuelmdezglez@gmail.com` en otro punto único de fallo, se derivan cuentas de servicio dedicadas:
- `automation@medicalia.org` (Automatización de Medicalia)
- `github-bot@coresearcher` (Bot de CI/CD de CoResearcher)
- `neuroos-bot@domain.org` (Notificaciones del Runtime)
