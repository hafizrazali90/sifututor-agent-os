#!/usr/bin/env bash
# Check Sentry and BetterStack monitoring status
# Sources: monitoring-readonly.conf
# Safe: no tokens printed; aggregate counts only
# Usage: ./scripts/agent-access/check-monitoring.sh [--sentry-only | --betterstack-only]

set -euo pipefail

CONF_DIR="${HOME}/.config/sifututor/agent-access"
CONF_FILE="$CONF_DIR/monitoring-readonly.conf"

echo "=== Monitoring Status Check ==="

if [[ ! -f "$CONF_FILE" ]]; then
  echo "✗ Conf file missing: $CONF_FILE"
  exit 1
fi

# shellcheck disable=SC1090
source "$CONF_FILE"

MODE="${1:-all}"

if [[ "$MODE" != "--betterstack-only" ]]; then
  echo "── Sentry: ${SENTRY_ORG_SLUG} / ${SENTRY_PROJECT_SLUG} ──"

  # Organization check
  ORG_STATUS=$(curl -s -o /dev/null -w '%{http_code}' \
    -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
    "https://sentry.io/api/0/organizations/${SENTRY_ORG_SLUG}/" 2>/dev/null || echo "000")

  if [[ "$ORG_STATUS" != "200" ]]; then
    printf '\033[31m✗\033[0m Sentry org API: HTTP %s\n' "$ORG_STATUS"
  else
    printf '\033[32m✓\033[0m Sentry org API: reachable\n'

    # Unresolved issue count for this project
    ISSUES=$(curl -s \
      -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
      "https://sentry.io/api/0/projects/${SENTRY_ORG_SLUG}/${SENTRY_PROJECT_SLUG}/issues/?query=is:unresolved&limit=25" \
      2>/dev/null)

    COUNT=$(echo "$ISSUES" | python3 -c "
import sys, json
try:
  d = json.load(sys.stdin)
  print(len(d))
except:
  print('parse-error')
" 2>/dev/null || echo "parse-error")

    echo "  Unresolved issues (first 25): $COUNT"

    # Print titles without any PII
    echo "$ISSUES" | python3 -c "
import sys, json
try:
  items = json.load(sys.stdin)
  for item in items[:5]:
    level = item.get('level','?')
    title = item.get('title','?')[:80]
    count = item.get('count','?')
    print(f'  [{level}] {title} (×{count})')
except:
  pass
" 2>/dev/null || true
  fi
  echo ""
fi

if [[ "$MODE" != "--sentry-only" ]]; then
  echo "── BetterStack: ${BETTERSTACK_TEAM_NAME} ──"

  # List monitors (uptime)
  BS_STATUS=$(curl -s -o /dev/null -w '%{http_code}' \
    -H "Authorization: Bearer $BETTERSTACK_UPTIME_TOKEN" \
    "https://uptime.betterstack.com/api/v2/monitors?per_page=50" 2>/dev/null || echo "000")

  if [[ "$BS_STATUS" != "200" ]]; then
    printf '\033[31m✗\033[0m BetterStack API: HTTP %s\n' "$BS_STATUS"
  else
    printf '\033[32m✓\033[0m BetterStack API: reachable\n'

    BS_MONITORS=$(curl -s \
      -H "Authorization: Bearer $BETTERSTACK_UPTIME_TOKEN" \
      "https://uptime.betterstack.com/api/v2/monitors?per_page=50" 2>/dev/null)

    echo "$BS_MONITORS" | python3 -c "
import sys, json
try:
  d = json.load(sys.stdin)
  monitors = d.get('data', [])
  up = [m for m in monitors if m.get('attributes',{}).get('status') == 'up']
  down = [m for m in monitors if m.get('attributes',{}).get('status') in ('down','incident')]
  paused = [m for m in monitors if m.get('attributes',{}).get('status') == 'paused']
  print(f'  Total: {len(monitors)}  Up: {len(up)}  Down: {len(down)}  Paused: {len(paused)}')
  for m in down:
    name = m.get('attributes',{}).get('pronounceable_name','?')
    url = m.get('attributes',{}).get('url','?')
    print(f'  ✗ DOWN: {name} ({url})')
except Exception as e:
  print(f'  parse error: {e}')
" 2>/dev/null || echo "  (could not parse response)"
  fi
fi
