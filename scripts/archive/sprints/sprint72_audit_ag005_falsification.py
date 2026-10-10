#!/usr/bin/env python3
"""
AUDIT-AG-005 — Context Bottleneck Falsification

Objective: Attempt to DESTROY the conclusion of AUDIT-AG-004.

The hypothesis under attack:
    Context fragmentation → deficient behavior

This is a FALSIFICATION audit. Nothing is improved. Nothing is built.
The goal is to demonstrate the conclusion is FALSE if possible.

Phases:
  1. Alternative Explanations — competing hypotheses without privileging E
  2. Counterfactual Replay — historical cases classified YES/NO/UNKNOWN
  3. Minimal Context Experiment — theoretical configs, information/redundancy/conflict
  4. Compression Audit — measure what information disappears during compilation
  5. Predictive Test — is there an observable prediction?

Special rule: Creating Context Engine / Context Graph / Memory Layer /
Knowledge Layer is FORBIDDEN during this audit.
"""
import json
import datetime
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_json(path: Path) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def load_jsonl(path: Path) -> list:
    items = []
    if not path.exists():
        return items
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    items.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return items


def line_count(path: Path) -> int:
    """Count lines in a file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


class AG005Falsifier:
    def __init__(self):
        self.now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # ------------------------------------------------------------------
    # FASE 1 — Alternative Explanations
    # ------------------------------------------------------------------
    def phase1_alternative_explanations(self) -> Dict[str, Any]:
        """Generate competing hypotheses without privileging E."""
        hypotheses = [
            {
                "id": "A",
                "name": "Prompt dilution",
                "description": "El prompt del agente es demasiado largo/diluido; la información crítica se pierde entre ruido",
                "status": "candidate",
                "evidence": "UNKNOWN — no se dispone del prompt efectivo del agente en el repo",
            },
            {
                "id": "B",
                "name": "Policy conflict",
                "description": "Reglas/policies en conflicto entre sí; el agente no puede obedecer todas simultáneamente",
                "status": "candidate",
                "evidence": "OBSERVED — docs/CHAIN_OF_AUTHORITY.md y docs/ARCHITECTURE_FREEZE.md imponen constraints que pueden solaparse",
            },
            {
                "id": "C",
                "name": "Tool-selection pathology",
                "description": "El agente elige herramientas incorrectas o no sabe cuándo usarlas",
                "status": "candidate",
                "evidence": "OBSERVED — scripts/ repositorio muestra 30+ scripts especializados; sin mapeo claro de cuándo usar cada uno",
            },
            {
                "id": "D",
                "name": "Termination failure",
                "description": "El agente no sabe cuándo detenerse; continúa indefinidamente o termina prematuramente",
                "status": "candidate",
                "evidence": "UNKNOWN — referido en feedback de AUDIT-AG-005 pero no documentado explícitamente en el repo",
            },
            {
                "id": "E",
                "name": "Context fragmentation",
                "description": "El comportamiento deficiente es causado por información dispersa que obliga al agente a reconciliar todo",
                "status": "candidate",
                "evidence": "OBSERVED — AUDIT-AG-004 compiló 16 secciones desde 10+ fuentes dispersas",
            },
        ]
        return {
            "objective": "Generar hypothesis competidoras. La hypothesis E no recibe privilegios.",
            "hypotheses": hypotheses,
            "note": "Todas son CANDIDATE. Ninguna es established. AUDIT-AG-005 intenta falsar E, no demostrarla.",
        }

    # ------------------------------------------------------------------
    # FASE 2 — Counterfactual Replay
    # ------------------------------------------------------------------
    def phase2_counterfactual_replay(self) -> Dict[str, Any]:
        """
        Historical cases: Would the failure have disappeared if the agent
        had received the complete Context Pack?
        Classify: YES / NO / UNKNOWN. No arguing. No speculating. Register.
        """
        # Read current_state.md size for reference
        current_state_path = PROJECT_ROOT / "artifacts" / "context_pack" / "current_state.md"
        current_state_lines = line_count(current_state_path)

        cases = [
            {
                "id": "BA-001",
                "name": "Blocked Loop",
                "description": "El agente entra en un bucle bloqueado: repite la misma acción sin progreso",
                "source": "Feedback AUDIT-AG-005 (Sprints 69-73)",
                "counterfactual": "Habría desaparecido si el agente hubiese recibido el Context Pack completo?",
                "classification": "UNKNOWN",
                "justification": "No hay evidencia en el repo que permita determinar si el Context Pack habría roto el bucle. El bucle podría ser independiente del contexto (p.ej. tool-selection pathology o termination failure).",
            },
            {
                "id": "BA-002",
                "name": "Behavior-as-Text",
                "description": "El agente lee las reglas pero no las obedece",
                "source": "Crisis Sprints 69-73, confirmada en AUDIT-AG-004 sección 5.4",
                "counterfactual": "Habría desaparecido si el agente hubiese recibido el Context Pack completo?",
                "classification": "NO",
                "justification": "El Context Pack NO añade nuevas reglas ni instrucciones. Cambia la organización de INFORMACIÓN, no el comportamiento esperado. Si el agente lee reglas pero no las obedece, recibir más información organizada no altera necesariamente el cumplimiento. El Context Pack no es un mecanismo de cumplimiento.",
            },
            {
                "id": "BA-003",
                "name": "Termination Failure",
                "description": "El agente no sabe cuándo detenerse; continúa o termina prematuramente",
                "source": "Feedback AUDIT-AG-005",
                "counterfactual": "Habría desaparecido si el agente hubiese recibido el Context Pack completo?",
                "classification": "UNKNOWN",
                "justification": "No hay evidencia en el repo. El Context Pack podría incluir objetivos/estado que ayuden a decidir cuándo terminar, pero también podría no cambiar nada si el fallo es de ejecución (no de información).",
            },
        ]
        return {
            "objective": "Tomar casos históricos y preguntar: habría desaparecido el fallo con Context Pack completo?",
            "classification_legend": {"YES": "El fallo habría desaparecido", "NO": "El fallo NO habría desaparecido", "UNKNOWN": "No determinable"},
            "context_pack_reference": f"artifacts/context_pack/current_state.md ({current_state_lines} líneas)",
            "cases": cases,
            "summary": {
                "YES": sum(1 for c in cases if c["classification"] == "YES"),
                "NO": sum(1 for c in cases if c["classification"] == "NO"),
                "UNKNOWN": sum(1 for c in cases if c["classification"] == "UNKNOWN"),
            },
            "note": "Resultado crítico: caso BA-002 (Behavior-as-Text) clasificado como NO. El Context Pack cambia información, no cumplimiento. Si BA-002 es representativo, la hypothesis E pierde fuerza explicativa.",
        }

    # ------------------------------------------------------------------
    # FASE 3 — Minimal Context Experiment
    # ------------------------------------------------------------------
    def phase3_minimal_context(self) -> Dict[str, Any]:
        """Three theoretical configurations. Calculate information/redundancy/conflict."""
        # Count sources that feed current_state.md
        current_state_path = PROJECT_ROOT / "artifacts" / "context_pack" / "current_state.md"
        current_state_lines = line_count(current_state_path)

        # Estimate source sizes (number of JSON records/entries)
        claims_data = load_json(PROJECT_ROOT / "knowledge" / "registry" / "claims.json") or {}
        findings_data = load_json(PROJECT_ROOT / "knowledge" / "registry" / "findings.json") or {}
        questions_data = load_json(PROJECT_ROOT / "knowledge" / "registry" / "questions.json") or {}
        models_data = load_json(PROJECT_ROOT / "knowledge" / "registry" / "combined_models.json") or {}
        contracts = list((PROJECT_ROOT / "knowledge" / "contracts").glob("*.json")) if (PROJECT_ROOT / "knowledge" / "contracts").exists() else []
        cap_data = load_json(PROJECT_ROOT / "ecosystem" / "registry" / "capabilities.json") or {}
        conn_data = load_json(PROJECT_ROOT / "ecosystem" / "registry" / "connectors.json") or {}
        memory_data = load_json(PROJECT_ROOT / "memory" / "neurodegeneration_memory.json") or {}
        traj = load_json(PROJECT_ROOT / "data" / "trajectories" / "langchain_ai_langgraph" / "trajectory_graph.json") or {}
        survival = load_json(PROJECT_ROOT / "artifacts" / "sprint70_survival_table.json") or {}
        compress = load_json(PROJECT_ROOT / "artifacts" / "compression_ledger.json") or {}

        source_entries = {
            "claims.json": len(claims_data.get("claims", {})),
            "findings.json": len(findings_data.get("findings", {})),
            "questions.json": len(questions_data.get("questions", {})),
            "combined_models.json": len(models_data.get("models", {})),
            "contracts/": len(contracts),
            "capabilities.json": len(cap_data.get("registrations", {})),
            "connectors.json": len(conn_data.get("registrations", {})),
            "neurodegeneration_memory.json": len(memory_data.get("hypotheses", [])) + len(memory_data.get("experiments", [])) + len(memory_data.get("lessons", [])),
            "trajectory_graph.json": len(traj.get("nodes", [])) + len(traj.get("edges", [])),
            "sprint70_survival_table.json": len(survival.get("table", [])),
            "compression_ledger.json": len(compress.get("ledger", [])),
        }
        total_source_entries = sum(source_entries.values())

        configs = [
            {
                "id": "A",
                "name": "Minimal state",
                "description": "Solo objetivo activo (H6) + estado del repo + instrucciones base",
                "information_added": "Mínima: objetivo único, estado del repositorio",
                "redundancy": "Baja — pocas fuentes solapadas",
                "conflicts": "Bajos — poca información que pueda contradecirse",
                "risk": "El agente no sabe qué datos existen ni dónde encontrarlos",
                "estimated_lines": 30,
            },
            {
                "id": "B",
                "name": "current_state.md (Context Pack completo)",
                "description": f"El Context Pack compilado ({current_state_lines} líneas) con 16 secciones del estado operativo",
                "information_added": f"Alta: {total_source_entries} entradas de {len(source_entries)} fuentes compiladas en un solo documento",
                "redundancy": "Media: las mismas entidades aparecen en registros y en resúmenes",
                "conflicts": "Potenciales: secciones pueden solaparse (survival table vs convergence review) sin jerarquía clara",
                "risk": "El Context Pack introduce COMPLEJIDAD ESTRUCTURAL: 16 secciones que el agente debe procesar — posiblemente equivalente a la fragmentación que intenta resolver",
                "estimated_lines": current_state_lines,
            },
            {
                "id": "C",
                "name": "current_state.md + ETS",
                "description": "Context Pack + sistema de reglas/policies existente",
                "information_added": "Máxima: contexto operativo + reglas de comportamiento",
                "redundancy": "Alta: ETS puede repetir o contradecir secciones del Context Pack (p.ej. límites de rol)",
                "conflicts": "Altos: el Context Pack describe estado (datos); ETS prescribe comportamiento (reglas). Si entran en conflicto, cuál gana?",
                "risk": "La adición de ETS re-introduce 'Behavior as Text' — el mismo mecanismo que la hypothesis E dice que no funciona",
                "estimated_lines": current_state_lines + 200,  # ETS estimado
            },
        ]

        return {
            "objective": "Construir tres configuraciones teóricas SIN implementarlas. Calcular información añadida, redundancia, conflictos potenciales.",
            "configs": configs,
            "critical_observation": "La configuración B (Context Pack) añade 16 secciones de información estructurada que el agente debe procesar. Esto ES complejidad nueva, no eliminación de complejidad. El Context Pack reorganiza la información pero no reduce la carga cognitiva total: la mueve de 'buscar fuentes' a 'interpretar secciones'.",
            "classification": "Esta observación es DERIVED (lógica, no medida empíricamente) — el coste de procesar el Context Pack no se ha medido contra el coste de buscar fuentes dispersas.",
        }

    # ------------------------------------------------------------------
    # FASE 4 — Compression Audit
    # ------------------------------------------------------------------
    def phase4_compression_audit(self) -> Dict[str, Any]:
        """
        Measure: original sources → current_state.md
        Calculate: compression_ratio, loss_ratio
        Question: What information disappears during compilation?
        """
        current_state_path = PROJECT_ROOT / "artifacts" / "context_pack" / "current_state.md"
        current_state_lines = line_count(current_state_path)

        # Source files that feed the compiler
        source_files = [
            PROJECT_ROOT / "knowledge" / "registry" / "claims.json",
            PROJECT_ROOT / "knowledge" / "registry" / "findings.json",
            PROJECT_ROOT / "knowledge" / "registry" / "questions.json",
            PROJECT_ROOT / "knowledge" / "registry" / "combined_models.json",
            PROJECT_ROOT / "ecosystem" / "registry" / "capabilities.json",
            PROJECT_ROOT / "ecosystem" / "registry" / "connectors.json",
            PROJECT_ROOT / "memory" / "neurodegeneration_memory.json",
            PROJECT_ROOT / "data" / "trajectories" / "langchain_ai_langgraph" / "trajectory_graph.json",
            PROJECT_ROOT / "data" / "trajectories" / "langchain_ai_langgraph" / "evaluation_metrics.json",
            PROJECT_ROOT / "artifacts" / "cross_repo_metrics.json",
            PROJECT_ROOT / "artifacts" / "sprint70_survival_table.json",
            PROJECT_ROOT / "artifacts" / "convergence_review.json",
            PROJECT_ROOT / "artifacts" / "compression_ledger.json",
        ]

        source_details = []
        total_source_lines = 0
        total_source_bytes = 0
        for src in source_files:
            lines = line_count(src)
            try:
                size = src.stat().st_size
            except Exception:
                size = 0
            total_source_lines += lines
            total_source_bytes += size
            source_details.append({
                "file": src.name,
                "lines": lines,
                "bytes": size,
            })

        # current_state.json comparison
        current_state_json_path = PROJECT_ROOT / "artifacts" / "context_pack" / "current_state.json"
        try:
            current_state_json_size = current_state_json_path.stat().st_size
        except Exception:
            current_state_json_size = 0

        # Compression ratio: output_input
        # A ratio < 1 means compression; > 1 means expansion
        compression_ratio_md = current_state_lines / total_source_lines if total_source_lines > 0 else 0
        compression_ratio_bytes = ((current_state_path.stat().st_size if current_state_path.exists() else 0)
                                   + current_state_json_size) / total_source_bytes if total_source_bytes > 0 else 0

        # Loss estimation: what fields/entities are NOT represented in current_state.md
        # Enumeration of what the compiler KEEPS vs what it DROPS
        kept = [
            "counts (claims, findings, questions, models)",
            "quality distribution (findings)",
            "status distribution (claims)",
            "consumer contract identifiers",
            "capability/connector counts",
            "session file names",
            "trajectory node/edge counts",
            "cross-repo metric table",
            "survival summary table",
            "convergence summary",
            "compression ledger table",
            "git commit hashes+messages",
            "recent artifact names+sizes",
        ]
        dropped = [
            "claim texts completos (solo conteos)",
            "finding descriptions completas (solo score buckets)",
            "preguntas individuales con detalles (solo conteo y estado)",
            "modelos individuales con componentes/effects (solo conteo)",
            "detalle de cada consumer contract (solo id+dominio)",
            "decisiones individuales de trajectory (solo conteos)",
            "rationale/evidence de cada decision",
            "contenido de cada issue de GitHub (0 issues, no aplica)",
            "provenance completa de cada claim (source URLs, timestamps)",
            "detalle de hypotheses/experiments en memoria",
            "contenido de 20+ artefactos markdown no estructurados",
        ]

        loss_estimation = {
            "kept_summary": kept,
            "dropped_summary": dropped,
            "estimated_loss_type": "Agregación: el Context Pack conserva CONTEOS y RESUMENES, pierde DETALLES INDIVIDUALES",
            "risk": "Si el agente necesita el detalle individual (p.ej. el evidence_anchor específico de un claim), el Context Pack NO lo tiene. Debe buscar en la fuente original.",
        }

        verdict = (
            f"Compression ratio (MD líneas): {compression_ratio_md:.4f} "
            f"({total_source_lines} → {current_state_lines} líneas). "
            f"Compression ratio (bytes): {compression_ratio_bytes:.4f}. "
            f"El Context Pack comprime ~{max(1, int(total_source_lines / max(1, current_state_lines)))}x en líneas. "
            f"PERO: la compresión es AGREGATIVA — los detalles individuales se pierden. "
            f"Compression ≠ estado operativo completo. El Context Pack es un ÍNDICE del estado, no el estado mismo."
        )

        return {
            "objective": "Medir qué información desaparece durante la compilación.",
            "source_files": source_details,
            "total_source_lines": total_source_lines,
            "total_source_bytes": total_source_bytes,
            "current_state_md_lines": current_state_lines,
            "current_state_json_size_bytes": current_state_json_size,
            "compression_ratio_md_lines": round(compression_ratio_md, 4),
            "compression_ratio_bytes": round(compression_ratio_bytes, 4),
            "loss_estimation": loss_estimation,
            "verdict": verdict,
            "classification": "OBSERVED — medido directamente contra archivos existentes",
            "critical_question": "Context Pack = Estado operativo? NO. Context Pack = índice agregado. La información individual vive en las fuentes. Si el agente necesita detalles, tendrá que buscar igualmente.",
        }

    # ------------------------------------------------------------------
    # FASE 5 — Predictive Test
    # ------------------------------------------------------------------
    def phase5_predictive_test(self) -> Dict[str, Any]:
        """
        The most important question. Identify an observable prediction.
        Without an observable prediction, the hypothesis remains UNDETERMINED.
        """
        predictions = [
            {
                "id": "P1",
                "prediction": "Dos agentes idénticos, con distinto contexto (Context A vs Context B), deberían divergir sistemáticamente en comportamiento (p.ej. número de tool calls, tiempo hasta primera acción útil, nº de búsquedas de archivos)",
                "observable": True,
                "measurable": "Sí: registrar tool calls, número de archivos leídos, tiempo hasta primera acción útil para cada agente en la misma tarea",
                "requires_implementation": True,
                "implemented": False,
                "status": "NOT_TESTED — no hay dos agentes instrumentados con contextos distintos",
            },
            {
                "id": "P2",
                "prediction": "Si Context fragmentation es la causa, un agente con Context Pack debería leer MENOS archivos (ya que no necesita buscarlos) — reducción medible en file reads por tarea",
                "observable": True,
                "measurable": "Sí: contar file reads por tarea con y sin Context Pack",
                "requires_implementation": True,
                "implemented": False,
                "status": "NOT_TESTED — no implementado",
            },
            {
                "id": "P3",
                "prediction": "Si la hypothesis es falsa (los fallos son de otro tipo), un agente con Context Pack mostraría el MISMO patrón de fallos (blocked loop, termination) — comportamiento idéntico en distintos contextos",
                "observable": True,
                "measurable": "Sí: comparar tasas de fallo entre configuraciones",
                "requires_implementation": True,
                "implemented": False,
                "status": "NOT_TESTED — no implementado",
            },
        ]

        overall_status = (
            "UNDETERMINED — existen predicciones observables definidas (P1, P2, P3) "
            "pero NINGUNA ha sido instrumentada ni medida. "
            "Sin ejecución, la hypothesis 'Context fragmentation → comportamiento deficiente' "
            "permanece UNDETERMINED, no establecida."
        )

        return {
            "objective": "Identificar una predicción observable. Sin predicción observable, la hypothesis permanece UNDETERMINED.",
            "predictions": predictions,
            "overall_status": overall_status,
            "classification": "OBSERVED (las predicciones están definidas) / UNKNOWN (no se ha ejecutado ninguna)",
        }

    # ------------------------------------------------------------------
    # Verdict
    # ------------------------------------------------------------------
    def compute_verdict(self, phase1: Dict, phase2: Dict, phase3: Dict, phase4: Dict, phase5: Dict) -> Dict[str, Any]:
        """Compute GREEN / YELLOW / RED verdict."""

        # Phase 2 signals
        phase2_summary = phase2["summary"]
        no_count = phase2_summary["NO"]
        unknown_count = phase2_summary["UNKNOWN"]

        # Phase 4 signal
        phase4_verdict = phase4["verdict"]

        # Phase 5 signal
        phase5_status = phase5["overall_status"]

        # Critical observations
        critical_points = [
            "FASE 2: El caso Behavior-as-Text (BA-002) se clasifica como NO habría desaparecido con Context Pack. El Context Pack cambia información, no cumplimiento. Esto DEBILITA la hypothesis E.",
            "FASE 3: El Context Pack añade 16 secciones de información que el agente debe procesar — complejidad estructural nueva, no eliminación.",
            "FASE 4: La compresión es AGREGATIVA. El Context Pack es un ÍNDICE del estado, no el estado completo. Los detalles individuales se pierden.",
            "FASE 5: Sin instrumentación, la hypothesis permanece UNDETERMINED.",
        ]

        # Scoring
        # The hypothesis E is weakened by:
        # - Phase 2: at least 1 historical case classified as NO
        # - Phase 4: compression loses individual details (Context Pack ≠ full state)
        # - Phase 5: no predictive test executed
        evidence_against = 3
        evidence_for = 1  # Phase 1 shows context fragmentation is OBSERVED as a condition

        if evidence_against >= 2 and no_count >= 1:
            verdict = "YELLOW"
            verdict_rationale = (
                "La hypothesis E (Context fragmentation) NO colapsa (RED) porque la fragmentación "
                "es OBSERVED como condición real del proyecto. "
                "PERO NO sobrevive como explicación suficiente (GREEN) porque: "
                "(1) el caso Behavior-as-Text sugiere que el fallo persiste independientemente del contexto, "
                "(2) la compresión del Context Pack pierde detalles individuales, "
                "(3) ningún test predictivo ha sido ejecutado. "
                "Evidencia insuficiente para establecer la hypothesis como causa principal."
            )
        elif evidence_against >= 3:
            verdict = "RED"
            verdict_rationale = "La hypothesis colapsa porque la evidencia en contra supera cualquier soporte."
        else:
            verdict = "GREEN"
            verdict_rationale = "La hypothesis sobrevive a la falsación."

        return {
            "verdict": verdict,
            "rationale": verdict_rationale,
            "critical_points": critical_points,
            "evidence_against_count": evidence_against,
            "evidence_for_count": evidence_for,
            "note": "Un resultado YELLOW no significa 'parece razonable'. Significa que NO hay evidencia suficiente para declarar la hypothesis como causa principal, y tampoco la hay para descartarla.",
        }


def main():
    print("=" * 60)
    print("AUDIT-AG-005 — Context Bottleneck Falsification")
    print("=" * 60)

    falsifier = AG005Falsifier()

    phase1 = falsifier.phase1_alternative_explanations()
    phase2 = falsifier.phase2_counterfactual_replay()
    phase3 = falsifier.phase3_minimal_context()
    phase4 = falsifier.phase4_compression_audit()
    phase5 = falsifier.phase5_predictive_test()
    verdict = falsifier.compute_verdict(phase1, phase2, phase3, phase4, phase5)

    result = {
        "audit_id": "AUDIT-AG-005",
        "generated_at": falsifier.now,
        "objective": "Intentar destruir la conclusión de AUDIT-AG-004. No mejorar. No construir.",
        "hypothesis_under_attack": "Context fragmentation → comportamiento deficiente",
        "special_rule_compliance": "OK — no se creó Context Engine, Context Graph, Memory Layer ni Knowledge Layer",
        "phases": {
            "FASE_1_alternative_explanations": phase1,
            "FASE_2_counterfactual_replay": phase2,
            "FASE_3_minimal_context_experiment": phase3,
            "FASE_4_compression_audit": phase4,
            "FASE_5_predictive_test": phase5,
        },
        "verdict": verdict,
    }

    output_path = PROJECT_ROOT / "artifacts" / "context_pack" / "audit_ag005_falsification.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    # Console summary
    print(f"\nFASE 1: {len(phase1['hypotheses'])} hypothesis competidoras (A-E, sin privilegios)")
    print(f"FASE 2: Counterfactual replay — {phase2['summary']}")
    print(f"  → BA-002 (Behavior-as-Text): {[c['classification'] for c in phase2['cases'] if c['id'] == 'BA-002'][0]}")
    print(f"FASE 3: 3 configuraciones teóricas analizadas (A/B/C)")
    print(f"FASE 4: Compression ratio (MD líneas): {phase4['compression_ratio_md_lines']} — Verdict: {phase4['verdict'][:80]}...")
    print(f"FASE 5: {phase5['overall_status'][:100]}")
    print(f"\nVEREDICTO FINAL: {verdict['verdict']}")
    print(f"  Racional: {verdict['rationale'][:200]}...")
    print(f"\nOutput: {output_path}")


if __name__ == "__main__":
    main()