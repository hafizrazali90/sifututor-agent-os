#!/usr/bin/env bash
# Run one command with the narrow Ripple destination read-only URL in its
# environment. The credential is never printed or passed as a command argument.
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
cleanup() { [ -n "$TUNNEL_PID" ] && kill "$TUNNEL_PID" 2>/dev/null || true; }
trap cleanup EXIT

if nc -z 127.0.0.1 "$LPORT" 2>/dev/null; then
  echo "lane_local_port_busy" >&2
  exit 1
fi

ssh -o BatchMode=yes -o ConnectTimeout=25 -o ExitOnForwardFailure=yes -N \
    -L "${LPORT}:${RIPPLE_DESTINATION_READONLY_REMOTE_HOST}:${RIPPLE_DESTINATION_READONLY_REMOTE_PORT}" \
    "$RIPPLE_DESTINATION_READONLY_SSH_HOST" >/dev/null 2>&1 &
TUNNEL_PID=$!
for _ in 1 2 3 4 5 6 7 8 9 10; do
  nc -z 127.0.0.1 "$LPORT" 2>/dev/null && break
  kill -0 "$TUNNEL_PID" 2>/dev/null || break
  sleep 1
done
nc -z 127.0.0.1 "$LPORT" 2>/dev/null || { echo "lane_tunnel_failed" >&2; exit 1; }

case "$RIPPLE_DESTINATION_READONLY_PASSWORD" in
  *[!A-Za-z0-9_-]*) echo "lane_password_not_url_safe" >&2; exit 1 ;;
esac

export V16_DESTINATION_READ_URL="postgresql://${RIPPLE_DESTINATION_READONLY_USERNAME}:${RIPPLE_DESTINATION_READONLY_PASSWORD}@127.0.0.1:${LPORT}/${RIPPLE_DESTINATION_READONLY_DATABASE}"
unset RIPPLE_DESTINATION_READONLY_PASSWORD
"$@"
