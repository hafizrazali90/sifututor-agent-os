#!/usr/bin/env bash
F=0; ok(){ printf "%-50s PASS%s\n" "$1" "${2:+ $2}"; }; bad(){ printf "%-50s FAIL%s\n" "$1" "${2:+ $2}"; F=$((F+1)); }
q(){ psql -X -qAt -v ON_ERROR_STOP=1 -c "$1" 2>/dev/null | head -1; }
refused(){ psql -X -qAt -v ON_ERROR_STOP=1 -c "$1" >/dev/null 2>&1 && return 1 || return 0; }
[ "$(q "SELECT current_database()")" = "ripple_suite_prod" ] && ok current_database || bad current_database
[ "$(q "SELECT current_user")" = "ripple_outreach_readonly" ] && ok current_user || bad current_user
[ "$(q "SELECT current_setting('transaction_read_only')")" = "on" ] && ok transaction_read_only || bad transaction_read_only
[ "$(q "SHOW search_path")" = "agent_read" ] && ok search_path_agent_read || bad search_path_agent_read
[ "$(q "SELECT current_setting('statement_timeout')")" = "30s" ] && ok statement_timeout || bad statement_timeout
for v in tutor_offer_restrictions app_settings crm_requests outreach_enrollment_work outreach_request_observations outreach_scheduling_intents outreach_operation_projections outreach_events outreach_material_revisions outreach_comparison_observations outreach_application_confirmations outreach_commands outreach_dispatch_grants outreach_discovery_sweeps crm_direct_contact_outcomes crm_fulfilment_cycles crm_request_candidates crm_request_candidate_outcome_events crm_parent_outcome_events crm_parent_outcome_tutor_states crm_recovery_events; do
  n=$(q "SELECT count(*) FROM $v"); case "$n" in ""|*[!0-9]*) bad "view_$v";; *) ok "view_$v" "rows=$n";; esac
done
[ "$(q "SELECT count(*) FROM information_schema.columns WHERE table_schema='agent_read' AND (column_name ILIKE '%phone%' OR column_name ILIKE '%email%' OR column_name ILIKE '%name%' OR column_name IN ('facts','application_evidence','body','desired','operation_context','provider_message_id','pause_reason','actor_id','remarks','accepted_facts'))")" = "0" ] && ok no_personal_columns || bad no_personal_columns
[ "$(q "SELECT (SELECT count(*) FROM crm_parent_outcome_events WHERE note IS NOT NULL OR recorded_by IS NOT NULL)+(SELECT count(*) FROM crm_parent_outcome_tutor_states WHERE note IS NOT NULL)+(SELECT count(*) FROM crm_recovery_events WHERE reason IS NOT NULL OR recorded_by IS NOT NULL OR decision ? 'note')+(SELECT count(*) FROM crm_request_candidate_outcome_events WHERE reason IS NOT NULL OR recorded_by IS NOT NULL)+(SELECT count(*) FROM tutor_offer_restrictions WHERE tutor_uid IS NOT NULL OR reason IS NOT NULL OR set_by_user_id IS NOT NULL OR lifted_by_user_id IS NOT NULL OR lifted_reason IS NOT NULL)")" = "0" ] && ok free_text_masked || bad free_text_masked
for t in crm_requests tutor_offer_restrictions outreach_submissions outreach_material_revisions users; do refused "SELECT 1 FROM public.$t LIMIT 1" && ok "base_refused_$t" || bad "base_refused_$t"; done
refused "SELECT facts FROM outreach_material_revisions LIMIT 1" && ok column_refused_facts || bad column_refused_facts
refused "INSERT INTO public.app_settings(key,value) VALUES ('x','1')" && ok dml_refused_insert || bad dml_refused_insert
refused "UPDATE public.crm_requests SET updated_at=now()" && ok dml_refused_update || bad dml_refused_update
refused "CREATE TABLE public.agent_lane_probe(id int)" && ok ddl_refused || bad ddl_refused
refused "SET default_transaction_read_only=off; INSERT INTO public.app_settings(key,value) VALUES ('x','1')" && ok write_refused_readonly_off || bad write_refused_readonly_off
refused "SET ROLE postgres" && ok set_role_refused || bad set_role_refused
[ "$(q "SELECT (rolsuper OR rolcreaterole OR rolcreatedb OR rolreplication OR rolbypassrls)::int FROM pg_roles WHERE rolname=current_user")" = "0" ] && ok role_attributes_minimal || bad role_attributes_minimal
[ "$(q "SELECT count(*) FROM information_schema.table_privileges WHERE grantee=current_user AND table_schema<>'agent_read'")" = "0" ] && ok grants_only_agent_read || bad grants_only_agent_read
printf "%-50s %s\n" failures "$F"; [ "$F" -eq 0 ]
