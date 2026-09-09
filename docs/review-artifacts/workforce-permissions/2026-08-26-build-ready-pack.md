# SIMS and Ripple Workforce Permissions — Build-Ready Pack

Date: 2026-08-26

Status: Phase A complete; security-sensitive implementation not started

Systems: SIMS (`sifu-tutor`) and Ripple (`ripple-suite`)

## 1. Outcome

The target model is one official staff identity and role, with each system owning
only its own feature permissions:

- SIMS owns staff identity, employment/access status, the official role, SIMS
  role permissions, and SIMS individual extra access.
- Ripple reads the official SIMS role and owns Ripple role bundles, Ripple
  permission dependencies, and Ripple individual extra access.
- A staff member's effective access is the published role bundle plus active
  individual extras plus required view dependencies.
- Role-inherited and dependency-inherited permissions are visible but cannot be
  unticked on the staff page.
- Sensitive actions are separate permissions and never arrive through a vague
  `Manage` permission.
- A new official SIMS role appears in Ripple as `Access pending` until a Ripple
  bundle is configured and published.
- Permission changes use draft, review summary, explicit publish, audit receipt,
  and restore-previous-version. Checkboxes do not save immediately.

This removes the current split-brain behavior without changing anyone's access
based on guesswork.

## 2. Evidence From Current Production And Committed Code

### SIMS

- Production has 12 active official role codes and no duplicate role codes.
- Production has 463 web permissions.
- The current SIMS role editor exposes 301 rows representing 297 unique keys.
- Four rows are duplicated in the editor:
  `mobile-notification-list`, `mobile-notification-add`,
  `mobile-notification-delete`, and `user-logs-list`.
- 166 database permissions are absent from the current role editor.
- 161 of those 166 have no current committed application reference and are
  strong archive candidates, subject to the migration preflight.
- SIMS still exposes approximately 83–85 Ripple-only feature keys and seeds
  them into SIMS roles even though Ripple's workforce runtime does not use
  those SIMS selections.
- `commitment-fees.waive-any-request` is present in production and assigned to
  roles, but current committed code never checks it. The real waiver action
  checks `commitment-fees.waive`; the old key is a dead permission.
- The source-controlled canonical-role list does not fully represent the 12
  roles that exist in production, so `SUPER_ADMIN` and `PRODUCTION_QA` must be
  made first-class without overwriting production assignments.

### Ripple

- Production contains 7 legacy local roles, 116 staff-role assignments, and
  190 legacy role-permission rows.
- Production also contains the separate, real workforce projection with 12
  official SIMS roles and 200 projected users.
- Only 43 of the 116 users in the legacy local-role system overlap a projected
  workforce account.
- Legacy role names conflict with official roles. For example, legacy
  `CX Onboarding` is assigned to staff whose official roles include Admin,
  Finance, Sales, Operations, Tutor Experience, and Customer Experience Admin.
- Ripple's live workforce authorization ignores the legacy local role matrix.
  It resolves a hard-coded bundle from the official SIMS role code.
- The old Ripple Staff Roles page still creates, renames, deletes, assigns, and
  immediately edits the legacy local roles, so it can report success without
  changing the access used by ordinary workforce sessions.
- Ripple's old Luna per-role tool overrides are keyed by the legacy numeric role
  ID. Workforce sessions use no applicable local role ID; production currently
  has no `role_tools` override entries.
- The projected SIMS permission arrays are stored in Ripple but are not the
  Ripple feature authority. This is correct for the target architecture, but
  the old SIMS UI and contract wording incorrectly imply otherwise.

## 3. Source Of Truth And Runtime Contract

```text
SIMS staff record
  -> official role code and active/inactive state
  -> signed workforce projection to Ripple

SIMS runtime
  -> published SIMS role bundle
  + active SIMS individual extras
  + SIMS dependency closure

Ripple runtime
  -> published Ripple bundle for the projected official role code
  + active Ripple individual extras keyed by SIMS user ID
  + Ripple dependency closure
```

Rules:

1. Access checks are server-side. Disabled buttons are explanation, not
   security.
2. `Manage` includes the required `View` permission only. It does not include
   approvals, exports, payments, deletion, publishing, security, QuickBooks, or
   MyInvois actions unless named explicitly.
3. A direct extra may only add access. Deny-overrides are out of scope because
   they make effective access difficult to understand and audit.
4. When a role later includes an individual extra, publish retires the now
   redundant direct grant with an audit record. Removing that role permission
   later does not silently reactivate the retired grant.
5. A staff role change takes effect only from a published official-role
   assignment. Ripple then recalculates from its bundle for the new role.
6. Inactive, archived, or deleted staff fail closed even if a bundle or direct
   grant exists.
7. Super Admin remains protected. A publish cannot remove the last active
   protected Super Admin or remove the publisher's own ability to administer
   access.
8. Existing active sessions carry an access version. A publish invalidates or
   refreshes stale sessions before the next protected action.

## 4. User Experience

### 4.1 Access overview

Use SIMS Pattern E (Settings), with calm operational density rather than large
cards.

The overview is a compact table with:

- role name and immutable role code;
- system (`SIMS` or `Ripple`);
- status: `Published`, `Draft changes`, `Access pending`, or `Archived`;
- number of active staff;
- number of enabled permissions;
- last published by and time;
- actions: `View`, `Edit draft`, `Review changes`, and `View history` as allowed.

The role list must not offer a Ripple role assignment. Ripple shows the
official SIMS role read-only with the copy: `Official role is managed in SIMS.`

### 4.2 Role permission editor

- Search by module, permission label, or description.
- Module groups are collapsible but search automatically opens matches.
- Each permission row shows a clear label, short description, and optional
  badge: `Financial`, `Security`, or `Destructive`.
- Vague or non-obvious rows have an accessible information icon. Hover, focus,
  or tap explains what the permission allows, excludes, and automatically
  includes.
- Dependencies are checked and disabled with `Required by <permission>`.
- A sticky summary shows selected permission count and draft change count.
- `Review changes` opens a before/after summary grouped into Added, Removed,
  Automatic dependencies, Staff affected, and Individual grants retired.
- Publishing requires a reason and produces a receipt. The button is
  `Publish access changes`, not `Save` or `Submit`.

### 4.3 Staff access editor

Both systems use the same states and wording:

- `From role` — checked and disabled.
- `Required dependency` — checked and disabled, with the source permission.
- `Individual extra` — checked and editable by Super Admin.
- `Not granted` — unchecked and editable by Super Admin.
- `Retired extra` — history only; it does not reactivate automatically.

The staff page shows all permissions for that system. It does not mix SIMS and
Ripple permissions into one save operation.

### 4.4 Locked actions for ordinary staff

- If staff can already view a page but cannot perform a related action, show
  the action disabled with a lock icon.
- Selecting or focusing it shows: `You do not have access to this action.
  Contact your manager or system administrator if you need it for your work.`
- Do not build an access-request form, queue, approval, notification, or ticket.
- If staff lack the module's View permission, the module and its sensitive data
  remain hidden and direct navigation returns a safe access-denied page. Do not
  expose every company feature to everyone merely to advertise it.

### 4.5 Required states

| State | Required behavior |
| --- | --- |
| Loading | Stable skeleton rows; controls do not jump |
| No roles | Explain how an official role is created in SIMS |
| Filtered empty | Offer `Clear filters` |
| Access pending | Explain that the system bundle must be configured and published |
| Read-only viewer | Show effective access and history; no editable-looking controls |
| Draft conflict | Stop publish and show who published a newer version |
| Publish in progress | Prevent duplicate publish |
| Partial sync failure | Keep the previous published version active and show recovery |
| Permission lost during edit | Stop and refresh; never accept the stale write |
| Restored version | Show the restored version as a new audited publication |

## 5. Permission Catalogue Actions

Internal keys remain stable when only wording changes. A new key is required
when one old key controls materially different actions.

### 5.1 Retire or archive

| Current item | Action | Reason / replacement |
| --- | --- | --- |
| Ripple local role creation, rename, delete, and assignment | Remove from active UI and disable writes after cutover | It does not control workforce access |
| Ripple `roles`, `staff_roles`, `role_permissions` as runtime authority | Archive read-only after reconciliation | Preserve audit; never use as migration truth |
| SIMS Ripple-only permission sections | Remove from SIMS editor and role publishing | Ripple owns Ripple permissions |
| SIMS shared Ripple catalogue as assignable authority | Retire; keep only a versioned compatibility boundary if the projection needs it temporarily | Current wording creates split ownership |
| Ripple `knowledge_eval` | Retire into `knowledge_evaluation_manage` | Legacy duplicate; proxy already treats the canonical key as authoritative |
| SIMS `commitment-fees.waive-any-request` | Archive after confirming no historical consumer | Dead permission; real action uses `commitment-fees.waive` |
| SIMS `operation-report-nakngaji-product-commission` | Archive grant and key | Feature is already declared retired in code |
| SIMS legacy `user-role-list`, `user-role-add`, `user-edit-edit`, `user-edit-delete` | Migrate to governed workforce-access permissions | Ambiguous legacy role CRUD |
| SIMS `level-list` / `subject-list` aliases | Archive after navigation cleanup | Modern keys are `level-view-list` / `subject-view-list` |
| SIMS `operation-report-invoice-status` | Remove stale navigation gate unless a real report route is restored | Current legacy menu checks a permission but renders no report link |
| Duplicate SIMS Mobile Notification and Activity Log rows | Collapse into one catalogue location per key | Same permission appears more than once |
| Ripple numeric-role Luna overrides | Retire or migrate by official role code | Numeric local roles do not apply to workforce sessions |

Database records are archived, not hard-deleted, during the first release.

### 5.2 Split before the new editor is published

| Current Ripple permission | Target permissions |
| --- | --- |
| `profiles_manage` | Generate tutor profiles; Edit tutor profiles; Confirm tutor profiles; Delete tutor profiles (Destructive) |
| `rating_write` | Create conduct records; Edit conduct records; Delete conduct records (Destructive) |
| `qa_manage` | View QA monitor; Manage QA checks and defects |
| `prompt_templates` | Configure profile display; Configure AI profile prompts |
| `accounts_write` | Record customer payment; Manage customer receipt allocation; Create credit/debit notes |
| `accounts_approve` | Review credit/debit notes; Void approved credit/debit notes (Financial) |
| `reconciliation_write` | Import bank statements; Resolve suspense items; Unlink reconciled matches (Financial) |
| `crm.view_tasks` | View CRM tasks; Complete CRM tasks |
| `crm.manage_leads` | Edit leads and stages; Run bulk lead changes |
| `crm.trigger_sims_poll` | View SIMS integration health; Run SIMS reconciliation |
| `crm.manage_integration_health` | Acknowledge integration incidents; Retry integration events; Repair integration records |
| `knowledge_base_manage` | Create/edit knowledge documents; Delete knowledge documents (Destructive) |
| `knowledge_source_manage` | Create/edit knowledge sources; Remove knowledge sources (Destructive) |
| `releases_manage` | Create/edit release notes; Publish release notes |
| `tutor_experience_suspend` | Suspend tutor verification; Restore tutor verification |
| `tutor_commitment_fee_share` | View/copy tutor payment links; Regenerate tutor payment links (Financial) |
| `collection_log_contact` | Log collection contact; Upload collection receipt; Archive collection invoice |
| `collection_notes_manage` | Edit collection notes; Delete collection notes (Destructive) |
| `collection_manage_blasts` | Prepare WhatsApp collection campaigns; Send/cancel collection campaigns |
| `pv_approve` | Approve/reject payment vouchers; Manage voucher banks; Configure voucher accounting integration |

The implementation audit must trace every route and handler currently using an
old combined key and assign it to exactly one target action. No old key is
removed until that route matrix has zero unresolved consumers.

### 5.3 Add governance permissions

Each system needs its own stable governance permissions:

- View role access.
- Edit role access drafts.
- Publish role access changes (Security).
- Restore a previous role access version (Security).
- View staff effective access.
- Grant staff individual extra access (Security).
- View access audit history.

SIMS additionally needs:

- Create official roles.
- Archive/restore official roles.
- Assign official staff roles.

Ripple does not receive those three actions.

### 5.4 Rename visible labels without changing behavior

Apply this rule to the complete catalogue, not just the examples below:

| Current label | Target label |
| --- | --- |
| `List`, `View List`, `List / View` | `View <record plural>` |
| `Add` | `Create <record>` |
| `Edit` | `Edit <record>` |
| `Delete` | `Delete <record>` |
| `Manage Records` | Split into the exact record actions |
| `API Usage` | `View AI usage and cost` |
| `Staff Roles` / `Manage Roles` | `View role access` / governed edit and publish actions |
| `Prepare QB Export` | `Prepare QuickBooks invoice export` |
| `Confirm QB Import` | `Record QuickBooks import results` |
| `Ask AI Chat` | `Use Luna AI` |
| `Write Accounts` | Split into exact payment/receipt/note actions |
| `Write Reconciliation` | Split into exact import/resolve/unlink actions |
| `Trigger SIMS Poll` | Split into view integration health and run reconciliation |
| `Request` in business labels | `Tutor Request` |

Use `Parent`, `Tutor Request`, `Class`, `Payment slip`, `Commitment fee`,
`MyInvois`, and `QuickBooks` consistently. Keep internal permission keys out of
ordinary staff copy; they remain available in audit/export detail.

### 5.5 Keep, but expose honestly

- Existing responsibility-specific permissions that already map to one action
  can retain their stable keys and receive clearer labels/descriptions.
- Revenue permissions remain in Ripple's catalogue, but while the Revenue
  runtime is disabled they must show the administrator status `Feature not active`
  and must not make ordinary staff think the empty ledger is usable.
- The protected `platform.staffless-recovery-access` permission stays hidden
  from normal role and individual-extra editors. It is a break-glass control,
  not ordinary staff access.

## 6. Role Defaults And Related-Information Access

Migration starts from each staff member's current effective official-role
access. It does not use the legacy Ripple role name. Default intent is:

| Official role | Default intent |
| --- | --- |
| Super Admin | All enabled permissions plus access governance; protected |
| Admin | Broad operational access; sensitive actions retained only where the current approved bundle already grants them |
| Finance & Accounting | Manage finance, invoices, payments, reconciliation, tutor payments, collections, and payment vouchers; broad related record views |
| Customer Experience (Admin) | CX Support operations plus broad parent, student, tutor, Tutor Request, class, invoice, and payment context |
| Customer Experience (Sales) | Lead and Tutor Request creation/matching workflow plus broad related context |
| Helpdesk | Combined CX Sales and CX Support actions, including Tutor Request creation, matching, and profile delivery; broad related context |
| Marketing | Read-only business outcomes and analytics, including relevant invoice/revenue context; marketing-owned actions only |
| Operation Manager | Broad operational management and related context; finance/security actions remain separately named |
| People & Culture | HR/staff management in SIMS and broad read-only operational context in Ripple |
| Production QA | Broad read-only production context plus QA operations; never automatic production superuser access |
| Tutor Experience | Tutor verification, commitment fee, tutor bank maintenance, and related operational context |
| Viewer | Broad read-only operational context; no mutations |

Before publish, generate a staff-by-staff diff of lost and gained permissions.
Any unexplained change blocks migration. Deliberate bundle improvements are a
separate reviewed publication after parity is proven.

## 7. Data Model And Publication

### Shared concepts

- Catalogue version.
- Role bundle draft and published versions.
- Immutable publication record with actor, reason, before/after diff, affected
  staff count, and checksum.
- Individual grant with source, status, granted by/at, retired by/at, and reason.
- Permission dependency metadata.
- Effective-access version for cache/session invalidation.

### SIMS

- Keep official roles and primary role assignment in SIMS.
- Store published SIMS role-permission versions separately from the mutable
  draft.
- Use the existing staff identity as the individual-grant key.
- Publish a workforce snapshot containing identity, access-active state,
  official role identity/version, and contract metadata. Do not publish
  Ripple-only feature grants as SIMS authority.

### Ripple

- Store Ripple role bundles by immutable official SIMS role code, never by
  legacy local numeric role ID.
- Store Ripple individual extras by stable SIMS user ID.
- Keep the current hard-coded official-role bundles as rollback baseline
  version 0 until the new published configuration has passed production smoke.
- Do not use the legacy local role matrix as rollback authority.

### Concurrency and retry

- Drafts carry a base version. Publish uses compare-and-swap; a stale draft
  cannot overwrite a newer publication.
- A repeated publish request with the same idempotency key returns the original
  publication receipt.
- If audit storage or effective-access materialization fails, the publication
  does not become active.
- Ripple projection retries are idempotent by source event ID and checksum.
- During a SIMS-to-Ripple outage, the last confirmed Ripple bundle remains
  active for already-known active staff; newly unknown roles remain Access
  pending. Inactive/revoked identities continue to fail closed according to the
  existing workforce outage policy.

## 8. Migration And Rollback

1. Snapshot current SIMS roles, role permissions, direct grants, current Ripple
   official bundles, legacy Ripple roles, sessions, and catalogue versions.
2. Add new versioned tables and read-only APIs without changing authorization.
3. Generate the canonical catalogues and fail the build on duplicate keys,
   unknown dependencies, cycles, or unlabelled sensitive actions.
4. Backfill published version 0 from the current effective official-role access.
5. Backfill individual extras only from a verified source. Do not infer extras
   from conflicting legacy Ripple roles.
6. Produce a before/after staff matrix for every active staff account in both
   systems. Block on unexplained gain or loss.
7. Enable the new UI read-only and compare its effective-access explanation
   with the existing runtime.
8. Enable draft/publish for Super Admin while authorization still reads version
   0 unless an explicit publication is activated.
9. Publish the parity bundles, invalidate stale sessions, and run role-based
   human journeys.
10. Disable legacy role writes and replace the old Ripple Staff Roles page.
11. Remove Ripple-only permission editing from SIMS and update the projection
    contract wording/tests.
12. Archive dead/duplicate permission keys after a zero-consumer scan.
13. Monitor access-denied spikes, unexpected access grants, session refresh,
    projection lag, and publication failures.

Rollback activates the previous published version, writes a new restore audit
record, invalidates sessions, and re-runs the staff parity report. Before the
first successful new publication, Ripple can return to hard-coded bundle
version 0. It must never fall back to the misleading legacy local-role matrix.

## 9. Test And Human-Journey Evidence

### Permanent automated coverage

SIMS:

- canonical catalogue uniqueness and complete labels;
- scan route middleware, controllers, Form Requests, policies, gates,
  navigation, and service checks for unknown/orphan permissions;
- role plus individual-extra union and dependency closure;
- individual-extra absorption and no silent reactivation;
- draft conflict, idempotent publish, audit receipt, and restore;
- protected last Super Admin and self-lockout prevention;
- new role Access pending contract;
- inactive staff fail closed;
- Playwright role editor, staff effective-access editor, locked action, and
  read-only People & Culture/Admin journeys.

Ripple:

- all proxy and handler permission checks belong to the canonical catalogue;
- every sensitive API route maps to its exact split permission;
- official-role bundle plus individual-extra union;
- unknown/unconfigured role Access pending;
- cache/session version refresh after publish;
- Luna tool policy keyed by official role code or staff extra, not local role ID;
- old role APIs reject writes after cutover;
- Playwright overview, draft/review/publish/restore, staff extra access, locked
  action, and representative role journeys.

### Required role smoke set

- Super Admin: edit, review, publish, restore, grant individual extra.
- Admin: expected broad access without bypassing protected Super Admin rules.
- Finance: invoice/payment/reconciliation actions and related views.
- Helpdesk: CX Sales plus CX Support workflows.
- Marketing: relevant analytics and invoice context, no finance mutation.
- People & Culture: staff/role read access and HR work, no access publish.
- Production QA: broad read and QA operations, no production superuser access.
- Viewer: related views only; locked-action message is clear.

Evidence must include focused tests, permanent E2E, desktop screenshots of the
default/draft/review/read-only/locked/error states, and production read-only
smoke after deployment. Code-level tests alone are insufficient.

## 10. Adversarial Review Findings

### Critical

1. **Two Ripple role systems present conflicting truths.** The legacy UI can
   save data that ordinary workforce authorization does not consume. Replace
   the UI and disable legacy writes at cutover.
2. **SIMS claims authority over Ripple feature keys that Ripple ignores.** Remove
   the Ripple-only editor sections from SIMS and correct the projection
   contract.
3. **Combined permissions conceal materially different financial, destructive,
   bulk, publishing, and integration actions.** Split them before making the
   editor the authoritative configuration surface.

### High

4. **Legacy role assignments cannot be migrated by name.** Production evidence
   shows widespread conflict with official SIMS roles. Migrate from current
   effective official-role access and keep legacy rows as audit only.
5. **Hard-coded bundles have no business-user publication or rollback trail.**
   Add versioned draft/publish/restore; keep the hard-coded bundle as version 0
   fallback during cutover.
6. **Ripple has no runtime individual-extra model for workforce users.** Add it
   by stable SIMS user ID and explain effective access in the UI.
7. **Session/cache staleness can leave revoked access usable.** Version every
   effective-access result and recheck server-side on protected actions.
8. **SIMS catalogue drift is not fully tested.** Current tests do not cover all
   controller/service/navigation enforcement and allow database-only dead keys.

### Medium

9. **Duplicate and vague SIMS rows make the matrix harder to understand.** Use
   one canonical catalogue and complete action-plus-record labels.
10. **Luna role tool settings are a dead end for workforce sessions.** Migrate
    to official role codes or remove the per-role control if it remains empty.
11. **Revenue permissions can imply a usable module while Revenue is inactive.**
    Display an honest inactive state until the separate Revenue activation is
    completed.
12. **Read-only and no-access UI are currently conflated.** Show effective
    access to authorised Admin/People & Culture, editable drafts only to Super
    Admin, and a simple locked-action explanation to ordinary staff.

## 11. Implementation Slices

1. Canonical catalogue and static completeness tests.
2. Versioned draft/publish/restore and audit model in SIMS.
3. SIMS role editor and staff individual-extra UX.
4. SIMS projection contract cleanup and Access pending behavior.
5. Versioned Ripple role bundles and individual extras.
6. Split Ripple permissions and route/handler migration.
7. Ripple access overview/editor/staff UX and locked actions.
8. Shadow parity, production migration, legacy write shutdown, and archive.
9. Permanent E2E, screenshot review, production smoke, and monitoring.

Each slice uses vertical-slice TDD and cannot weaken existing enforcement while
the next slice is incomplete.

## 12. Security-Sensitive Stop Point

This document completes diagnosis, product decisions, architecture, migration,
rollback, UX, and adversarial review. It does not authorize changing role
assignments, permission grants, authentication behavior, database schemas, or
production access. Those changes begin only after explicit Phase B approval.
