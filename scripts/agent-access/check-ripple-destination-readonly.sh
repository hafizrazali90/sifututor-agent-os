#!/usr/bin/env bash
# Safe verification for the `ripple-destination-readonly` lane (ripple-suite#1089).
#
# Proves the lane is reachable and that its privilege boundary holds, WITHOUT
# reading a single business row. Every line it prints is a fixed token or a
# count. It never prints a credential, a connection string, a business value, or
# a raw PostgreSQL error message: each failure is mapped to a fixed token so a
# provider error cannot smuggle data or a hostname into a transcript.
#
#   bash scripts/agent-access/check-ripple-destination-readonly.sh
#
# Exit 0 = every check as expected. Exit 1 = at least one check FAIL.
set -uo pipefail

CONF="$HOME/.config/sifututor/agent-access/ripple-destination-readonly.conf"
FAILURES=0

emit() { printf '%-46s %s\n' "$1" "$2"; }
ok()   { emit "$1" "PASS${2:+ $2}"; }
bad()  { emit "$1" "FAIL${2:+ $2}"; FAILURES=$((FAILURES + 1)); }

[ -f "$CONF" ] || { emit conf_present "FAIL missing"; exit 1; }
perms=$(stat -f '%Lp' "$CONF" 2>/dev/null || stat -c '%a' "$CONF")
[ "$perms" = "600" ] && ok conf_mode 0600 || bad conf_mode "$perms"
dperms=$(stat -f '%Lp' "$(dirname "$CONF")" 2>/dev/null || stat -c '%a' "$(dirname "$CONF")")
[ "$dperms" = "700" ] && ok conf_dir_mode 0700 || bad conf_dir_mode "$dperms"

# shellcheck disable=SC1090
set -a; . "$CONF"; set +a

SSH_HOST="$RIPPLE_DESTINATION_READONLY_SSH_HOST"
LPORT="$RIPPLE_DESTINATION_READONLY_LOCAL_PORT"
DB="$RIPPLE_DESTINATION_READONLY_DATABASE"
USR="$RIPPLE_DESTINATION_READONLY_USERNAME"

TUNNEL_PID=""
cleanup() { [ -n "$TUNNEL_PID" ] && kill "$TUNNEL_PID" 2>/dev/null; }
trap cleanup EXIT

if ! nc -z 127.0.0.1 "$LPORT" 2>/dev/null; then
  ssh -o ConnectTimeout=25 -o ExitOnForwardFailure=yes -N \
      -L "${LPORT}:${RIPPLE_DESTINATION_READONLY_REMOTE_HOST}:${RIPPLE_DESTINATION_READONLY_REMOTE_PORT}" \
      "$SSH_HOST" &
  TUNNEL_PID=$!
  for _ in 1 2 3 4 5 6 7 8 9 10; do
    nc -z 127.0.0.1 "$LPORT" 2>/dev/null && break
    sleep 1
  done
fi
nc -z 127.0.0.1 "$LPORT" 2>/dev/null && ok ssh_tunnel open || { bad ssh_tunnel closed; exit 1; }

export PGPASSWORD="$RIPPLE_DESTINATION_READONLY_PASSWORD"
export PGCONNECT_TIMEOUT=15

# Runs one statement and echoes ONLY its first output field, or the fixed token
# `ERR`. The provider's message is discarded, never surfaced.
q() { psql -h 127.0.0.1 -p "$LPORT" -U "$USR" -d "$DB" -X -qAt -v ON_ERROR_STOP=1 \
        -c "$1" 2>/dev/null | head -1 || true; }
# True when the statement is REFUSED. Used for every negative control.
refused() { psql -h 127.0.0.1 -p "$LPORT" -U "$USR" -d "$DB" -X -qAt -v ON_ERROR_STOP=1 \
              -c "$1" >/dev/null 2>&1 && return 1 || return 0; }

# --- identity and session mode -------------------------------------------
[ "$(q 'SELECT current_database()')" = "$DB" ] && ok current_database || bad current_database
[ "$(q 'SELECT current_user')" = "$USR" ]      && ok current_user      || bad current_user
[ "$(q "SELECT current_setting('transaction_read_only')")" = "on" ] \
  && ok transaction_read_only on || bad transaction_read_only
[ "$(q "SELECT current_setting('statement_timeout')")" = "30s" ] \
  && ok statement_timeout 30s || bad statement_timeout

# --- the four views are reachable (count only, never a row) ---------------
for v in v16_read_crm_requests v16_read_tutor_conduct v16_read_onboarding_prospects v16_read_effect_receipts; do
  n=$(q "SELECT count(*) FROM $v")
  case "$n" in ''|*[!0-9]*) bad "view_reachable_$v" ;; *) ok "view_reachable_$v" "rows=$n" ;; esac
done

# --- the receipts view must not outlive its reason to be empty ------------
# It is a shaped empty view only because `v16_business_effect_receipts` is
# absent. If that table ever lands, an empty view would silently report "no
# replays" forever, so this check fails closed the moment both are true.
base_present=$(q "SELECT (to_regclass('public.v16_business_effect_receipts') IS NOT NULL)::int")
view_bound=$(q "SELECT (pg_get_viewdef('public.v16_read_effect_receipts'::regclass) LIKE '%v16_business_effect_receipts%')::int")
if [ "$base_present" = "1" ] && [ "$view_bound" = "0" ]; then
  bad receipts_view_current "base_table_present_view_empty"
else
  ok receipts_view_current "base=$base_present bound=$view_bound"
fi

# --- each view exposes exactly the approved columns ------------------------
# The column list IS the control: a widened view would hand this role a personal column
# without any grant changing, so the check is on the served definition, not on the DDL file.
check_columns() {
  want="$2"
  got=$(q "SELECT string_agg(column_name, ',' ORDER BY ordinal_position) FROM information_schema.columns WHERE table_schema='public' AND table_name='$1'")
  [ "$got" = "$want" ] && ok "view_columns_$1" || bad "view_columns_$1" "unexpected"
}
check_columns v16_read_crm_requests "id,sims_request_id,current_sub_stage,sims_deleted_at,updated_at"
check_columns v16_read_tutor_conduct "id,tutor_id,incident_date,related_request_uid,deleted_at,updated_at"
check_columns v16_read_onboarding_prospects "id,phone,stage,version,updated_at"
check_columns v16_read_effect_receipts "effect_key"

# --- base tables are unreachable ------------------------------------------
for t in crm_requests tutor_conduct_records tutor_onboarding_prospects users staff; do
  refused "SELECT 1 FROM $t LIMIT 1" && ok "base_table_refused_$t" || bad "base_table_refused_$t"
done

# --- unlisted columns are unreachable -------------------------------------
refused "SELECT full_name FROM v16_read_onboarding_prospects LIMIT 1" \
  && ok column_refused_prospect_full_name || bad column_refused_prospect_full_name
refused "SELECT email FROM v16_read_onboarding_prospects LIMIT 1" \
  && ok column_refused_prospect_email || bad column_refused_prospect_email
refused "SELECT is_lost FROM v16_read_crm_requests LIMIT 1" \
  && ok column_refused_request_is_lost || bad column_refused_request_is_lost
refused "SELECT notes FROM v16_read_tutor_conduct LIMIT 1" \
  && ok column_refused_conduct_notes || bad column_refused_conduct_notes

# --- writes and DDL are refused -------------------------------------------
refused "INSERT INTO crm_requests (id) VALUES (0)"              && ok dml_refused_insert   || bad dml_refused_insert
refused "UPDATE crm_requests SET updated_at = NOW()"            && ok dml_refused_update   || bad dml_refused_update
refused "DELETE FROM crm_requests"                              && ok dml_refused_delete   || bad dml_refused_delete
refused "CREATE TABLE v16_lane_probe (id int)"                  && ok ddl_refused_create_table || bad ddl_refused_create_table
refused "CREATE SCHEMA v16_lane_probe"                          && ok ddl_refused_create_schema || bad ddl_refused_create_schema
refused "CREATE OR REPLACE VIEW v16_read_crm_requests AS SELECT 1 AS id" \
  && ok ddl_refused_replace_view || bad ddl_refused_replace_view
refused "SELECT 1; CREATE TABLE v16_lane_probe2 (id int)"       && ok multi_statement_refused || bad multi_statement_refused
refused "SELECT id FROM v16_read_crm_requests LIMIT 1 FOR UPDATE" && ok select_for_update_refused || bad select_for_update_refused

# --- the read-only GUC is defence in depth, not the boundary --------------
# `default_transaction_read_only` is USERSET in PostgreSQL, so this role CAN
# turn it off. That must not matter: with it off, a write is still refused on
# privileges. Proving that is stronger than claiming the GUC is immutable.
refused "SET default_transaction_read_only = off; INSERT INTO crm_requests (id) VALUES (0)" \
  && ok write_refused_with_readonly_off || bad write_refused_with_readonly_off

# --- no escalation ---------------------------------------------------------
refused "SET ROLE postgres"                     && ok set_role_postgres_refused || bad set_role_postgres_refused
refused "SET ROLE ripple_suite_prod_user"       && ok set_role_app_user_refused || bad set_role_app_user_refused
refused "ALTER ROLE ripple_destination_readonly SET default_transaction_read_only = off" \
  && ok alter_own_role_refused || bad alter_own_role_refused
refused "GRANT SELECT ON v16_read_crm_requests TO PUBLIC" && ok grant_refused || bad grant_refused
[ "$(q "SELECT count(*) FROM information_schema.table_privileges WHERE grantee=current_user")" = "4" ] \
  && ok grant_count 4 || bad grant_count
[ "$(q "SELECT count(*) FROM pg_auth_members m JOIN pg_roles r ON r.oid=m.member WHERE r.rolname=current_user")" = "0" ] \
  && ok role_memberships 0 || bad role_memberships
[ "$(q "SELECT (rolsuper OR rolcreaterole OR rolcreatedb OR rolreplication OR rolbypassrls)::int FROM pg_roles WHERE rolname=current_user")" = "0" ] \
  && ok role_attributes minimal || bad role_attributes

emit failures "$FAILURES"
[ "$FAILURES" -eq 0 ] || exit 1
