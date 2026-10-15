# Operational Playbook for Mass Discovery of Identities and Services (IDENTITY DISCOVERY PLAYBOOK)

**Version:** 1.0.0  
**Governance:** Empirical Discovery and Physical Census  
**Golden Rule:** *"An asset only becomes MIGRATED when there is verifiable proof of login, credential in vault, MFA and successful proof."*  

---

## 1. Physical Discovery Operational Procedure (5 Sources)

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

### Source 1 — Browsers (Chrome & Edge)
- **Action:** Export and inspect logins saved in Chrome (`chrome://password-manager/settings`) and Microsoft Edge (`edge://wallet/passwords`).
- **Objective:** Discover secondary portals, old domains and educational or travel platforms.

### Source 2 — Search Filters in Gmail
- **Search Filters:**
  ```text
  subject:(verify OR verification OR "welcome to" OR "confirm your account" OR "password reset" OR "security alert")
  ```
- **Objective:** Reveal registrations in forgotten services over the years.

### Source 3 — Password Managers
- Export census from Chrome Password Manager or Bitwarden Vault.

### Source 4 — MFA Authenticators (MFA Audit)
- Audit account lists in Google Authenticator, Microsoft Authenticator and YubiKeys FIDO2.
- Reveals high security assets that are not usually found in browsers.

### Source 5 — GitHub Ecosystem
- Audit Organizations (`github.com/settings/organizations`), active PATs (`github.com/settings/tokens`), and authorized OAuth Apps.

---

## 2. Strict State Transition Criteria

$$\text{INVENTORIED} \overset{\text{Demostración Físicamente Probada}}{\longrightarrow} \text{MIGRATED} \overset{\text{Auditoría de Invariantes Pass}}{\longrightarrow} \text{VALIDATED}$$

1. **`DISCOVERED`:** Asset identified in a source (e.g. found in Gmail filter).
2. **`INVENTORIED`:** Registered with ID, category and tier in `ACCESS_INVENTORY.csv`.
3. **`MIGRATED`:** Requires Bitwarden credential + MFA + proven successful physical login.
4. **`VALIDATED`:** Demonstration of ephemeral lease and audited trace in `audit_trail.jsonl`.