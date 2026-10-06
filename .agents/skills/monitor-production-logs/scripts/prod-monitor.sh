#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/home/sifututortutorla/public_html"
APP_USER="sifututortutorla"
# The app account's bare "php" is a web-style PHP on this server; use the command-line one.
PHP_BIN="/usr/local/bin/php"
SSH_ALIAS="${SIFUTUTOR_PROD_SSH:-production}"
BASE_URL="${SIFUTUTOR_PROD_URL:-https://sifu-tutor.tutorla.tech}"
WRITE_MARKER=0

for arg in "$@"; do
  case "$arg" in
    --marker) WRITE_MARKER=1 ;;
    -h|--help)
      cat <<'USAGE'
Usage: prod-monitor.sh [--marker]

Read-only production monitoring by default.
Every git and php command on the server runs as the application account
(sifututortutorla), never as root, so no root-owned file can appear in the
checkout. If that account cannot be used the script stops; it never falls
back to root.
--marker writes one harmless Laravel info log marker through the default channel.
USAGE
      exit 0
      ;;
    *) echo "Unknown argument: $arg" >&2; exit 2 ;;
  esac
done

echo "== Production runtime =="
# Git facts: run as the app account; --no-optional-locks keeps git from refreshing .git/index.
ssh "$SSH_ALIAS" bash -s -- "$APP_DIR" "$APP_USER" <<'REMOTE'
set -u
APP_DIR="$1"; APP_USER="$2"
cd "$APP_DIR" || { echo "ERROR: cannot enter app directory"; exit 1; }
if ! sudo -n -u "$APP_USER" true 2>/dev/null; then
  echo "ERROR: cannot run commands as $APP_USER; refusing to fall back to root"
  exit 3
fi
as_app() { sudo -n -u "$APP_USER" "$@"; }
echo "head=$(as_app git --no-optional-locks rev-parse --short HEAD 2>&1 | head -1)"
echo "branch=$(as_app git --no-optional-locks branch --show-current 2>&1 | head -1)"
if [ -f storage/framework/down ]; then echo "maintenance=true"; else echo "maintenance=false"; fi
echo "index_owner=$(stat -c %U .git/index)"
REMOTE

# Config facts: read the cached config file with plain php (no Laravel boot, nothing written).
# Prints booleans and non-secret values only; the Logtail token is reported as present or not.
ssh "$SSH_ALIAS" "cd '$APP_DIR' && sudo -n -u '$APP_USER' '$PHP_BIN' -- bootstrap/cache/config.php" <<'PHP'
<?php
$f = $argv[1] ?? '';
if (!is_file($f)) { echo "ERROR: config cache missing\n"; exit(1); }
$c = require $f;
$logtail = $c['logging']['channels']['logtail'] ?? [];
echo json_encode([
    'env' => $c['app']['env'] ?? null,
    'debug' => $c['app']['debug'] ?? null,
    'default_log_channel' => $c['logging']['default'] ?? null,
    'stack_channels' => $c['logging']['channels']['stack']['channels'] ?? null,
    'logtail_channel_defined' => array_key_exists('logtail', $c['logging']['channels'] ?? []),
    'logtail_token_present' => !empty($logtail['handler_with']['sourceToken'] ?? null),
    'logtail_endpoint' => $logtail['handler_with']['endpoint'] ?? null,
    'sentry_config_exists' => is_file('config/sentry.php'),
    'sentry_dsn_present' => !empty($c['sentry']['dsn'] ?? null),
], JSON_PRETTY_PRINT), "\n";
PHP
echo

echo "== Git status =="
ssh "$SSH_ALIAS" "cd '$APP_DIR' && sudo -n -u '$APP_USER' git --no-optional-locks status --short --branch"
echo

echo "== Public route smoke =="
curl -sS -i "$BASE_URL/api/tutor/class/stuck-classes" | sed -n '1,24p'
echo
curl -sS -i -X POST "$BASE_URL/api/tutor/class/mark-attended" | sed -n '1,24p'
echo

if [[ "$WRITE_MARKER" == "1" ]]; then
  MARKER="codex-prod-monitor-marker-$(date -u +%Y%m%dT%H%M%SZ)"
  echo "== Writing marker =="
  ssh "$SSH_ALIAS" "cd '$APP_DIR' && sudo -n -u '$APP_USER' env MARKER='$MARKER' '$PHP_BIN' artisan tinker --execute='\\Illuminate\\Support\\Facades\\Log::info(getenv(\"MARKER\"), [\"commit\" => trim(shell_exec(\"git rev-parse --short HEAD\")), \"channel\" => config(\"logging.default\")]); echo getenv(\"MARKER\");'"
  echo
fi

echo "== Laravel log regression scan =="
ssh "$SSH_ALIAS" "cd '$APP_DIR' && LOG_FILE=\$(ls -1t storage/logs/laravel-*.log 2>/dev/null | head -1); echo \"file=\$LOG_FILE\"; tail -n 400 \"\$LOG_FILE\" | grep -E 'production\\.(ERROR|CRITICAL)|Data truncated|status.*failed|undefined method App\\\\Services\\\\ClassService::getStuckClasses|protected method.*verifyBundledPayment|codex-prod-monitor-marker|codex-prod-stack-logtail-verify' | tail -80 || true"
echo

echo "== BetterStack/Sentry access helper =="
if [[ -x "$HOME/.config/sifututor/check-monitoring-access.sh" ]]; then
  bash "$HOME/.config/sifututor/check-monitoring-access.sh"
else
  echo "helper_missing=$HOME/.config/sifututor/check-monitoring-access.sh"
fi
