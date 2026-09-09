# CyberSecurity Malaysia incident response ticketing: internal research brief

**Prepared:** 09/09/2026
**For:** Hafiz Razali, Learnest Lab Malaysia
**Ledger:** BD-CSM-001 (docs/agent-playbooks/mission-ledger/cross-project.md)
**Status:** Internal. Not client-facing. Written to be honest about where we are weak.
**Positioning:** Open. Prime contractor was assumed when this brief was
written; that assumption was reopened later the same day and is now held
until the agency replies. Section 5 is retained because its assessment of our
gaps holds under any positioning.
**Revised:** 09/09/2026, see section 8.

---

## 1. Bottom line

Five findings that change how we should approach this.

1. **The "24x7 CERT" premise is not supported by MyCERT's own published
   profile.** Their RFC 2350 profile states business hours 09:00 to 18:00
   Monday to Friday, with a 24x7 mobile number for after hours. That is an
   on-call model, not a staffed round-the-clock operation. It materially
   lowers the licensing and support footprint we should be costing.

2. **The volume is small.** 6,209 incidents in 2024, roughly 17 per day. Every
   platform under consideration handles that without effort. Scale is not a
   selection criterion here, and anyone selling scale is selling the wrong
   thing.

3. **"OTRS" is an ambiguous word and the ambiguity is a trap.** OTRS AG's
   product is proprietary and commercial. The free lineage everyone actually
   means is the OTRS 6 Community Edition fork line, now Znuny and OTOBO. If
   CSM's paperwork says "OTRS" without qualification, we must establish which
   of the three they mean before anything else.

4. **TheHive is not free at this scale.** TheHive 5's Community licence is
   capped at 2 users and 1 organisation. For a national CERT that is a
   demonstration licence, not a deployment. TheHive here means paid per-user
   Gold or Platinum.

5. **No credible platform vendor has a Malaysian presence.** Best Practical
   (RTIR) is US, Znuny and OTOBO are German, StrangeBee (TheHive) is French.
   That absence is precisely the gap a local implementation and support
   partner fills, and it is the most defensible thing we can say about
   ourselves. Caveat: absence of a published APAC partner is not proof one
   does not exist. Verify before we assert it to CSM.

---

## 2. Evidence discipline

What follows is separated deliberately, because the premise of this
opportunity has already changed twice.

**Verified against primary sources**

- MyCERT operating hours, constituency, reporting channels, PGP key
  (MyCERT's own RFC 2350 profile)
- 2024 incident volumes and category breakdown (CSM's own statistics page)
- CSM procurement route, thresholds, vendor requirements and full 2025/2026
  procurement register (CSM's own procurement page)
- National CSIRT tooling survey figures (peer-reviewed paper, OIC-CERT
  Journal 2022, first author is a MyCERT staff member)
- Platform licences, versions and quota limits (vendor documentation and
  pricing pages)
- Act 854 commencement and NCII reporting duty (NACSA and legal analyses)

**Still unverified, do not repeat as fact**

- That CSM pays roughly RM120,000 per year for OTRS. Third-hand via
  Shahruzzani. No primary source found. Nothing in CSM's published
  procurement register corresponds to it.
- That CSM is dissatisfied with its current arrangement.
- That a ticketing requirement exists at all in any live form.
- Whether MyCERT's published RFC 2350 profile is current. It does not present
  as recently revised: the listed PGP key is 1024-bit, which is long
  obsolete. Treat the hours as indicative and confirm.
- Which ticketing tool MyCERT itself uses today. MyCERT was one of the 17
  CSIRTs in the 2022 survey but responses were not attributed.

---

## 3. What MyCERT actually has to handle

### Mandate and constituency

MyCERT serves all Internet users in Malaysia, every sector plus home users.
That is an unusually broad constituency: it means a high proportion of reports
come from ordinary members of the public, not from technical staff at member
organisations. The system must be forgiving of low-quality, non-technical
intake.

### Reporting channels

Cyber999 is the public-facing intake service:

- Email `cyber999@cybersecurity.my`
- Cyber999 hotline 1300-88-2999
- 24/7 mobile +6019-2665850
- Online form
- Cyber999 mobile application
- PGP-encrypted submissions for sensitive reports

The 2022 survey found that across national CSIRTs, email is universal (17 of
17, 100%), telephone 76.5%, online form 70.6%. MyCERT additionally runs a
mobile app, which is uncommon. **Multi-channel intake into one queue is the
core requirement**, and it is the thing most generic ITSM tools do badly.

### Volume and mix, 2024

| Category | Incidents | Share |
|---|---:|---:|
| Fraud | 4,219 | 68.0% |
| Content related | 578 | 9.3% |
| Malicious codes | 427 | 6.9% |
| Intrusion attempt | 408 | 6.6% |
| Intrusion | 347 | 5.6% |
| Vulnerabilities report | 113 | 1.8% |
| Spam | 97 | 1.6% |
| Denial of service | 20 | 0.3% |
| **Total** | **6,209** | 100% |

The single most important thing in this table: **this is overwhelmingly a
fraud desk, not a malware desk.** Two-thirds of the workload is fraud, and
fraud cases are correlation-heavy and evidence-heavy. They need attachment
handling, linking of related reports, referral to law enforcement and
financial institutions, and long-lived case history. They do not need
malware sandboxing or threat-intel enrichment, which is what the
security-branded tools optimise for.

This cuts against TheHive specifically. TheHive is built around observables,
IOCs, analyser enrichment via Cortex and MISP threat-intel sharing. That is a
superb fit for a SOC chasing intrusions and a mediocre fit for a queue that is
68% consumer fraud reports.

### How CSIRTs actually classify

From the 2022 survey (n=17): 12 (70.6%) classify incidents entirely manually,
5 (29.4%) use a hybrid of manual and automated, **zero use automation alone**.
For deciding responses, 14 manual, 2 automated plus manual.

Implication: automation and AI classification are not where the value is, and
promising them would be overselling. The value is in making manual handling
fast and consistent.

### The statutory boundary, which we must not get wrong

The Cyber Security Act 2024 (Act 854) came into force 26 August 2024. Under
section 23, NCII entities must notify **the Chief Executive of NACSA** and
their sector lead. That statutory channel runs to NACSA, not to CSM or MyCERT.

So Cyber999 remains a voluntary public-facing service sitting alongside the
statutory regime. **If anyone frames this ticketing requirement as Act 854
compliance tooling, that is a scoping error and we should say so.** Getting
this boundary right in the first meeting is a credibility marker; getting it
wrong is disqualifying.

### CSM's actual technical environment

Reconstructed entirely from CSM's published procurement register, no back
channel required:

| System | Reference | Relevance |
|---|---|---|
| Elastic X-Pack Platinum | SH/18/2025 | Already licensed. OTOBO and TheHive both use Elasticsearch. Reuse argument available. |
| USM Anywhere SIEM | SH/05/2025 | Integration target for any ticketing system. |
| Integrated Business Process Management System | SH/01/2026 | **Awarded 2026. Possible scope overlap with ticketing. Highest-value question to ask.** |
| HCL Domino Collaboration Express | SH/01/2026, SH/02/2026 | Legacy mail and workflow. Migration or coexistence question. |
| Microsoft 365 and Exchange Online | SH/02/2025, SH/10/2025 | Identity and mail. SSO integration target. |
| Sangfor and DPTech firewalls | SH/06/2025, SH/05/2026 | Network context. |

Two observations. First, CSM buys subscriptions and licences far more often
than it buys implementation services, which tells us how they are used to
contracting. Second, they run both HCL Domino and Microsoft 365, which is an
awkward split and suggests a live modernisation agenda.

---

## 4. The platform landscape, honestly

### The five, compared

| | **RTIR** | **Znuny** | **OTOBO** | **OTRS (AG)** | **TheHive 5** |
|---|---|---|---|---|---|
| Licence | GPL-2.0 | GPL-3.0 | GPL-3.0 | Proprietary | Freemium, proprietary core |
| Language | Perl | Perl | Perl | Perl | Scala / JVM |
| Current line | RT/RTIR 5.0 | 7.3.x stable, 6.5.x LTS | 11.0.x | 8.x | 5.x |
| Built for CERTs? | **Yes, purpose-built** | No, general ITSM | No, general ITSM | No, general ITSM | **Yes, SOC/IR** |
| Free at CSM's scale? | Yes | Yes | Yes | No | **No, 2-user cap** |
| Vendor location | US | Germany | Germany | Germany | France |
| Malaysian presence | None found | None found | None found | None found | None found |

### RTIR

The CSIRT-native option and, on the evidence, the sector default. In the 2022
survey of 17 national CSIRTs, **RTIR was used by 8 (47.1%)**, nearly half, more
than every other tool combined except in-house builds. It ships pre-configured
queues for the actual CSIRT workflow: incident report triage, incident
handling, investigation, countermeasures. It has built-in WHOIS and network
lookup, correlation of multiple reports to a common root incident, and
constituency handling. ITU has published RTIR guidance for national CIRT
capacity building, which matters in a Malaysian context given the ITU-IMPACT
history in Cyberjaya.

Honest downsides: the interface is dated and unattractive, it is Perl, and
Best Practical is a small US company with no visible APAC presence. Perl RT
deployments are also notoriously fiddly to tune.

### Znuny

The conservative continuation of OTRS 6 Community Edition, launched 2021 by
the OTTER Alliance, with OTRS co-founder Martin Edenhofer among the
initiators. GPL-3.0, genuinely free, larger community than OTOBO, and the
6.5 LTS line is explicitly stability-first. If CSM's incumbent really is an
OTRS 6 derivative, Znuny is the lowest-risk migration because it is
deliberately the closest to the original.

Honest downsides: it is a general ITSM system, not a CERT system. Everything
CERT-specific has to be built as configuration. No official Docker images. No
AI classification, though per section 3 that is not actually a loss.

### OTOBO

The more actively modernised fork, by Rother OSS. Version 11.0.16 as of April
2026, with version 10 end-of-life on 1 January 2026, which shows a real
release cadence. Integrated Elasticsearch, official Docker images and Compose
templates, improved REST API, migration scripts from OTRS 6, optional AI
classification module.

Honest downsides: smaller community and smaller developer team than Znuny, so
more key-person risk. The comparison source I used for the feature differences
is OTOBO's own documentation site, so discount its framing accordingly.

### OTRS (OTRS AG)

Proprietary and commercially licensed since the Community Edition was declared
end of life in December 2020. Note that the 2022 CSIRT survey already
classified OTRS as "a commercial system", used by 3 of 17 (17.65%).

If CSM genuinely holds an OTRS AG contract, then a recurring annual fee is
entirely plausible and the RM120,000 figure stops being implausible. But that
is a hypothesis, not a finding.

### TheHive 5

Technically the deepest incident response product of the five, and the modern
SOC standard alongside Cortex and MISP. Also the worst fit for this particular
workload and the worst fit commercially.

- Community licence: 2 users, 1 organisation, 1 Cortex server, 1 MISP server.
  Unusable for a national CERT.
- Gold and Platinum are per-user with a 5-user minimum and prices are not
  published, meaning a sales conversation and an unpredictable line item.
- TheHive 4 has been unmaintained since 31 December 2022, so "just use the
  old open source version" is not an option.
- Its design centre is observables and threat intel. CSM's workload is 68%
  fraud.

**We should not steer CSM to TheHive, and equally we should not dismiss it
without stating what it is genuinely better at**, which is intrusion and
malware casework with threat-intel enrichment. If CSM's real ambition is to
build out a modern SOC capability rather than to run Cyber999 more
efficiently, TheHive deserves to be on the list.

### The read, product-neutral

On evidence rather than preference:

- If the goal is **Cyber999 intake done properly**, RTIR is the strongest fit
  and has the strongest peer validation among national CSIRTs.
- If the goal is **continuity with an existing OTRS 6 estate**, Znuny is the
  lowest-risk path and OTOBO the more modern one.
- If the goal is **a SOC capability**, TheHive is the right product and should
  be costed as commercial software, not as free software.

We genuinely do not yet know which of those three goals CSM has. That is
question 5 to Shahruzzani and it should also be the first question in any
meeting with Affan.

---

## 5. Learnest Lab as prime contractor, honestly

Hafiz has chosen the prime contractor route. Written plainly, here is where
that leaves us.

**What we have**

- MOF registration confirmed, which is listed in CSM's own vendor
  requirements. This is a real gate and we are through it.
- Genuine local presence, which no platform vendor has.
- Real delivery record on Laravel, React, React Native and infrastructure.

**What we do not have, and should not pretend to**

1. **No security delivery record.** Not one prior CERT, SOC or incident
   response engagement. For a national cyber security agency this is the
   single biggest objection and there is no way to argue it away. It has to
   be mitigated, most credibly by pairing with someone who has it.
2. **No Perl capability.** Four of the five candidate platforms are Perl.
   This is not a small detail: it is the implementation language of the most
   likely winner. Hire, partner, or accept that we can only offer
   integration and support rather than deep platform work.
3. **MOF field codes unknown.** Registration alone is not sufficient. Field
   codes determine which categories a vendor can be invited under. If we do
   not hold the right ICT codes, the registration does not help us. **Action
   for Hafiz: look up our codes.**
4. **Bumiputera status unknown**, which affects eligibility on some
   government work.
5. **No security clearance** for staff, which may be required to touch a
   national CERT's case data.
6. **Never delivered to a Malaysian government agency before.** Sebut harga
   invitation lists favour known vendors, and we are not one.

**The honest strategic read**

CSM buys subscriptions and licences far more readily than implementation
services, and it procures by invited sebut harga. Two consequences follow.
First, the contest is about getting invited, which is a relationship and
prequalification problem, not a technical one. Second, a first engagement is
much more likely to be small. Our realistic entry is not "win the ticketing
implementation" but "be the local partner on a small, well-scoped piece and
build the record we currently lack."

Going in as prime on a national CERT system with zero security delivery
history is the highest-risk version of this. It is Hafiz's call and it is a
legitimate one, but the brief would be dishonest if it did not say that
plainly.

**Update, later on 09/09/2026:** having read the above, Hafiz reopened the
positioning question rather than confirming prime. It is now held open until
the agency replies. Nothing downstream depends on it yet.

---

## 6. What to do next

**Not blocked on anyone**

1. Look up Learnest Lab's MOF field codes and confirm they cover ICT software
   and services. Highest value action available right now, and still open.
2. Look up our Bumiputera status. Still open.

**Decided and closed on 09/09/2026**

- CSM vendor registration: on hold until the agency replies, to avoid
  approaching them from two directions at once.
- Perl capability: deferred. No hire and no partner search until we know
  which platform is actually in play.
- Qualification via the informal contact: dropped entirely. See section 8.

**Blocked on Affan**

His reply. If it comes, the first meeting should establish which of the three
goals in section 4 CSM actually has, before any platform is discussed.

**Explicitly not doing yet**

Building a client-facing platform comparison. Section 4 is the internal
version. Turning it into a CSM-facing document before we know whether a
requirement exists would be effort spent on an assumption, and it risks
anchoring CSM on a platform choice before we understand their goal.

---

## 7. Sources

- MyCERT RFC 2350 profile : https://www.mycert.org.my/portal/full?id=92c511bd-04f2-4da2-984e-31323e5a7049
- CSM reported incidents 2024 : https://www.cybersecurity.my/portal-main/statistics-details?id=21
- CSM procurement register and vendor requirements : https://www.cybersecurity.my/portal-main/procurement
- Mohd Kassim, S. R., Li, S., and Arief, B. (2022) "Incident Response Practices Across National CSIRTs: Results from an Online Survey", OIC-CERT Journal of Cyber Security, 4(1), pp. 67-84 : https://kar.kent.ac.uk/94119/
- Cyber Security Act 2024 (Act 854), NACSA : https://www.nacsa.gov.my/act854.php
- RTIR source and licence : https://github.com/bestpractical/rtir
- RTIR product page : https://requesttracker.com/rtir/
- ITU, RTIR for incident management : https://www.itu.int/en/ITU-D/Cybersecurity/Documents/RTIR.pdf
- TheHive licence tiers : https://docs.strangebee.com/thehive/installation/licenses/about-licenses/
- TheHive quotas and pricing : https://strangebee.com/pricing/
- Znuny downloads and releases : https://download.znuny.org/
- OTOBO and Znuny comparison (publisher is OTOBO, discount accordingly) : https://otobo-docs.softoft.de/en/ecosystem/otrs-forks/otobo-znuny-difference/
- OTRS on the Community Edition end of life : https://otrs.com/blog/otrs-community-edition/difference-between-forks-and-otrs/

---

## 8. Revisions, 09/09/2026

This brief was written and then reviewed the same day. Three decisions
changed its standing. They are recorded here rather than by rewriting the
analysis, so the reasoning stays auditable.

1. **Qualification through the informal contact was dropped in full.** A
   nine-question message had been drafted. It was reviewed question by
   question and then killed, to keep a partner relationship clear of
   information-gathering where that person also works at the agency. This is
   consistent with the earlier decision to keep their agency address off
   vendor correspondence.

   Accepted consequences: the reported annual cost figure stays permanently
   unverified, we never establish whether the agency is genuinely
   dissatisfied, and the opportunity now rests entirely on a reply to the
   approach sent 09/09/2026.

2. **Vendor registration is on hold**, rather than being completed now.

3. **Positioning is reopened.** Prime contractor is no longer assumed.

Section 4's platform analysis and section 3's operational profile are
unaffected by all three, because they rest on public primary sources rather
than on our position or on anything the informal contact said.
