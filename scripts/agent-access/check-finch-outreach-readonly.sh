#!/usr/bin/env bash
# Verify the Finch outreach read-only lane without printing credentials or rows:
# views readable, no personal columns, base tables/other databases/writes refused.
set -uo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
exec "$DIR/finch-outreach-readonly-run.sh" -- bash "$DIR/check-finch-outreach-readonly-inner.sh"
