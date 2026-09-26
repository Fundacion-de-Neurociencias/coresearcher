"""
scripts/audit_physics_megarepo_full.py
Persistent, resumable, zero-cost batch pipeline for auditing a physics megarepo.

Usage:
    python scripts/audit_physics_megarepo_full.py --repo-path /path/to/physics_repo

All processing is 100% local (Lenovo). No data leaves the machine.
Configurable via CLI flags or environment variables (LAYA_ENDPOINT, LOCAL_IA_ENDPOINT, etc.).
Press Ctrl+C at any time to checkpoint and resume later with the same command.
"""

from __future__ import annotations
import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from python.discovery.physics_corpus_auditor import (
    PhysicsCorpusAuditor,
    CorpusItemType,
    MegarepoPeerReviewReport,
    ItemVerificationVerdict,
    UniversalPhysicsDivision,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SUPPORTED_EXTENSIONS = {
    ".tex", ".md", ".txt", ".py", ".jl", ".cpp", ".f90", ".c", ".h",
    ".csv", ".tsv", ".dat", ".h5", ".parquet", ".fits",
    ".json", ".yaml", ".yml", ".ini", ".pdf",
}

BANNER = """
╔══════════════════════════════════════════════════════════════════════╗
║       CoResearcher — Physics Megarepo Peer Review Pipeline v3.0      ║
║       100%% Local · Zero Cloud · Resumable · ADR-DISCOVERY-028        ║
╚══════════════════════════════════════════════════════════════════════╝
"""


# ---------------------------------------------------------------------------
# Checkpoint helpers
# ---------------------------------------------------------------------------

def load_checkpoint(checkpoint_file: Path) -> set:
    """Returns set of already-processed item_ids."""
    if checkpoint_file.is_file():
        try:
            with open(checkpoint_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return set(data.get("completed_ids", []))
        except Exception:
            return set()
    return set()


def save_checkpoint(checkpoint_file: Path, completed_ids: set) -> None:
    checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
    with open(checkpoint_file, "w", encoding="utf-8") as f:
        json.dump({"completed_ids": sorted(completed_ids), "updated_at": datetime.utcnow().isoformat()}, f, indent=2)


# ---------------------------------------------------------------------------
# File walker
# ---------------------------------------------------------------------------

def walk_repo(repo_path: Path, allowed_divisions: set | None = None) -> list[Path]:
    """Recursively collects all supported-extension files under repo_path."""
    files = []
    for p in sorted(repo_path.rglob("*")):
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS:
            # Skip hidden dirs / build artifacts
            parts = p.parts
            if any(part.startswith(".") or part in {"__pycache__", "node_modules", "dist", "build"} for part in parts):
                continue
            files.append(p)
    return files


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run_pipeline(args: argparse.Namespace) -> None:
    print(BANNER)

    # Inject env overrides from CLI
    if args.laya_endpoint:
        os.environ["LAYA_ENDPOINT"] = args.laya_endpoint
    if args.laya_model:
        os.environ["LAYA_MODEL"] = args.laya_model
    if args.local_ia_endpoint:
        os.environ["LOCAL_IA_ENDPOINT"] = args.local_ia_endpoint
    if args.local_ia_model:
        os.environ["LOCAL_IA_MODEL"] = args.local_ia_model

    repo_path = Path(args.repo_path).resolve()
    output_dir = Path(args.output_dir).resolve()
    checkpoint_file = Path(args.checkpoint_file).resolve()
    batch_size = args.batch_size

    if not repo_path.is_dir():
        print(f"[ERROR] Repo path does not exist: {repo_path}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    verdicts_dir = output_dir / "verdicts"
    verdicts_dir.mkdir(parents=True, exist_ok=True)

    # Parse division filter
    allowed_divisions: set | None = None
    if args.divisions:
        allowed_divisions = {d.strip().upper() for d in args.divisions.split(",")}

    print(f"[INFO] Repo: {repo_path}")
    print(f"[INFO] Output: {output_dir}")
    print(f"[INFO] Checkpoint: {checkpoint_file}")
    print(f"[INFO] Laya endpoint: {os.getenv('LAYA_ENDPOINT', 'http://localhost:11434')}")
    print(f"[INFO] Local IA endpoint: {os.getenv('LOCAL_IA_ENDPOINT', 'http://localhost:1234')}")
    print()

    # Load checkpoint
    completed_ids = load_checkpoint(checkpoint_file)
    print(f"[CHECKPOINT] {len(completed_ids)} items already processed — will skip them.")

    # Walk repo
    all_files = walk_repo(repo_path, allowed_divisions)
    total_files = len(all_files)
    print(f"[SCAN] Found {total_files} files to audit.\n")

    # Init auditor
    auditor = PhysicsCorpusAuditor()

    all_verdicts: list[ItemVerificationVerdict] = []
    all_items = []
    sound_count = 0
    rejected_count = 0
    perpetual_count = 0
    division_counts: dict[str, int] = {div.value: 0 for div in UniversalPhysicsDivision}

    processed = 0
    skipped = 0
    errors = 0

    try:
        for idx, file_path in enumerate(all_files, start=1):
            # Extract item
            item = auditor.scan_and_extract_file(file_path)
            if item is None:
                errors += 1
                continue

            # Division filter
            if allowed_divisions and item.division.value not in allowed_divisions:
                skipped += 1
                continue

            # Skip already done
            if item.item_id in completed_ids:
                skipped += 1
                continue

            # Route to appropriate audit method
            try:
                if item.item_type == CorpusItemType.MATHEMATICAL_PROOF:
                    verdict = auditor.audit_proof_item(item)
                elif item.item_type == CorpusItemType.PATENT_TECHNICAL_CLAIM or item.is_perpetual_motion_risk:
                    verdict = auditor.audit_patent_item(item, force_overunity=item.is_perpetual_motion_risk)
                    if not verdict.is_sound and any(
                        "Perpetual Motion" in v or "Overunity" in v for v in verdict.violations
                    ):
                        perpetual_count += 1
                elif item.item_type == CorpusItemType.CHAPTER_THEORY:
                    verdict = auditor.audit_chapter_deep(item)
                elif item.item_type == CorpusItemType.SIMULATION_SOLVER:
                    verdict = auditor.audit_simulation_deep(item)
                else:
                    verdict = auditor.audit_experiment_item(item)
            except Exception as exc:
                errors += 1
                print(f"  [ERROR] {file_path.name}: {exc}")
                continue

            # Tally
            if verdict.is_sound:
                sound_count += 1
            else:
                rejected_count += 1
            division_counts[item.division.value] = division_counts.get(item.division.value, 0) + 1

            all_verdicts.append(verdict)
            all_items.append(item)
            processed += 1

            # Save individual verdict JSON
            verdict_file = verdicts_dir / f"{item.item_id}.json"
            with open(verdict_file, "w", encoding="utf-8") as vf:
                json.dump(verdict.to_dict(), vf, indent=2, ensure_ascii=False)

            # Update checkpoint
            completed_ids.add(item.item_id)
            save_checkpoint(checkpoint_file, completed_ids)

            # Progress display
            if processed % batch_size == 0 or idx == total_files:
                pct = 100.0 * idx / total_files
                print(
                    f"  [{pct:5.1f}%] {idx}/{total_files} scanned | "
                    f"Audited: {processed} | Sound: {sound_count} | "
                    f"Rejected: {rejected_count} | Errors: {errors} | "
                    f"Last: {item.division.value[:20]}"
                )

    except KeyboardInterrupt:
        print("\n\n[INTERRUPT] Ctrl+C received. Saving checkpoint...")
        save_checkpoint(checkpoint_file, completed_ids)
        print(f"[CHECKPOINT SAVED] {checkpoint_file}")
        print("Resume auditing by running the same command again.")
        if not all_items:
            sys.exit(0)

    # Final report
    if not all_items:
        print("[INFO] No new items audited. All done or nothing to process.")
        return

    mean_rcs = sum(v.rcs_level for v in all_verdicts) / max(1, len(all_verdicts))

    if sound_count == len(all_verdicts):
        judgment = "EXCELLENT: All audited items pass rigorous internal coherence checks."
    elif sound_count >= len(all_verdicts) * 0.75:
        judgment = "SUBSTANTIAL MERIT WITH REQUIRED REVISIONS: Most items sound; specific issues flagged."
    else:
        judgment = "MAJOR RECONSTRUCTION REQUIRED: Substantial coherence or conservation breaches detected."

    import hashlib
    dossier_raw = json.dumps([v.to_dict() for v in all_verdicts], sort_keys=True)
    dossier_hash = f"sha256:{hashlib.sha256(dossier_raw.encode('utf-8')).hexdigest()[:24]}"

    report = MegarepoPeerReviewReport(
        repo_path=str(repo_path),
        total_items_scanned=processed,
        theories_count=sum(1 for i in all_items if i.item_type == CorpusItemType.CHAPTER_THEORY),
        proofs_count=sum(1 for i in all_items if i.item_type == CorpusItemType.MATHEMATICAL_PROOF),
        experiments_count=sum(1 for i in all_items if i.item_type in [
            CorpusItemType.EXPERIMENT_DATASET, CorpusItemType.SIMULATION_SOLVER
        ]),
        patents_count=sum(1 for i in all_items if i.item_type == CorpusItemType.PATENT_TECHNICAL_CLAIM),
        verified_sound_count=sound_count,
        falsified_or_rejected_count=rejected_count,
        perpetual_motion_interceptions_count=perpetual_count,
        division_breakdown=division_counts,
        mean_reality_contact_score=mean_rcs,
        item_verdicts=all_verdicts,
        overall_editorial_judgment=judgment,
        som_corpus_dossier_hash=dossier_hash,
    )

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    final_report_path = output_dir / f"final_report_{timestamp}.json"
    with open(final_report_path, "w", encoding="utf-8") as rf:
        json.dump(report.to_dict(), rf, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print(f"  PHYSICS CORPUS AUDIT COMPLETE")
    print(f"  Items audited:   {processed}")
    print(f"  Sound:           {sound_count}  ({100*sound_count//max(1,processed)}%%)")
    print(f"  Rejected:        {rejected_count}")
    print(f"  Perpetual motion intercepted: {perpetual_count}")
    print(f"  Mean RCS:        {mean_rcs:.2f}")
    print(f"  Judgment:        {judgment[:60]}...")
    print(f"  Report:          {final_report_path}")
    print(f"  SOM Hash:        {dossier_hash}")
    print("=" * 70)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="CoResearcher Physics Megarepo Peer Review Pipeline v3.0 (100%% local, zero cost)"
    )
    p.add_argument("--repo-path", required=True, help="Path to the physics megarepo root directory")
    p.add_argument("--output-dir", default="./audit_results", help="Directory for verdict JSONs and final report")
    p.add_argument("--checkpoint-file", default="./corpus_audit_checkpoint.json",
                   help="JSON checkpoint file tracking processed item IDs (enables resume)")
    p.add_argument("--batch-size", type=int, default=20, help="Progress display interval (items)")
    p.add_argument("--laya-endpoint", default=None, help="Laya System 1 endpoint (overrides LAYA_ENDPOINT env)")
    p.add_argument("--laya-model", default=None, help="Laya model name (overrides LAYA_MODEL env)")
    p.add_argument("--local-ia-endpoint", default=None,
                   help="Local IA System 2 endpoint (overrides LOCAL_IA_ENDPOINT env)")
    p.add_argument("--local-ia-model", default=None, help="Local IA model name (overrides LOCAL_IA_MODEL env)")
    p.add_argument("--divisions", default=None,
                   help="Comma-separated list of division names to audit (default: all). "
                        "Example: FUNDAMENTAL_HIGH_ENERGY,GRAVITATION_RELATIVITY_COSMOLOGY")
    return p


if __name__ == "__main__":
    # Try loading .env if python-dotenv is available
    try:
        from dotenv import load_dotenv
        env_file = REPO_ROOT / ".env"
        if env_file.is_file():
            load_dotenv(env_file)
    except ImportError:
        pass

    parser = build_parser()
    args = parser.parse_args()
    run_pipeline(args)
