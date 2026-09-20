#!/usr/bin/env bash
# Agent Access Doctor — verify all lanes are configured and reachable
# Safe: never prints secret values
# Usage: ./scripts/agent-access/agent-access-doctor.sh

set -euo pipefail

CONF_DIR="${HOME}/.config/sifututor/agent-access"
STRICT_DB="${AGENT_ACCESS_STRICT_DB:-0}"
PASS=0
FAIL=0
WARN=0

green() { printf '\033[32m✓\033[0m %s\n' "$*"; }
red()   { printf '\033[31m✗\033[0m %s\n' "$*"; }
warn()  { printf '\033[33m~\033[0m %s\n' "$*"; }
info()  { printf '  %s\n' "$*"; }

check_conf() {
  local name="$1"
  local file="$CONF_DIR/$name"
  if [[ -f "$file" ]]; then
    local keys
    keys=$(grep -c '^[A-Z_]*=' "$file" 2>/dev/null || echo 0)
    green "conf: $name ($keys keys)"
    PASS=$((PASS+1))
    return 0
  else
    red "conf missing: $name"
    FAIL=$((FAIL+1))
    return 1
  fi
}

echo "=== Agent Access Doctor ==="
echo "Conf dir: $CONF_DIR"
echo ""

# ── Conf file presence ───────────────────────────────────────────────────────
echo "── Conf files ──"
EXPECTED=(
  backup-admin.conf
  backup-readonly.conf
  cloudflare-admin.conf
  cloudflare-dns-write.conf
  cloudflare-readonly.conf
  cloudflare-sifututormy-dns-write.conf
  cpanel-admin.conf
  creative-hub-production-smoke.conf
  database-admin.conf
  database-readonly.conf
  lls-database-readonly.conf
  monitoring-readonly.conf
  payment-readonly.conf
  payment-write.conf
  production-smoke.conf
  ripple-staging-smoke.conf
  server-admin.conf
  server-ssh.conf
  staging-smoke.conf
  wasabi-ripple-storage-scoped.conf
  wasabi-ripple-storage.conf
)

for conf in "${EXPECTED[@]}"; do
  check_conf "$conf"
done

# M365 special file
if [[ -f "${HOME}/.config/sifututor/m365-readonly.env" ]]; then
  green "conf: m365-readonly.env"
  PASS=$((PASS+1))
else
  warn "conf optional: m365-readonly.env (Teams Planner access)"
  WARN=$((WARN+1))
fi

# SharePoint delegated read-only lane. Missing setup is a warning because the
# first owner login/consent is intentionally separate from installation.
SHAREPOINT_CONFIG="${HOME}/.config/sifututor/sharepoint-readonly.json"
if [[ -f "$SHAREPOINT_CONFIG" ]]; then
  MODE=$(stat -f '%Lp' "$SHAREPOINT_CONFIG" 2>/dev/null || stat -c '%a' "$SHAREPOINT_CONFIG" 2>/dev/null || echo unknown)
  if [[ "$MODE" == "600" ]]; then
    green "conf: sharepoint-readonly.json (mode 600)"
    PASS=$((PASS+1))
  else
    red "conf: sharepoint-readonly.json has unsafe mode $MODE (expected 600)"
    FAIL=$((FAIL+1))
  fi
else
  warn "conf optional: sharepoint-readonly.json (first consent not completed)"
  WARN=$((WARN+1))
fi

# Lokka binary
if [[ -x "${HOME}/.codex/bin/m365-lokka-from-agent-access.sh" ]]; then
  green "binary: m365-lokka-from-agent-access.sh"
  PASS=$((PASS+1))
else
  warn "binary optional: m365-lokka-from-agent-access.sh"
  WARN=$((WARN+1))
fi

echo ""

# ── Connectivity checks ───────────────────────────────────────────────────────
echo "── Connectivity ──"

# SIMS production smoke (no auth needed)
if source "$CONF_DIR/production-smoke.conf" 2>/dev/null; then
  CODE=$(curl -sI -o /dev/null -w '%{http_code}' --max-time 8 "${SIMS_SMOKE_BASE_URL}/login" 2>/dev/null || echo "000")
  if [[ "$CODE" == "200" || "$CODE" == "302" ]]; then
    green "SIMS production: HTTP $CODE (${SIMS_SMOKE_BASE_URL})"
    PASS=$((PASS+1))
  else
    red "SIMS production: HTTP $CODE (${SIMS_SMOKE_BASE_URL})"
    FAIL=$((FAIL+1))
  fi
else
  warn "SIMS production: conf not sourceable"
  WARN=$((WARN+1))
fi

# SIMS staging smoke
if source "$CONF_DIR/staging-smoke.conf" 2>/dev/null; then
  CODE=$(curl -sI -o /dev/null -w '%{http_code}' --max-time 8 "${SIMS_SMOKE_BASE_URL}/login" 2>/dev/null || echo "000")
  if [[ "$CODE" == "200" || "$CODE" == "302" ]]; then
    green "SIMS staging: HTTP $CODE (${SIMS_SMOKE_BASE_URL})"
    PASS=$((PASS+1))
  else
    red "SIMS staging: HTTP $CODE (${SIMS_SMOKE_BASE_URL})"
    FAIL=$((FAIL+1))
  fi
else
  warn "SIMS staging: conf not sourceable"
  WARN=$((WARN+1))
fi

# SSL cert check for st.admin
CERT_EXPIRY=$(echo | openssl s_client -servername st.admin.sifututor.my \
  -connect st.admin.sifututor.my:443 2>/dev/null | \
  openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2 || echo "FAILED")
if [[ "$CERT_EXPIRY" != "FAILED" && -n "$CERT_EXPIRY" ]]; then
  green "SSL cert: st.admin.sifututor.my — expires $CERT_EXPIRY"
  PASS=$((PASS+1))
else
  red "SSL cert: st.admin.sifututor.my — could not verify"
  FAIL=$((FAIL+1))
fi

# Production SSH
SSH_ALIAS=$(source "$CONF_DIR/server-ssh.conf" 2>/dev/null && echo "$PRODUCTION_SSH_ALIAS" || echo "production")
SSH_RESULT=$(ssh -o ConnectTimeout=8 -o BatchMode=yes "$SSH_ALIAS" "echo ssh-ok" 2>/dev/null || echo "FAILED")
if [[ "$SSH_RESULT" == "ssh-ok" ]]; then
  green "SSH production ($SSH_ALIAS): connected"
  PASS=$((PASS+1))
else
  red "SSH production ($SSH_ALIAS): connection failed"
  FAIL=$((FAIL+1))
fi

# Cloudflare read-only API (list zones without printing token)
if source "$CONF_DIR/cloudflare-readonly.conf" 2>/dev/null; then
  CF_STATUS=$(curl -s -o /dev/null -w '%{http_code}' \
    -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
    "https://api.cloudflare.com/client/v4/zones?per_page=1" 2>/dev/null || echo "000")
  if [[ "$CF_STATUS" == "200" ]]; then
    green "Cloudflare readonly: API reachable (HTTP $CF_STATUS)"
    PASS=$((PASS+1))
  else
    red "Cloudflare readonly: API returned HTTP $CF_STATUS"
    FAIL=$((FAIL+1))
  fi
else
  warn "Cloudflare readonly: conf not sourceable"
  WARN=$((WARN+1))
fi

# SIMS DB readonly (connection test only)
if source "$CONF_DIR/database-readonly.conf" 2>/dev/null; then
  if mysql -h "$SIMS_DB_READONLY_HOST" -P "$SIMS_DB_READONLY_PORT" \
    -u "$SIMS_DB_READONLY_USERNAME" -p"$SIMS_DB_READONLY_PASSWORD" \
    "$SIMS_DB_READONLY_DATABASE" \
    --connect-timeout=8 \
    -e "SELECT 1;" > /dev/null 2>&1; then
    green "SIMS DB readonly: connection OK (${SIMS_DB_READONLY_HOST}:${SIMS_DB_READONLY_PORT})"
    PASS=$((PASS+1))
  else
    if [[ "$STRICT_DB" == "1" ]]; then
      red "SIMS DB readonly: connection failed (${SIMS_DB_READONLY_HOST}:${SIMS_DB_READONLY_PORT})"
      FAIL=$((FAIL+1))
    else
      warn "SIMS DB readonly: direct connection unavailable (${SIMS_DB_READONLY_HOST}:${SIMS_DB_READONLY_PORT})"
      info "Production 3306 is normally firewalled from local. Use the approved SSH tunnel path, or rerun with AGENT_ACCESS_STRICT_DB=1 when direct DB access is expected."
      WARN=$((WARN+1))
    fi
  fi
else
  warn "SIMS DB readonly: conf not sourceable"
  WARN=$((WARN+1))
fi

# Monitoring: Sentry reachability
if source "$CONF_DIR/monitoring-readonly.conf" 2>/dev/null; then
  SENTRY_STATUS=$(curl -s -o /dev/null -w '%{http_code}' \
    -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
    "https://sentry.io/api/0/organizations/${SENTRY_ORG_SLUG}/" 2>/dev/null || echo "000")
  if [[ "$SENTRY_STATUS" == "200" ]]; then
    green "Sentry: API reachable (org: ${SENTRY_ORG_SLUG})"
    PASS=$((PASS+1))
  else
    red "Sentry: API returned HTTP $SENTRY_STATUS"
    FAIL=$((FAIL+1))
  fi
else
  warn "Monitoring: conf not sourceable"
  WARN=$((WARN+1))
fi

# Ripple prod HTTP check
RIPPLE_CODE=$(curl -sI -o /dev/null -w '%{http_code}' --max-time 8 \
  "https://ripple.admin.sifututor.my/login" 2>/dev/null || echo "000")
if [[ "$RIPPLE_CODE" == "200" || "$RIPPLE_CODE" == "302" ]]; then
  green "Ripple prod: HTTP $RIPPLE_CODE (https://ripple.admin.sifututor.my)"
  PASS=$((PASS+1))
else
  red "Ripple prod: HTTP $RIPPLE_CODE"
  FAIL=$((FAIL+1))
fi

echo ""
echo "── Summary ──"
printf "  %s pass  %s fail  %s warn\n" "$PASS" "$FAIL" "$WARN"

if [[ "$FAIL" -gt 0 ]]; then
  echo "  Some lanes need attention. Run the specific check script for details."
  exit 1
else
  echo "  All checked lanes are operational."
  exit 0
fi
