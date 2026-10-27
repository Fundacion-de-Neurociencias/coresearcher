#!/usr/bin/env bash
# End-to-end demo of `oase formal` in an OASE checkout with apply.sh applied.
#
#   integrations/oase/demo/run_demo.sh <OASE_DIR> [PROJECT_DIR]
#
# Creates an OASE program (oase init), runs phase 1 and phase 2 on the
# illustrative hypotheses in inputs/, builds the example Stage 1 assessment
# record from the analysis, and copies raw/formal/ and gate/ back into
# artifacts/. Needs the OASE tools environment with CoResearcher importable
# (pip install, or CORESEARCHER_HOME).
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OASE="${1:?usage: run_demo.sh <OASE_DIR> [PROJECT_DIR]}"
PROJECT="${2:-$(mktemp -d)/formal-demo}"
export PYTHONPATH="$OASE/tools${PYTHONPATH:+:$PYTHONPATH}"
export OASE_NO_DIRTY_WARNING=1
export SCION_AGENT_SLUG="formal-demo"
oase() { python3 -m oase "$@"; }

oase init "$PROJECT" >/dev/null
export OASE_PROJECT="$PROJECT"
mkdir -p "$PROJECT/inputs"
cp "$HERE"/inputs/*.json "$PROJECT/inputs/"
cd "$PROJECT"

step() {
  echo "\$ oase $*"
  oase "$@"
  echo "exit $?"
}

# (a) pre-tournament review: the target hypothesis against its rival, with a prediction
step formal run inputs/H-0001.json --formal inputs/H-0001.formal.json \
  --rival inputs/H-0002.formal.json \
  --consequence "not (stage == 'early' and trem2_function == 'normal' and treatment == 'agonist') or dystrophy_change != 'increase'"
step formal analyze raw/formal/fm-H-0001_vs_H-0002.meta.json
# (a) the rival on its own, with the same prediction
step formal run inputs/H-0002.json --formal inputs/H-0002.formal.json   --consequence "not (stage == 'early' and trem2_function == 'normal' and treatment == 'agonist') or dystrophy_change != 'increase'"
step formal analyze raw/formal/fm-H-0002.meta.json
# (a) two evolved variants with defects
for id in H-0003 H-0004; do
  step formal run "inputs/$id.json" --formal "inputs/$id.formal.json"
  step formal analyze "raw/formal/fm-$id.meta.json"
done
# A non-verdict: prose with no formalizer model configured is BLOCKED, never a negative.
step formal run inputs/H-0001.json --out raw/formal/blocked
step formal analyze raw/formal/blocked/fm-H-0001.meta.json

# (b) Stage 1 gate: an assessment record citing the analysis
python3 "$HERE/make_assessment.py" raw/formal/fm-H-0001_vs_H-0002.analysis.json AR-001 > gate-AR-001.json
python3 "$HERE/make_assessment.py" raw/formal/fm-H-0003.analysis.json AR-002 > gate-AR-002.json
python3 "$HERE/make_assessment.py" raw/formal/blocked/fm-H-0001.analysis.json AR-003 > gate-AR-003.json

rm -rf "$HERE/artifacts"
mkdir -p "$HERE/artifacts/gate"
mkdir -p "$HERE/artifacts/raw" && cp -r raw/formal "$HERE/artifacts/raw/"
cp gate-AR-*.json "$HERE/artifacts/gate/"
echo "artifacts: $HERE/artifacts"
