#!/usr/bin/env bash
# Runs one command with the V16 destination read-only lane attached (#1089).
#
#   bash scripts/agent-access/ripple-destination-readonly-run.sh -- <command> [args...]
#
# It opens an SSH tunnel to KVM8 (the PostgreSQL server listens on localhost only),
# exports `V16_DESTINATION_READ_URL` into the child process environment, runs the command
# and closes the tunnel. The credential is never passed as a command-line argument, so it
# does not appear in any process listing, and it is never echoed.
#
# The role behind that URL holds SELECT on four `v16_read_*` views and nothing else. See
# `docs/agent-playbooks/agent-access-map.md`, lane `ripple-destination-readonly`.
set -euo pipefail

CONF="$HOME/.config/sifututor/agent-access/ripple-destination-readonly.conf"
[ -f "$CONF" ] || { echo "lane_conf_missing" >&2; exit 1; }
[ "$(stat -f '%Lp' "$CONF" 2>/dev/null || stat -c '%a' "$CONF")" = "600" ] \
  || { echo "lane_conf_mode_unsafe" >&2; exit 1; }

[ "${1:-}" = "--" ] || { echo "usage: ... -- <command> [args...]" >&2; exit 2; }
shift
[ "$#" -gt 0 ] || { echo "no_command" >&2; exit 2; }

# shellcheck disable=SC1090
set -a; . "$CONF"; set +a

LPORT="$RIPPLE_DESTINATION_READONLY_LOCAL_PORT"
TUNNEL_PID=""
cleanup() { [ -n "$TUNNEL_PID" ] && kill "$TUNNEL_PID" 2>/dev/null; return 0; }
trap cleanup EXIT

if ! nc -z 127.0.0.1 "$LPORT" 2>/dev/null; then
  ssh -o ConnectTimeout=25 -o ExitOnForwardFailure=yes -N \
      -L "${LPORT}:${RIPPLE_DESTINATION_READONLY_REMOTE_HOST}:${RIPPLE_DESTINATION_READONLY_REMOTE_PORT}" \
      "$RIPPLE_DESTINATION_READONLY_SSH_HOST" &
  TUNNEL_PID=$!
  for _ in 1 2 3 4 5 6 7 8 9 10; do
    nc -z 127.0.0.1 "$LPORT" 2>/dev/null && break
    sleep 1
  done
fi
nc -z 127.0.0.1 "$LPORT" 2>/dev/null || { echo "lane_tunnel_failed" >&2; exit 1; }

# The password is base64url (A-Za-z0-9-_), so it needs no percent-encoding here. The
# generator enforces that alphabet; a different one would have to encode.
case "$RIPPLE_DESTINATION_READONLY_PASSWORD" in
  *[!A-Za-z0-9_-]*) echo "lane_password_not_url_safe" >&2; exit 1 ;;
esac

export V16_DESTINATION_READ_URL="postgresql://${RIPPLE_DESTINATION_READONLY_USERNAME}:${RIPPLE_DESTINATION_READONLY_PASSWORD}@127.0.0.1:${LPORT}/${RIPPLE_DESTINATION_READONLY_DATABASE}"
unset RIPPLE_DESTINATION_READONLY_PASSWORD

"$@"
