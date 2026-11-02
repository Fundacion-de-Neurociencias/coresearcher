#!/usr/bin/env bash
# Runs one openai/math Comparator target on a Linux workstation, without the hosted runner's time limit
# (ADR-DISCOVERY-092). Same preflight and record writer as the `Lean kernel checks` workflow; the record's
# checked_by is "local:$KERNEL_CHECKED_BY".
#
#   KERNEL_CHECKED_BY="lenovo (WSL2)" bash scripts/lean/run_comparator_local.sh \
#       openai-math-eth-378-subexponential-sat ComparatorChallenges/SubexponentialSAT.json /path/to/out
#
# Needs: git, curl, go (1.24+), python3 with requirements.txt installed. Pins are read from the workflow file.
set -euo pipefail

TARGET="$1"
CONFIG="$2"
OUT="$3"
TIMEOUT="${KERNEL_TIMEOUT:-86400}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
WF="$ROOT/.github/workflows/lean-kernel.yml"

pin() { sed -n "s/^  $1: \([0-9a-f]\{40\}\).*/\1/p" "$WF"; }
export OPENAI_MATH_COMMIT="$(pin OPENAI_MATH_COMMIT)" COMPARATOR_COMMIT="$(pin COMPARATOR_COMMIT)"
export LEAN4EXPORT_COMMIT="$(pin LEAN4EXPORT_COMMIT)" LANDRUN_COMMIT="$(pin LANDRUN_COMMIT)" ELAN_COMMIT="$(pin ELAN_COMMIT)"
export WORK="${WORK:-$HOME/kernel-work}" BLOCKED_FILE="${WORK}/blocked.txt"
export GITHUB_ENV="$WORK/github_env" GITHUB_PATH="$WORK/github_path" GITHUB_OUTPUT="$WORK/github_output"
mkdir -p "$WORK" "$OUT"
: > "$GITHUB_OUTPUT"

bash "$ROOT/scripts/lean/comparator_preflight.sh" 2>&1 | tee "$WORK/preflight.log"
export PATH="$WORK/bin:$HOME/.elan/bin:$PATH"

SOURCE="{\"repository\": \"openai/math\", \"commit\": \"$OPENAI_MATH_COMMIT\", \"config\": \"lean/$CONFIG\"}"
if [ -f "$BLOCKED_FILE" ]; then
  python3 "$ROOT/scripts/lean/kernel_check.py" blocked --kind comparator --target "$TARGET" --out "$OUT" \
    --reason "$(cat "$BLOCKED_FILE")" --log "$WORK/preflight.log" --source "$SOURCE"
  exit 0
fi
GUARD=""
if grep -q "systemd_run=true" "$GITHUB_OUTPUT"; then GUARD="--systemd-run"; fi
python3 "$ROOT/scripts/lean/kernel_check.py" comparator --project "$WORK/math/lean" --config "$CONFIG" \
  --target "$TARGET" --out "$OUT" --commit "$OPENAI_MATH_COMMIT" --landrun "$LANDRUN_COMMIT" \
  --timeout "$TIMEOUT" $GUARD
