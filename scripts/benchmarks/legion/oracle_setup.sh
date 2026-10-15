#!/usr/bin/env bash
# Toolchain for the Lean/Comparator oracle (LEAN_ORACLE_PROTOCOL.md), installed entirely under $HOME: no sudo.
# Idempotent: re-running skips what is already installed. Run as a NON-root user on Linux.
#
#   bash scripts/benchmarks/legion/oracle_setup.sh            # default install dir: ~/oracle
#   ORACLE_HOME=/data/oracle bash scripts/benchmarks/legion/oracle_setup.sh
#   PREFLIGHT_ONLY=1 bash scripts/benchmarks/legion/oracle_setup.sh   # check the machine, install nothing
#
# Then follow LEGION_RUNBOOK.md section 3. Verified preflight on 2026-10-15 (Ubuntu 24.04 under WSL2, kernel 5.15).
set -euo pipefail

ORACLE_HOME="${ORACLE_HOME:-$HOME/oracle}"
MATH_COMMIT=1581d4cbdd69a0faf34b2089614fe2a814316a6a
GO_VERSION=1.23.4
export PATH="$HOME/.elan/bin:$HOME/go-sdk/go/bin:$ORACLE_HOME/bin:$PATH"
: "${XDG_RUNTIME_DIR:=/run/user/$(id -u)}"; export XDG_RUNTIME_DIR
log() { echo "[$(date +%H:%M:%S)] $*"; }
die() { echo "PREFLIGHT FAILED: $*" >&2; exit 1; }

# ---------------------------------------------------------------- preflight
[ "$(uname -s)" = Linux ] || die "Comparator needs Linux."
[ "$(id -u)" != 0 ] || die "do not run as root (Comparator refuses it)."
# grep -c reads the whole stream, so pipefail does not trip on SIGPIPE from zcat.
landlock=$( { cat /sys/kernel/security/lsm 2>/dev/null; echo; cat "/boot/config-$(uname -r)" 2>/dev/null
              zcat /proc/config.gz 2>/dev/null; } | grep -ci "landlock" || true)
[ "${landlock:-0}" -gt 0 ] || die "kernel without Landlock (landrun cannot sandbox)."
# systemd-run --user needs the user manager's bus. WSLg points XDG_RUNTIME_DIR elsewhere, so prefer /run/user/UID.
[ -S "/run/user/$(id -u)/bus" ] && export XDG_RUNTIME_DIR="/run/user/$(id -u)"
user_state=$(systemctl --user is-system-running 2>/dev/null || true)
case "$user_state" in
  running|degraded) ;;
  *) die "no systemd user session (state '${user_state:-none}'), needed by systemd-run --user. On a desktop login it
exists; on a headless or WSL machine run 'loginctl enable-linger $(id -un)' once, then open a new shell." ;;
esac
for tool in git curl tar python3; do command -v "$tool" >/dev/null || die "missing $tool"; done
free_gb=$(df -BG --output=avail "$HOME" | tail -1 | tr -dc 0-9)
[ "$free_gb" -ge 30 ] || die "need at least 30 GB free in \$HOME (have ${free_gb} GB)."
log "preflight ok: $(nproc) cores, $(free -g | awk '/Mem/{print $2}') GB RAM, ${free_gb} GB free"
[ "${PREFLIGHT_ONLY:-0}" = 1 ] && exit 0

mkdir -p "$ORACLE_HOME/bin" && cd "$ORACLE_HOME"

# ---------------------------------------------------------------- Lean
if [ ! -x "$HOME/.elan/bin/elan" ]; then
  log "installing elan"
  curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -o elan-init.sh
  sh elan-init.sh -y --default-toolchain none >/dev/null
fi

# ---------------------------------------------------------------- openai/math at the pinned commit
[ -d openai-math ] || { log "cloning openai/math"; git clone -q https://github.com/openai/math.git openai-math; }
git -C openai-math checkout -q "$MATH_COMMIT"
LEAN_TOOLCHAIN=$(cat openai-math/lean/lean-toolchain)
LEANVER=${LEAN_TOOLCHAIN##*:}
log "openai/math $MATH_COMMIT, toolchain $LEAN_TOOLCHAIN"
# The Mathlib cache is ~9,000 files; on a slow link this step takes an hour or more. Re-running resumes it.
(cd openai-math/lean && lake exe cache get) && log "Mathlib cache ok"

# ---------------------------------------------------------------- landrun (Go, main branch)
if [ ! -x "$HOME/go-sdk/go/bin/go" ]; then
  log "installing Go $GO_VERSION under ~/go-sdk"
  mkdir -p "$HOME/go-sdk" && curl -sSfL "https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz" | tar -xz -C "$HOME/go-sdk"
fi
if [ ! -x "$ORACLE_HOME/bin/landrun" ]; then
  log "building landrun (main)"
  rm -rf landrun && git clone -q https://github.com/Zouuup/landrun.git landrun
  (cd landrun && go build -o "$ORACLE_HOME/bin/landrun" ./cmd/landrun)
fi

# ---------------------------------------------------------------- lean4export and comparator, for the pinned Lean
build_lean_tool() {  # $1 = repo name under github.com/leanprover
  local name=$1
  [ -x "$ORACLE_HOME/bin/$name" ] && return
  log "building $name for $LEANVER"
  rm -rf "$name" && git clone -q "https://github.com/leanprover/$name.git"
  (
    cd "$name"
    if git rev-parse -q --verify "refs/tags/$LEANVER" >/dev/null; then git checkout -q "$LEANVER"
    else log "$name has no tag $LEANVER; using its default branch with the pinned toolchain"; fi
    echo "$LEAN_TOOLCHAIN" > lean-toolchain
    lake build
    cp ".lake/build/bin/$name" "$ORACLE_HOME/bin/"
  )
}
build_lean_tool lean4export
build_lean_tool comparator

log "tools in $ORACLE_HOME/bin: $(ls "$ORACLE_HOME/bin" | tr '\n' ' ')"
log "SETUP_DONE. Add to PATH: export PATH=\"$ORACLE_HOME/bin:\$HOME/.elan/bin:\$PATH\""
