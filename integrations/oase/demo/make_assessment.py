"""Build an OASE evidence-assessment record (AR) that cites an `oase formal analyze` record.

    python3 make_assessment.py raw/formal/fm-H-0001_vs_H-0002.analysis.json AR-001 > AR-001.json

Nothing is decided here: `execution_outcome`, `evidence_status` and `evidence` are
copied from `assessment.evidence_assessment` of the analysis, which is where the
tool mapped its own verdict (a non-verdict maps to blocked / not_assessed). The
concept reference is the demo's illustrative concept IC-001.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def build(analysis_path: Path, ar_id: str, concept_ref: str = "IC-001") -> dict:
    record = json.loads(analysis_path.read_text(encoding="utf-8"))
    assessment = record["assessment"]
    mapping = assessment["evidence_assessment"]
    hid = assessment["hypothesis_id"]
    return {
        "schema": "oase.evidence-assessment.v1",
        "id": ar_id,
        "concept_ref": concept_ref,
        "claim": f"{hid} is formally sound: not vacuous, not self-contradictory, falsifiable",
        "evidence_status": mapping["evidence_status"],
        "execution_outcome": mapping["execution_outcome"],
        "evidence": {
            **mapping["evidence"],
            "analysis_path": analysis_path.as_posix(),
        },
        "mandatory_relays": [r["code"] for r in record.get("mandatory_relays", [])],
        "assessed_at": record["timestamp"],
        "assessed_by": record["written_by"],
        "rationale": (
            f"oase formal analyze: formal_status={assessment['formal_status']}, "
            f"criteria.max_formal_defects.met={assessment['criteria']['max_formal_defects']['met']}, "
            f"reproduces_run={assessment['reproduction']['reproduces_run']}; "
            f"threshold_set {record['threshold_set']}."
        ),
    }


if __name__ == "__main__":
    print(json.dumps(build(Path(sys.argv[1]), sys.argv[2]), indent=2))
