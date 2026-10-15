# MCP Servers - Tips para CoResearcher

## Qué son los MCP Servers

Extensiones locales que añaden **herramientas y recursos** a Cline.

---

## Configuración rápida

1. **Crear servidor**:
```bash
npx @modelcontextprotocol/create-server nombre
cd nombre
npm install
npm run build
```

2. **Añadir a cline_mcp_settings.json**:
```json
{
  "mcpServers": {
    "nombre": {
      "command": "node",
      "args": ["C:/ruta/nombre/build/index.js"],
      "env": {"API_KEY": "valor"}
    }
  }
}
```

3. **Las tools aparecen automáticamente** en el prompt

---

## Limitaciones clave

- ✅ Acceso a APIs, bases de datos, archivos
- ❌ No pueden hacer autenticación OAuth interactiva
- ❌ No pueden abrir navegadores
- ❌ No pueden pedir input al usuario

---

## Para CoResearcher

Los MCP servers NO son necesarios ahora. La infraestructura ya está construida con:

- Observatorio de artefactos científicos
- Scientific Activity Ledger
- Validación de DOI readiness

Enfoque actual: **Publicar ledger_base.json con DOI** antes de añadir más herramientas.