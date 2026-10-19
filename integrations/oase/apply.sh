#!/usr/bin/env bash
# Install the `oase formal` adapter (CoResearcher formal verifier) into an OASE checkout.
#
#   integrations/oase/apply.sh [--dry-run] [--skill-uri URI] <OASE_DIR>
#
# OASE_DIR is applications/open-agentic-science-engine inside a clone of
# GoogleCloudPlatform/LifeSciences. The edits (see apply.py) are anchored on
# the pinned commit below; another commit is accepted with a warning, and any
# anchor that moved stops the install with exit 2 instead of patching a guess.
#
# What it does:
#   - copies formal.py to tools/oase/commands/formal.py
#   - cli.py: imports `formal` and adds `cli.add_command(formal)` before enforce_phase_two(cli)
#   - core/context.py: ARTIFACT_DIRS["formal"] = "raw/formal"
#   - core/thresholds.py: declares the threshold set formal@1.0
#   - core/provenance.py: registers the formal.* relay codes
#   - commands/doctor.py: adds the formal capability check to `oase doctor`
#   - adds skills/formal-hypothesis-verification/SKILL.md
#   - grants that skill to hypex-reflection, scientific-reviewer and science-program-lead
#
# --dry-run prints the unified diff and writes nothing. Applying twice is a no-op.
# The engine itself is not copied: install CoResearcher into the OASE tools
# environment, or export CORESEARCHER_HOME=<coresearcher checkout>.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PINNED_COMMIT="b7e5e3576668ba9630f053e93389b21bbc2e67f6"
PYTHON="${PYTHON:-python3}"

args=()
oase=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) args+=("--dry-run"); shift ;;
    --skill-uri) args+=("--skill-uri" "$2"); shift 2 ;;
    -h|--help) sed -n '2,24p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    -*) echo "apply.sh: unknown option $1" >&2; exit 2 ;;
    *) oase="$1"; shift ;;
  esac
done

if [[ -z "$oase" ]]; then
  echo "usage: apply.sh [--dry-run] [--skill-uri URI] <OASE_DIR>" >&2
  exit 2
fi
if [[ ! -f "$oase/tools/oase/cli.py" ]]; then
  echo "apply.sh: $oase is not an OASE engine directory (no tools/oase/cli.py)" >&2
  exit 2
fi

head="$(git -C "$oase" rev-parse HEAD 2>/dev/null || echo unknown)"
if [[ "$head" != "$PINNED_COMMIT" ]]; then
  echo "apply.sh: warning: $oase is at $head, the adapter is pinned to $PINNED_COMMIT" >&2
fi

exec "$PYTHON" "$HERE/apply.py" --oase "$oase" "${args[@]}"
