#!/usr/bin/env bash
# Run Ripple's reusable authenticated Luna staging RBAC smoke.
# The product wrapper sources the external mode-600 credential lane.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
RIPPLE_SUITE_DIR="${RIPPLE_SUITE_DIR:-$WORKSPACE_ROOT/ripple-suite}"

if [[ ! -f "$RIPPLE_SUITE_DIR/package.json" ]]; then
  echo "Ripple Suite directory not found: $RIPPLE_SUITE_DIR"
  exit 1
fi

if ! grep -q '"test:staging-luna-auth-smoke"' "$RIPPLE_SUITE_DIR/package.json"; then
  echo "Ripple staging Luna smoke is not available in: $RIPPLE_SUITE_DIR"
  exit 1
fi

npm --prefix "$RIPPLE_SUITE_DIR" run test:staging-luna-auth-smoke
