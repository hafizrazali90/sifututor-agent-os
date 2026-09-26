#!/usr/bin/env bash
# Run one command with the Finch production outreach read-only lane available on
# a temporary local tunnel. The child gets SQLCMDSERVER/SQLCMDDATABASE/
# SQLCMDUSER/SQLCMDPASSWORD in its environment; the credential is never printed
# or passed as an argument. Example:
#   finch-outreach-readonly-run.sh -- sqlcmd -C -Q "SELECT COUNT(*) FROM agent_read.outreach_operations"
set -euo pipefail
CONF="$HOME/.config/sifututor/agent-access/finch-outreach-readonly.conf"
[ -f "$CONF" ] || { echo "lane_conf_missing" >&2; exit 1; }
[ "$(stat -f '%Lp' "$CONF" 2>/dev/null || stat -c '%a' "$CONF")" = "600" ] || { echo "lane_conf_mode_unsafe" >&2; exit 1; }
[ "${1:-}" = "--" ] || { echo "usage: $0 -- <command> [args...]" >&2; exit 2; }
shift; [ "$#" -gt 0 ] || { echo "no_command" >&2; exit 2; }
# shellcheck disable=SC1090
. "$CONF"
LPORT="$FINCH_OUTREACH_READONLY_LOCAL_PORT"; TUNNEL_PID=""
cleanup() { [ -n "$TUNNEL_PID" ] && kill "$TUNNEL_PID" 2>/dev/null || true; }
trap cleanup EXIT
nc -z 127.0.0.1 "$LPORT" 2>/dev/null && { echo "lane_local_port_busy" >&2; exit 1; }
ssh -o BatchMode=yes -o ConnectTimeout=25 -o ExitOnForwardFailure=yes -N \
  -L "${LPORT}:${FINCH_OUTREACH_READONLY_REMOTE_HOST}:${FINCH_OUTREACH_READONLY_REMOTE_PORT}" \
  "$FINCH_OUTREACH_READONLY_SSH_HOST" >/dev/null 2>&1 &
TUNNEL_PID=$!
for _ in 1 2 3 4 5 6 7 8 9 10; do nc -z 127.0.0.1 "$LPORT" 2>/dev/null && break; kill -0 "$TUNNEL_PID" 2>/dev/null || break; sleep 1; done
nc -z 127.0.0.1 "$LPORT" 2>/dev/null || { echo "lane_tunnel_failed" >&2; exit 1; }
SQLCMDSERVER="127.0.0.1,${LPORT}" SQLCMDDATABASE="$FINCH_OUTREACH_READONLY_DATABASE" \
SQLCMDUSER="$FINCH_OUTREACH_READONLY_USERNAME" SQLCMDPASSWORD="$FINCH_OUTREACH_READONLY_PASSWORD" "$@"
