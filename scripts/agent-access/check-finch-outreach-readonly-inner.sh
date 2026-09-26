#!/usr/bin/env bash
# Inner checks for check-finch-outreach-readonly.sh; runs inside the lane runner.
F=0; ok(){ printf "%-50s PASS%s\n" "$1" "${2:+ $2}"; }; bad(){ printf "%-50s FAIL%s\n" "$1" "${2:+ $2}"; F=$((F+1)); }
q(){ sqlcmd -C -h -1 -W -b -Q "SET NOCOUNT ON; $1" 2>/dev/null | head -1 | tr -d "\r"; }
refused(){ sqlcmd -C -b -Q "SET NOCOUNT ON; $1" >/dev/null 2>&1 && return 1 || return 0; }
[ "$(q "SELECT DB_NAME()")" = "teaminbox" ] && ok current_database || bad current_database
[ "$(q "SELECT SUSER_SNAME()")" = "agent_outreach_readonly" ] && ok current_login || bad current_login
[ "$(q "SELECT IS_SRVROLEMEMBER('sysadmin')")" = "0" ] && ok not_sysadmin || bad not_sysadmin
[ "$(q "SELECT COUNT(*) FROM sys.database_role_members m JOIN sys.database_principals p ON p.principal_id=m.member_principal_id WHERE p.name=USER_NAME()")" = "0" ] && ok no_database_roles || bad no_database_roles
for v in outreach_operations outreach_jobs outreach_requests outreach_holds outreach_manual_evidence outreach_history_bindings outreach_legacy_pair_blocks outreach_legacy_request_holds outreach_policy outreach_daily_coverage ripple_broadcast_operations ripple_broadcast_recipients outreach_queue_status; do
  n=$(q "SELECT COUNT(*) FROM agent_read.$v"); case "$n" in ""|*[!0-9]*) bad "view_$v";; *) ok "view_$v" "rows=$n";; esac
done
[ "$(q "SELECT COUNT(*) FROM sys.columns c JOIN sys.views v ON v.object_id=c.object_id WHERE v.schema_id=SCHEMA_ID('agent_read') AND (c.name LIKE '%phone%' OR c.name IN ('content','body_json','recipient_id','metadata','provider_message_id','ripple_actor_name','ripple_request_uid','resolved_by','reviewed_by','session_id','last_error','provider_error_message'))")" = "0" ] && ok no_personal_columns || bad no_personal_columns
for t in wa_outreach_operations wa_message_queue wa_ripple_tutor_broadcast_recipients tickets; do refused "SELECT TOP 1 1 FROM dbo.$t" && ok "base_refused_$t" || bad "base_refused_$t"; done
refused "SELECT TOP 1 1 FROM finch_staging.dbo.wa_outreach_operations" && ok other_database_refused || bad other_database_refused
refused "UPDATE agent_read.outreach_requests SET paused=paused" && ok view_update_refused || bad view_update_refused
refused "DELETE FROM agent_read.outreach_jobs WHERE 1=0" && ok view_delete_refused || bad view_delete_refused
refused "INSERT INTO dbo.wa_outreach_holds(scope) VALUES ('x')" && ok base_insert_refused || bad base_insert_refused
refused "CREATE TABLE dbo.agent_lane_probe(id int)" && ok ddl_refused || bad ddl_refused
refused "EXECUTE AS USER = 'dbo'; SELECT 1" && ok impersonation_refused || bad impersonation_refused
printf "%-50s %s\n" failures "$F"; [ "$F" -eq 0 ]
