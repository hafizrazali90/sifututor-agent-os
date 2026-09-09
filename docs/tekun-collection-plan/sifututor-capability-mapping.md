# Sifututor Capability Mapping For A TEKUN Corporation Collection Partnership

**Status:** Internal planning evidence, 31 August 2026.

**Purpose:** Separate capability we can credibly reuse from collection-specific adaptation, new build and decisions that only TEKUN Corporation can make.

## 1. Executive conclusion

Sifututor does **not** currently operate a TEKUN collection platform and this document does not claim prior debt-collection delivery. The credible proposition is stronger than a generic software promise: Sifututor has already built and operates many of the difficult foundations required for a multi-stakeholder, transaction-sensitive live service. These include authoritative records, role-based staff workflows, customer and provider channels, reconciliation, omnichannel communication, governed analytics, audit-oriented delivery controls, monitoring and recovery.

Those foundations reduce delivery risk, but they do not eliminate the need for a dedicated collection domain. Arrears strategies, statutory contact controls, notices, identity-verification evidence, promises to pay, hardship, complaints, settlement authority, representative competency and per-principal reporting must be designed specifically for TEKUN Corporation's confirmed portfolios and regulatory pathway.

The proposal should therefore use this positioning:

> We bring proven experience operating complex, multi-stakeholder and financially sensitive platforms, then adapt those foundations into a TEKUN Corporation-owned collection platform and managed operating service governed by TEKUN Corporation's policy, authority and compliance requirements.

## 2. Classification used

| Label | Meaning | Proposal rule |
| --- | --- | --- |
| **Proven foundation** | Evidenced in the current Sifututor ecosystem | May be used as capability proof, with its sourcebook limitation |
| **Adapt for TEKUN** | A proven pattern needs TEKUN-specific data, workflow, policy or integration | Describe as proposed adaptation, never as live TEKUN capability |
| **New collection build** | Domain functionality is not evidenced as an existing Sifututor capability | Place in solution scope and roadmap |
| **Discovery / authority** | Cannot be designed until TEKUN, a portfolio owner, compliance or counsel decides | Ask before commitment; do not infer |

## 3. Foundation-to-solution map

| TEKUN need | Sifututor evidence today | Classification | Proposed use | Evidence / limitation |
| --- | --- | --- | --- | --- |
| One authoritative operating record | SIMS governs identities, requests, classes, invoices and payments | **Proven foundation → Adapt** | Create a dedicated collection account, case and portfolio authority model | `CLM-ARCH-001`, `CLM-SYS-SIMS-001`; not a debt ledger today |
| Separate organisations and portfolios | Kelasapp demonstrates tenant-scoped identity, access and data; Finch is multi-tenant and multi-brand | **Proven foundation → Adapt** | Segregate each principal's accounts, policies, agents and reports | `CLM-SYS-KEL-001`, `CLM-SYS-FIN-001`; isolation must be independently tested for the new platform |
| Staff permissions and authority | SIMS and Ripple use role- and responsibility-based access | **Proven foundation → Adapt** | Agent, supervisor, manager, compliance, finance, auditor and principal roles | `CLM-SYS-SIMS-001`, `CLM-SYS-RIP-001`; legal authority limits remain TEKUN-owned |
| Work queues and accountable ownership | Ripple concentrates staff work and decisions; Finch records conversation ownership | **Proven foundation → Adapt** | Case queues, assignment, reassignment, escalation and supervisor oversight | Existing patterns are reusable; collection strategy rules are new |
| End-to-end state transitions | SIMS links request, assignment, delivery, verification, billing and payment | **Proven foundation → Adapt** | Link assignment, contact, promise, payment, reconciliation, cessation and closure | `CLM-NAR-001`, `CLM-SYS-SIMS-001`; collection states require a new domain model |
| Customer contact across channels | Finch provides multi-channel conversation context and ownership | **Proven foundation → Adapt** | Govern call, WhatsApp, SMS, email and letter history in one case view where permitted | `CLM-SYS-FIN-001`; supported channels and regulatory use require confirmation |
| Call and interaction evidence | Privacy-aware customer-evidence capture exists as a controlled capability pattern | **Proven pattern → Adapt** | Consent-, access- and retention-governed call evidence and coaching | `CLM-CAP-CX-001`; explicitly not universally deployed |
| Payment evidence and reconciliation | SIMS/Ripple support bank and gateway evidence, matching, exceptions and controlled finance transitions | **Proven foundation → Adapt** | Match principal/payment-provider evidence to accounts and promises without agent cash handling | `CLM-SYS-RIP-001`, sourcebook interface catalogue; actual money flow is discovery |
| Financial review and audit context | SIMS and Ripple provide typed states, financial review rules and traceable transaction context | **Proven foundation → Adapt** | Approval evidence for adjustments, settlement recommendations and fee calculations | Authority and accounting treatment belong to TEKUN/principal |
| Customer self-service | Parent App proves authenticated self-service for status, invoices, payments and support | **Proven foundation → Adapt** | Optional debtor portal for notices, statement, payment routes, disputes and hardship | A new audience, legal wording and identity model are required |
| Operational reporting | SIMS/Ripple and owner analytics provide governed operating and finance insight | **Proven foundation → Adapt** | Agent, supervisor, compliance, management and principal views | `CLM-ANA-001`; collection KPI definitions and data sources are new |
| Secure integrations | Mobile apps, payment providers, Ripple and analytics use managed contracts and explicit authority boundaries | **Proven foundation → Adapt** | Principal data intake, payment evidence, messaging and regulatory/reporting interfaces | `CLM-ARCH-002`, `CLM-ARCH-004`; every interface requires a TEKUN-specific contract |
| Monitoring and incident response | Shared error, log, uptime, performance and release-monitoring capabilities | **Proven foundation → Adapt** | Service health, failed-feed detection, alerting and incident governance | `CLM-TRU-001`; target coverage/SLA to be agreed |
| Backup and recoverability | SIMS recovery was demonstrated across protected components with off-server object-lock protection and monitoring | **Point-in-time proven foundation → Adapt** | Define recovery objectives, backups and restore exercises for TEKUN | `CLM-RES-001`, verified 28 July 2026; no guarantee or certification claim |
| Controlled analytics and AI | Owner analytics is curated and read-only; Agent OS uses governed human–AI processes | **Proven foundation → Later adaptation** | Summaries, quality sampling, knowledge support and explainable prioritisation after policy approval | `CLM-ANA-001`, `CLM-AI-001`; no autonomous consequential decision claim |
| Repeatable delivery and continuous improvement | Agent OS formalises planning, evidence, review, memory and guardrails | **Proven foundation → Adapt** | Govern releases, operational learning, runbooks and joint roadmap | `CLM-SYS-OPS-001`; one contributor, not a substitute for collection expertise |

## 4. Collection-specific capability that must be built or configured

| Domain | Required capability | Classification | Governing dependency |
| --- | --- | --- | --- |
| Portfolio intake | Import, validation, deduplication, account provenance, assignment and return | **New collection build** | Principal file/API formats and acceptance rules |
| Debt and arrears | Balances by component, instalments, ageing, point-in-time snapshots, portfolio cohorts | **New collection build** | Product definitions and principal ledger authority |
| Strategy | Configurable treatment paths by principal, product, ageing, risk and status | **New collection build** | TEKUN-approved strategy and legal scope |
| Conduct controls | Contact-hour and frequency controls, notice gate, identity-verification gate, third-party disclosure prevention | **New collection build** | Confirmed applicable standards and channel rules |
| Notice management | Templates, mandatory fields, delivery evidence and seven-day pre-action gate where applicable | **New collection build** | Compliance-approved wording and service method |
| Promise management | Promise amount/date, follow-up, kept/broken classification and payment matching | **New collection build** | Reconciliation timing and tolerance rules |
| Customer treatment | Dispute, complaint, hardship, deceased/bankrupt and vulnerable-customer pathways | **New collection build** | TEKUN policy, principal authority and legal review |
| Cessation and holds | Immediate stop on settlement/accepted plan; hardship and legal holds | **New collection build** | Authoritative event source and override rules |
| Decision authority | Settlement, discount, restructure, write-off and legal-escalation approval matrix | **Discovery → New build** | TEKUN/principal RACI and limits |
| Representative governance | Appointment, authorisation document, training, annual competency and revocation records | **New collection build + operating process** | Employer/representative model and regulatory pathway |
| Quality and compliance | Call review, exception monitoring, remediation, complaints reporting and audit export | **New collection build + operating process** | Compliance ownership and sampling rules |
| Principal service | Per-principal policy, SLA, reporting pack, onboarding and offboarding | **New collection build** | Contract terms and portfolio-owner expectations |
| Regulatory reporting | Complaints, credit-reporting and other required submission support | **Discovery → New build/integration** | Confirmed applicability, format and accountable submitter |
| Data protection | Access anomaly detection, breach register, retention/disposal and export | **Adapt + New controls** | Confirmed controller/processor roles and applicable criteria |
| Managed collection operation | Recruitment/assignment, BM scripts, training, supervision, QA, workforce planning and escalation | **New operating capability to prove** | Authorisation model, staffing, channel scope and TEKUN oversight |

## 5. What only TEKUN Corporation can authorise or confirm

- Applicable regulatory pathway and current authorisation/application/declaration status.
- Which principals and portfolios are active and which products are in scope.
- Collection policy, risk appetite, approved channels and treatment strategy.
- Settlement, restructure, write-off and legal-escalation authority.
- Data-controller/processor roles, hosting constraints, retention and disclosure rules.
- Payment destination, reconciliation source and official receipt/statement process.
- Whether existing staff, systems or external providers are retained, integrated or transitioned.
- Baseline definitions, pilot cohort, guardrail measures and success criteria.
- Procurement, budget and commercial structure.

## 6. Capability proof story for the stakeholder document

The final source document should use three levels of proof:

1. **What we already operate:** live multi-stakeholder platform, specialised staff workspaces, financial controls, communication, analytics and platform-health disciplines.
2. **What those foundations enable for TEKUN:** a faster and lower-risk route to a dedicated, TEKUN-owned collection platform.
3. **What will be created jointly:** collection-domain controls, operating playbooks, portfolio intelligence and measurable improvement under TEKUN's authority.

It must not use Sifututor's education workflows as if they prove collection performance. They prove the ability to build and operate complex service infrastructure; the pilot must prove collection outcomes.

## 7. Internal readiness decisions before commitment

| Decision | Owner | Why it matters |
| --- | --- | --- |
| Who is the proposed contracting entity and delivery owner? | Leadership | Establishes accountability and references |
| Can we lawfully perform collection ourselves, and under whose authorisation? | Legal/compliance | Determines the operating model and timing |
| Can we recruit, train, supervise and assess collection representatives? | Operations | Software alone cannot deliver managed collection |
| What BM language, scripts and documentation quality can we sustain? | Operations/compliance | Core customer-treatment requirement |
| Which existing components may be reused versus only used as design knowledge? | Engineering | Prevents accidental product or data coupling |
| Can we meet the confirmed privacy, security and incident duties? | Security/compliance | Required before handling portfolio data |
| What capacity, cost and risk can we carry in a pilot? | Finance/leadership | Required before commercial design |
