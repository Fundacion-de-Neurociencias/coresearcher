#!/usr/bin/env bash
# Setup for the Lean oracle of the openai/math pilot on the Lenovo Legion (LEAN_ORACLE_PROTOCOL.md, section 4).
#
# Installs, under TOOLS_DIR, the three Comparator tools built with the project's own Lean toolchain, and checks out
# openai/math at the pinned commit with its Mathlib cache. Re-running it is safe: finished steps are skipped.
#
#   bash scripts/benchmarks/legion_lean_oracle_setup.sh [TOOLS_DIR] [MATH_ROOT]
#
# Defaults: TOOLS_DIR=~/oracle-tools, MATH_ROOT=~/openai-math. It prints the lines to add to the shell at the end.
# Then run `python scripts/benchmarks/openai_math_lean_oracle.py preflight --math-root MATH_ROOT`.
#
# Why each tool is built with the project's toolchain (v4.34.1) instead of its own: .olean files carry the Lean
# version that wrote them, and lean4export and comparator read the project's .olean files. Upstream tags exist for
# v4.34.0 only; v4.34.1 is a patch release of the same line.
set -euo pipefail

TOOLS_DIR="${1:-$HOME/oracle-tools}"
MATH_ROOT="${2:-$HOME/openai-math}"
MATH_COMMIT="1581d4cbdd69a0faf34b2089614fe2a814316a6a"
COMPARATOR_TAG="v4.34.0"   # d03acab154d269c06e60e4de7e4cc85deebff94b; pins lean4export 076e8e5 (its v4.34.0 tag)
LEAN4EXPORT_TAG="v4.34.0"  # 076e8e57707e813375e8f9da8bf989799ace9680

if [ "$(id -u)" = "0" ]; then
  echo "Run this as the unprivileged user that will run Comparator, not as root." >&2
  exit 1
fi
for tool in git go elan; do
  command -v "$tool" >/dev/null || { echo "missing: $tool (install it first; see the runbook)" >&2; exit 1; }
done
mkdir -p "$TOOLS_DIR/bin"

# 1. openai/math at the pinned commit, and its Mathlib cache.
if [ ! -d "$MATH_ROOT/.git" ]; then
  git init -q "$MATH_ROOT"
  git -C "$MATH_ROOT" remote add origin https://github.com/openai/math.git
fi
if [ "$(git -C "$MATH_ROOT" rev-parse HEAD 2>/dev/null || true)" != "$MATH_COMMIT" ]; then
  git -C "$MATH_ROOT" fetch -q --depth 1 origin "$MATH_COMMIT"
  git -C "$MATH_ROOT" checkout -q --detach FETCH_HEAD
fi
TOOLCHAIN="$(cat "$MATH_ROOT/lean/lean-toolchain")"
echo "openai/math at $(git -C "$MATH_ROOT" rev-parse --short HEAD), toolchain $TOOLCHAIN"
# No `lake update`: the manifest is part of the pinned commit, and updating would move the dependencies.
(cd "$MATH_ROOT/lean" && lake exe cache get)

# The lakefile patches 11 dependencies while Lake resolves them, but applies the patches for these 12 only in its
# `post_update` hook, which runs on `lake update` alone. Without them, rellich-kondrachov (and others) fail to build
# against the pinned Mathlib. Apply the same patches with the same checks as the hook, without moving any commit.
POST_UPDATE_PATCHED="fixed-point-theorems PrimeNumberTheoremAnd Zeta3Irrational rellich-kondrachov carleson StrongPNT
  AbsorptionCutoff AINTLIB ClassFieldTheory schoenflies-lean SphereEversion gromov"
for label in $POST_UPDATE_PATCHED; do
  dep="$MATH_ROOT/lean/.lake/packages/$label"
  patch="$MATH_ROOT/lean/patches/$label-lean4341.patch"
  if git -C "$dep" apply --check --reverse "$patch" 2>/dev/null; then
    continue
  fi
  git -C "$dep" apply --check "$patch"
  git -C "$dep" apply --whitespace=nowarn "$patch"
  git -C "$dep" apply --check --reverse "$patch"
  echo "$label: applied compatibility patch"
done

# 2. landrun from the main branch (Comparator README). The commit is recorded in tools.txt.
if [ ! -x "$TOOLS_DIR/bin/landrun" ]; then
  rm -rf "$TOOLS_DIR/src/landrun"
  git clone -q --depth 1 https://github.com/Zouuup/landrun.git "$TOOLS_DIR/src/landrun"
  (cd "$TOOLS_DIR/src/landrun" && go build -o "$TOOLS_DIR/bin/landrun" ./cmd/landrun)
fi

# 3. lean4export and comparator at their v4.34.0 tags, built with the project's toolchain.
build_lean_tool() {  # name tag exe
  local src="$TOOLS_DIR/src/$1"
  if [ ! -x "$TOOLS_DIR/bin/$3" ]; then
    rm -rf "$src"
    git clone -q --depth 1 --branch "$2" "https://github.com/leanprover/$1.git" "$src"
    echo "$TOOLCHAIN" > "$src/lean-toolchain"
    (cd "$src" && lake build "$3")
    ln -sf "$src/.lake/build/bin/$3" "$TOOLS_DIR/bin/$3"
  fi
}
build_lean_tool lean4export "$LEAN4EXPORT_TAG" lean4export
build_lean_tool comparator "$COMPARATOR_TAG" comparator

{
  echo "openai/math $(git -C "$MATH_ROOT" rev-parse HEAD)"
  echo "toolchain $TOOLCHAIN"
  echo "landrun $(git -C "$TOOLS_DIR/src/landrun" rev-parse HEAD)"
  echo "lean4export $(git -C "$TOOLS_DIR/src/lean4export" rev-parse HEAD)"
  echo "comparator $(git -C "$TOOLS_DIR/src/comparator" rev-parse HEAD)"
  echo "post_update patches applied: $(echo $POST_UPDATE_PATCHED)"
} > "$TOOLS_DIR/tools.txt"
cat "$TOOLS_DIR/tools.txt"

echo
echo "Add to the shell (or the git-ignored .env), then run the preflight:"
echo "  export PATH=\"$TOOLS_DIR/bin:\$PATH\""
echo "  python scripts/benchmarks/openai_math_lean_oracle.py preflight --math-root $MATH_ROOT"
