#!/usr/bin/env bash
# Check DNS records for key Sifututor domains via Cloudflare read-only API
# Safe: no token printed; uses the scoped zone config for each domain
# Usage: ./scripts/agent-access/check-cloudflare-dns.sh [domain]

set -euo pipefail

CONF_DIR="${HOME}/.config/sifututor/agent-access"

echo "=== Cloudflare DNS Check ==="

# Key domains to check
CHECK_DOMAINS=(
  "st.admin.sifututor.my"
  "cloud.tutorla.tech"
  "sifu-staging.tutorla.tech"
  "ripple.admin.sifututor.my"
  "api.sifu-tutor.tutorla.tech"
  "koda.tutorla.tech"
)

if [[ -n "${1:-}" ]]; then
  CHECK_DOMAINS=("$1")
fi

load_zone_config() {
  local domain="$1"
  local conf_file=""

  unset CLOUDFLARE_API_TOKEN CLOUDFLARE_ZONE_ID CF_API_TOKEN CF_ZONE_ID

  case "$domain" in
    *.tutorla.tech|tutorla.tech)
      conf_file="$CONF_DIR/cloudflare-readonly.conf"
      ;;
    *.sifututor.my|sifututor.my)
      conf_file="$CONF_DIR/cloudflare-sifututormy-dns-write.conf"
      ;;
    *)
      echo "  $domain: unsupported zone"
      return 1
      ;;
  esac

  if [[ ! -f "$conf_file" ]]; then
    echo "  $domain: conf missing: $conf_file"
    return 1
  fi

  # shellcheck disable=SC1090
  source "$conf_file"

  CF_TOKEN="${CLOUDFLARE_API_TOKEN:-${CF_API_TOKEN:-}}"
  CF_ZONE="${CLOUDFLARE_ZONE_ID:-${CF_ZONE_ID:-}}"

  if [[ -z "$CF_TOKEN" || -z "$CF_ZONE" ]]; then
    echo "  $domain: Cloudflare token or zone id not configured in $(basename "$conf_file")"
    return 1
  fi
}

check_api() {
  local domain="$1"
  local status
  status=$(curl -s -o /dev/null -w '%{http_code}' \
    -H "Authorization: Bearer $CF_TOKEN" \
    "https://api.cloudflare.com/client/v4/zones/${CF_ZONE}" 2>/dev/null || echo "000")

  if [[ "$status" != "200" ]]; then
    echo "  $domain: Cloudflare API HTTP $status"
    return 1
  fi
}

cf_lookup() {
  local domain="$1"

  load_zone_config "$domain" || return
  check_api "$domain" || return

  local result
  result=$(curl -s \
    -H "Authorization: Bearer $CF_TOKEN" \
    "https://api.cloudflare.com/client/v4/zones/${CF_ZONE}/dns_records?name=${domain}&type=A" 2>/dev/null)

  local success
  success=$(echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success','false'))" 2>/dev/null || echo "false")

  if [[ "$success" != "True" && "$success" != "true" ]]; then
    echo "  $domain: API error"
    return
  fi

  local count
  count=$(echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('result',[])))" 2>/dev/null || echo "0")

  if [[ "$count" -eq 0 ]]; then
    echo "  $domain: no A record found"
    return
  fi

  echo "$result" | python3 -c "
import sys, json
d = json.load(sys.stdin)
for r in d.get('result', []):
    proxied = '(CF proxied)' if r.get('proxied') else '(DNS-only)'
    print(f\"  {r['name']} → {r['content']} {proxied} TTL={r.get('ttl','auto')}\")
" 2>/dev/null || echo "  $domain: parse error"
}

echo "── Key domain A records ──"
for domain in "${CHECK_DOMAINS[@]}"; do
  cf_lookup "$domain"
done

echo ""
echo "── SSL status for st.admin.sifututor.my ──"
echo | openssl s_client -servername st.admin.sifututor.my \
  -connect st.admin.sifututor.my:443 2>/dev/null | \
  openssl x509 -noout -subject -issuer -dates 2>/dev/null || \
  echo "  Could not retrieve SSL info"
