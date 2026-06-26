#!/usr/bin/env bash
# Check SSL certificate for st.admin.sifututor.my
# Safe: no credentials needed — reads public TLS handshake only
# Usage: ./scripts/agent-access/check-st-admin-cert.sh [--warn-days N]

set -euo pipefail

DOMAIN="st.admin.sifututor.my"
WARN_DAYS="${2:-30}"

if [[ "${1:-}" == "--warn-days" && -n "${2:-}" ]]; then
  WARN_DAYS="$2"
fi

echo "=== SSL Certificate Check: $DOMAIN ==="

# Fetch cert info
CERT_INFO=$(echo | openssl s_client -servername "$DOMAIN" \
  -connect "$DOMAIN:443" 2>/dev/null | \
  openssl x509 -noout -subject -issuer -dates -ext subjectAltName 2>/dev/null)

if [[ -z "$CERT_INFO" ]]; then
  echo "✗ Could not retrieve certificate for $DOMAIN"
  exit 1
fi

echo "$CERT_INFO"
echo ""

# Extract and check expiry
NOT_AFTER=$(echo | openssl s_client -servername "$DOMAIN" \
  -connect "$DOMAIN:443" 2>/dev/null | \
  openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)

if [[ -z "$NOT_AFTER" ]]; then
  echo "✗ Could not parse expiry date"
  exit 1
fi

EXPIRY_EPOCH=$(date -j -f "%b %d %H:%M:%S %Y %Z" "$NOT_AFTER" "+%s" 2>/dev/null \
  || date -d "$NOT_AFTER" "+%s" 2>/dev/null || echo "0")
NOW_EPOCH=$(date "+%s")
DAYS_LEFT=$(( (EXPIRY_EPOCH - NOW_EPOCH) / 86400 ))

if [[ "$DAYS_LEFT" -lt 0 ]]; then
  echo "✗ EXPIRED ${DAYS_LEFT#-} days ago (${NOT_AFTER})"
  exit 2
elif [[ "$DAYS_LEFT" -lt "$WARN_DAYS" ]]; then
  echo "~ WARNING: expires in $DAYS_LEFT days (${NOT_AFTER})"
  echo "  Run: /root/.acme.sh/acme.sh --renew -d $DOMAIN --force"
  exit 1
else
  echo "✓ Valid for $DAYS_LEFT more days (expires ${NOT_AFTER})"
fi

# Verify API route is reachable with valid TLS
echo ""
echo "── API route check ──"
HTTP_CODE=$(curl -sI -o /dev/null -w '%{http_code}' --max-time 8 \
  "https://${DOMAIN}/api/ripple/invoices/81917/mark-paid" 2>/dev/null || echo "000")
ALLOW_HEADER=$(curl -sI --max-time 8 \
  "https://${DOMAIN}/api/ripple/invoices/81917/mark-paid" 2>/dev/null | \
  grep -i '^allow:' | tr -d '\r' || echo "")

if [[ "$HTTP_CODE" == "405" ]]; then
  echo "✓ API route /api/ripple/invoices/81917/mark-paid: HTTP 405 $ALLOW_HEADER"
elif [[ "$HTTP_CODE" == "000" ]]; then
  echo "✗ API route: connection failed (possible SSL error)"
  exit 1
else
  echo "  API route: HTTP $HTTP_CODE (expected 405 — route exists but may need POST)"
fi

echo ""
echo "acme.sh renewal schedule:"
ls -1 /root/.acme.sh/st.admin.sifututor.my/ 2>/dev/null | head -5 || \
  echo "  (run on production server: ssh production 'ls /root/.acme.sh/st.admin.sifututor.my/')"
