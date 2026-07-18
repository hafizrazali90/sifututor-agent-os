#!/usr/bin/env bash
# Check cPanel AutoSSL status on the production server
# Sources: server-ssh.conf (SSH alias)
# Safe: reads log files only; no secrets printed
# Usage: ./scripts/agent-access/check-cpanel-autossl.sh [--staging]

set -euo pipefail

CONF_DIR="${HOME}/.config/sifututor/agent-access"

echo "=== cPanel AutoSSL Status Check ==="

TARGET="${1:-}"
if [[ "$TARGET" == "--staging" ]]; then
  SSH_ALIAS="webvoyager"
  SERVER_LABEL="WebVoyager staging (151.246.1.218)"
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
