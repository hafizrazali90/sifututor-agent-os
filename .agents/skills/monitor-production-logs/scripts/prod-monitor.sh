#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/home/sifututortutorla/public_html"
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
--marker writes one harmless Laravel info log marker through the default channel.
USAGE
      exit 0
      ;;
    *) echo "Unknown argument: $arg" >&2; exit 2 ;;
  esac
done

echo "== Production runtime =="
ssh "$SSH_ALIAS" "cd '$APP_DIR' && php artisan tinker --execute='echo json_encode([
    \"head\" => trim(shell_exec(\"git rev-parse --short HEAD\")),
    \"branch\" => trim(shell_exec(\"git branch --show-current\")),
    \"env\" => app()->environment(),
    \"maintenance\" => app()->isDownForMaintenance(),
    \"debug\" => config(\"app.debug\"),
    \"default_log_channel\" => config(\"logging.default\"),
    \"stack_channels\" => config(\"logging.channels.stack.channels\"),
    \"logtail_channel_defined\" => array_key_exists(\"logtail\", config(\"logging.channels\", [])),
    \"logtail_token_present\" => filled(data_get(config(\"logging.channels.logtail\"), \"handler_with.sourceToken\")),
    \"logtail_endpoint\" => data_get(config(\"logging.channels.logtail\"), \"handler_with.endpoint\"),
    \"sentry_config_exists\" => file_exists(config_path(\"sentry.php\")),
    \"sentry_dsn_present\" => filled(config(\"sentry.dsn\")),
], JSON_PRETTY_PRINT);'"
echo

echo "== Git status =="
ssh "$SSH_ALIAS" "cd '$APP_DIR' && git status --short --branch"
echo

echo "== Public route smoke =="
curl -sS -i "$BASE_URL/api/tutor/class/stuck-classes" | sed -n '1,24p'
echo
curl -sS -i -X POST "$BASE_URL/api/tutor/class/mark-attended" | sed -n '1,24p'
echo

if [[ "$WRITE_MARKER" == "1" ]]; then
  MARKER="codex-prod-monitor-marker-$(date -u +%Y%m%dT%H%M%SZ)"
  echo "== Writing marker =="
  ssh "$SSH_ALIAS" "cd '$APP_DIR' && MARKER='$MARKER' php artisan tinker --execute='\\Illuminate\\Support\\Facades\\Log::info(getenv(\"MARKER\"), [\"commit\" => trim(shell_exec(\"git rev-parse --short HEAD\")), \"channel\" => config(\"logging.default\")]); echo getenv(\"MARKER\");'"
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
