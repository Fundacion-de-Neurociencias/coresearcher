"""Question bank for the hypothesis inspiration protocol (section 5.1). Deterministic and offline.

    python scripts/benchmarks/build_question_bank.py            # writes question_bank.json and prints its hash

The bank draws 50 questions per life-science domain from the frozen vocabulary, with seed 61000. The vocabulary and
this procedure are fixed before any run: a change to either changes the bank hash, which the protocol records.
"""

import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
BENCH = ROOT / "docs" / "reference" / "benchmarks"
VOCABULARY = BENCH / "inspiration" / "question_vocabulary.json"
PROTOCOL = BENCH / "HYPOTHESIS_INSPIRATION_PROTOCOL.md"
BANK = BENCH / "inspiration" / "question_bank.json"
SEED = 61000
PER_DOMAIN = 50


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(vocabulary: dict) -> list:
    """All questions of all domains, in a fixed order. Each domain is sampled with its own seeded generator, so adding
    a domain later does not change the questions of the existing ones."""
    questions = []
    for domain_index, (domain, parts) in enumerate(vocabulary["domains"].items()):
        combos = [(e, o, p) for e in parts["exposure"] for o in parts["outcome"] for p in parts["population"]]
        rng = random.Random(SEED + domain_index)
        chosen = sorted(rng.sample(combos, PER_DOMAIN))
        for k, (exposure, outcome, population) in enumerate(chosen, start=1):
            questions.append(
                {
                    "id": f"Q-{domain}-{k:03d}",
                    "domain": domain,
                    "text": vocabulary["template"].format(exposure=exposure, outcome=outcome, population=population),
                    "exposure": exposure,
                    "outcome": outcome,
                    "population": population,
                }
            )
    return questions


def main(argv=None) -> int:
    vocabulary = json.loads(VOCABULARY.read_text(encoding="utf-8"))
    questions = build(vocabulary)
    texts = [q["text"] for q in questions]
    if len(set(texts)) != len(texts):
        raise SystemExit("Duplicate questions in the bank; the vocabulary must be revised.")
    bank = {
        "seed": SEED,
        "per_domain": PER_DOMAIN,
        "vocabulary_sha256": _sha256(VOCABULARY),
        "protocol_sha256": _sha256(PROTOCOL),
        "questions": questions,
    }
    BANK.write_text(json.dumps(bank, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    bank_hash = hashlib.sha256(json.dumps(questions, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    print(f"Wrote {BANK.relative_to(ROOT)}: {len(questions)} questions, content hash {bank_hash}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
