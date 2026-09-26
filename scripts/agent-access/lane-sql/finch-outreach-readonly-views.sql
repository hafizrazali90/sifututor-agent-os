-- Finch production (teaminbox) read-only outreach views for the agent lane
-- `finch-outreach-readonly`. Views are owned by dbo so the reader needs SELECT
-- on schema agent_read only; no phone numbers, names, message bodies, template
-- values, provider payloads or free-text staff fields are exposed.
SET NOCOUNT ON;
IF SCHEMA_ID('agent_read') IS NULL EXEC('CREATE SCHEMA agent_read AUTHORIZATION dbo');
GO
CREATE OR ALTER VIEW agent_read.outreach_operations AS
SELECT company_guid, operation_id, tutor_id, contact_digest, origin, state, state_version, queue_id, broadcast_id,
       usage_date, reserved_micros, cost_micros, cost_basis, cost_currency, accepted_at, first_delivered_at,
       attempts, reason, created_at, updated_at
FROM dbo.wa_outreach_operations;
GO
CREATE OR ALTER VIEW agent_read.outreach_jobs AS
SELECT company_guid, operation_id, sims_request_id, tutor_id, batch_id FROM dbo.wa_outreach_jobs;
GO
CREATE OR ALTER VIEW agent_read.outreach_requests AS
SELECT company_guid, sims_request_id, initial_batch_id, batch_id, sequence, revision_hash, control_version, paused,
       allowance, first_delivered_at
FROM dbo.wa_outreach_requests;
GO
CREATE OR ALTER VIEW agent_read.outreach_holds AS
SELECT company_guid, scope, subject_key, reason, created_at, resolved_at FROM dbo.wa_outreach_holds;
GO
CREATE OR ALTER VIEW agent_read.outreach_manual_evidence AS
SELECT company_guid, queue_id, broadcast_id, contact_digest, usage_date, state, accepted_at, cost_micros, cost_basis,
       created_at, updated_at
FROM dbo.wa_outreach_manual_evidence;
GO
CREATE OR ALTER VIEW agent_read.outreach_history_bindings AS
SELECT company_guid, queue_id, sims_request_id, tutor_id, contact_digest, resolver_version, resolved_at
FROM dbo.wa_outreach_history_bindings;
GO
CREATE OR ALTER VIEW agent_read.outreach_legacy_pair_blocks AS
SELECT company_guid, sims_request_id, tutor_id, imported_at FROM dbo.wa_outreach_legacy_pair_blocks;
GO
CREATE OR ALTER VIEW agent_read.outreach_legacy_request_holds AS
SELECT company_guid, sims_request_id, imported_at FROM dbo.wa_outreach_legacy_request_holds;
GO
CREATE OR ALTER VIEW agent_read.outreach_policy AS
SELECT company_guid, policy_json, globally_stopped, updated_at FROM dbo.wa_outreach_policy;
GO
CREATE OR ALTER VIEW agent_read.outreach_daily_coverage AS
SELECT company_guid, usage_date, manual_spend_complete, prior_spend_micros, reviewed_at FROM dbo.wa_outreach_daily_coverage;
GO
CREATE OR ALTER VIEW agent_read.ripple_broadcast_operations AS
SELECT id, company_guid, operation_id, template_key, ripple_request_id, broadcast_id, status, error_code,
       recipient_count_requested, recipient_count_queued, created_at, updated_at
FROM dbo.wa_ripple_tutor_broadcast_operations;
GO
CREATE OR ALTER VIEW agent_read.ripple_broadcast_recipients AS
SELECT id, company_guid, operation_row_id, tutor_id, queue_id, status, error_code, created_at
FROM dbo.wa_ripple_tutor_broadcast_recipients;
GO
-- Delivery status only for queue rows that belong to tutor outreach or Ripple tutor broadcasts.
CREATE OR ALTER VIEW agent_read.outreach_queue_status AS
SELECT q.id AS queue_id, q.broadcast_id, q.status, q.provider_status, q.provider_status_at, q.provider_error_code,
       q.attempts, q.scheduled_at, q.sent_at, q.created_at
FROM dbo.wa_message_queue q
WHERE EXISTS (SELECT 1 FROM dbo.wa_outreach_operations o WHERE o.queue_id = q.id)
   OR EXISTS (SELECT 1 FROM dbo.wa_outreach_manual_evidence m WHERE m.queue_id = q.id)
   OR EXISTS (SELECT 1 FROM dbo.wa_ripple_tutor_broadcast_recipients r WHERE r.queue_id = q.id);
GO
