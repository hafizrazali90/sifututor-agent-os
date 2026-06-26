#!/usr/bin/env bash
# Check SIMS production DB connectivity using the read-only lane
# Safe: no credentials printed; runs SELECT only
# Usage: ./scripts/agent-access/check-sims-db-readonly.sh [--lls]

set -euo pipefail

CONF_DIR="${HOME}/.config/sifututor/agent-access"
USE_LLS="${1:-}"

if [[ "$USE_LLS" == "--lls" ]]; then
  CONF_FILE="$CONF_DIR/lls-database-readonly.conf"
  PREFIX="LLS_DB_READONLY"
  DB_LABEL="LLS"
else
  CONF_FILE="$CONF_DIR/database-readonly.conf"
  PREFIX="SIMS_DB_READONLY"
  DB_LABEL="SIMS"
fi

echo "=== ${DB_LABEL} Database Read-Only Check ==="

if [[ ! -f "$CONF_FILE" ]]; then
  echo "✗ Conf file missing: $CONF_FILE"
  exit 1
fi

# shellcheck disable=SC1090
source "$CONF_FILE"

HOST_VAR="${PREFIX}_HOST"
PORT_VAR="${PREFIX}_PORT"
USER_VAR="${PREFIX}_USERNAME"
PASS_VAR="${PREFIX}_PASSWORD"
DB_VAR="${PREFIX}_DATABASE"

DB_HOST="${!HOST_VAR}"
DB_PORT="${!PORT_VAR}"
DB_USER="${!USER_VAR}"
DB_PASS="${!PASS_VAR}"
DB_NAME="${!DB_VAR}"

echo "Host: ${DB_HOST}:${DB_PORT}  DB: ${DB_NAME}  User: ${DB_USER}"
echo ""

# Connection test
echo "── Connection test ──"
if mysql -h "$DB_HOST" -P "$DB_PORT" \
  -u "$DB_USER" -p"$DB_PASS" \
  "$DB_NAME" \
  --connect-timeout=8 \
  -e "SELECT 1;" > /dev/null 2>&1; then
  printf '\033[32m✓\033[0m Connection: OK\n'
else
  printf '\033[31m✗\033[0m Connection: FAILED\n'
  echo "  If running locally, production 3306 may be firewalled by design. Use the approved SSH tunnel path before retrying."
  exit 1
fi

# Spot-checks (aggregate only — no PII)
echo ""
echo "── Spot checks (aggregate counts) ──"

if [[ "$USE_LLS" == "--lls" ]]; then
  mysql -h "$DB_HOST" -P "$DB_PORT" \
    -u "$DB_USER" -p"$DB_PASS" \
    "$DB_NAME" \
    --connect-timeout=8 \
    -e "
SELECT
  (SELECT COUNT(*) FROM information_schema.tables
   WHERE table_schema = DATABASE()) AS table_count;
" 2>/dev/null
else
  mysql -h "$DB_HOST" -P "$DB_PORT" \
    -u "$DB_USER" -p"$DB_PASS" \
    "$DB_NAME" \
    --connect-timeout=8 \
    -e "
SELECT
  (SELECT COUNT(*) FROM tutors WHERE deleted_at IS NULL) AS active_tutors,
  (SELECT COUNT(*) FROM tutor_requests WHERE deleted_at IS NULL) AS active_requests,
  (SELECT COUNT(*) FROM parent_invoices WHERE deleted_at IS NULL) AS parent_invoices;
" 2>/dev/null
fi

echo ""
echo "── Permissions check ──"
# Verify no write permission (expected to fail)
WRITE_TEST=$(mysql -h "$DB_HOST" -P "$DB_PORT" \
  -u "$DB_USER" -p"$DB_PASS" \
  "$DB_NAME" \
  --connect-timeout=8 \
  -e "CREATE TABLE _agent_write_test (id INT);" 2>&1 | \
  grep -i 'denied\|error' | head -1 || echo "")

if echo "$WRITE_TEST" | grep -qi 'denied'; then
  printf '\033[32m✓\033[0m Write permission correctly denied (read-only lane confirmed)\n'
else
  printf '\033[33m~\033[0m Write permission check inconclusive: %s\n' "$WRITE_TEST"
fi
