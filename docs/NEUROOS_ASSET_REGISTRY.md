# Registro Real de Activos de NeuroOS (NEUROOS ASSET REGISTRY)

**Versión:** 1.0.0  
**Directiva:** ANTIGRAVITY-002  
**Estado:** Activo - Inventario Físico de Sistema

Este documento recopila el inventario físico y real de repositorios, herramientas, runtimes y plugins disponibles en la infraestructura local (`C:\Users\usuario`).

---

## 1. Core de Orquestación y Gobernanza

| Activo | Ruta en Disco | Tipo | Descripción |
| :--- | :--- | :--- | :--- |
| **NeuroOS Kernel** | `C:\Users\usuario\NeuroOS` | Repository / Engine | Plano de control global, políticas (`.neuroos-active-policy.yaml`), manifiestos y esquemas de orquestación. |
| **SkillSpector** | `C:\Users\usuario\AppData\Local\Programs\skillspector\skillspector.exe` | CLI Security Tool | Escáner de seguridad estático y semántico para verificar skills y agentes antes de desplegarlos. |

---

## 2. Subsistemas Especializados del Ecosistema

| Subsistema | Ruta Principal | Tecnologías / Componentes Clave | Estado Ontológico |
| :--- | :--- | :--- | :--- |
| **CoResearcher** | `C:\Users\usuario\coresearcher` | Python, JSON Schema, `constitution_rules.yaml` | **FROZEN (ARQ-001→003)**: Trazabilidad inmutable (`EvidenceGraph`), Gobernanza (`DecisionGraph`), Misiones (`MissionGraph`). |
| **EditXT** | `C:\Users\usuario\Editxt` | Python, Markdown Validators | Activo: Auditoría de calidad crítica y revisión sintética (`ReviewGraph`). |
| **World Model / AI Scientists** | `C:\Users\usuario\World Model` | Python (`distinction/`, `invariants/`, `relations/`) | Activo: Inferencia estocástica, simulación biofísica y generación de hipótesis. |
| **GeneForge Ecosystem** | `C:\Users\usuario\GeneForge Ecosystem`<br>`C:\Users\usuario\GeneForgeLang Ecosystem` | Python Parser (`gf/parser.py`), AST, `gfl-plugin-blast` | Activo: Compilador de BioDSL para genómica sintética y sitios de empalme (2-space indent). |
| **Neurodiagnoses** | `C:\Users\usuario\Neurodiagnoses`<br>`C:\Users\usuario\Neurodiagnoses Ecosystem`<br>`C:\Users\usuario\Neurodiagnoses WebApp` | Python, REST APIs (EBRAINS), Web App | Activo: Apoyo al diagnóstico neuroclínico (CJD, DLB, AD) basado en criterios reales (McKeith et al.). |
| **PharmaOracle** | `C:\Users\usuario\PharmaOracle` | Python (`pharmaoracle/`, `ontrack/`) | Activo: Inferencia de binding fármaco-diana y farmacogenómica. |
| **ManuEl Runtime** | `C:\Users\usuario\ManuEl`<br>`C:\Users\usuario\ManuEl_Runtime` | Python, Daemon Process Host | Activo: Host para la ejecución continua de agentes de segundo plano (Claude Code, OpenCode, Codex). |

---

## 3. Catálogo de Skills Científicas y Herramientas MCP Integradas

Ubicación principal de plugins: `C:\Users\usuario\.gemini\config\plugins\science\skills\`

* **Genómica y Variantes:** `ensembl-database`, `gnomad-database`, `dbsnp-database`, `clinvar-database`, `alphagenome-single-variant-analysis`, `ucsc-conservation-and-tfbs`.
* **Proteínas y Estructura:** `uniprot-database`, `alphafold-database-fetch-and-analyze`, `pdb-database`, `foldseek-structural-search`, `interpro-database`, `protein-sequence-msa`.
* **Química y Fármacos:** `pubchem-database`, `chembl-database`, `openfda-database`, `opentargets-database`.
* **Expresión y Redes:** `gtex-database`, `human-protein-atlas-database`, `string-database`, `reactome-database`, `quickgo-database`.
* **Literatura y Publicaciones:** `pubmed-database`, `literature-search-europepmc`, `literature-search-arxiv`, `literature-search-biorxiv`, `literature-search-openalex`.
* **Indexación y Análisis de Código:** `codebase-grapher` (`CODEBASE_GRAPH.md`).
