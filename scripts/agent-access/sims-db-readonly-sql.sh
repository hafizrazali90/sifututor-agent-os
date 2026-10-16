#!/usr/bin/env bash
# Lane 4 helper: read-only SQL against SIMS production through the existing read-only account.
# Same idea as ripple-prod-sql-readonly.sh: one SELECT, SHOW, EXPLAIN or DESCRIBE per call, nothing else.
# The account itself is SELECT-only; this text guard is a second layer. No credential is printed.
#
# Usage:  scripts/agent-access/sims-db-readonly-sql.sh "SELECT COUNT(*) FROM notifications"
#         scripts/agent-access/sims-db-readonly-sql.sh < query.sql
# Rules:  do not print PII columns (emails, phones, IC numbers, names). Aggregate first.

set -euo pipefail

CONF_FILE="${HOME}/.config/sifututor/agent-access/database-readonly.conf"
[[ -f "$CONF_FILE" ]] || { echo "refused: the read-only conf file is missing" >&2; exit 2; }
# shellcheck disable=SC1090
source "$CONF_FILE"

if [[ $# -ge 1 ]]; then SQL="$1"; else SQL="$(cat)"; fi
SQL="${SQL#"${SQL%%[![:space:]]*}"}"
SQL="${SQL%"${SQL##*[![:space:]]}"}"
SQL="${SQL%;}"
LOWER="$(printf '%s' "$SQL" | tr '[:upper:]' '[:lower:]')"

refuse() { echo "refused: $1" >&2; exit 3; }

[[ -n "$SQL" ]] || refuse "empty query"
[[ "$LOWER" != *";"* ]] || refuse "one statement per call"
[[ "$LOWER" =~ ^(select|with|explain|show|describe|desc)([^a-z0-9_]|$) ]] || refuse "only select, with, explain, show or describe"
ESCAPES='into[[:space:]]+(outfile|dumpfile)|load_file|load[[:space:]]+data|(^|[^a-z_])(insert|update|delete|drop|alter|truncate|create|grant|revoke|replace|call|lock|unlock|set|kill|handler)[[:space:]]|sleep[[:space:]]*\(|benchmark[[:space:]]*\(|for[[:space:]]+update|lock[[:space:]]+in[[:space:]]+share'
if [[ "$LOWER" =~ $ESCAPES ]]; then
  refuse "this could write, lock, read files or stall the server; use a plain query"
fi

# shellcheck source=lib/mysql-client.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib/mysql-client.sh"
MYSQL="$(sifu_mysql_client)" || { echo "refused: no mysql 8.x client found (brew install mysql@8.4)" >&2; exit 2; }

if [[ "${SIMS_DB_SQL_DRY_RUN:-}" == "1" ]]; then echo "ok: guard accepted the query (dry run, no connection)"; exit 0; fi

"$MYSQL" -h "$SIMS_DB_READONLY_HOST" -P "$SIMS_DB_READONLY_PORT" -u "$SIMS_DB_READONLY_USERNAME" -p"$SIMS_DB_READONLY_PASSWORD" \
  "$SIMS_DB_READONLY_DATABASE" --connect-timeout=8 --batch --column-names \
  --init-command="SET SESSION MAX_EXECUTION_TIME=30000" -e "$SQL" 2>&1 | grep -v 'Using a password on the command line' || true
