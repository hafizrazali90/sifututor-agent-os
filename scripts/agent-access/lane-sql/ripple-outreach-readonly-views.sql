-- Ripple production (ripple_suite_prod) read-only views for the agent lane
-- `ripple-outreach-readonly`. Views keep the source table names inside schema
-- agent_read and the reader's search_path is agent_read only, so unchanged
-- application read queries run against them. No parent addresses, message
-- bodies, phone numbers, staff identities or free-text reasons are exposed.
BEGIN;
CREATE SCHEMA IF NOT EXISTS agent_read AUTHORIZATION postgres;
DROP VIEW IF EXISTS agent_read.tutor_offer_restrictions;
CREATE VIEW agent_read.tutor_offer_restrictions AS
  SELECT id, tutor_id, NULL::varchar AS tutor_uid, policy, NULL::text AS reason, related_conduct_id, source,
         NULL::integer AS set_by_user_id, set_at, NULL::integer AS lifted_by_user_id, lifted_at, NULL::text AS lifted_reason
  FROM public.tutor_offer_restrictions;
CREATE OR REPLACE VIEW agent_read.app_settings AS
  SELECT key, value, updated_at FROM public.app_settings
  WHERE key IN ('general_exclude_test_data', 'level_categories', 'algorithm_config');
CREATE OR REPLACE VIEW agent_read.crm_requests AS
  SELECT id, sims_request_id, sims_deleted_at FROM public.crm_requests;
CREATE OR REPLACE VIEW agent_read.outreach_enrollment_work AS
  SELECT company_guid, sims_request_id, state, reason, first_seen_at, last_seen_at, next_attempt_at, attempt_count,
         initial_batch_id, initial_revision_hash, history_checked_at, managed_safety_ready, registered_at, updated_at
  FROM public.outreach_enrollment_work;
CREATE OR REPLACE VIEW agent_read.outreach_request_observations AS
  SELECT company_guid, sims_request_id, crm_request_id, enrolled_at, history_complete, observed_revision,
         observed_revision_hash, facts_read_at, facts_unavailable_reason, pause_intent, control_version,
         acknowledged_control_version, due_at, updated_at, lease_owner, lease_expires_at, enrollment_revision,
         enrollment_revision_hash
  FROM public.outreach_request_observations;
CREATE OR REPLACE VIEW agent_read.outreach_scheduling_intents AS
  SELECT company_guid, batch_intent_id, sims_request_id, sequence, revision_hash, policy_version, state_version,
         wakeup_at, created_at
  FROM public.outreach_scheduling_intents;
CREATE OR REPLACE VIEW agent_read.outreach_operation_projections AS
  SELECT company_guid, operation_id, sims_tutor_id, contact_digest, origin, state, state_version, jobs, accepted_at,
         first_delivered_at, uncertain, cost_micros, cost_currency, cost_basis, observed_at, cost_conflict, state_conflict
  FROM public.outreach_operation_projections;
CREATE OR REPLACE VIEW agent_read.outreach_events AS
  SELECT company_guid, event_id, operation_id, type, event_at, observed_at, cost_micros, cost_currency, cost_basis,
         received_at, state_version, event_time_basis
  FROM public.outreach_events;
CREATE OR REPLACE VIEW agent_read.outreach_material_revisions AS
  SELECT company_guid, sims_request_id, revision, revision_hash, observed_at, source_observed_at
  FROM public.outreach_material_revisions;
CREATE OR REPLACE VIEW agent_read.outreach_comparison_observations AS
  SELECT * FROM public.outreach_comparison_observations;
CREATE OR REPLACE VIEW agent_read.outreach_application_confirmations AS
  SELECT company_guid, sims_request_id, sims_tutor_id, application_activity_id, confirmed_revision_hash, operation_id,
         recorded_at, confirmed_occurrence
  FROM public.outreach_application_confirmations;
CREATE OR REPLACE VIEW agent_read.outreach_commands AS
  SELECT company_guid, command_id, scope, sims_request_id, action, expected_version, status, effective_version,
         rejection_reason, created_at, acknowledged_at
  FROM public.outreach_commands;
CREATE OR REPLACE VIEW agent_read.outreach_dispatch_grants AS
  SELECT company_guid, operation_id, claim_generation, grant_id, attempt, decision, reason, expires_at, issued_at
  FROM public.outreach_dispatch_grants;
CREATE OR REPLACE VIEW agent_read.outreach_discovery_sweeps AS
  SELECT * FROM public.outreach_discovery_sweeps;
DROP VIEW IF EXISTS agent_read.crm_direct_contact_outcomes;
CREATE VIEW agent_read.crm_direct_contact_outcomes AS
  SELECT operation_id, sims_request_id, fulfilment_cycle_id, sims_tutor_id, outcome, status, outreach_binding, occurred_at, recorded_at
  FROM public.crm_direct_contact_outcomes;
-- Candidate/parent outcome evidence used by outreach matching. Free-text notes,
-- reasons and staff IDs are returned as NULL so application reads run unchanged.
CREATE OR REPLACE VIEW agent_read.crm_fulfilment_cycles AS
  SELECT id, request_id, cycle_number, status, version, closed_at, created_at, updated_at, cycle_kind FROM public.crm_fulfilment_cycles;
CREATE OR REPLACE VIEW agent_read.crm_request_candidates AS
  SELECT id, request_id, fulfilment_cycle_id, sims_tutor_id, source, status, version, created_at, updated_at FROM public.crm_request_candidates;
CREATE OR REPLACE VIEW agent_read.crm_request_candidate_outcome_events AS
  SELECT id, operation_id, request_id, fulfilment_cycle_id, sims_tutor_id, responsibility, action, category,
         NULL::text AS reason, NULL::integer AS recorded_by, recorded_at, previous_outcome_id,
         CASE WHEN legacy_evidence IS NULL THEN NULL ELSE jsonb_build_object('id', legacy_evidence->'id',
           'cycleId', legacy_evidence->'cycleId', 'recordedAt', legacy_evidence->'recordedAt') END AS legacy_evidence
  FROM public.crm_request_candidate_outcome_events;
CREATE OR REPLACE VIEW agent_read.crm_parent_outcome_events AS
  SELECT id, request_id, fulfilment_cycle_id, event_class, outcome, supersedes_event_id, correction_of_event_id,
         NULL::text AS note, NULL::text AS compensation_note, NULL::integer AS recorded_by, decided_at, recorded_at
  FROM public.crm_parent_outcome_events;
CREATE OR REPLACE VIEW agent_read.crm_parent_outcome_tutor_states AS
  SELECT id, event_id, candidate_id, state, NULL::text AS note FROM public.crm_parent_outcome_tutor_states;
CREATE OR REPLACE VIEW agent_read.crm_recovery_events AS
  SELECT id, request_id, sims_request_id, fulfilment_cycle_id, kind, candidate_id, sims_tutor_id, withdrawal_stage,
         decision - 'note' AS decision, NULL::text AS reason, NULL::integer AS recorded_by, occurred_at, created_at
  FROM public.crm_recovery_events;
GRANT SELECT ON ALL TABLES IN SCHEMA agent_read TO ripple_outreach_readonly;
COMMIT;
