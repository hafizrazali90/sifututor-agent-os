#!/usr/bin/env bash
# Verify the narrow Ripple production destination reader without printing
# credentials, connection strings, business rows, or raw provider errors.
set -uo pipefail

CONF="$HOME/.config/sifututor/agent-access/ripple-destination-readonly.conf"
FAILURES=0

emit() { printf '%-46s %s\n' "$1" "$2"; }
ok()   { emit "$1" "PASS${2:+ $2}"; }
bad()  { emit "$1" "FAIL${2:+ $2}"; FAILURES=$((FAILURES + 1)); }

[ -f "$CONF" ] || { emit conf_present "FAIL missing"; exit 1; }
perms=$(stat -f '%Lp' "$CONF" 2>/dev/null || stat -c '%a' "$CONF")
[ "$perms" = "600" ] && ok conf_mode 0600 || bad conf_mode "$perms"

# shellcheck disable=SC1090
set -a; . "$CONF"; set +a

SSH_HOST="$RIPPLE_DESTINATION_READONLY_SSH_HOST"
LPORT="$RIPPLE_DESTINATION_READONLY_LOCAL_PORT"
DB="$RIPPLE_DESTINATION_READONLY_DATABASE"
USR="$RIPPLE_DESTINATION_READONLY_USERNAME"
TUNNEL_PID=""

cleanup() { [ -n "$TUNNEL_PID" ] && kill "$TUNNEL_PID" 2>/dev/null || true; }
trap cleanup EXIT

if nc -z 127.0.0.1 "$LPORT" 2>/dev/null; then
  emit ssh_tunnel "FAIL local_port_busy"
  exit 1
fi

ssh -o BatchMode=yes -o ConnectTimeout=25 -o ExitOnForwardFailure=yes -N \
    -L "${LPORT}:${RIPPLE_DESTINATION_READONLY_REMOTE_HOST}:${RIPPLE_DESTINATION_READONLY_REMOTE_PORT}" \
    "$SSH_HOST" >/dev/null 2>&1 &
TUNNEL_PID=$!
for _ in 1 2 3 4 5 6 7 8 9 10; do
  nc -z 127.0.0.1 "$LPORT" 2>/dev/null && break
  kill -0 "$TUNNEL_PID" 2>/dev/null || break
  sleep 1
done
nc -z 127.0.0.1 "$LPORT" 2>/dev/null && ok ssh_tunnel open || { bad ssh_tunnel closed; exit 1; }

export PGPASSWORD="$RIPPLE_DESTINATION_READONLY_PASSWORD"
export PGCONNECT_TIMEOUT=15

q() {
  psql -h 127.0.0.1 -p "$LPORT" -U "$USR" -d "$DB" -X -qAt \
    -v ON_ERROR_STOP=1 -c "$1" 2>/dev/null | head -1 || true
}
refused() {
  psql -h 127.0.0.1 -p "$LPORT" -U "$USR" -d "$DB" -X -qAt \
    -v ON_ERROR_STOP=1 -c "$1" >/dev/null 2>&1 && return 1 || return 0
}

[ "$(q 'SELECT current_database()')" = "$DB" ] && ok current_database || bad current_database
[ "$(q 'SELECT current_user')" = "$USR" ] && ok current_user || bad current_user
[ "$(q "SELECT current_setting('transaction_read_only')")" = "on" ] \
  && ok transaction_read_only on || bad transaction_read_only
[ "$(q "SELECT current_setting('statement_timeout')")" = "30s" ] \
  && ok statement_timeout 30s || bad statement_timeout

for view in v16_read_crm_requests v16_read_tutor_conduct v16_read_onboarding_prospects v16_read_effect_receipts; do
  count=$(q "SELECT count(*) FROM $view")
  case "$count" in
    ''|*[!0-9]*) bad "view_reachable_$view" ;;
    *) ok "view_reachable_$view" "rows=$count" ;;
  esac
done

check_columns() {
  expected="$2"
  actual=$(q "SELECT string_agg(column_name, ',' ORDER BY ordinal_position) FROM information_schema.columns WHERE table_schema='public' AND table_name='$1'")
  [ "$actual" = "$expected" ] && ok "view_columns_$1" || bad "view_columns_$1" unexpected
}
check_columns v16_read_crm_requests "id,sims_request_id,current_sub_stage,sims_deleted_at,updated_at"
check_columns v16_read_tutor_conduct "id,tutor_id,incident_date,related_request_uid,deleted_at,updated_at"
check_columns v16_read_onboarding_prospects "id,phone,stage,version,updated_at"
check_columns v16_read_effect_receipts "effect_key"

for table in crm_requests tutor_conduct_records tutor_onboarding_prospects users staff; do
  refused "SELECT 1 FROM $table LIMIT 1" && ok "base_table_refused_$table" || bad "base_table_refused_$table"
done

refused "SELECT full_name FROM v16_read_onboarding_prospects LIMIT 1" \
  && ok column_refused_prospect_full_name || bad column_refused_prospect_full_name
refused "SELECT email FROM v16_read_onboarding_prospects LIMIT 1" \
  && ok column_refused_prospect_email || bad column_refused_prospect_email
refused "SELECT is_lost FROM v16_read_crm_requests LIMIT 1" \
  && ok column_refused_request_is_lost || bad column_refused_request_is_lost
refused "SELECT notes FROM v16_read_tutor_conduct LIMIT 1" \
  && ok column_refused_conduct_notes || bad column_refused_conduct_notes

refused "INSERT INTO crm_requests (id) VALUES (0)" && ok dml_refused_insert || bad dml_refused_insert
refused "UPDATE crm_requests SET updated_at = NOW()" && ok dml_refused_update || bad dml_refused_update
refused "DELETE FROM crm_requests" && ok dml_refused_delete || bad dml_refused_delete
refused "CREATE TABLE v16_lane_probe (id int)" && ok ddl_refused_create_table || bad ddl_refused_create_table
refused "CREATE SCHEMA v16_lane_probe" && ok ddl_refused_create_schema || bad ddl_refused_create_schema
refused "SELECT id FROM v16_read_crm_requests LIMIT 1 FOR UPDATE" \
  && ok select_for_update_refused || bad select_for_update_refused
refused "SET default_transaction_read_only = off; INSERT INTO crm_requests (id) VALUES (0)" \
  && ok write_refused_with_readonly_off || bad write_refused_with_readonly_off
refused "SET ROLE postgres" && ok set_role_postgres_refused || bad set_role_postgres_refused
refused "GRANT SELECT ON v16_read_crm_requests TO PUBLIC" && ok grant_refused || bad grant_refused

[ "$(q "SELECT count(*) FROM information_schema.table_privileges WHERE grantee=current_user")" = "4" ] \
  && ok grant_count 4 || bad grant_count
[ "$(q "SELECT count(*) FROM pg_auth_members m JOIN pg_roles r ON r.oid=m.member WHERE r.rolname=current_user")" = "0" ] \
  && ok role_memberships 0 || bad role_memberships
[ "$(q "SELECT (rolsuper OR rolcreaterole OR rolcreatedb OR rolreplication OR rolbypassrls)::int FROM pg_roles WHERE rolname=current_user")" = "0" ] \
  && ok role_attributes minimal || bad role_attributes

base_present=$(q "SELECT (to_regclass('public.v16_business_effect_receipts') IS NOT NULL)::int")
view_bound=$(q "SELECT (pg_get_viewdef('public.v16_read_effect_receipts'::regclass) LIKE '%v16_business_effect_receipts%')::int")
if [ "$base_present" = "1" ] && [ "$view_bound" = "0" ]; then
  bad receipts_view_current stale
else
  ok receipts_view_current "base=$base_present bound=$view_bound"
fi

emit failures "$FAILURES"
[ "$FAILURES" -eq 0 ]
