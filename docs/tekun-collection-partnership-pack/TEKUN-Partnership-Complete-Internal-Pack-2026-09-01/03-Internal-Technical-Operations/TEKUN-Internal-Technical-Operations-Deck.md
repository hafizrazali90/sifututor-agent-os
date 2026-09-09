<!-- deck: TEKUN Internal Technical and Operations Presentation -->
<!-- classification: Confidential — internal working use only -->
<!-- governed-source: TEKUN Collection Partnership Sourcebook v1.0 -->

<!-- layout: cover -->
# TEKUN Collection Partnership
## Internal Technical and Operations Briefing

**How the platform, people, controls, evidence and roadmap connect end to end**

Confidential — internal working use only  
31 August 2026

**35-slide core briefing + 7-slide optional reference appendix**

<!-- notes: This is the internal depth deck. It is not approved for external circulation. -->

---

<!-- layout: statement -->
# Purpose of this briefing

> Give product, engineering, operations, finance, compliance and leadership one shared model of what we are proposing, what is known, what remains to be discovered and how we prove value safely.

The external story is concise. This deck preserves the operating detail needed to design, estimate and govern the work.

<!-- sources: Sourcebook — How to use this sourcebook -->

---

<!-- layout: two-column -->
# The truth boundary

## Established or publicly stated

- TEKUN Corporation is an established collection operator.
- Its public history includes a collection call centre since 2015.
- It publicly states approximately 30 appointing organisations.
- Public collection or recovery appointments continued in 2026.
- Sifututor has operated live services since 2018; new SIMS went live in May 2025.

## Proposed or conditional

- The platform and managed service described here do not yet exist for TEKUN.
- Portfolio applicability, authority, privacy roles and registration status require confirmation.
- Current systems, providers, volumes, economics and baseline are not publicly known.
- No outcome, date, staffing level or price is promised.

<!-- sources: Sourcebook Executive Orientation and Chapters 1–2, 18 -->

---

<!-- layout: milestone -->
# Evidence known today

| Evidence | Practical meaning | Use constraint |
| --- | --- | --- |
| TCorp registration and 2015 collection-centre history | Established operating identity | Attribute to TCorp |
| MOF field code and ~30 appointments stated publicly | Multi-principal operating context | Reverify current figure |
| Awqaf Education and MOCCIS activity in 2026 | Continuing market activity | No value, volume or performance inferred |
| Consumer-credit framework and standards | More explicit operational controls | Apply portfolio by portfolio |
| Sifututor live platform history | Relevant platform-operating proof | Not debt-collection proof |

<!-- sources: Sourcebook Chapters 1–2, 18, 23 -->

---

<!-- layout: guardrails -->
# Material unknowns drive discovery—not speculation

- Current platform, dialler, CRM, payment and reporting architecture
- Internal and third-party operating responsibilities
- Provider identity, contract value, commission basis and transition terms
- Portfolio owners, products, volumes, ageing and contactability
- Registration/authorisation status by legal entity and activity
- Payment recipient, receipt issuer and reconciliation authority
- Baseline performance, cost, complaints, conduct and service health
- Data-controller/processor roles, retention and security obligations

**Rule:** unknown does not mean absent, weak or non-compliant.

<!-- sources: Sourcebook Chapters 1, 22, 26; Appendices C, E and G -->

---

<!-- layout: impact-chain -->
# Proposed operating model

TEKUN Corporation owns and governs the platform. Our team builds, operates, maintains and improves it while performing or coordinating only authorised collection work.

The model connects:

1. portfolio and policy authority;
2. platform delivery and service operations;
3. controlled customer engagement;
4. payment evidence and reconciliation;
5. reporting, assurance and improvement.

<!-- visual: ../tekun-collection-assets/generated-diagrams/diagram-1.svg -->
<!-- sources: Sourcebook Executive Orientation and Chapter 4 -->

---

<!-- layout: partnership -->
# Responsibility model

## TEKUN Corporation

- Principal relationships
- Policy and risk appetite
- Portfolio acceptance
- Consequential authority
- Strategic and regulatory oversight

## Partner delivery

- Platform build and operation
- Authorised service execution
- Integrations and evidence
- Monitoring and support
- Improvement and transition

## Joint governance

- Baseline and KPIs
- Pilot and service levels
- Incidents and changes
- Learning and roadmap
- Expansion gates

<!-- sources: Sourcebook Chapters 4–5 -->

---

<!-- layout: ownership -->
# Authority is explicit at every consequential moment

| Moment | System behaviour | Human authority |
| --- | --- | --- |
| Portfolio acceptance | Validate and quarantine until accepted | TEKUN/principal authority |
| Strategy assignment | Apply approved policy version | TEKUN collection governance |
| Settlement/write-off | Recommend and route; never auto-assume | Named accountable party |
| Legal escalation | Hold until prerequisites and approval exist | Legal/TEKUN authority |
| Complaint/hardship | Pause standard treatment and assign specialist | Approved specialist/governance |
| Policy override | Require reason, approver and audit | Delegated authorised role |

<!-- sources: Sourcebook Chapters 5 and 7 -->

---

<!-- layout: lifecycle -->
# Core collection lifecycle

**Intake → Validate → Segment → Assign → Notify → Verify → Engage → Promise/protect/escalate → Pay → Reconcile → Cease/close → Report and improve**

Every transition needs:

- entry criteria and source data;
- allowed action and accountable owner;
- authority and customer-treatment gates;
- outcome, timestamp and evidence;
- retry, exception, hold and recovery behaviour.

<!-- visual: ../tekun-collection-assets/generated-diagrams/diagram-4.svg -->
<!-- sources: Sourcebook Chapter 6 -->

---

<!-- layout: standard -->
# Case state is more than “open” or “closed”

| State family | Example states | Why separation matters |
| --- | --- | --- |
| Intake | received, rejected, quarantined, accepted | Prevents bad data entering production work |
| Work | ready, assigned, due, attempted, awaiting follow-up | Makes workload and ownership visible |
| Promise | proposed, accepted, due, kept, broken, superseded | Prevents false success from an unverified promise |
| Protection | dispute, hardship, vulnerability, complaint, legal hold | Removes protected cases from standard pressure |
| Payment | reported, evidenced, matched, reconciled, reversed | Creates trustworthy outcomes |
| Closure | settled, arrangement, withdrawn, returned, exhausted | Explains why collection stopped |

<!-- sources: Sourcebook Chapters 6, 9 and 12 -->

---

<!-- layout: architecture -->
# Logical platform architecture

1. **Experience:** agent, supervisor, management, compliance, finance and principal views.
2. **Portfolio authority:** principal, product, agreement, account, case and policy.
3. **Controlled interaction:** queues, notices, verification, contact, promises and holds.
4. **Evidence and money:** payment source, reconciliation, reversals and cessation.
5. **Enterprise intelligence:** performance, conduct, service health, risk and roadmap.

<!-- visual: ../tekun-collection-assets/generated-diagrams/diagram-6.svg -->
<!-- sources: Sourcebook Chapter 8 -->

---

<!-- layout: standard -->
# Information hierarchy and segregation

**Enterprise → Principal → Portfolio → Product/policy → Customer/account → Case → Interaction/evidence**

- A principal sees only its authorised portfolios.
- Policies are versioned and attached to the correct population.
- A customer may have more than one account; each debt and authority chain remains distinct.
- Case activity never changes an authoritative balance without an approved write path.
- Imports, withdrawals and corrections preserve provenance.
- Enterprise analytics use governed aggregation without weakening principal boundaries.

<!-- sources: Sourcebook Chapter 9 -->

---

<!-- layout: two-column -->
# Front-line workspace design

## Agent sees

- prioritised cases and due work;
- verified context and approved next action;
- identity and disclosure steps;
- contact history, promises and payment status;
- clear protected-case and escalation routes;
- only the information needed for assigned work.

## System prevents or redirects

- action outside contact policy;
- disclosure before identity verification;
- work on a settled, held or withdrawn case;
- unapproved channel, script or notice;
- payment receipt by representatives;
- consequential decisions outside authority.

<!-- sources: Sourcebook Chapters 10–11 -->

---

<!-- layout: two-column -->
# Supervisor and control workspaces

## Supervisor

- queue health and capacity;
- ageing, unreachable cases and due promises;
- representative competency and quality;
- exceptions, complaints and protected cases;
- workload rebalance and coaching evidence.

## Independent control views

- compliance: contact, notice, disclosure and conduct exceptions;
- privacy/security: access, export and incident evidence;
- finance: payment, match, reversal and ageing exceptions;
- management: portfolio, service, cost, value and risk.

<!-- sources: Sourcebook Chapters 10, 12 and 14 -->

---

<!-- layout: guardrails -->
# Customer-treatment controls become product requirements

- Identity gate before debt disclosure
- Configurable contact window, frequency and channel policy
- Approved notice template, mandatory fields, version and delivery evidence
- No third-party disclosure without confirmed authority
- No representative receipt of money
- Immediate stop or redirect on authoritative settlement/arrangement event
- Protected queues for disputes, hardship, vulnerability and complaints
- Appointment, training, assessment and authorisation currency
- Complete evidence for action, override, approval and exception

Final configuration follows confirmed applicability and TEKUN-approved policy.

<!-- sources: Sourcebook Chapter 11 -->

---

<!-- layout: standard -->
# Protected branches need their own lifecycle

**Trigger → Immediate hold → Specialist ownership → Assessment/evidence → Approved resolution → Controlled return or closure**

Protected cases include:

- disputed balance, identity or liability;
- hardship and vulnerability;
- deceased, bankrupt or legally restricted status;
- complaint or alleged misconduct;
- legal hold or principal withdrawal;
- confirmed settlement or accepted arrangement.

No performance target may silently release a hold or return a case to ordinary treatment.

<!-- sources: Sourcebook Chapters 6, 7 and 11 -->

---

<!-- layout: standard -->
# Promise, payment and reconciliation are separate facts

**Promise made ≠ payment reported ≠ evidence received ≠ payment reconciled**

- Customer pays through an approved official channel.
- Representatives record conversation and promise but never receive funds.
- Finance or an authoritative feed supplies transaction evidence.
- Matching handles reference quality, duplicates, partials and reversals.
- Unmatched evidence remains visible as an exception.
- Reconciled truth changes treatment and feeds outcome reporting.
- Any fee calculation uses agreed qualifying reconciled evidence.

<!-- visual: ../tekun-collection-assets/generated-diagrams/diagram-8.svg -->
<!-- sources: Sourcebook Chapter 12 -->

---

<!-- layout: standard -->
# Integration catalogue

| Interface | Direction | Core controls |
| --- | --- | --- |
| Principal portfolio feed | Inbound | Schema, source, dedupe, corrections and withdrawals |
| Status/performance report | Outbound | Definitions, approval and principal segregation |
| Messaging/telephony | Two-way | Identity, channel, timing, frequency and evidence |
| Payment evidence | Inbound | Source validation, duplicates, reversal and retry |
| Notices/documents | Outbound | Approved version, content and delivery evidence |
| Regulatory/reporting support | Outbound | Accountable submitter and approval before release |
| Analytics | Read-oriented | Curated access, masking, audit and governed definitions |

<!-- sources: Sourcebook Chapter 13 -->

---

<!-- layout: two-column -->
# Trust model

## Prevent and contain

- strong authentication and least privilege;
- principal, portfolio and role boundaries;
- encryption, minimisation and controlled export;
- validated interfaces and named write paths;
- tamper-evident material event history.

## Detect and recover

- service, feed, queue and unusual-access monitoring;
- severity, ownership and incident communication;
- protected backups and restore testing;
- controlled releases, rollback and post-release checks;
- lessons converted into controls and runbooks.

<!-- sources: Sourcebook Chapter 13 -->

---

<!-- layout: standard -->
# Reporting layers share one governed truth

| Audience | Decision view |
| --- | --- |
| Agent | What should I safely do now? |
| Supervisor | Where are workload, quality and exceptions drifting? |
| Finance | Which reported outcomes are reconciled? |
| Compliance/privacy | Where are conduct, complaint or access risks? |
| Collection management | Which strategies and cohorts are working? |
| Principal | What happened within my authorised portfolio? |
| TCorp leadership | Is the service healthy, valuable and ready to expand? |

<!-- visual: ../tekun-collection-assets/generated-diagrams/diagram-10.svg -->
<!-- sources: Sourcebook Chapter 14 -->

---

<!-- layout: service -->
# Managed operating cells

- **TCorp service owner:** relationships, policy, authority and outcomes
- **Collection manager:** strategy, allocation, performance and escalation
- **Supervisor:** daily queues, capacity, coaching and exceptions
- **Authorised representatives:** controlled contact and evidence
- **Protected-case specialists:** disputes, complaints, hardship and vulnerability
- **Finance/reconciliation:** payment truth and exceptions
- **Compliance/privacy:** independent interpretation and oversight
- **Platform operations:** service, integrations, incidents and recovery
- **Product/improvement:** friction analysis and governed roadmap

<!-- sources: Sourcebook Chapter 15 -->

---

<!-- layout: standard -->
# Competency and quality lifecycle

**Screen → Train → Assess → Authorise → Observe/sample → Coach/remediate → Reassess**

Quality must balance:

- outcome and productivity;
- correct identity and disclosure;
- accuracy of explanation and record;
- compliant timing, frequency, notice and channel;
- appropriate complaint, dispute and hardship handling;
- evidence completeness;
- security and privacy behaviour.

A material concern can suspend authorisation before the next periodic review.

<!-- sources: Sourcebook Chapter 16 -->

---

<!-- layout: standard -->
# Service management closes the operational loop

**Observe → Detect → Triage → Correct → Verify → Release/adopt → Monitor → Learn**

- A software incident, failed feed, queue spike or conduct exception follows a named response path.
- Business, technology and control owners see the same event with different responsibilities.
- Changes require evidence for both the technical component and the human journey.
- Rollback, recovery and communication are planned before release.
- Repeated friction becomes a jointly prioritised improvement item.

<!-- visual: ../tekun-collection-assets/generated-diagrams/diagram-11.svg -->
<!-- sources: Sourcebook Chapter 17 -->

---

<!-- layout: milestone -->
# Our relevant capability foundation

| Existing capability | Relevance | Boundary |
| --- | --- | --- |
| SIMS operating core | Identities, workflows, finance and reports | Not a debt system |
| Ripple staff workspace | Queues, roles and governed decisions | Collection design is new |
| Kelasapp separation | Multi-organisation patterns | New isolation needs proof |
| Finch conversations | Multi-channel ownership | Channels need approval |
| Mobile/self-service | Authenticated participant communication | Customer portal would be new |
| Analytics and monitoring | Curated insight and service health | TEKUN definitions are new |
| Agent OS | Evidence, playbooks and human oversight | Not legal or collection authority |

<!-- sources: Sourcebook Chapter 18 -->

---

<!-- layout: impact-chain -->
# Capability-to-value chain

Connected data and guided work improve case context and consistency. Payment integration turns claimed outcomes into reconciled truth. Customer-treatment controls protect service credibility. Reliable reporting builds principal confidence. Repeatable onboarding creates growth capacity.

**Technology → operating signal → verified outcome → strategic contribution**

Portfolio mix, customer circumstances, policy, staffing, authority and economic conditions remain material influences.

<!-- visual: ../tekun-collection-assets/generated-diagrams/diagram-2.svg -->
<!-- sources: Sourcebook Chapters 3 and 19 -->

---

<!-- layout: value -->
# Balanced scorecard

| Lens | Core questions |
| --- | --- |
| Operations | Are cases workable, owned and acted on at the right time? |
| Financial | Which qualifying outcomes are reconciled and at what cost? |
| Portfolio | Are cohorts curing, rolling or ageing differently? |
| Customer treatment | Are complaints, disputes, hardship and cessation controlled? |
| Compliance | Did notices, contact, identity, disclosure and data access stay within policy? |
| Platform health | Is the service available, recoverable and receiving reliable feeds? |
| Strategic growth | Can TCorp onboard and retain more principals without uncontrolled reinvention? |

<!-- sources: Sourcebook Chapter 20 -->

---

<!-- layout: two-column -->
# KPI definitions are contracts about meaning

## Example definitions

- Right-party contact = verified customer conversations ÷ valid attempts
- Kept promise = due promises fulfilled within agreed tolerance ÷ promises due
- Collection rate = reconciled qualifying amount ÷ agreed amount due
- Recovery rate = reconciled recovery from named frozen cohort ÷ cohort opening value

## Every KPI also needs

- population and time window;
- authoritative source;
- owner and refresh frequency;
- exclusions and adjustment events;
- quality threshold;
- known misuse or misinterpretation risk.

<!-- sources: Sourcebook Chapter 20 and Appendix D -->

---

<!-- layout: pilot -->
# Pilot design: prove the whole system, not one number

- One principal, product or controlled cohort
- Written comparable baseline and known changes
- Confirmed authority, representatives, channels and policy
- Minimum complete lifecycle with payment evidence and service monitoring
- Weekly operating and monthly governance reviews
- Outcome, conduct, reconciliation and platform-health evidence
- Explicit expand, adjust, re-baseline or stop decision

<!-- visual: ../tekun-collection-assets/generated-diagrams/diagram-12.svg -->
<!-- sources: Sourcebook Chapter 21 -->

---

<!-- layout: roadmap -->
# Roadmap I: establish trust and prove control

## H0 — Align and baseline

- Stakeholder, authority and portfolio map
- Current lifecycle, provider and system map
- Data and money-flow architecture
- KPI dictionary and pilot cohort

## H1 — Trusted foundation

- Principal/portfolio model and segregation
- Identity, roles, policy versions and audit
- Intake, queues and health monitoring
- Core journey and recovery evidence

## H2 — Controlled pilot

- Authorised live work
- Customer-treatment and protected branches
- Payment evidence, reconciliation and reporting
- Balanced evidence gate

<!-- sources: Sourcebook Chapter 24 -->

---

<!-- layout: roadmap -->
# Roadmap II: scale only after evidence

## H3 — Integrated performance scale

- Automated portfolio and payment feeds
- Stable reconciliation and reporting
- Service levels and capacity planning
- Governed strategy comparison

## H4 — Multi-principal growth

- Reusable onboarding and policy configuration
- Tested tenant/principal segregation
- Accepted per-principal reporting
- Controlled operational expansion

## H5 — Governed intelligence

- Explainable summaries and quality assistance
- Forecasting only from sufficient clean history
- Bias/control review and human authority
- Evidence-led strategy and joint roadmap

<!-- sources: Sourcebook Chapter 24 -->

---

<!-- layout: standard -->
# Commercial architecture comes after operational truth

- Separate mobilisation, platform and managed-service components.
- Confirm portfolio volumes, channels, hours, roles and integrations first.
- Use only reconciled qualifying evidence for any outcome-linked element.
- Balance outcome incentives with customer-treatment guardrails.
- Define communication and third-party pass-through costs transparently.
- Preserve export, documentation and transition support.
- Revisit economics after pilot evidence rather than pricing assumptions.

No pricing model or fee percentage is approved in this deck.

<!-- sources: Sourcebook Chapter 22 -->

---

<!-- layout: two-column -->
# Discovery workstreams

## Business and control

- Entities, principals and portfolios
- Authority and regulatory applicability
- Policy, notices and customer treatment
- Baseline, KPIs and commercial inputs
- Workforce, competency and governance

## Platform and transition

- Current systems, providers and contracts
- Data model, interfaces and money flow
- Privacy, security, retention and recovery
- Pilot cohort and acceptance evidence
- Migration, coexistence and transition support

<!-- sources: Sourcebook Chapter 26 and Appendix E -->

---

<!-- layout: standard -->
# Delivery governance and assurance

| Forum | Cadence | Purpose |
| --- | --- | --- |
| Joint steering | Quarterly or at major gate | Strategy, value, roadmap and principal expansion |
| Performance forum | Monthly | Cohorts, outcomes, capacity, finance and actions |
| Compliance/customer-treatment forum | Monthly and event-driven | Conduct, complaints, holds, privacy and remediation |
| Delivery/change forum | Weekly | Product, engineering, incidents, releases and dependencies |
| Daily operations | Daily | Queues, staffing, exceptions and service health |

A collection target cannot excuse a conduct failure. A control issue cannot be hidden inside a performance report.

<!-- sources: Sourcebook Chapters 7, 17 and 27 -->

---

<!-- layout: guardrails -->
# Risks we control through design

- **Wrong authority:** explicit responsibility and approval maps
- **Wrong customer or disclosure:** identity gates and minimum information
- **Over-contact or invalid notice:** policy engine, schedule and version evidence
- **Continued contact after resolution:** authoritative cessation events and exception alerts
- **False performance:** reconciled evidence and governed cohorts
- **Principal data leakage:** segregation, access review and export controls
- **Failed integration or service:** monitoring, retry, incident and recovery evidence
- **Unhealthy lock-in:** export, documentation, configuration history and transition readiness

<!-- sources: Sourcebook Chapter 27 -->

---

<!-- layout: decision -->
# Internal next step

## Prepare one governed discovery and pilot co-design package

It must produce the current-state map, authority model, portfolio segmentation, data/money flows, baseline, KPI dictionary, pilot cohort, minimum architecture, transition approach, evidence plan and commercial inputs.

> Build only after we know who has authority, what truth sources exist, how success is measured and how customer treatment is protected.

**End the core briefing here. Slides 36–42 are optional working-reference appendices.**

<!-- sources: Sourcebook Chapters 26–28 -->

---

<!-- layout: standard -->
# Internal appendix: KPI dictionary I

| ID | Indicator | Owner | Interpretation safeguard |
| --- | --- | --- | --- |
| O1 | Contact coverage | Collection manager | Pair with frequency compliance; volume is not quality |
| O2 | Right-party contact rate | Collection manager | Data quality and identity rules affect result |
| O3 | Promise-to-pay rate | Collection manager | Pair with kept promises |
| O4 | Kept-promise rate | Collection manager/finance | Fix tolerance; use reconciled evidence |
| O5 | Time to first substantive action | Collection manager | Define substantive to prevent gaming |
| F1 | Reconciled amount collected | Finance | Exclude reversals, dishonoured and misapplied payments |
| F2 | Collection rate | Finance | State due amount, cohort, period and exclusions |
| F3 | Recovery rate | Finance | Freeze opening cohort and adjustment rules |
| F4 | Net recovery | Finance | Agree attributable cost method |
| F5 | Cost-to-collect | Finance | Segment by portfolio mix and arrears age |

<!-- sources: Sourcebook Appendix D -->

---

<!-- layout: standard -->
# Internal appendix: KPI dictionary II

| ID | Indicator | Owner | Interpretation safeguard |
| --- | --- | --- | --- |
| P1 | Ageing/PAR | Finance | State threshold, balance and restructure treatment |
| P2 | Roll rate | Collection manager | Requires reliable point-in-time snapshots |
| P3 | Cure rate | Collection manager | Separate payment cure from restructure cure |
| T1 | Complaint rate | Compliance | Low rate may indicate inaccessible intake |
| T2 | Complaint resolution time | Compliance | Track ageing and overdue cases |
| T3 | Hardship outcome/timeliness | Compliance | Approval rate alone is not quality |
| T4 | Cessation compliance | Compliance | Investigate every exception |
| C1 | Contact-window exceptions | Compliance | Confirm target and rule set |
| C2 | Identity-verification exceptions | Compliance | Debt-discussion population must be reliable |
| C3 | Contact-frequency exceptions | Compliance | Count across all integrated channels |
| C4 | Notice-gate compliance | Compliance | Validate fields and delivery evidence |

<!-- sources: Sourcebook Appendix D -->

---

<!-- layout: standard -->
# Internal appendix: KPI dictionary III

| ID | Indicator | Owner | Interpretation safeguard |
| --- | --- | --- | --- |
| C5 | Third-party disclosure exceptions | Compliance/privacy | Consent and relationship evidence required |
| C6 | Payment-handling exceptions | Compliance | Representative receipt should be zero where rule applies |
| C7 | Representative validity/competency | Compliance/operations | Active population and due dates current |
| C8 | Data-access anomalies | Privacy/security | Track investigation and closure, not alerts alone |
| H1 | Critical-workflow availability | Platform operations | Measure safe journey, not homepage only |
| H2 | Incident restore time | Platform operations | Segment by severity |
| H3 | Recovery proof freshness | Platform operations | Successful backup is not successful restore |
| H4 | Reconciliation ageing | Finance/platform | Pair value, item count and cause |
| S1 | Principal onboarding lead time | TCorp management | Write start/end conditions |
| S2 | Capacity headroom | TCorp management | Quality and conduct remain constraints |

Every KPI record also needs formula, population, period, source, exclusions, frequency, target type and gaming risk.

<!-- sources: Sourcebook Appendix D -->

---

<!-- layout: questions -->
# Internal appendix: discovery questions 1–12

1. Which outcomes should improve, in priority order?
2. What is the main operating constraint today?
3. What defines success for management, board and principals?
4. Which regulatory pathway and current status applies to each portfolio?
5. Which activities could a partner perform, under what authorisation?
6. Who holds settlement, restructure, write-off, legal and closure authority?
7. Which complaints, hardship, conduct and reporting processes are mandatory from day one?
8. Which appointing organisations and portfolios are active?
9. What products, volumes, value, ageing, geography and history are involved?
10. How are accounts assigned, updated, suspended, returned and closed?
11. Which activities are performed by TCorp staff?
12. Are external providers used for operations, people, technology, channels, data, payment, field or legal work?

<!-- sources: Sourcebook Appendix E -->

---

<!-- layout: questions -->
# Internal appendix: discovery questions 13–24

13. What does each provider do and what transition or contract constraints exist?
14. Which systems support the lifecycle today?
15. How are queues and treatment strategies defined and approved?
16. How are identity, contact, notice, consent, promises and cessation evidenced?
17. How are complaints, disputes, hardship, vulnerability and legal holds handled?
18. How are representatives trained, authorised, supervised and assessed?
19. Where do customers pay and what event stops collection?
20. Who reconciles payment, in which system and cycle?
21. What data arrives from each principal and which quality issues matter?
22. Which integrations exist or are required?
23. What privacy/data roles, hosting, retention, breach, export and audit constraints apply?
24. Which cohort and scorecard should govern a bounded pilot?

<!-- sources: Sourcebook Appendix E -->

---

<!-- layout: compact -->
# Internal appendix: assurance and transition evidence

| Assurance question | Required evidence |
| --- | --- |
| Are only authorised people acting? | Identity, role, competency and authorisation records |
| Are actions permitted now? | Notice, contact, consent, hold and authority gates |
| Was the customer treated fairly? | Interaction, quality, complaint and hardship evidence |
| Is a collection result real? | Reconciled payment evidence and cohort definition |
| Did payment stop action correctly? | Cessation timestamp and post-stop exception report |
| Is each principal separated? | Access/isolation tests and principal-scoped reporting |
| Can an incident be understood and service recovered? | Monitoring, audit, incident, backup and restore evidence |
| Can TCorp govern or transition? | Documentation, export and tested transition exercise |

**Transition inventory:** data export; configuration/policy versions; data dictionary; interface specifications; runbooks; protected-case registers; permitted history; reconciliation evidence; access tests; recovery proof; change logs; cessation evidence; transition plan.

<!-- sources: Sourcebook Chapter 27 -->

---

<!-- layout: standard -->
# Internal appendix: commercial archetypes

| Model | Strength | Risk | Appropriate use |
| --- | --- | --- | --- |
| Fixed platform and operating fee | Predictable; funds essential controls | Weak direct outcome alignment | Foundation and minimum service |
| Per-account or capacity fee | Scales with workload | Can reward volume over resolution | Clear workable population |
| Success fee | Strong outcome alignment | Conduct pressure, cohort bias and disputes | Strict guardrails and reconciled evidence only |
| Gain-share above baseline | Pays for measured improvement | Depends entirely on baseline integrity | After defensible pilot/baseline |
| Hybrid fixed plus performance | Funds reliability while sharing upside | More calculation/governance detail | Recommended direction after discovery |

No model, price or percentage is approved. Any variable component must remain subject to customer-treatment and service guardrails.

<!-- sources: Sourcebook Chapter 22 -->
