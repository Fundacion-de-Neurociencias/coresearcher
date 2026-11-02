#!/usr/bin/env bash
# Prepares an openai/math Comparator check on a Linux runner (ADR-DISCOVERY-091).
#
# Installs landrun, checks that Landlock really confines it, installs elan, checks out openai/math at the pinned
# commit, builds lean4export and comparator, and fetches the Mathlib cache. On the first failing step it writes
# the reason to $BLOCKED_FILE and stops: the check is then recorded as BLOCKED, never as a pass.
#
# Environment: OPENAI_MATH_COMMIT, COMPARATOR_COMMIT, LEAN4EXPORT_COMMIT, LANDRUN_COMMIT, ELAN_COMMIT,
#              WORK (a scratch directory), BLOCKED_FILE, GITHUB_ENV, GITHUB_PATH, GITHUB_OUTPUT.
set -uo pipefail

mkdir -p "$WORK"
rm -f "$BLOCKED_FILE"

blocked() {
  echo "$1" > "$BLOCKED_FILE"
  echo "BLOCKED: $1"
  exit 0
}

step() {
  echo "::group::$1"
  echo "+ $1"
}

end_step() { echo "::endgroup::"; }

step "kernel and Landlock"
uname -a
LSM=$(sudo cat /sys/kernel/security/lsm 2>/dev/null || true)
echo "LSM: $LSM"
end_step
case ",$LSM," in
  *,landlock,*) ;;
  *) blocked "Landlock is not enabled in this runner's kernel (LSM list: '${LSM:-unreadable}'), so landrun cannot sandbox Comparator" ;;
esac

step "landrun at $LANDRUN_COMMIT"
GOBIN="$WORK/bin" go install "github.com/zouuup/landrun/cmd/landrun@$LANDRUN_COMMIT" || {
  end_step
  blocked "go install of landrun at $LANDRUN_COMMIT failed"
}
export PATH="$WORK/bin:$PATH"
echo "$WORK/bin" >> "$GITHUB_PATH"
end_step

step "landrun confines a process (the flags Comparator passes)"
PROBE="$WORK/landrun-probe"
mkdir -p "$PROBE"
landrun --best-effort --ro / --rw /dev -ldd -add-exec -- /usr/bin/true || {
  end_step
  blocked "landrun could not start a sandboxed process with Comparator's flags on this runner"
}
if landrun --best-effort --ro / --rw /dev -ldd -add-exec -- /usr/bin/touch "$PROBE/escape" 2>/dev/null; then
  end_step
  blocked "landrun ran but did not confine writes (a write under a read-only rule succeeded), so Comparator's sandbox would not hold"
fi
echo "landrun refused a write outside its rules, as it should"
end_step

step "elan at $ELAN_COMMIT"
curl -sSfL "https://raw.githubusercontent.com/leanprover/elan/$ELAN_COMMIT/elan-init.sh" -o "$WORK/elan-init.sh" \
  && sh "$WORK/elan-init.sh" -y --default-toolchain none || {
  end_step
  blocked "elan could not be installed"
}
export PATH="$HOME/.elan/bin:$PATH"
echo "$HOME/.elan/bin" >> "$GITHUB_PATH"
end_step

clone() {  # clone <url> <commit> <dir>
  git init -q "$3" && git -C "$3" fetch -q --depth 1 "$1" "$2" && git -C "$3" checkout -q FETCH_HEAD
}

step "openai/math at $OPENAI_MATH_COMMIT"
clone https://github.com/openai/math "$OPENAI_MATH_COMMIT" "$WORK/math" || {
  end_step
  blocked "could not check out openai/math at $OPENAI_MATH_COMMIT"
}
echo "toolchain: $(cat "$WORK/math/lean/lean-toolchain")"
end_step

step "lean4export at $LEAN4EXPORT_COMMIT, built with the toolchain of openai/math"
# lean4export reads the project's .olean files, whose header names the exact Lean version: built with its own
# v4.34.0 toolchain it refuses the v4.34.1 oleans of openai/math ("incompatible header"). So it is built with the
# project's toolchain (a patch release apart from the tag's).
clone https://github.com/leanprover/lean4export "$LEAN4EXPORT_COMMIT" "$WORK/lean4export" \
  && cp "$WORK/math/lean/lean-toolchain" "$WORK/lean4export/lean-toolchain" \
  && echo "lean4export toolchain: $(cat "$WORK/lean4export/lean-toolchain")" \
  && (cd "$WORK/lean4export" && lake build lean4export) || {
  end_step
  blocked "lean4export at $LEAN4EXPORT_COMMIT did not build"
}
end_step

step "comparator at $COMPARATOR_COMMIT"
clone https://github.com/leanprover/comparator "$COMPARATOR_COMMIT" "$WORK/comparator" \
  && (cd "$WORK/comparator" && lake build comparator) || {
  end_step
  blocked "comparator at $COMPARATOR_COMMIT did not build"
}
ln -sf "$WORK/lean4export/.lake/build/bin/lean4export" "$WORK/bin/lean4export"
ln -sf "$WORK/comparator/.lake/build/bin/comparator" "$WORK/bin/comparator"
end_step

step "Mathlib cache and pinned dependencies of openai/math (lake exe cache get)"
(cd "$WORK/math/lean" && lake exe cache get) || {
  end_step
  blocked "lake exe cache get failed in openai/math/lean (dependencies or Mathlib cache could not be fetched)"
}
df -h / | tail -1
end_step

step "systemd-run guard"
if systemd-run --user --pipe --wait --collect --quiet --property=RestrictAddressFamilies=~AF_UNIX /usr/bin/true; then
  echo "systemd_run=true" >> "$GITHUB_OUTPUT"
  echo "systemd-run --user works; Comparator runs under it"
else
  echo "systemd_run=false" >> "$GITHUB_OUTPUT"
  echo "systemd-run --user is not available on this runner; Comparator runs under landrun alone (recorded)"
fi
end_step
echo "ready"
