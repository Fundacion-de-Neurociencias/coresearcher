# Playbook Operativo de Descubrimiento Masivo de Identidades y Servicios (IDENTITY DISCOVERY PLAYBOOK)

**Versión:** 1.0.0  
**Gobernanza:** Descubrimiento Empírico y Censo Físico  
**Regla de Oro:** *"Un activo solo pasa a MIGRATED cuando existe prueba verificable de login, credencial en bóveda, MFA y prueba exitosa."*  

---

## 1. Procedimiento Operativo de Descubrimiento Físico (5 Fuentes)

```text
┌────────────────────────┐    ┌────────────────────────┐    ┌────────────────────────┐
│ FUENTE 1: NAVEGADORES  │───>│ FUENTE 2: GMAIL SEARCH │───>│ FUENTE 3: GESTORES PASS│
│ Chrome / Edge Passwords│    │ Filtros de Verificación│    │ Exportación Bitwarden  │
└────────────────────────┘    └────────────────────────┘    └───────────┬────────────┘
                                                                        │
┌────────────────────────┐    ┌────────────────────────┐                │
│ FUENTE 5: GITHUB ORGAN │<───│ FUENTE 4: AUTENTICADOR │<───────────────┘
│ PATs / OAuth Apps      │    │ Authenticator / YubiKey│
└────────────────────────┘    └────────────────────────┘
```

### Fuente 1 — Navegadores (Chrome & Edge)
- **Acción:** Exportar e inspeccionar logins guardados en Chrome (`chrome://password-manager/settings`) y Microsoft Edge (`edge://wallet/passwords`).
- **Objetivo:** Descubrir portales secundarios, dominios antiguos y plataformas docentes o de viajes.

### Fuente 2 — Filtros de Búsqueda en Gmail
- **Filtros de Búsqueda:**
  ```text
  subject:(verify OR verification OR "welcome to" OR "confirm your account" OR "password reset" OR "security alert")
  ```
- **Objetivo:** Revelar altas en servicios olvidados a lo largo de los años.

### Fuente 3 — Gestores de Contraseñas
- Exportar censo desde Chrome Password Manager o Bitwarden Vault.

### Fuente 4 — Autenticadores MFA (MFA Audit)
- Auditar listas de cuentas en Google Authenticator, Microsoft Authenticator y YubiKeys FIDO2.
- Revela activos de alta seguridad que no suelen figurar en navegadores.

### Fuente 5 — Ecosistema GitHub
- Auditar Organizaciones (`github.com/settings/organizations`), PATs activos (`github.com/settings/tokens`), y OAuth Apps autorizadas.

---

## 2. Criterios Estrictos de Transición de Estado

$$\text{INVENTORIED} \overset{\text{Demostración Físicamente Probada}}{\longrightarrow} \text{MIGRATED} \overset{\text{Auditoría de Invariantes Pass}}{\longrightarrow} \text{VALIDATED}$$

1. **`DISCOVERED`:** Activo identificado en una fuente (ej. hallado en filtro Gmail).
2. **`INVENTORIED`:** Registrado con ID, categoría y tier en `ACCESS_INVENTORY.csv`.
3. **`MIGRATED`:** Requiere credencial en Bitwarden + MFA + login físico exitoso probado.
4. **`VALIDATED`:** Demostración de lease efímero y traza auditada en `audit_trail.jsonl`.
