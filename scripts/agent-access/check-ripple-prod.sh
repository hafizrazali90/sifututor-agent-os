#!/usr/bin/env bash
# Check Ripple Suite production health
# Sources: server-ssh.conf (SSH alias), production-smoke.conf (SIMS base URL)
# Safe: no secrets printed
# Usage: ./scripts/agent-access/check-ripple-prod.sh

set -euo pipefail

CONF_DIR="${HOME}/.config/sifututor/agent-access"

echo "=== Ripple Suite Production Health ==="

# Load SSH alias (non-secret)
if [[ -f "$CONF_DIR/server-ssh.conf" ]]; then
  # shellcheck disable=SC1090
  source "$CONF_DIR/server-ssh.conf"
  KVM8_ALIAS="staging"   # Ripple runs on KVM8 (staging SSH alias)
  SIMS_ALIAS="${PRODUCTION_SSH_ALIAS:-production}"
else
  KVM8_ALIAS="staging"
  SIMS_ALIAS="production"
fi

# 1. Ripple HTTPS
echo "── HTTP checks ──"
RIPPLE_URL="https://ripple.admin.sifututor.my"
RIPPLE_CODE=$(curl -sI -o /dev/null -w '%{http_code}' --max-time 10 "${RIPPLE_URL}/login" 2>/dev/null || echo "000")
if [[ "$RIPPLE_CODE" == "200" || "$RIPPLE_CODE" == "302" ]]; then
  printf '\033[32m✓\033[0m Ripple /login: HTTP %s\n' "$RIPPLE_CODE"
else
  printf '\033[31m✗\033[0m Ripple /login: HTTP %s\n' "$RIPPLE_CODE"
fi

# 2. SIMS API reachable from client (SSL check)
SIMS_MARK_PAID="https://st.admin.sifututor.my/api/ripple/invoices/81917/mark-paid"
SIMS_CODE=$(curl -sI -o /dev/null -w '%{http_code}' --max-time 10 "$SIMS_MARK_PAID" 2>/dev/null || echo "000")
if [[ "$SIMS_CODE" == "405" ]]; then
  printf '\033[32m✓\033[0m SIMS API /api/ripple mark-paid route: HTTP 405 (TLS OK)\n'
elif [[ "$SIMS_CODE" == "000" ]]; then
  printf '\033[31m✗\033[0m SIMS API: connection failed (possible SSL/network error)\n'
else
  printf '  SIMS API: HTTP %s\n' "$SIMS_CODE"
fi

# 3. SIMS SSL cert expiry
CERT_EXPIRY=$(echo | openssl s_client -servername st.admin.sifututor.my \
  -connect st.admin.sifututor.my:443 2>/dev/null | \
  openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2 || echo "FAILED")
if [[ "$CERT_EXPIRY" != "FAILED" && -n "$CERT_EXPIRY" ]]; then
  printf '  SIMS SSL: expires %s\n' "$CERT_EXPIRY"
fi

echo ""
echo "── PM2 status (KVM8) ──"

# 4. Check PM2 on KVM8
PM2_OUTPUT=$(ssh -o ConnectTimeout=10 -o BatchMode=yes "$KVM8_ALIAS" \
  "PM2_HOME=/home/deploy/.pm2 pm2 list --no-color 2>/dev/null | grep -E 'ripple-suite-prod|name'" 2>/dev/null || echo "SSH_FAILED")

if [[ "$PM2_OUTPUT" == "SSH_FAILED" ]]; then
  printf '\033[31m✗\033[0m SSH to KVM8 (%s): failed\n' "$KVM8_ALIAS"
else
  echo "$PM2_OUTPUT"
  if echo "$PM2_OUTPUT" | grep -q "online"; then
    printf '\033[32m✓\033[0m ripple-suite-prod: online\n'
  else
    printf '\033[31m✗\033[0m ripple-suite-prod: not online\n'
  fi
fi

echo ""
echo "── SIMS_API_BASE_URL in PM2 env ──"
PM2_ID=$(ssh -o ConnectTimeout=10 -o BatchMode=yes "$KVM8_ALIAS" \
  "PM2_HOME=/home/deploy/.pm2 pm2 list --no-color 2>/dev/null | awk -F'│' '/ripple-suite-prod/ { gsub(/ /, \"\", \$2); print \$2; exit }'" 2>/dev/null | xargs || echo "")

if [[ -n "$PM2_ID" ]]; then
  SIMS_API_URL=$(ssh -o ConnectTimeout=10 -o BatchMode=yes "$KVM8_ALIAS" \
    "PM2_HOME=/home/deploy/.pm2 pm2 env '$PM2_ID' 2>/dev/null | grep 'SIMS_API_BASE_URL:'" 2>/dev/null | \
    sed 's/.*SIMS_API_BASE_URL: //' | perl -pe 's/\e\[[0-9;]*[A-Za-z]//g' | xargs || echo "UNKNOWN")
else
  SIMS_API_URL="UNKNOWN"
fi
printf '  SIMS_API_BASE_URL = %s\n' "$SIMS_API_URL"

if echo "$SIMS_API_URL" | grep -q "st.admin.sifututor.my"; then
  printf '\033[32m✓\033[0m Using canonical SIMS URL\n'
elif echo "$SIMS_API_URL" | grep -q "cloud.tutorla.tech"; then
  printf '\033[33m~\033[0m Using temporary cloud.tutorla.tech fallback (was set during SSL incident)\n'
  echo "  To revert: source /etc/prod-env/ripple-suite.env; pm2 restart ripple-suite-prod --update-env"
fi

echo ""
echo "── Recent SIMS API errors (last 5 min) ──"
ERROR_LOGS=$(ssh -o ConnectTimeout=10 -o BatchMode=yes "$KVM8_ALIAS" \
  "PM2_HOME=/home/deploy/.pm2 pm2 logs ripple-suite-prod --lines 50 --nostream 2>/dev/null | \
  grep 'sims-api.*error\|SIMS.*fail\|CERT_HAS_EXPIRED' | tail -20" 2>/dev/null || echo "")
RECENT_ERRORS=$(printf '%s\n' "$ERROR_LOGS" | python3 -c '
import datetime as dt
import json
import re
import sys

cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=5)
for line in sys.stdin:
    match = re.search(r"(\{.*\})", line)
    if not match:
        continue
    try:
        payload = json.loads(match.group(1))
        timestamp = payload.get("ts")
        if not timestamp:
            continue
        seen_at = dt.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except Exception:
        continue
    if seen_at >= cutoff:
        print(line.rstrip())
')

if [[ -z "$RECENT_ERRORS" ]]; then
  printf '\033[32m✓\033[0m No SIMS API errors in recent logs\n'
else
  printf '\033[31m✗\033[0m SIMS API errors found:\n'
  echo "$RECENT_ERRORS"
fi
