#!/usr/bin/env bash
# Run this yourself on the home PC, inside Ubuntu (WSL). An agent must never run it or see what is typed.
# It gives Claude on the PC access to the Koda memory server:
#   1. asks for the Koda key with echo off (twice) and saves it, mode 600, in ~/.config/sifututor/koda-key.conf
#   2. adds one guarded line to your shell profile so every shell loads the key
#   3. creates a minimal .mcp.json in the repo (Koda only, key by variable reference) if none exists
#   4. runs Koda's read-only health check and prints only PASS or FAIL
# Usage: scripts/agent-access/setup-pc-koda.sh
# Test switches: SIFUTUTOR_CONFIG_DIR, SIFUTUTOR_PROFILE_FILE, SIFUTUTOR_REPO, SIFUTUTOR_SKIP_HEALTH=1

set -euo pipefail

CONF_DIR="${SIFUTUTOR_CONFIG_DIR:-$HOME/.config/sifututor}"
KEY_FILE="$CONF_DIR/koda-key.conf"
PROFILE="${SIFUTUTOR_PROFILE_FILE:-$HOME/.bashrc}"
REPO="${SIFUTUTOR_REPO:-$HOME/Projects/Sifututor}"
MARK="# sifututor koda key (added by setup-pc-koda.sh)"

if [[ ! -t 0 ]]; then
  echo "This script needs a real terminal so the key can be typed with echo off." >&2
  echo "Run it yourself on the PC. Do not pipe input into it." >&2
  exit 2
fi

umask 077
KEY=""; CONFIRM=""; TMP=""
cleanup() {
  unset KEY CONFIRM
  if [[ -n "${TMP:-}" ]]; then rm -f "$TMP"; fi
}
trap cleanup EXIT

printf 'Koda key (hidden): '
read -rs KEY
printf '\n'
printf 'Koda key again (hidden): '
read -rs CONFIRM
printf '\n'
if [[ -z "$KEY" ]]; then echo "The key is empty. Nothing written." >&2; exit 1; fi
if [[ "$KEY" != "$CONFIRM" ]]; then echo "The two entries differ. Nothing written." >&2; exit 1; fi
if [[ "$KEY" == *[[:space:]]* ]]; then echo "The key contains a space or a line break. Nothing written." >&2; exit 1; fi

mkdir -p "$CONF_DIR"
chmod 700 "$CONF_DIR"
TMP="$(mktemp "$CONF_DIR/.koda-key.XXXXXX")"
printf 'KODA_API_KEY=%q\n' "$KEY" > "$TMP"
chmod 600 "$TMP"
mv "$TMP" "$KEY_FILE"
TMP=""
echo "Saved $KEY_FILE (mode 600)."

touch "$PROFILE"
if ! grep -qF "$MARK" "$PROFILE"; then
  {
    printf '\n%s\n' "$MARK"
    printf '%s\n' "[ -f \"$KEY_FILE\" ] && { set -a; . \"$KEY_FILE\"; set +a; }"
  } >> "$PROFILE"
  echo "Added the key-loading line to $PROFILE."
else
  echo "$PROFILE already loads the key; left as it was."
fi

MCP="$REPO/.mcp.json"
if [[ -e "$MCP" ]]; then
  echo "$MCP already exists; left as it was."
elif [[ -d "$REPO" ]]; then
  printf '%s\n' '{' '  "mcpServers": {' '    "memory": {' '      "type": "http",' \
    '      "url": "https://koda.tutorla.tech/mcp",' '      "headers": {' \
    '        "Authorization": "Bearer ${KODA_API_KEY}"' '      }' '    }' '  }' '}' > "$MCP"
  echo "Created $MCP (Koda only; it refers to the key by variable name)."
else
  echo "Repo folder $REPO not found; skipped .mcp.json."
fi

if [[ "${SIFUTUTOR_SKIP_HEALTH:-0}" == "1" ]]; then
  echo "Health check skipped."
else
  if ( set -a; . "$KEY_FILE"; set +a; "$REPO/scripts/agent-checks/koda" health ) > /dev/null 2>&1; then
    echo "Koda health check: PASS"
  else
    echo "Koda health check: FAIL (the key may be wrong, or the PC cannot reach koda.tutorla.tech)"
    exit 1
  fi
fi
echo "Open a new Ubuntu shell so the profile line takes effect."
