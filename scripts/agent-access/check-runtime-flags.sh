#!/usr/bin/env bash
# Print the effective production feature flags for SIMS or Ripple, read-only.
# Safe: prints only boolean flag values and a few named mode values. Any other
# value is replaced by "<hidden>". Never prints secrets, URLs, or whole files.
# Usage: ./scripts/agent-access/check-runtime-flags.sh sims|ripple
# Diff two runs to prove a deploy or flag change touched nothing else.

set -euo pipefail

TARGET="${1:-}"
SIMS_ALIAS="production"
SIMS_ROOT="/home/sifututortutorla/public_html"
RIPPLE_ALIAS="staging"   # Ripple production runs on KVM8 (staging SSH alias)
RIPPLE_FLAG_FILE="/etc/prod-env/ripple-suite.env"
RIPPLE_DB="ripple_suite_prod"

sims_flags() {
  ssh -o BatchMode=yes -o ConnectTimeout=15 "$SIMS_ALIAS" \
    "cd '$SIMS_ROOT' && git rev-parse --short HEAD && php -- bootstrap/cache/config.php" <<'PHP'
<?php
$f = $argv[1] ?? '';
if (!is_file($f)) { echo "NO_CONFIG_CACHE\n"; exit; }
$c = require $f;
$out = [];
$walk = function ($v, $p) use (&$walk, &$out) {
  if (is_array($v)) { foreach ($v as $k => $x) $walk($x, $p === '' ? (string) $k : "$p.$k"); return; }
  if (is_bool($v)) $out[$p] = $v ? 'ON' : 'off';
};
foreach (['sims', 'features', 'phone-identity', 'public-links', 'bonus'] as $root) $walk($c[$root] ?? [], $root);
$walk($c['services']['ripple'] ?? [], 'services.ripple');
foreach (['sims.legacy_deduction_mode', 'sims.billing.tutor_commitment_fee_eligibility_mode'] as $k) {
  $v = $c; foreach (explode('.', $k) as $s) { $v = is_array($v) && array_key_exists($s, $v) ? $v[$s] : null; }
  $out[$k] = is_string($v) && preg_match('/^[a-z_]{1,30}$/', $v) ? $v : '<hidden>';
}
ksort($out);
foreach ($out as $k => $v) echo "$k=$v\n";
PHP
}

ripple_flags() {
  # Named keys only; values outside the safe set are hidden.
  local keys='TUTOR_OUTREACH_WORKER_ENABLED|TUTOR_OUTREACH_REQUEST_FIRST_ENABLED|TUTOR_OUTREACH_OFFER_LINKS_ENABLED|TUTOR_OUTREACH_EXECUTION|FINCH_TUTOR_BROADCAST_ENABLED|FINCH_TUTOR_ACTIVITY_SYNC_ENABLED|FINCH_TUTOR_ACTIVITY_UI_ENABLED|FINCH_WHATSAPP_ACTIVITY_SYNC_ENABLED|FINCH_CONTEXT_ENABLED|WORKFORCE_PERMISSION_GOVERNANCE_ENABLED|USE_NEON|USE_MOCK_DATA'
  ssh -o BatchMode=yes -o ConnectTimeout=15 "$RIPPLE_ALIAS" "
    git -C /opt/deploy/ripple-suite/repo-prod rev-parse --short HEAD 2>/dev/null || echo 'sha=unknown'
    sudo -n grep -E '^($keys)=' '$RIPPLE_FLAG_FILE' \
      | sed -E 's/^([A-Z_]+)=\"?(true|false|legacy|pgboss|0|1)\"?\$/env.\1=\2/; t; s/^([A-Z_]+)=.*/env.\1=<hidden>/' | sort
    for k in \$(echo '$keys' | tr '|' ' '); do sudo -n grep -q \"^\$k=\" '$RIPPLE_FLAG_FILE' || echo \"env.\$k=unset\"; done
    q() { sudo -n -u postgres psql -d '$RIPPLE_DB' -AtF '=' -c \"\$1\"; }
    q \"SELECT 'db.capability.' || flag_key, CASE WHEN enabled THEN 'ON' ELSE 'off' END FROM integration_capability_flags ORDER BY 1\"
    q \"SELECT 'db.crm_settings.' || key, value::text FROM crm_settings WHERE key IN ('polling_enabled','crm_v3_create_enabled','first_class_monitoring_enabled') ORDER BY 1\"
    q \"SELECT 'db.tutor_onboarding.enabled', value::text FROM tutor_onboarding_settings WHERE key = 'enabled'\"
    q \"SELECT 'db.workforce.enforcement_enabled', enforcement_enabled::text FROM workforce_access_projection_state\"
    q \"SELECT 'db.knowledge_packs.kill_switch_engaged_count', count(*) FILTER (WHERE kill_switch_engaged)::text FROM knowledge_packs\"
    ls /opt/deploy/ripple-suite/.outreach-pause-* >/dev/null 2>&1 && echo 'file.outreach_pause_marker=present' || echo 'file.outreach_pause_marker=absent'
  "
}

case "$TARGET" in
  sims) sims_flags ;;
  ripple) ripple_flags ;;
  *) echo "usage: $0 sims|ripple" >&2; exit 2 ;;
esac
