#!/usr/bin/env bash
# Check certificate renewal status.
#   default   : cPanel AutoSSL on the SIMS production server
#   --staging : certbot on the Finch box, which hosts SIMS staging (sifu-staging.tutorla.tech).
#               Finch has no cPanel; the old WebVoyager host this flag used to target is decommissioned.
# Sources: server-ssh.conf (SSH alias)
# Safe: reads certificate dates and log lines only; no secrets printed
# Usage: ./scripts/agent-access/check-cpanel-autossl.sh [--staging]

set -euo pipefail

CONF_DIR="${HOME}/.config/sifututor/agent-access"

echo "=== cPanel AutoSSL Status Check ==="

TARGET="${1:-}"
if [[ "$TARGET" == "--staging" ]]; then
  SSH_ALIAS="${STAGING_CERT_SSH_ALIAS:-finch}"
  SERVER_LABEL="Finch staging (SIMS staging, certbot)"
else
  SSH_ALIAS="production"
  SERVER_LABEL="Production (151.246.1.164)"
fi

echo "Server: $SERVER_LABEL"
echo ""

# SSH connectivity
SSH_RESULT=$(ssh -o ConnectTimeout=10 -o BatchMode=yes "$SSH_ALIAS" \
  "echo ssh-ok" 2>/dev/null || echo "FAILED")

if [[ "$SSH_RESULT" != "ssh-ok" ]]; then
  echo "✗ SSH to $SSH_ALIAS failed"
  exit 1
fi

printf '\033[32m✓\033[0m SSH: connected\n'
echo ""

if [[ "$TARGET" == "--staging" ]]; then
  echo "── certbot certificates (names and expiry only) ──"
  ssh -o ConnectTimeout=10 -o BatchMode=yes "$SSH_ALIAS" '
    certbot certificates 2>/dev/null | grep -E "Certificate Name|Domains:|Expiry Date" | sed "s/^ *//"
    echo ""
    echo "── renewal timer ──"
    systemctl is-active certbot.timer 2>/dev/null || echo "certbot.timer: not active (check cron)"
    systemctl list-timers certbot.timer --no-pager 2>/dev/null | sed -n "1,2p" | cut -c1-120
    echo ""
    echo "── last renewal log lines ──"
    tail -n 6 /var/log/letsencrypt/letsencrypt.log 2>/dev/null | cut -c1-140 || echo "  (no log)"
  ' 2>/dev/null
  echo ""
  echo "── certificate as served on the public URL ──"
  echo | openssl s_client -connect sifu-staging.tutorla.tech:443 -servername sifu-staging.tutorla.tech 2>/dev/null \
    | openssl x509 -noout -subject -issuer -dates 2>/dev/null || echo "  (could not read the served certificate)"
  exit 0
fi

echo "── Latest AutoSSL run ──"
ssh -o ConnectTimeout=10 -o BatchMode=yes "$SSH_ALIAS" "
  LATEST=\$(ls /var/cpanel/logs/autossl/ 2>/dev/null | sort | tail -1)
  if [[ -z \"\$LATEST\" ]]; then
    echo 'No AutoSSL logs found'
    exit 0
  fi
  echo \"Last run: \$LATEST\"
  echo ''
  echo '── st.admin.sifututor.my entries ──'
  grep 'st.admin.sifututor.my' /var/cpanel/logs/autossl/\"\$LATEST\"/txt 2>/dev/null | \
    grep -E 'error|warn|OK|expired|managed|DCV|document root' | head -20 || echo '  (none)'
  echo ''
  echo '── Certificate expiry in storage ──'
  CERT=~sifututortutorla/ssl/certs/st_admin_sifututor_my_b89ca_24e7b*.crt
  if ls \$CERT 2>/dev/null | head -1 > /dev/null 2>&1; then
    openssl x509 -noout -subject -dates -in \$(ls \$CERT | head -1) 2>/dev/null || echo '  (unreadable)'
  else
    echo '  No legacy st_admin cert in storage'
  fi
  echo ''
  echo '── Combined file cert expiry ──'
  COMBINED=/var/cpanel/ssl/apache_tls/st.admin.sifututor.my.sifu-tutor.tutorla.tech/combined
  if [[ -f \"\$COMBINED\" ]]; then
    openssl x509 -noout -subject -issuer -dates -in \"\$COMBINED\" 2>/dev/null
  else
    echo '  Combined file not found at expected path'
  fi
  echo ''
  echo '── acme.sh renewal config ──'
  ls /root/.acme.sh/st.admin.sifututor.my/ 2>/dev/null || echo '  acme.sh cert dir not found'
  echo ''
  crontab -l 2>/dev/null | grep acme || echo '  No acme.sh cron found'
" 2>/dev/null
