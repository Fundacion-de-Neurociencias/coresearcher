#!/usr/bin/env bash
# CI job `oase-conformance`: OASE at the pinned commit, with and without the adapter.
#
#   integrations/oase/ci/conformance.sh [WORKDIR]
#
# 1. Clone GoogleCloudPlatform/LifeSciences (sparse: the OASE engine only) at the pinned commit.
# 2. Install OASE's locked tool requirements and CoResearcher's runtime requirements.
# 3. Run OASE's checkers on the pristine tree (baseline), apply the adapter, run them again,
#    and fail on any problem the adapter introduces (compare_checks.py).
# 4. Run OASE's own conformance tests on the patched tree, and OASE's tools/tests suite on both trees
#    (no failure may appear that the pristine tree does not have); then the adapter's tests.
# 5. Check that apply.sh is idempotent and that --dry-run writes nothing.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
ADAPTER="$REPO/integrations/oase"
PIN="b7e5e3576668ba9630f053e93389b21bbc2e67f6"
ENGINE="applications/open-agentic-science-engine"
WORK="${1:-${RUNNER_TEMP:-/tmp}/oase-conformance}"

rm -rf "$WORK" && mkdir -p "$WORK"
git clone --quiet --filter=blob:none --no-checkout https://github.com/GoogleCloudPlatform/LifeSciences.git "$WORK/pristine"
git -C "$WORK/pristine" sparse-checkout set "$ENGINE"
git -C "$WORK/pristine" checkout --quiet "$PIN"
test "$(git -C "$WORK/pristine" rev-parse HEAD)" = "$PIN"
cp -a "$WORK/pristine" "$WORK/patched"
PRISTINE="$WORK/pristine/$ENGINE"
PATCHED="$WORK/patched/$ENGINE"

python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r "$PRISTINE/tools/requirements.txt"
python -m pip install --quiet -r "$REPO/requirements.txt" pytest jsonschema

export OASE_NO_DIRTY_WARNING=1 CORESEARCHER_HOME="$REPO" PYTHONWARNINGS=ignore

checks() {  # $1 = engine dir, $2 = label
  local rc
  for checker in relay:check_relay_codes threshold:check_threshold_names; do
    local kind="${checker%%:*}" script="${checker#*:}"
    set +e
    (cd "$1" && PYTHONPATH="$1/tools" python "tools/$script.py") >"$WORK/$kind.$2.out" 2>&1
    rc=$?
    set -e
    echo "$rc" >"$WORK/$kind.$2.rc"
  done
}

echo "::group::OASE checkers on the pristine tree (baseline)"
checks "$PRISTINE" pristine
cat "$WORK"/relay.pristine.out "$WORK"/threshold.pristine.out | grep -E "problem|check [123]|placed" || true
echo "::endgroup::"

echo "::group::Dry run prints the diff and writes nothing"
bash "$ADAPTER/apply.sh" --dry-run "$PATCHED" >"$WORK/apply.diff"
grep -q '^+cli.add_command(formal)' "$WORK/apply.diff"
test -z "$(git -C "$WORK/patched" status --porcelain)"
echo "::endgroup::"

echo "::group::Apply (twice: the second run must change nothing)"
bash "$ADAPTER/apply.sh" "$PATCHED"
bash "$ADAPTER/apply.sh" "$PATCHED" | grep -q "already applied"
git -C "$WORK/patched" status --short
echo "::endgroup::"

echo "::group::OASE checkers on the patched tree"
checks "$PATCHED" patched
status=0
for kind in relay threshold; do
  python "$ADAPTER/ci/compare_checks.py" "$kind" \
    "$WORK/$kind.pristine.out" "$(cat "$WORK/$kind.pristine.rc")" \
    "$WORK/$kind.patched.out" "$(cat "$WORK/$kind.patched.rc")" || status=1
done
grep -HE "registered relay codes|check [123]: [0-9]" "$WORK"/relay.*.out || true
echo "::endgroup::"
[ "$status" -eq 0 ]

echo "::group::OASE conformance tests on the patched tree"
(cd "$PATCHED" && PYTHONPATH="$PATCHED/tools" python -m pytest -q -p no:cacheprovider \
  tests/test_artifact_dirs_completeness.py \
  tools/tests/test_cli_option_conformance.py \
  tests/test_comparable_field_coverage.py \
  tests/test_skill_frontmatter.py \
  tests/test_tools_list.py \
  tests/test_policy.py \
  tools/tests/test_artifact_dirs.py \
  tools/tests/test_doctor_project.py)
echo "::endgroup::"

echo "::group::OASE tools/tests: the adapter adds no failure to the pristine baseline"
for tree in pristine patched; do
  dir="$WORK/$tree/$ENGINE"
  (cd "$dir" && PYTHONPATH="$dir/tools" python -m pytest -q -p no:cacheprovider tools/tests -rfE 2>&1 || true) \
    | tee "$WORK/tools-tests.$tree.out" | tail -1
  grep -E "^(FAILED|ERROR) " "$WORK/tools-tests.$tree.out" | sed 's/ - .*//' | sort -u >"$WORK/tools-tests.$tree.failed" || true
done
grep -Eq "[0-9]+ passed" "$WORK/tools-tests.patched.out"
new_failures="$(comm -13 "$WORK/tools-tests.pristine.failed" "$WORK/tools-tests.patched.failed")"
if [ -n "$new_failures" ]; then
  echo "failures introduced by the adapter:" >&2
  echo "$new_failures" >&2
  exit 1
fi
echo "baseline failures (upstream, unchanged): $(wc -l <"$WORK/tools-tests.pristine.failed")"
echo "::endgroup::"

echo "::group::Adapter integration tests"
(cd "$WORK" && PYTHONPATH="$PATCHED/tools" python -m pytest -q -p no:cacheprovider -o addopts="" \
  "$ADAPTER/tests")
echo "::endgroup::"
