# Auditoría Física de Secretos y Plan de Remedicación de NeuroOS (PHYSICAL SECRETS AUDIT)

**Versión:** 1.0.0  
**Gobernanza:** Directiva ANTIGRAVITY-006  
**Principio Fundamental:** *"La realidad física prevalece sobre cualquier definición declarativa en YAML."*  
**Estado:** Activo - Diagnóstico Físico y Plan de Remedicación  

---

## 1. Diagnóstico de Discrepancias entre Política y Realidad Física

```text
[ Declaración Política YAML ]                    [ Realidad Física Actual en Disco ]
Certificados FNMT = BLACK                        Certificados instalados en el almacén de Windows
(Prohibido acceso a agentes)          VS         (Accesible por procesos locales en la máquina)
```

| Activo | Zona Declarada | Ubicación Física Actual | Riesgo Detectado | Plan de Remedicación (Directiva 006) |
| :--- | :---: | :--- | :--- | :--- |
| **Certificados Digitales FNMT / DNIe** | **BLACK** | Almacén de Certificados de Windows local (donde opera Antigravity). | **ALTO**: Un proceso local podría invocar la firma de certificados en Windows. | **REMEDIACIONAL**: Migrar certificados a Token Hardware físico (YubiKey / Smartcard DNIe) fuera de la máquina o restringir uso exclusivo en Lenovo offline. |
| **GitHub Tokens (Global)** | **BLACK / CONTROLLED** | Archivos de configuración local git (`.gitconfig` / credential manager). | **MEDIO**: Riesgo de que un único token tenga permisos de Owner sobre 50 repositorios. | **REMEDIACIONAL**: Segmentar tokens en Fine-Grained Personal Access Tokens por repositorio (`Medicalia_Token`, `GeneForge_Token`). |
| **Bóveda de Contraseñas** | **BLACK** | Bóveda local instalada. | **CONTROLADO**: Requiere contraseña maestra y MFA. | Mantener en Bitwarden con Master Password exclusivo de Manuel. |
| **Claves API LLM (OpenAI/Gemini)** | **CONTROLLED** | Variables de entorno del usuario en sistema local. | **MEDIO**: Repetición de variables en scripts. | **REMEDIACIONAL**: Centralizar en el `Credential Broker` de ManuEl; eliminar claves `.env` dispersas en repositorios. |

---

## 2. Las 4 Capas Físicas de Protección de Secretos

```text
[ Capa 0: Root of Trust ] ───────> Solo Manuel (Hardware YubiKey / DNIe / Bitwarden Master)
[ Capa 1: Secret Vault ] ────────> Managed por ManuEl en Lenovo (Bitwarden CLI / Infisical)
[ Capa 2: Credential Broker ] ───> Emite tokens derivados temporales (TTL 15m)
[ Capa 3: Ejecutores (Antigravity)]> Consume tokens epímeros; nunca posee llaves maestras
```

---

## 3. Matriz de Auditoría de Ubicación Física de Secretos

| Secreto / Credencial | ¿Dónde reside físicamente? | ¿Quién tiene acceso físico? | ¿Quién puede usarlo? | Plan de Recuperación en Caso de Pérdida del Equipo |
| :--- | :--- | :--- | :--- | :--- |
| **FNMT / DNIe** | Token Hardware YubiKey / DNIe físico. | Solo Manuel (físicamente en mano). | Solo Manuel. | Re-emisión presencial en oficina de acreditación de la FNMT. |
| **Bitwarden Master Key** | Memoria física de Manuel + Backup cifrado en papel ignífugo. | Solo Manuel. | Solo Manuel. | Kit de recuperación de emergencia cifrado fuera de línea. |
| **GitHub Fine-Grained Tokens** | Vault Central en Lenovo (`vault_ref`). | ManuEl Runtime. | Antigravity (vía Lease efímero < 15m). | Revocación instantánea desde el panel de GitHub por Manuel. |
| **OAuth Tokens (Email)** | Vault Central en Lenovo. | ManuEl Runtime. | Antigravity (preparación de borradores). | Revocación de la sesión de aplicación en Google Admin / Microsoft 365. |
