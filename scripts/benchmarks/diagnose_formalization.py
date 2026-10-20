"""Diagnostic for the falsifiability pilot. NOT part of the pre-registered protocol.

Takes up to 20 hypotheses that the pilot excluded (fixed seed 65000), formalizes each once at the frozen decoding,
and stores the raw model output, so that failures can be told apart: format, schema, or content.
Its output is a separate file and is never read by the pilot's scoring.

    python scripts/benchmarks/diagnose_formalization.py
"""

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from python.discovery.formalizer import ChatClient, formalize  # noqa: E402

PILOT = ROOT / "docs" / "reference" / "benchmarks" / "falsifiability"
HYPOTHESES = PILOT / "hypotheses.jsonl"
MEASURES = PILOT / "measures.jsonl"
OUT = PILOT / "diagnostic_formalization.jsonl"
MODEL = "qwen2.5:14b-instruct-q4_K_M"
SEED = 65000
SAMPLE = 20
RAW_CHARS = 2000


def select(measures, hypotheses):
    """Excluded items only, sampled with a fixed seed."""
    prose = {h["question_id"]: h["prose"] for h in hypotheses}
    excluded = [m for m in measures if m["formalization"] == "EXCLUDED"]
    rng = random.Random(SEED)
    chosen = rng.sample(excluded, min(SAMPLE, len(excluded)))
    return [{"question_id": m["question_id"], "gate_reason": m["reason"], "prose": prose[m["question_id"]]} for m in chosen]


def main() -> int:
    hypotheses = [json.loads(line) for line in HYPOTHESES.read_text(encoding="utf-8").splitlines()]
    measures = [json.loads(line) for line in MEASURES.read_text(encoding="utf-8").splitlines()]
    client = ChatClient(model=MODEL)
    rows = []
    for item in select(measures, hypotheses):
        result = formalize(item["prose"], client, hypothesis_id=item["question_id"])
        rows.append({
            "question_id": item["question_id"],
            "gate_reason": item["gate_reason"],
            "status": result.status.value,
            "error": result.error,
            "raw_output": result.raw_output[:RAW_CHARS],
        })
    OUT.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    print(f"Wrote {len(rows)} diagnostic rows to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
