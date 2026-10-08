#!/usr/bin/env bash
# Lane 40: read-only SQL against Ripple production (ripple_suite_prod, local PostgreSQL on the KVM8 box).
# Runs over `ssh staging` as the postgres OS account, so no password or connection string is handled here.
# The session is forced read-only with a 60 second statement timeout. The text guard below only blocks the
# ways out of read-only mode and server file reads; it does not refuse ordinary queries.
#
# Usage:  scripts/agent-access/ripple-prod-sql-readonly.sh "SELECT count(*) FROM crm_leads"
#         scripts/agent-access/ripple-prod-sql-readonly.sh < query.sql
# Env:    RIPPLE_PROD_SQL_FORMAT=csv (default) | table      RIPPLE_PROD_SQL_DRY_RUN=1 (check the guard, no ssh)

set -euo pipefail

DB="${RIPPLE_PROD_DB:-ripple_suite_prod}"
ALIAS_NAME="${RIPPLE_PROD_SQL_SSH_ALIAS:-staging}"
FORMAT="${RIPPLE_PROD_SQL_FORMAT:-csv}"

if [[ ! "$DB" =~ ^[a-z0-9_]+$ || ! "$ALIAS_NAME" =~ ^[a-z0-9_-]+$ ]]; then
  echo "refused: bad database or ssh alias name" >&2
  exit 2
fi

if [[ $# -ge 1 ]]; then SQL="$1"; else SQL="$(cat)"; fi

# Normalise: one optional trailing semicolon, lowercase copy for matching.
SQL="${SQL#"${SQL%%[![:space:]]*}"}"
SQL="${SQL%"${SQL##*[![:space:]]}"}"
SQL="${SQL%;}"
LOWER="$(printf '%s' "$SQL" | tr '[:upper:]' '[:lower:]')"

refuse() { echo "refused: $1" >&2; exit 3; }

[[ -n "$SQL" ]] || refuse "empty query"
[[ "$LOWER" != *";"* ]] || refuse "one statement per call (remove the extra semicolon)"
[[ "$LOWER" =~ ^(select|with|explain|show|table|values)([^a-z0-9_]|$) ]] || refuse "only select, with, explain, show, table or values queries"

# Ways out of read-only mode, transaction control, and server file or program access.
ESCAPES='read[[:space:]]+write|set[[:space:]]+(session|local|role|transaction)|reset[[:space:]]|(^|[^a-z_])(begin|commit|rollback|savepoint)([^a-z_]|$)|(^|[^a-z_])copy([^a-z_]|$)|pg_read_file|pg_read_binary_file|pg_ls_dir|pg_stat_file|lo_import|lo_export|dblink|pg_terminate_backend|pg_cancel_backend|pg_reload_conf|set_config[[:space:]]*\(|pg_read_server_files'
if [[ "$LOWER" =~ $ESCAPES ]]; then
  refuse "this would leave read-only mode or read server files; use a plain query"
fi

if [[ "${RIPPLE_PROD_SQL_DRY_RUN:-0}" == "1" ]]; then
  echo "accepted"
  exit 0
fi

case "$FORMAT" in
  csv) FLAGS="--csv" ;;
  table) FLAGS="" ;;
  *) echo "refused: RIPPLE_PROD_SQL_FORMAT must be csv or table" >&2; exit 2 ;;
esac

printf '%s;\n' "$SQL" | ssh -o BatchMode=yes "$ALIAS_NAME" \
  "runuser -u postgres -- env PGOPTIONS='-c default_transaction_read_only=on -c statement_timeout=60000' psql -X -q -d $DB -v ON_ERROR_STOP=1 $FLAGS -f -"
