#!/usr/bin/env bash
# Verify the Ripple outreach read-only lane without printing credentials or rows.
set -uo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
exec "$DIR/ripple-outreach-readonly-run.sh" -- bash "$DIR/check-ripple-outreach-readonly-inner.sh"
