# VAULT MIGRATION PLAN

**Version:** 1.0.0  
**Governance:** Discovery Plan and Physical Inventory of Accesses  
**Allowed States:** `NOT_DISCOVERED` | `DISCOVERED` | `INVENTORIED` | `MIGRATED` | `VALIDATED`  

---

## 1. Phases of the Migration Plan to Bitwarden / Vault Central

```text
[ NOT_DISCOVERED ] ──> [ DISCOVERED ] ──> [ INVENTORIED ] ──> [ MIGRATED ] ──> [ VALIDATED ]
```

1. **Phase 1: Discovery and Census in Browsers and Managers:**  
   Export the map of logins saved in Chrome/Edge/Devices to the unified inventory.
2. **Phase 2: Creation of Collections in Bitwarden:**  
   - `Development` (Phase A)
   - `University` (Phase B)
   - `Foundation` (Phase B)
   - `ISPA` (Phase B)
   - `Travel` (Phase B)
   - `Finance` (Exclusive Manuel - No delegation)
3. **Phase 3: Physically Validated Migration (MIGRATED):**  
   Transfer keys, configure MFA in the vault, and enter referral URIs (`vault_ref`).
4. **Phase 4: Real Execution Test (VALIDATED):**  
   Demonstration of login and issuance of ephemeral lease with registered audit.

---

## 2. Operational Capabilities Matrix (`discover`, `read`, `act`)

| Identity / Service | Permission `discover` | Permission `read` | Permission `act` | Current Status |
| :--- | :---: | :---: | :---: | :---: |
| **GitHub Operations** | **true** | **true** | **true** | **MIGRATED** |
| **Vercel Deployments** | **true** | **true** | **true** | **MIGRATED** |
| **Medalia Repo** | **true** | **true** | **true** | **INVENTORIED** |
| **University of Oviedo** | **true** | **true** | **false** | **INVENTORIED** |
| **Neuroscience Foundation** | **true** | **true** | **false** | **INVENTORIED** |
| **HUCA Neurology Ops** | **true** | **false** | **false** | **INVENTORIED** |
| **Sovereign Personal Gmail** | **false** | **false** | **false** | **INVENTORIED** |