# Test plan: Auth, Roles & Multi-tenancy

> Exhaustive manual catalog for sign-up, sign-in, password reset, invites, role resolution,
> route/API gating, and cross-tenant isolation. Format + method: [QA-METHODOLOGY.md](QA-METHODOLOGY.md).
> Style/depth matched to [test-plan-billing.md](test-plan-billing.md).
>
> **Rewritten 2026-07-04 for the Better Auth migration** (Clerk removed 2026-07-02). Auth stack is now
> **Better Auth** (email + password, organization plugin as the tenant boundary, roles ASSIGNED on the
> membership at invite time). Grounding commits: 684d456 (Better Auth core + org role model), ddb9f4d
> (Clerk removed), 37d499e (link-based invites with assigned roles), 06b08ab (password reset + email
> verification via Resend), b175d3e (teacher self-service), 561d9ab (branded auth screens), 2b53ee7
> (missing-membership denial), 3cddbee (invite landing + centre switcher), b68ac79 (BM term alignment).
>
> Grounded in `src/libs/auth-server.ts` (Better Auth instance), `src/libs/Access.ts` (getAccessContext,
> requireOperator/requireOperatorContext, requireOwner/requireOwnerContext, requireTeacher),
> `src/libs/access-role.ts` (toAppRole, resolveMemberRole: a MISSING membership row throws, never
> defaults to staff), `src/libs/Auth.ts` (requireOrgId), `src/proxy.ts` (middleware cookie gate),
> the operator route-group guard `(auth)/dashboard/(operator)/layout.tsx`, `api/attendance/route.ts`
> (teacherBlocked ownership scoping), `api/payouts/[id]/pdf/route.ts` (own-payslip scoping),
> `src/features/auth/*` (SignInForm, SignUpForm, ForgotPasswordForm, ResetPasswordForm, AcceptInvite,
> InviteMembers, OrgOnboarding), and `src/features/dashboard/account-menu.tsx` (centre switcher).
> Default tier **T1** (auth + isolation: the highest stakes across ~100 centres).
>
> Roles (assigned on the Better Auth org membership, per `access-role.ts`):
> - **operator**: the centre owner (org creator; membership role `owner`/`admin`/`operator`). Full access,
>   including owner-only payment settings and member management.
> - **staff**: membership role `staff`/`member`/anything unknown. Operational access; blocked from
>   owner-only settings pages/APIs; cannot invite members.
> - **teacher**: membership role `teacher` (assigned on the invite). Attendance for own classes,
>   My classes, My pay, own payslip. The matching `teachers` record is picked by email on first login;
>   the ROLE never comes from the email match (the old Clerk footgun is gone).
> - **public**: token-only access (public invoice page), no login.
>
> **Grounded status-code / redirect map (do not guess):**
> - No session cookie on a `/dashboard` or `/onboarding` page -> middleware **redirects to `/sign-in`** (proxy.ts).
> - Signed-in user opening `/sign-in` or `/sign-up` -> middleware **redirects to `/dashboard`**.
> - No auth on any API -> **401** `{ "error": "Not authenticated" }`.
> - Authenticated but no active centre: API -> **401** `{ "error": "No active organisation selected" }`;
>   guarded pages -> **redirect** to `/onboarding/organization-selection`.
> - Session points at a centre the user is no longer a member of (removed member) -> API **401**
>   `{ "error": "Not a member of this organisation" }`; pages redirect to onboarding (2b53ee7).
> - Teacher on an operator API (requireOperatorContext) -> **401** `{ "error": "Forbidden: operators only" }` (not 403).
> - Staff or teacher on an owner-only API (requireOwnerContext) -> **401** `{ "error": "Forbidden: owner only" }`.
> - Teacher on an operator page -> **redirect** to `/dashboard/attendance`. Staff on an owner-only page ->
>   **redirect** to `/dashboard/billing`. Operator/staff on a teacher self-service page -> **redirect** to `/dashboard`.
> - Teacher on an attendance class they do not teach -> **403** `{ "error": "Forbidden" }` (teacherBlocked).
> - Teacher fetching a payslip PDF that is not their own -> **404** (deliberately not 403; hides existence).
> - Cross-tenant record by id (page or API) -> **404 / not-found** (service query scoped by orgId returns null).
>
> **Shared test state (dev/staging):** operator login `operator@kelastest.local` / `newpassword6789`;
> teacher login `teacher@kelastest.local` / `password12345`. URLs shown unprefixed are the English
> locale; prepend `/ms` for Bahasa Melayu (e.g. `/ms/sign-in`). Where a string is user-facing the
> expected result quotes the exact EN string with the BM equivalent in parentheses.
>
> Smoke subset (@smoke): TC-AUTH-001, 002, 010, 012, 030, 032, 050, 061, 070, 100, 110, 121, 150.

---

## A. Sign-in & onboarding redirect

### TC-AUTH-001: Sign in with one centre lands the operator on the dashboard
**Tags**: @smoke @regression **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-1 | **Risk**: R-AUTH-signin | **Type**: E2E
**Before you start**: Start logged out (private/incognito window). Use the dev operator account, which belongs to exactly one centre.
**Test Data**: email `operator@kelastest.local`, password `newpassword6789`.
| Step | Action |
|------|--------|
| 1 | Open `/sign-in`. Confirm the branded card: Kelasapp logo above a card titled "Sign in to Kelasapp" (BM: "Log masuk ke Kelasapp") |
| 2 | Enter the email and password, press "Sign in" (BM: "Log masuk") |
| 3 | Wait for the redirect to settle |
**What you should see**: While submitting the button reads "Signing in..." (BM: "Sedang log masuk..."). Because the account belongs to exactly one centre, that centre is activated automatically and you land on `/dashboard` with the full operator sidebar (Dashboard; Classes, Teachers, Attendance; Students, Guardians; Billing, Teacher pay; Business, Payments, Invoicing, Programs, Levels, Members). No onboarding screen, no error.
**What you actually saw**: ___
**Status**: Pass / Fail / Blocked

### TC-AUTH-002: Signed-in user with no centre is sent to onboarding
**Tags**: @smoke @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-2 | **Risk**: R-AUTH-noorg | **Type**: E2E
**Before you start**: A Better Auth user that belongs to no centre (a fresh sign-up that has not created or joined one; see TC-AUTH-100 steps 1-3 to make one). Sign in as that user.
| Step | Action |
|------|--------|
| 1 | Sign in; note where the app sends you |
| 2 | Manually navigate to `/dashboard` |
**What you should see**: Both routes end on `/onboarding/organization-selection` showing "Set up your centre" (BM: "Sediakan pusat anda"). The dashboard never renders and no centre data is shown. (Grounded: sign-in with zero centres pushes onboarding; the page guard turns "No active organisation selected" into the same redirect.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-003: Logged-out user opening a dashboard URL is sent to sign-in
**Tags**: @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-2 | **Risk**: R-AUTH-unauth | **Type**: E2E
**Before you start**: Fully logged out (clear cookies / private window).
| Step | Action |
|------|--------|
| 1 | Paste a deep dashboard URL directly, e.g. `/dashboard/billing`, into the address bar |
| 2 | Repeat with `/onboarding/organization-selection` |
**What you should see**: Neither page renders. The middleware redirects each to `/sign-in` ("Sign in to Kelasapp"). No centre data, no dashboard chrome. (Grounded: proxy.ts cookie check covers both `dashboard` and `onboarding` paths.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-004: Onboarding lets the user create a centre or continue to an existing one
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: US-AUTH-2 | **Risk**: R-AUTH-orgselect | **Type**: E2E
**Before you start**: Signed in as a user who belongs to at least one centre but has no active centre yet (e.g. a user in 2+ centres straight after sign-in), sitting on `/onboarding/organization-selection`.
**Test Data**: new centre name `Pusat Tuisyen Bestari QA`.
| Step | Action |
|------|--------|
| 1 | Read the card: heading "Set up your centre", existing centres listed under "Continue to a centre" (BM: "Teruskan ke pusat") |
| 2 | Click one of the existing centre buttons |
| 3 | Sign out, sign back in, return to onboarding, and instead type the Test Data name under "Centre name" (BM: "Nama pusat") and press "Create centre" (BM: "Cipta pusat") |
**What you should see**: Step 2: the centre is activated and you land on `/dashboard` in the role you hold in that centre. Step 3: the new centre is created, activated, and you land on `/dashboard` as its **operator** (creator role is operator). No error text ("Something went wrong. Please try again." must NOT appear).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

---

## B. Role resolution & landing

### TC-AUTH-010: Centre creator resolves to operator with the full nav
**Tags**: @smoke @regression **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-3 | **Risk**: R-ROLE-operator | **Type**: E2E
**Before you start**: Sign in as `operator@kelastest.local` / `newpassword6789` (the user who created the centre, so their membership role is `owner`/`operator`).
| Step | Action |
|------|--------|
| 1 | Land on the dashboard and read the left sidebar group by group |
| 2 | Open each Settings item once (Business, Payments, Invoicing, Programs, Levels, Members) |
**What you should see**: Role resolves to **operator**. Sidebar shows every group: Overview (Dashboard), Academic (Classes, Teachers, Attendance), People (Students, Guardians), Finance (Billing, Teacher pay), Settings (Business, Payments, Invoicing, Programs, Levels, Members). Every page opens without a redirect, including the owner-only ones (Business, Payments, Invoicing).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-011: Member invited as Staff resolves to staff
**Tags**: @regression **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-3 | **Risk**: R-ROLE-staff | **Type**: E2E
**Before you start**: A member who joined centre A through an invite with role **Staff** (see TC-AUTH-122 to create one). Sign in as them.
| Step | Action |
|------|--------|
| 1 | Land on the dashboard and read the sidebar |
| 2 | Open Classes, Students, Billing, Teacher pay: all should render |
| 3 | Open Settings > Business |
**What you should see**: Role resolves to **staff**. Steps 1-2: staff sees the same operator sidebar and can open the operational pages. Step 3: the owner-only page does NOT render; you are redirected to `/dashboard/billing` (requireOwner sends non-operators there). Staff is never treated as teacher and never as owner.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-012: Member invited as Teacher resolves to teacher and lands on Attendance
**Tags**: @smoke @regression **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-3 | **Risk**: R-ROLE-teacher | **Type**: E2E
**Before you start**: Sign in as the dev teacher `teacher@kelastest.local` / `password12345` (a member whose membership role is `teacher`, joined via a teacher invite).
| Step | Action |
|------|--------|
| 1 | Sign in and observe the landing page |
| 2 | Read the sidebar |
**What you should see**: Role resolves to **teacher**. Landing settles on `/dashboard/attendance` (sign-in pushes `/dashboard`, the operator group guard bounces teachers to Attendance). The sidebar shows ONLY the teacher items: "Attendance" (BM: "Kehadiran"), "My classes" (BM: "Kelas saya"), "My pay" (BM: "Bayaran saya"). No Billing, no Students, no Settings.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-013: Operator in one centre, staff in another: role follows the active centre
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: US-AUTH-3 | **Risk**: R-ROLE-perorg | **Type**: E2E
**Before you start**: One user who created centre A (operator there) and accepted a **Staff** invite into centre B. Sign in as that user with centre A active.
| Step | Action |
|------|--------|
| 1 | With centre A active, open Settings > Business (owner-only) |
| 2 | Open the account menu (avatar, bottom of sidebar), use "Switch centre" (BM: "Tukar pusat") to switch to centre B |
| 3 | Open Settings > Business again |
**What you should see**: Step 1: the page renders (operator in A). Step 3: redirected to `/dashboard/billing` (staff in B). Role is recomputed from the ACTIVE centre's membership row on every request, never carried over.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

---

## C. Teacher record linking (email picks the record, never the role)

> Since 37d499e the role comes from the membership (assigned on the invite). The email match ONLY
> picks WHICH `teachers` record a teacher-role member is linked to, on their first authenticated
> request: same centre, status `active`, unlinked (`clerk_user_id` NULL; column name retained from
> the Clerk era), emails compared trimmed + lowercased.

### TC-AUTH-020: Teacher's first login links them to the matching teacher record
**Tags**: @regression @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-4 | **Risk**: R-LINK-firstlogin | **Type**: E2E
**Before you start**: As operator of centre A: (1) create a teacher record (Teachers > New teacher) with email `cikgu.baru@kelastest.local` and status active; (2) create an invite with role **Teacher** for that same email and copy the link (Settings > Members). No user with that email exists yet.
**Test Data**: teacher email `cikgu.baru@kelastest.local`, name `Cikgu Aminah binti Hassan`, any password of 8+ characters.
| Step | Action |
|------|--------|
| 1 | In a private window, open the invite link and sign up with the Test Data email |
| 2 | Observe the landing page and sidebar |
| 3 | Open `/dashboard/my-classes` |
| 4 | As operator, open that teacher's profile (Teachers > the row) |
**What you should see**: The new member resolves to **teacher** and lands on `/dashboard/attendance`. My classes shows the classes assigned to the `Cikgu Aminah binti Hassan` record (or the empty state "You're not assigned to any classes yet." if none), proving the record linked. Signing out and back in keeps resolving to the same linked record (no re-matching).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-021: Record match is case-insensitive and whitespace-trimmed
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: US-AUTH-4 | **Risk**: R-LINK-casing | **Type**: E2E
**Before you start**: An active, unlinked teacher record in centre A whose stored email has mixed case and padding: `  Cikgu.Mixed@Kelastest.Local `. If the Teachers form trims on save, set the value directly on `teachers.email` in the DB. Then invite `cikgu.mixed@kelastest.local` with role Teacher and have them sign up via the link.
| Step | Action |
|------|--------|
| 1 | Sign in as that new member for the first time and open `/dashboard/my-classes` |
**What you should see**: The record still links (both sides are trimmed + lowercased before comparing). The member resolves to teacher, lands on Attendance, and My classes reflects the linked record's classes.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-022: An email match never grants the teacher role (role comes from the invite)
**Tags**: @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-4 | **Risk**: R-LINK-nomatch | **Type**: E2E
**Before you start**: Centre A has an active, unlinked teacher record with email `dua.peranan@kelastest.local`. Invite that SAME email with role **Staff** and have the person join via the link.
| Step | Action |
|------|--------|
| 1 | Sign in as the new member and read the landing + sidebar |
| 2 | As operator, open the teacher record with that email and confirm it is still unlinked (no login/link indicator; if in doubt check `teachers.clerk_user_id` stays NULL in the DB) |
**What you should see**: The member resolves to **staff** (operator-style sidebar, no "My classes"/"My pay"). The matching teacher record is NOT claimed: linking only ever runs for members whose assigned role is teacher. This is the regression guard for the old Clerk footgun where an email match silently created a teacher. REGRESSION: role-from-email footgun removed, commit 37d499e (+ 684d456 role model).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-023: Linking only considers teacher records in the active centre
**Tags**: @regression @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-4 | **Risk**: R-LINK-crossorg | **Type**: E2E
**Before you start**: Centre A has an active unlinked teacher record with email `kongsi@kelastest.local`. Centre B has NO teacher record with that email. Invite `kongsi@kelastest.local` into centre **B** with role **Teacher** and have them join via the link (centre B active).
| Step | Action |
|------|--------|
| 1 | Sign in as that member with centre B active; open `/dashboard/my-classes` and `/dashboard/attendance` |
| 2 | As operator of centre A, confirm centre A's `kongsi@` teacher record is still unlinked |
**What you should see**: In centre B the member is a teacher with NO linked record (the linking query is scoped by orgId, so centre A's record is never matched): My classes is empty and every attendance class returns the 403 block of TC-AUTH-063. Centre A's record is untouched. They never see centre A's classes.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-024: Linking ignores inactive and already-linked teacher records
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: US-AUTH-4 | **Risk**: R-LINK-inactive | **Type**: E2E
**Before you start**: Centre A has exactly one teacher record with email `berhenti@kelastest.local`, unlinked but with status **inactive** (archive it from the teacher's profile). Invite that email with role **Teacher**; join via the link.
| Step | Action |
|------|--------|
| 1 | Sign in as that member; open `/dashboard/my-classes` |
| 2 | As the same member, call `GET /api/attendance?classId=<any-centre-A-class-id>&date=<a date that class meets>` (get a class id from the operator; dates in the API are `YYYY-MM-DD`) |
**What you should see**: No link is made (only active, unlinked records are linkable). The member still resolves to teacher (role is from the membership) but with no record: My classes is empty and the attendance call returns **403** `{ "error": "Forbidden" }`. Nothing silently attaches to the archived record.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

---

## D. Teacher blocked from operator pages (redirect)

### TC-AUTH-030: Teacher visiting any operator page is redirected to Attendance
**Tags**: @smoke @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-5 | **Risk**: R-GATE-page | **Type**: E2E
**Before you start**: Sign in as the teacher `teacher@kelastest.local` / `password12345`.
**Test Data**: operator URLs to try one by one: `/dashboard`, `/dashboard/billing`, `/dashboard/payroll`, `/dashboard/students`, `/dashboard/guardians`, `/dashboard/classes`, `/dashboard/teachers`, `/dashboard/setup/programs`, `/dashboard/settings/business`, `/dashboard/billing/settings`, `/dashboard/settings/invoicing`, `/dashboard/organization-profile`.
| Step | Action |
|------|--------|
| 1 | Paste `/dashboard/billing` into the address bar |
| 2 | Repeat with each operator URL in Test Data |
**What you should see**: Every one redirects to `/dashboard/attendance`. No operator page body (no invoice list, no payroll, no student data, no member list) ever renders, even momentarily as data. (Grounded: one `requireOperator` guard in the `(operator)` route-group layout covers all of them.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-031: Teacher CAN reach Attendance and their self-service pages
**Tags**: @regression **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-5 | **Risk**: R-GATE-attendance | **Type**: E2E
**Before you start**: Sign in as a teacher in centre A who is assigned to at least one class.
| Step | Action |
|------|--------|
| 1 | Open `/dashboard/attendance` and open one of their own classes from the day's list |
| 2 | Open `/dashboard/my-classes` and `/dashboard/my-pay` |
**What you should see**: The attendance index and the class roster render (attendance sits outside the `(operator)` route group). The teacher can mark attendance for their own class. "My classes" and "My pay" both render (see section N for their content checks).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-032: Teacher calling an operator API gets 401 (not 403)
**Tags**: @smoke @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-6 | **Risk**: R-GATE-api | **Type**: API
**Before you start**: Sign in as a teacher in centre A in a browser. Use DevTools (Network tab "fetch" replay, or `fetch` in the console) so requests carry that teacher's session cookie.
**Test Data**: operator endpoints to call directly: `GET /api/invoicing/invoices`, `GET /api/students`, `GET /api/classes`, `GET /api/teachers`, `POST /api/invoicing/generate`, `POST /api/payouts/generate`.
| Step | Action |
|------|--------|
| 1 | As the teacher, call `GET /api/invoicing/invoices` |
| 2 | Repeat for each endpoint in Test Data |
**What you should see**: Each returns **HTTP 401** with body `{ "error": "Forbidden: operators only" }`. No invoice/student/class/teacher data is returned. (Grounded: requireOperatorContext throws OrgRequiredError for teachers, mapped to 401 in every route catch block.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-033: Staff CAN call operator APIs (the operator gate blocks only teachers)
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: US-AUTH-6 | **Risk**: R-GATE-staff | **Type**: API
**Before you start**: Sign in as a **staff** member of centre A (joined via a Staff invite).
| Step | Action |
|------|--------|
| 1 | Call `GET /api/invoicing/invoices` as staff |
| 2 | Call `GET /api/classes` as staff |
| 3 | Call `POST /api/payouts/generate` with a valid body as staff |
**What you should see**: HTTP 200 with centre A data (requireOperatorContext allows operator + staff, blocking only role `teacher`). Staff sharing the operational surface, including running payroll, is the DOCUMENTED role model (auth-permissions.ts: staff = "everything operational, EXCEPT the owner-only payment settings and member management"). Owner-only exceptions are asserted in section O.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

---

## E. Direct-URL / direct-POST privilege bypass (control hidden, server still enforces)

### TC-AUTH-040: Teacher direct-POST to a write endpoint is rejected server-side
**Tags**: @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-6 | **Risk**: R-BYPASS-write | **Type**: API
**Before you start**: Teacher session in centre A. Find a real class id you DO have access to from `/dashboard/attendance` (so the id itself is valid) to prove the rejection is on role, not on id.
**Test Data**: `POST /api/classes` with a minimal valid class body; `PATCH /api/invoicing/invoices/<any-id>` with `{ "action": "issue" }`.
| Step | Action |
|------|--------|
| 1 | As the teacher, send `POST /api/classes` with a valid body (the UI button is hidden for teachers; call the API anyway) |
| 2 | Send `PATCH /api/invoicing/invoices/<id>` with `{ "action": "issue" }` |
**What you should see**: Both return **401** `{ "error": "Forbidden: operators only" }`; no class is created, no invoice is issued. The hidden UI control is not the security boundary; the server is.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-041: Staff direct call to an owner-only API is rejected with the owner message
**Tags**: @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-6 | **Risk**: R-BYPASS-staff | **Type**: API
**Before you start**: Staff session in centre A. These endpoints control where parents' money goes (bank account / DuitNow QR) and invoicing configuration, so since the Better Auth migration they are owner-gated (requireOwnerContext), no longer an undocumented gap.
**Test Data**: `PUT /api/settings/business` with a valid body; `GET /api/invoicing/settings`; `PUT /api/invoicing/settings` with a valid body; `PUT /api/settings/invoicing` with a valid body.
| Step | Action |
|------|--------|
| 1 | As staff, call each endpoint in Test Data (the UI never offers these to staff; call them anyway) |
| 2 | Record the exact status + body for each |
**What you should see**: Every call returns **401** `{ "error": "Forbidden: owner only" }` and no setting changes. Note the message differs from the operator gate ("Forbidden: operators only"): that distinction is the audit trail of WHICH gate fired.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-042: Unknown PATCH action on an invoice is rejected, not silently applied
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: US-AUTH-6 | **Risk**: R-BYPASS-action | **Type**: API
**Before you start**: Operator session in centre A; a real invoice id from centre A (open any invoice from Billing and copy the id from the URL).
**Test Data**: `PATCH /api/invoicing/invoices/<id>` with `{ "action": "delete" }` then `{ "action": "" }`.
| Step | Action |
|------|--------|
| 1 | Send the PATCH with action `delete` |
| 2 | Send the PATCH with an empty action |
**What you should see**: HTTP **422** `{ "error": "Unknown action" }` for each; the invoice is unchanged. No undefined action path mutates data. (Same contract on `PATCH /api/payouts/<id>`.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

---

## F. Cross-tenant IDOR per representative record (URL id + API)

> Setup for all F-cases: two centres, A and B. As operator of centre **B**, obtain a real centre **A**
> record id (from a known seed/fixture or a separate centre-A session) for: a class, a student, an
> invoice, a payout, and a teacher. The id is valid; the only thing wrong is that it belongs to
> centre A. Stay authenticated as centre B.

### TC-AUTH-050: Cross-tenant: centre B cannot open centre A's class (page + API)
**Tags**: @smoke @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-7 | **Risk**: R-IDOR-class | **Type**: E2E
**Before you start**: Centre B operator session; a real centre-A class id.
| Step | Action |
|------|--------|
| 1 | As centre B, open `/dashboard/classes/<centre-A-class-id>` |
| 2 | As centre B, call `GET /api/classes/<centre-A-class-id>` |
**What you should see**: Page shows not-found; API returns **404** `{ "error": "Not found" }`. Centre A's class name, roster, and fee never render or return. (Grounded: service query scoped by orgId returns null -> 404.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-051: Cross-tenant: centre B cannot open centre A's student
**Tags**: @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-7 | **Risk**: R-IDOR-student | **Type**: E2E
**Before you start**: Centre B operator; a real centre-A student id.
| Step | Action |
|------|--------|
| 1 | Open `/dashboard/students/<centre-A-student-id>` as centre B |
| 2 | Call `GET /api/students/<centre-A-student-id>` as centre B |
**What you should see**: Not-found page; API **404** Not found. None of centre A's student PII (name, IC, guardian) leaks.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-052: Cross-tenant: centre B cannot open or mutate centre A's invoice
**Tags**: @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-7 | **Risk**: R-IDOR-invoice | **Type**: API
**Before you start**: Centre B operator; a real centre-A invoice id.
| Step | Action |
|------|--------|
| 1 | Open `/dashboard/billing/<centre-A-invoice-id>` as centre B |
| 2 | Call `GET /api/invoicing/invoices/<centre-A-invoice-id>` as centre B |
| 3 | Call `PATCH /api/invoicing/invoices/<centre-A-invoice-id>` with `{ "action":"void","reason":"x" }` as centre B |
**What you should see**: Page not-found; GET returns **404** Not found; the PATCH returns **404** (`not_found` from the service) and does NOT void centre A's invoice. No centre A money data leaks or changes.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-053: Cross-tenant: centre B cannot open or mutate centre A's payout
**Tags**: @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-7 | **Risk**: R-IDOR-payout | **Type**: API
**Before you start**: Centre B operator; a real centre-A payout id.
| Step | Action |
|------|--------|
| 1 | Open `/dashboard/payroll/<centre-A-payout-id>` as centre B |
| 2 | Call `GET /api/payouts/<centre-A-payout-id>` as centre B |
| 3 | Call `PATCH /api/payouts/<centre-A-payout-id>` with `{ "action": "mark_paid" }` as centre B |
**What you should see**: Page not-found; GET **404**; the mutation returns not-found and does NOT change centre A's payout state. Teacher pay figures for centre A never render.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-054: Cross-tenant: centre B cannot open centre A's teacher (PII)
**Tags**: @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-7 | **Risk**: R-IDOR-teacher | **Type**: E2E
**Before you start**: Centre B operator; a real centre-A teacher id.
| Step | Action |
|------|--------|
| 1 | Open `/dashboard/teachers/<centre-A-teacher-id>` as centre B |
| 2 | Call `GET /api/teachers/<centre-A-teacher-id>` as centre B |
**What you should see**: Not-found page; API **404** Not found. Centre A teacher's IC, bank details, and email never leak.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-055: Cross-tenant attendance: centre B cannot read another centre's roster by classId
**Tags**: @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-7 | **Risk**: R-IDOR-roster | **Type**: API
**Before you start**: Operator (or teacher) session in centre B; a real centre-A class id; a valid date the class meets (format `YYYY-MM-DD` in the API).
| Step | Action |
|------|--------|
| 1 | As centre B, call `GET /api/attendance?classId=<centre-A-class-id>&date=<valid-date>` |
**What you should see**: **404** Not found (getRosterForDate is org-scoped and returns null for a foreign class). No centre A roster, no student names, are returned.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-056: Cross-tenant write: centre B cannot POST attendance against centre A's class
**Tags**: @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-7 | **Risk**: R-IDOR-attwrite | **Type**: API
**Before you start**: Operator session in centre B; a real centre-A class id.
| Step | Action |
|------|--------|
| 1 | As centre B, `POST /api/attendance` with a valid body referencing `<centre-A-class-id>` |
**What you should see**: The mark is rejected (the org-scoped service finds no such class in centre B); it surfaces as the `class_not_found` **404** path. No attendance row or frozen pay is written to centre A's class.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

---

## G. Teacher accessing a class they do not teach (in-centre ownership)

### TC-AUTH-061: Teacher reading the roster of a class they do not teach -> 403
**Tags**: @smoke @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-8 | **Risk**: R-OWN-read | **Type**: API
**Before you start**: Teacher in centre A. Identify a class in **the same centre A** that this teacher is NOT assigned to (ask the operator for a class id, or read one off an operator session). Note a date that class meets.
| Step | Action |
|------|--------|
| 1 | As the teacher, call `GET /api/attendance?classId=<not-mine>&date=<valid>` |
**What you should see**: **HTTP 403** `{ "error": "Forbidden" }` (teacherBlocked: role teacher + not isClassTeacher). The roster is NOT returned. Note this is 403, distinct from the cross-tenant 404 and the operator-API 401.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-062: Teacher marking attendance on a class they do not teach -> 403
**Tags**: @regression @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-8 | **Risk**: R-OWN-write | **Type**: API
**Before you start**: Same setup as TC-AUTH-061 (teacher + a same-centre class they are not assigned to).
| Step | Action |
|------|--------|
| 1 | As the teacher, `POST /api/attendance` with a valid body for `<not-mine>` |
**What you should see**: **HTTP 403** Forbidden; no attendance is saved, no frozen pay is computed for that class. The block happens before any write.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-063: Teacher with no linked teacher record is blocked from every attendance class
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-8 | **Risk**: R-OWN-noteacher | **Type**: API
**Before you start**: This state is now first-class reproducible: invite an email with role **Teacher** WITHOUT creating a matching teacher record first (or use the TC-AUTH-024 archived-record setup). Sign in as that member: role is teacher, `teacherId` is null.
| Step | Action |
|------|--------|
| 1 | As that user, call `GET /api/attendance?classId=<any-centre-A-class-id>&date=<valid>` |
| 2 | Open `/dashboard/my-classes` |
**What you should see**: Step 1: **403** Forbidden for ANY class (teacherBlocked returns true when role is teacher and teacherId is null). Step 2: the empty state "You're not assigned to any classes yet." (BM: "Anda belum ditugaskan ke mana-mana kelas."). No roster, no other teacher's data.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-064: Operator/staff are NOT subject to the teacher ownership block
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: US-AUTH-8 | **Risk**: R-OWN-operator | **Type**: API
**Before you start**: Operator in centre A; any class id in centre A and a valid meeting date.
| Step | Action |
|------|--------|
| 1 | As operator, `GET /api/attendance?classId=<any-centre-A-class>&date=<valid>` |
**What you should see**: HTTP 200 with the roster (teacherBlocked returns false for non-teacher roles). Operators/staff may touch any class in their centre.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

---

## H. List endpoints never leak another centre

### TC-AUTH-070: Every list endpoint shows only the current centre's rows
**Tags**: @smoke @regression @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-9 | **Risk**: R-LEAK-list | **Type**: API
**Before you start**: Centre A has known records in every area; centre B also has its own records. Sign in as operator of centre **B**. Know roughly how many centre-A rows exist (so you can confirm none appear).
**Test Data**: list endpoints: `GET /api/classes`, `/api/students`, `/api/guardians`, `/api/teachers`, `/api/invoicing/invoices`, `/api/taxonomy/programs`, `/api/taxonomy/levels`.
| Step | Action |
|------|--------|
| 1 | As centre B, call each list endpoint in Test Data |
| 2 | For each response, confirm every returned row belongs to centre B |
**What you should see**: Each list contains only centre B rows. No centre A class, student, guardian, teacher, invoice, program, or level ever appears. (Grounded: tenant-isolation test exists in every feature service, e.g. "never leaks another org invoices", "isolates students by org".)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-071: List UI pages also show only the current centre's data
**Tags**: @regression @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-9 | **Risk**: R-LEAK-listui | **Type**: E2E
**Before you start**: Same two-centre setup; operator of centre B in the browser.
| Step | Action |
|------|--------|
| 1 | Open Classes, Students, Guardians, Teachers, Billing list pages as centre B |
| 2 | Scan each list |
**What you should see**: Every list is centre-B-only and matches the API result. No centre A row is visible on any screen.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-072: Reports/CSV/PDF exports are centre-scoped
**Tags**: @regression @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-9 | **Risk**: R-LEAK-export | **Type**: API
**Before you start**: Operator of centre B; both centres have attendance data.
| Step | Action |
|------|--------|
| 1 | As centre B, call `GET /api/reports/csv` and `GET /api/reports/pdf` for a date range |
| 2 | Inspect the rows/figures in the output |
**What you should see**: Output contains only centre B students/classes/figures (reports service "isolates reports by org"). No centre A names or numbers appear in the export.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

---

## I. Session expiry / logged-out API

### TC-AUTH-080: Logged-out call to any API returns 401, not data
**Tags**: @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-2 | **Risk**: R-SESSION-noauth | **Type**: API
**Before you start**: No session (clear cookies / private window).
**Test Data**: `GET /api/invoicing/invoices`, `GET /api/students`, `GET /api/attendance?classId=x&date=2026-06-30`.
| Step | Action |
|------|--------|
| 1 | With no session, call each endpoint in Test Data |
**What you should see**: Each returns **401** `{ "error": "Not authenticated" }`. No centre data, no class list, no roster. (Grounded: getSession returns null -> OrgRequiredError 'Not authenticated' -> 401.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-081: Session killed mid-use forces re-auth on the next protected call
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: US-AUTH-2 | **Risk**: R-SESSION-expiry | **Type**: E2E
**Before you start**: Operator signed in with two tabs open on the dashboard. Kill the session from tab 2: open the account menu and choose "Sign out" (BM: "Log keluar"), or delete the Better Auth session cookie in DevTools > Application > Cookies.
| Step | Action |
|------|--------|
| 1 | In the stale tab 1, trigger a protected action (open Billing via the sidebar, or submit any form) |
| 2 | In the same stale tab, call `GET /api/students` from the console |
**What you should see**: The page navigation redirects to `/sign-in` (middleware sees no session cookie); the API call returns **401** `{ "error": "Not authenticated" }`. No stale-session action mutates data.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-082: Authenticated-but-no-active-centre API call returns 401 with the no-org message
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: US-AUTH-2 | **Risk**: R-SESSION-noorg | **Type**: API
**Before you start**: Sign in as a user who belongs to 2+ centres and STOP on the onboarding/centre-pick screen without choosing one (a fresh multi-centre session has no active centre yet). Alternatively use a fresh sign-up that has created no centre.
| Step | Action |
|------|--------|
| 1 | Without picking a centre, call `GET /api/students` from the console |
**What you should see**: **401** `{ "error": "No active organisation selected" }`. No data. (Distinct OrgRequiredError message but same 401 status; no-auth, no-org, and removed-member all map to 401 with distinct messages.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

---

## J. Switching centre context (account-menu centre switcher)

> The switcher lives in the account menu (avatar at the bottom of the sidebar) under the label
> "Switch centre" (BM: "Tukar pusat"). It is HIDDEN for single-centre users and appears only when
> the user belongs to 2+ centres. Added in 3cddbee.

### TC-AUTH-090: Switching the active centre re-scopes all data to the new centre
**Tags**: @regression @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-10 | **Risk**: R-SWITCH-scope | **Type**: E2E
**Before you start**: A user who belongs to both centre A and centre B (e.g. operator of both). Sign in and activate centre A; note a distinctive centre-A class/student name.
| Step | Action |
|------|--------|
| 1 | While on centre A, note the Classes list contents |
| 2 | Open the account menu; under "Switch centre" click centre B (the active centre shows a check mark) |
| 3 | Confirm you land on `/dashboard`, then reopen Classes (and Students, Billing) |
**What you should see**: After the switch every list shows centre B data only; the distinctive centre-A record is gone. The check mark in the switcher now sits on centre B. No centre A data bleeds into the centre B view. (Grounded: setActive re-verifies membership server-side and rewrites `activeOrganizationId` on the session.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-091: After switching centres, the role is recomputed for the new centre
**Tags**: @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-10 | **Risk**: R-SWITCH-role | **Type**: E2E
**Before you start**: A user who is operator of centre A and a teacher (teacher-role member) in centre B. Sign in with centre A active.
| Step | Action |
|------|--------|
| 1 | Confirm the full operator sidebar with centre A active |
| 2 | Switch to centre B via the account menu |
| 3 | Observe the landing + sidebar |
**What you should see**: With centre B active the user resolves to **teacher**: the sidebar collapses to Attendance / My classes / My pay and `/dashboard` redirects to `/dashboard/attendance`. The centre-A operator capability does NOT persist into centre B.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-092: A stale id from the previous centre is not reachable after switching
**Tags**: @regression @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-10 | **Risk**: R-SWITCH-staleid | **Type**: API
**Before you start**: Operator of both centres. While centre A is active, note a real centre-A invoice id. Switch the active centre to B via the account menu.
| Step | Action |
|------|--------|
| 1 | With centre B active, call `GET /api/invoicing/invoices/<centre-A-invoice-id>` |
| 2 | With centre B active, open `/dashboard/billing/<centre-A-invoice-id>` |
**What you should see**: **404** Not found; page not-found. An id that was valid one moment ago (under centre A) is correctly invisible once centre B is the active tenant. Tenant scoping follows the active centre, not the URL.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

---

## K. Sign-up, sign-in negatives & account basics (Better Auth)

### TC-AUTH-100: Sign up, create a centre, and become its operator
**Tags**: @smoke @regression **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-11 | **Risk**: R-SIGNUP-happy | **Type**: E2E
**Before you start**: Logged out, private window. Use an email that has never been registered.
**Test Data**: name `Puan Salmah binti Omar`, email `salmah.qa@kelastest.local`, password `KataLaluan#2026`, centre name `Pusat Mengaji An-Nur QA`.
| Step | Action |
|------|--------|
| 1 | Open `/sign-up`. Confirm the branded card "Create your Kelasapp account" (BM: "Cipta akaun Kelasapp anda") with the hint "At least 8 characters." (BM: "Sekurang-kurangnya 8 aksara.") under Password |
| 2 | Fill the Test Data and press "Create account" (BM: "Cipta akaun") |
| 3 | On the onboarding screen "Set up your centre", enter the centre name and press "Create centre" |
| 4 | Read the sidebar and open Settings > Business |
**What you should see**: Step 2 auto-signs you in and lands on `/onboarding/organization-selection` (a new account has no centre). Step 3 creates + activates the centre and lands on `/dashboard`. Step 4: the full operator sidebar renders and the owner-only Business page opens (creator role is **operator**).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-101: Password shorter than 8 characters cannot create an account
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: US-AUTH-11 | **Risk**: R-SIGNUP-shortpw | **Type**: E2E
**Before you start**: Logged out on `/sign-up`.
**Test Data**: password `abc1234` (7 characters).
| Step | Action |
|------|--------|
| 1 | Fill name/email and the 7-character password, press "Create account" |
| 2 | Bypass the UI: from the console call the sign-up API directly with the same 7-character password (`POST /api/auth/sign-up/email` with `{ "name": "x", "email": "pendek.qa@kelastest.local", "password": "abc1234" }`) |
**What you should see**: Step 1: the browser blocks submission (the field has `minLength={8}`; native "use at least 8 characters" style message) and no request is sent. Step 2: the server ALSO rejects the short password with an error response (Better Auth minimum), and no account for `pendek.qa@kelastest.local` is created (signing in with it fails).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-102: Signing up with an email that already has an account fails cleanly
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: US-AUTH-11 | **Risk**: R-SIGNUP-duplicate | **Type**: E2E
**Before you start**: Logged out on `/sign-up`. Use an email that already exists: `operator@kelastest.local`.
| Step | Action |
|------|--------|
| 1 | Fill the form with the existing email and any valid password, press "Create account" |
**What you should see**: You stay on the sign-up page with an inline error under the form (Better Auth's duplicate-account message; the form falls back to "Could not create the account. Please try again." / BM: "Tidak dapat mencipta akaun. Sila cuba lagi."). No second account is created and the existing account's password is unchanged (the original credentials still sign in).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-103: Wrong password shows an inline error and no session is created
**Tags**: @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-1 | **Risk**: R-SIGNIN-wrongpw | **Type**: E2E
**Before you start**: Logged out on `/sign-in`.
**Test Data**: email `operator@kelastest.local`, password `salahpassword1` (wrong on purpose).
| Step | Action |
|------|--------|
| 1 | Submit the wrong credentials |
| 2 | Without signing in, navigate to `/dashboard` |
**What you should see**: Step 1: an inline error appears in the form (Better Auth's message, typically "Invalid email or password"; the form falls back to "Could not sign in. Check your email and password." / BM: "Tidak dapat log masuk. Semak e-mel dan kata laluan anda."). You remain on `/sign-in`. Step 2: still redirected to `/sign-in`, proving no session cookie was set.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-104: A signed-in user cannot re-open the sign-in or sign-up pages
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Linked**: US-AUTH-1 | **Risk**: R-SIGNIN-bounce | **Type**: E2E
**Before you start**: Signed in as any dashboard user.
| Step | Action |
|------|--------|
| 1 | Paste `/sign-in` into the address bar |
| 2 | Paste `/sign-up` into the address bar |
**What you should see**: Both redirect to `/dashboard` (middleware: auth pages bounce users who already have a session cookie). The sign-in/sign-up forms never render.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-105: Email verification is available but not required (record the contract)
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: US-AUTH-11 | **Risk**: R-SIGNUP-verify | **Type**: Feature
**Before you start**: A freshly signed-up account (TC-AUTH-100) that has never clicked any verification link.
| Step | Action |
|------|--------|
| 1 | Without verifying the email, use the app: create a centre, open pages, call an API |
| 2 | Record whether any screen asks you to verify, and whether anything is blocked |
**What you should see**: Everything works unverified: verification is deliberately NOT required so beta signup stays frictionless (auth-server.ts). The verification mailer exists (subject "Verify your Kelasapp email" via Resend) but no UI currently triggers it. Record this as the pinned contract: if a future change starts requiring verification, this case must be rewritten deliberately, not fail silently.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-106: Account page shows the signed-in user's profile, for every role
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T3 | **Linked**: US-AUTH-11 | **Risk**: R-PROFILE-page | **Type**: E2E
**Before you start**: Signed in (run once as operator, once as teacher).
| Step | Action |
|------|--------|
| 1 | Open the account menu (avatar at the bottom of the sidebar) and click "Account" (BM: "Akaun") |
**What you should see**: `/dashboard/user-profile` renders "Your profile" (BM: "Profil anda") with the user's name and email on a card. Teachers can reach it too (it sits outside the operator route group). The menu header also shows the same name + email above the items.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

---

## L. Password reset (forgot / reset, via Resend)

> Added in 06b08ab. Dev note for testers: when `RESEND_API_KEY` is unset (local dev), the reset
> email is NOT sent; the link is printed in the server log instead (src/libs/Email.ts). On staging
> with the key set, check the real inbox. In production a missing key makes sending fail loudly.

### TC-AUTH-110: Full reset journey: request link, set new password, old one stops working
**Tags**: @smoke @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-12 | **Risk**: R-RESET-happy | **Type**: E2E
**Before you start**: A known account you can receive email for (or read the dev server log). Note its CURRENT password.
**Test Data**: new password `BaruSelamat#99`.
| Step | Action |
|------|--------|
| 1 | On `/sign-in`, click "Forgot password?" (BM: "Lupa kata laluan?") |
| 2 | On "Reset your password" (BM: "Set semula kata laluan anda"), enter the account email and press "Send reset link" (BM: "Hantar pautan set semula") |
| 3 | Open the emailed link (or copy it from the dev server log). It lands on `/reset-password?token=...` |
| 4 | On "Set a new password" (BM: "Set kata laluan baharu"), enter the Test Data password and press "Update password" (BM: "Kemas kini kata laluan") |
| 5 | Sign in with the OLD password, then with the NEW password |
**What you should see**: Step 2 shows the neutral confirmation "If that email has an account, a reset link is on its way. Check your inbox." (BM: "Jika e-mel itu mempunyai akaun, pautan set semula sedang dihantar. Semak peti masuk anda."). Step 4 redirects to `/sign-in`. Step 5: the old password is rejected with the inline sign-in error; the new password signs in successfully.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-111: Unknown email gets the same neutral confirmation (no account enumeration)
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T1 | **Linked**: US-AUTH-12 | **Risk**: R-RESET-enum | **Type**: E2E
**Before you start**: Logged out on `/forgot-password`.
**Test Data**: email `tiada.akaun@kelastest.local` (no account exists for it).
| Step | Action |
|------|--------|
| 1 | Submit the unknown email |
| 2 | Compare the response, wording, and rough response time against TC-AUTH-110 step 2 |
**What you should see**: The identical neutral message "If that email has an account, a reset link is on its way. Check your inbox." Nothing on screen or in the network response reveals whether the account exists. No email is sent to that address.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-112: Reset page without a token shows the invalid-link card
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Linked**: US-AUTH-12 | **Risk**: R-RESET-notoken | **Type**: E2E
**Before you start**: Logged out.
| Step | Action |
|------|--------|
| 1 | Open `/reset-password` directly, with no `token` query parameter |
**What you should see**: No password form. A card titled "Invalid reset link" (BM: "Pautan set semula tidak sah") with "This link is missing its token or has expired." and a "Request a new reset link" (BM: "Minta pautan set semula baharu") link that goes to `/forgot-password`.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-113: A tampered or expired token cannot set a password
**Tags**: @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-12 | **Risk**: R-RESET-badtoken | **Type**: E2E
**Before you start**: Request a real reset link, then alter 2-3 characters in the middle of its `token` value.
**Test Data**: attempted new password `CubaGodam#1`.
| Step | Action |
|------|--------|
| 1 | Open the tampered link; the form renders (the token is only validated on submit) |
| 2 | Submit the Test Data password |
| 3 | Sign in with the account's ORIGINAL password |
**What you should see**: Step 2 shows the inline error "Could not reset your password. The link may have expired." (BM: "Tidak dapat set semula kata laluan. Pautan mungkin telah tamat tempoh."); you stay on the reset page. Step 3: the original password STILL works; nothing changed.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-114: New password under 8 characters is blocked on the reset form
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Linked**: US-AUTH-12 | **Risk**: R-RESET-shortpw | **Type**: E2E
**Before you start**: A valid, fresh reset link open on `/reset-password?token=...`.
**Test Data**: password `pendek7` (7 characters).
| Step | Action |
|------|--------|
| 1 | Enter the 7-character password and press "Update password" |
**What you should see**: The browser blocks submission (field `minLength={8}`); no request is sent and the token is not consumed (submitting a valid 8+ password afterwards still works).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-115: A reset link is single-use
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T1 | **Linked**: US-AUTH-12 | **Risk**: R-RESET-reuse | **Type**: E2E
**Before you start**: Complete a successful reset (TC-AUTH-110) and KEEP the used link.
**Test Data**: second attempt password `GunaSemula#2`.
| Step | Action |
|------|--------|
| 1 | Open the SAME link again and submit the Test Data password |
| 2 | Sign in with the password set in TC-AUTH-110, then with `GunaSemula#2` |
**What you should see**: Step 1 fails with "Could not reset your password. The link may have expired.". Step 2: the TC-AUTH-110 password still works and `GunaSemula#2` does not. A captured link cannot be replayed.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

---

## M. Link-based invites with assigned roles

> Added in 37d499e (+ landing fix in 3cddbee, form alignment f182293). Invites are LINK-based:
> the operator creates an invitation with an assigned role (Teacher or Staff) at Settings >
> Members, then shares the accept link by copy or WhatsApp. No invitation email is sent by design.

### TC-AUTH-120: Operator creates a teacher invite and gets a shareable link
**Tags**: @regression **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-13 | **Risk**: R-INV-create | **Type**: E2E
**Before you start**: Operator session (`operator@kelastest.local` / `newpassword6789`). Open Settings > Members.
**Test Data**: invite email `cikgu.jemput@kelastest.local`, role `Teacher`.
| Step | Action |
|------|--------|
| 1 | Under "Invite a teacher or staff member" (BM: "Jemput guru atau kakitangan"), enter the email, keep Role = "Teacher" (BM: "Guru"), press "Create invite" (BM: "Cipta jemputan") |
| 2 | Confirm the invite appears under "Pending invites" (BM: "Jemputan menunggu") with a "Teacher" role badge |
| 3 | Press "Copy link" (BM: "Salin pautan") and paste it somewhere to inspect |
**What you should see**: The pending row shows the email + role badge. The copied link has the shape `<origin>/<locale>/accept-invite?invitationId=<id>`. No email is sent (by design; the link is the delivery).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-121: A new user joins through the invite link and gets the ASSIGNED teacher role
**Tags**: @smoke @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-13 | **Risk**: R-INV-teacher | **Type**: E2E
**Before you start**: The TC-AUTH-120 invite link for `cikgu.jemput@kelastest.local`; an active teacher record with the same email already exists in the centre (create it first under Teachers). No user account exists for that email yet.
**Test Data**: name `Cikgu Farid bin Musa`, password `JemputanOk#8`.
| Step | Action |
|------|--------|
| 1 | In a private window, open the invite link. Confirm the card "Join your centre" (BM: "Sertai pusat anda") with the hint "Use the email your centre invited." (BM: "Guna e-mel yang dijemput oleh pusat anda.") |
| 2 | Fill name, the INVITED email, and password; press "Join centre" (BM: "Sertai pusat") |
| 3 | Observe the landing page + sidebar |
| 4 | As operator, open Settings > Members |
**What you should see**: Step 2 signs the user up and joins them with the role FROM THE INVITATION. Step 3: teacher landing (`/dashboard/attendance`, teacher-only sidebar). Step 4: the member list now shows `Cikgu Farid bin Musa` with the "Teacher" badge, and the invite is gone from "Pending invites". REGRESSION: assigned-role invites, commit 37d499e.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-122: A staff invite is honored: the invitee becomes staff, not teacher, not owner
**Tags**: @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-13 | **Risk**: R-INV-staff | **Type**: E2E
**Before you start**: As operator, create an invite for `kerani.qa@kelastest.local` with Role = "Staff" (BM: "Kakitangan") and copy the link. No account exists for that email.
| Step | Action |
|------|--------|
| 1 | In a private window, open the link and sign up with the invited email |
| 2 | Read the landing + sidebar; open Classes and Billing; then open Settings > Business |
| 3 | Open Settings > Members as this new user |
**What you should see**: Step 2: staff landing on `/dashboard` with the operator-style sidebar; Classes and Billing open; the owner-only Business page redirects to `/dashboard/billing`. Step 3: the Members page renders the member list but WITHOUT the "Invite a teacher or staff member" form (the invite form renders only for operators).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-123: An already-signed-in invitee accepts with one click
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: US-AUTH-13 | **Risk**: R-INV-signedin | **Type**: E2E
**Before you start**: An existing signed-in user (their own account, any centre or none). As operator of centre A, create an invite for THAT user's email and share the link.
| Step | Action |
|------|--------|
| 1 | As the signed-in invitee, open the invite link |
| 2 | Press "Join centre" |
**What you should see**: Step 1 shows the signed-in variant: "Accept the invitation to join this centre." (BM: "Terima jemputan untuk menyertai pusat ini.") with a single "Join centre" button (no sign-up form). Step 2 joins them with the assigned role and lands on the dashboard of the JOINED centre.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-124: Signing up with a different email than the invited one cannot join
**Tags**: @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-13 | **Risk**: R-INV-wrongemail | **Type**: E2E
**Before you start**: A pending invite for `betul@kelastest.local`. Open its link in a private window.
**Test Data**: sign-up email `salah@kelastest.local` (different from the invited one), any valid password.
| Step | Action |
|------|--------|
| 1 | On the invite landing, sign up with the WRONG email from Test Data |
| 2 | As operator, check Settings > Members and "Pending invites" |
**What you should see**: The join fails with an inline error (Better Auth rejects an accept from a different email; the form falls back to "Could not join. Check the link or ask your centre to resend it." / BM: "Tidak dapat menyertai. Semak pautan atau minta pusat anda hantar semula."). Step 2: `salah@kelastest.local` is NOT in the member list and the invite for `betul@` is still pending. (The wrong-email account may exist as a centre-less user; that is acceptable, membership is what must not exist.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-125: A link with a missing or mangled invitation id fails safely
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: US-AUTH-13 | **Risk**: R-INV-badid | **Type**: E2E
**Before you start**: Logged out or signed in, either works.
**Test Data**: `/accept-invite` (no query), and `/accept-invite?invitationId=tak-wujud-123`.
| Step | Action |
|------|--------|
| 1 | Open `/accept-invite` with no invitationId |
| 2 | Open the mangled-id URL and attempt to join |
**What you should see**: Step 1: the card "Invalid invite link" (BM: "Pautan jemputan tidak sah") with "This link is missing its invitation. Ask your centre for a new one."; no form. Step 2: the form renders but joining fails with the inline join error; no membership is created.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-126: A cancelled invite's link no longer works
**Tags**: @regression @security **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: US-AUTH-13 | **Risk**: R-INV-cancel | **Type**: E2E
**Before you start**: As operator, create an invite and COPY its link. Then press "Cancel" (BM: "Batal") on that pending row.
| Step | Action |
|------|--------|
| 1 | Confirm the row disappears from "Pending invites" |
| 2 | In a private window, open the copied link and attempt to join with the invited email |
**What you should see**: The join fails with the inline error ("Could not join. Check the link or ask your centre to resend it." or Better Auth's own message). No membership is created; the member list is unchanged.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-127: Accepting an invite activates the INVITED centre for a multi-centre user
**Tags**: @regression @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-13 | **Risk**: R-INV-landing | **Type**: E2E
**Before you start**: A signed-in user who already belongs to centre A (and ideally a centre C too). As operator of centre **B**, invite that user's email and share the link.
| Step | Action |
|------|--------|
| 1 | As the multi-centre user, open the link and press "Join centre" |
| 2 | Read which centre's data the dashboard shows (check a distinctive class/student name, and the check mark under "Switch centre" in the account menu) |
**What you should see**: The dashboard lands on centre **B**, the centre from the accepted invitation, with B's data. It must NOT activate a guessed "last in the list" centre. **Notes**: REGRESSION: invite landing activated the wrong centre for multi-centre users; fixed in commit 3cddbee.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-128: Staff cannot create invites, in the UI or by direct API call
**Tags**: @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-13 | **Risk**: R-INV-staffcreate | **Type**: API
**Before you start**: Staff session in centre A (member management is operator-only in the role model: auth-permissions.ts gives staff no invitation grants).
**Test Data**: `POST /api/auth/organization/invite-member` with JSON body `{ "email": "penyusup@kelastest.local", "role": "staff" }`.
| Step | Action |
|------|--------|
| 1 | Open Settings > Members as staff: confirm no invite form is shown |
| 2 | From the console, send the Test Data request with the staff session cookies |
| 3 | As operator, check "Pending invites" |
**What you should see**: Step 2: the Better Auth endpoint rejects the call with an error status (not 2xx); Step 3: NO pending invite for `penyusup@kelastest.local` exists. The hidden form is not the boundary; the permission model is.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-129: The WhatsApp share button carries the invite link and message
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P2 | **Tier**: T2 | **Linked**: US-AUTH-13 | **Risk**: R-INV-whatsapp | **Type**: E2E
**Before you start**: Operator session with at least one pending invite visible.
| Step | Action |
|------|--------|
| 1 | On a pending invite row, click the "WhatsApp" button (it opens a new tab) |
| 2 | Inspect the prefilled message in the wa.me composer |
**What you should see**: A `https://wa.me/?text=...` tab opens with the message "You've been invited to join our centre on Kelasapp. Open this link to join: <link>" (BM: "Anda dijemput untuk menyertai pusat kami di Kelasapp. Buka pautan ini untuk menyertai: <link>"), where <link> is the same accept link as "Copy link". WhatsApp-first sharing is a primary path for Malaysian centres, hence P2.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

---

## N. Teacher self-service (My classes / My pay / own payslip)

> Added in b175d3e. Pages are guarded by requireTeacher (non-teachers are redirected to `/dashboard`);
> row scoping is by the linked teacherId; the payslip PDF hides other teachers' payouts behind 404.

### TC-AUTH-130: My classes shows only the signed-in teacher's classes
**Tags**: @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-14 | **Risk**: R-SELF-classes | **Type**: E2E
**Before you start**: Teacher session (`teacher@kelastest.local` / `password12345`) linked to a record with at least one assigned class; the centre must also have classes taught by OTHER teachers (verify via an operator session).
| Step | Action |
|------|--------|
| 1 | Open "My classes" from the sidebar |
| 2 | Compare the list against the operator's Classes list filtered by this teacher |
**What you should see**: The page titled "My classes" (BM: "Kelas saya") lists exactly the classes assigned to this teacher (name, schedule days/times, program/level) and none taught by anyone else. With no assignments it shows "You're not assigned to any classes yet." (BM: "Anda belum ditugaskan ke mana-mana kelas.").
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-131: My pay shows only the teacher's own months, with paid vs in-process states
**Tags**: @regression @security @data-integrity **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-14 | **Risk**: R-SELF-pay | **Type**: E2E
**Before you start**: Teacher session whose record has at least one PAID payout and one DRAFT payout (as operator: Teacher pay > generate, then mark one month paid). Other teachers must also have payouts.
| Step | Action |
|------|--------|
| 1 | Open "My pay" from the sidebar |
| 2 | Check each row's status chip and buttons |
**What you should see**: The page "My pay" (BM: "Bayaran saya") lists only this teacher's months with the net RM amount. The paid month shows "Paid <date>" (BM: "Dibayar <date>", date in DD/MM/YYYY) and a "Download payslip" (BM: "Muat turun slip gaji") button. The draft month shows "In process" (BM: "Dalam proses") and NO download button (the payslip only exists once the money moved). No other teacher's amounts appear anywhere. With no payouts: "No payslips yet. They'll appear here once your centre marks a payout as paid."
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-132: Teacher downloads their own paid payslip PDF
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T1 | **Linked**: US-AUTH-14 | **Risk**: R-SELF-payslip | **Type**: E2E
**Before you start**: Teacher session with a paid payout visible on My pay.
| Step | Action |
|------|--------|
| 1 | Click "Download payslip" on the paid month |
**What you should see**: A PDF downloads (filename `payslip-<YYYY-MM>.pdf`) showing this teacher's name, the month, session lines, and the net pay in RM. It matches the figures shown on My pay.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-133: Teacher requesting another teacher's payslip by id gets 404, not 403
**Tags**: @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-14 | **Risk**: R-SELF-otherslip | **Type**: API
**Before you start**: Teacher session in centre A. From an operator session, note the payout id of a DIFFERENT teacher in the same centre (Teacher pay > open that payout, copy the id from the URL).
| Step | Action |
|------|--------|
| 1 | As the teacher, request `GET /api/payouts/<other-teacher-payout-id>/pdf` |
**What you should see**: **404** `{ "error": "Not found" }`. Deliberately NOT 403: a 403 would confirm the id exists. No PDF, no name, no amount leaks. (Grounded: the pdf route returns 404 when `payout.teacherId !== ctx.teacherId` for teacher role.) REGRESSION: own-payslip scoping, commit b175d3e.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-134: Operators and staff are bounced off the teacher self-service pages
**Tags**: @regression **Severity**: S3 Medium | **Priority**: P3 | **Tier**: T2 | **Linked**: US-AUTH-14 | **Risk**: R-SELF-nonteacher | **Type**: E2E
**Before you start**: Operator session (repeat as staff if available).
| Step | Action |
|------|--------|
| 1 | Paste `/dashboard/my-classes` into the address bar |
| 2 | Paste `/dashboard/my-pay` into the address bar |
**What you should see**: Both redirect to `/dashboard` (requireTeacher sends non-teachers to the operator dashboard). Neither teacher page renders for an operator, and neither appears in the operator sidebar.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

---

## O. Owner-only gating (payment + invoicing settings)

> requireOwner / requireOwnerContext: only role **operator** passes. These control where parents'
> money is sent (bank account / DuitNow QR) and invoicing configuration.

### TC-AUTH-140: Staff opening an owner-only page is redirected to Billing
**Tags**: @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-15 | **Risk**: R-OWNER-page | **Type**: E2E
**Before you start**: Staff session in centre A.
**Test Data**: owner-only URLs: `/dashboard/settings/business`, `/dashboard/settings/invoicing`, `/dashboard/billing/settings`.
| Step | Action |
|------|--------|
| 1 | Paste each URL in Test Data into the address bar, one by one |
**What you should see**: Each redirects to `/dashboard/billing`. No bank account, DuitNow QR, or invoicing configuration ever renders for staff. (Teachers hitting the same URLs land on `/dashboard/attendance` instead: the operator-group guard fires first.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-141: Teacher calling an owner-only API gets the owner-gate 401
**Tags**: @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-15 | **Risk**: R-OWNER-api | **Type**: API
**Before you start**: Teacher session in centre A. (The staff variant of this call is TC-AUTH-041.)
| Step | Action |
|------|--------|
| 1 | As the teacher, call `GET /api/invoicing/settings` |
| 2 | As the teacher, call `PUT /api/settings/business` with any valid body |
**What you should see**: Both return **401** `{ "error": "Forbidden: owner only" }` and nothing changes. (The owner gate runs before the operator gate would even be relevant; the message pins WHICH gate fired.)
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-142: The operator passes the owner gate
**Tags**: @regression **Severity**: S2 High | **Priority**: P2 | **Tier**: T2 | **Linked**: US-AUTH-15 | **Risk**: R-OWNER-pass | **Type**: E2E
**Before you start**: Operator session (`operator@kelastest.local` / `newpassword6789`).
| Step | Action |
|------|--------|
| 1 | Open Settings > Business, Settings > Invoicing, and Settings > Payments: all should render |
| 2 | Change a harmless value (e.g. the business display name), save, and revert it |
**What you should see**: All three owner-only pages render for the operator and the save round-trips with a success state (HTTP 200 on the PUT). The owner gate blocks only non-operators, never the owner.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

---

## P. Removed membership is denied, never defaulted (2b53ee7)

> Better Auth's removeMember does NOT revoke the removed user's session, so their session can still
> point at the centre after removal. getAccessContext must throw, not default to staff. Before the
> fix, a removed teacher silently ESCALATED to staff-level access. There is no remove-member UI yet:
> remove via the Better Auth endpoint as operator (console: `fetch('/api/auth/organization/remove-member',
> { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ "memberIdOrEmail":
> "<email>" }) })`) or delete the user's row from the `member` table for that org in the DB.

### TC-AUTH-150: A removed member's live session is denied on the next page load
**Tags**: @smoke @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-16 | **Risk**: R-REMOVED-page | **Type**: E2E
**Before you start**: A staff member of centre A signed in on browser 1. In browser 2, as operator, remove them (see section note). Do NOT sign browser 1 out.
| Step | Action |
|------|--------|
| 1 | In browser 1 (the removed member's still-open session), click any sidebar item or reload `/dashboard` |
**What you should see**: The dashboard does NOT render. The removed member is redirected to `/onboarding/organization-selection`, where centre A no longer appears under "Continue to a centre". They are never silently treated as staff of a centre they left. **Notes**: REGRESSION: missing membership row defaulted to staff; fixed in commit 2b53ee7 (resolveMemberRole throws; unit-tested in src/libs/access-role.test.ts).
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-151: A removed member's API call returns the membership 401
**Tags**: @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-16 | **Risk**: R-REMOVED-api | **Type**: API
**Before you start**: Same setup as TC-AUTH-150: a removed member whose session still points at centre A.
| Step | Action |
|------|--------|
| 1 | From the removed member's session, call `GET /api/students` |
| 2 | Call `GET /api/invoicing/invoices` |
**What you should see**: Both return **401** `{ "error": "Not a member of this organisation" }`. No centre A data returns. The message is distinct from "Not authenticated" and "No active organisation selected": it identifies the removed-membership path. **Notes**: REGRESSION: commit 2b53ee7.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

### TC-AUTH-152: A removed teacher does not escalate: teacher surface is denied too
**Tags**: @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-16 | **Risk**: R-REMOVED-teacher | **Type**: E2E
**Before you start**: A TEACHER of centre A signed in on browser 1 (linked record, at least one class). In browser 2, as operator, remove their membership. Do not sign browser 1 out.
| Step | Action |
|------|--------|
| 1 | In browser 1, reload `/dashboard/attendance`, then `/dashboard/my-classes` |
| 2 | From the same session, call `GET /api/attendance?classId=<their-old-class-id>&date=<valid>` |
**What you should see**: Step 1: both pages redirect to `/onboarding/organization-selection`. Step 2: **401** `{ "error": "Not a member of this organisation" }`. The pre-fix behavior (removed teacher resurfacing with staff-level operator access) must never reappear. **Notes**: REGRESSION: removed teacher escalated to staff; fixed in commit 2b53ee7.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

---

## Q. Sign out

### TC-AUTH-153: Sign out ends the session everywhere
**Tags**: @regression @security **Severity**: S1 Critical | **Priority**: P1 | **Tier**: T1 | **Linked**: US-AUTH-2 | **Risk**: R-SIGNOUT | **Type**: E2E
**Before you start**: Signed in as any dashboard user.
| Step | Action |
|------|--------|
| 1 | Open the account menu and press "Sign out" (BM: "Log keluar") |
| 2 | Press the browser Back button toward the dashboard |
| 3 | From the console, call `GET /api/students` |
**What you should see**: Step 1 lands on the public home page (`/`). Step 2: any dashboard URL redirects to `/sign-in` (no cached authenticated page should expose data; if a cached shell flashes, no fresh data loads). Step 3: **401** `{ "error": "Not authenticated" }`.
**What you actually saw**: ___ **Status**: Pass / Fail / Blocked

---

## Coverage note

Rewritten 2026-07-04 against the Better Auth stack on `feat/finish-mvp-polish` (Clerk fully removed
in ddb9f4d). All 40 pre-migration cases kept their TC IDs and were rewritten in place where stale;
35 new cases were appended (TC-AUTH-100 to 153). **No cases were deleted**: every behaviour the
Clerk-era cases covered has a Better Auth analogue (org switcher became the account-menu centre
switcher, Clerk sign-in became the Better Auth email+password screens, first-login email linking
survives but now only picks the teacher record, never the role).

Techniques walked (per QA-METHODOLOGY §5):
- **Happy path** (1): TC-AUTH-001, 004, 010, 011, 012, 031, 064, 100, 110, 120, 121, 122, 123, 130, 131, 132, 142.
- **Equivalence + boundary** (2): password length floor at sign-up (101) and reset (114); missing vs mangled token/invite id (112, 113, 125).
- **Negative / validation + server-side bypass** (3): direct-POST write rejection (040), owner-API bypass (041, 141), unknown PATCH action 422 (042), short password via direct API (101), wrong-email invite accept (124), staff invite-creation bypass (128), no-org API 401 (082).
- **Format / locale** (4): every user-facing observable quotes the exact EN string with its BM
  equivalent (b68ac79 aligned the BM auth terms, e.g. "e-mel", "Jemputan menunggu"); visible dates
  DD/MM/YYYY (131); API dates are `YYYY-MM-DD` by contract (024, 055, 061).
- **Permissions / role** (5): operator vs staff vs teacher landing + nav (010/011/012/013), teacher
  page redirect (030), teacher API 401 (032), staff allowed on operator APIs (033), owner-only gate
  pages + APIs (041, 140, 141, 142), teacher self-service gate both directions (031, 134), invite
  role assignment honored (121, 122), member-management operator-only (128).
- **Cross-tenant / IDOR** (6): per representative record: class (050), student (051), invoice (052),
  payout (053), teacher (054), roster read (055), attendance write (056); stale id post-switch (092);
  cross-centre teacher-record linking blocked (023); other-teacher payslip hidden as 404 (133).
- **State transition / auth lifecycle** (7): sign-up -> onboarding -> centre creation (100), first-login
  record linking (020-024), invite pending -> accepted / cancelled / wrong-email (121, 124, 126),
  reset token valid -> used -> reused (110, 115), session live -> killed (081), membership live ->
  removed (150-152), centre switch re-scope + role recompute (090/091), sign-out (153).
- **Concurrency / idempotency** (8): single-use reset token (115); duplicate sign-up on an existing
  email (102). Rapid double-submit of auth forms is skipped: buttons disable while busy and Better
  Auth upstream covers replay; low residual risk.
- **Empty / loading / error states** (9): no-centre onboarding (002), logged-out redirects (003, 080),
  invalid reset link card (112), invalid invite card (125), teacher empty states (063, 130, 131).
- **Data integrity** (10): list endpoints never leak (070/071/072), linking scoped + active-only
  (023/024), no cross-centre write (056/062), invite activates the correct centre (127), payslip
  figures match My pay (132).
- **Accessibility** (11): skipped here; keyboard/label/contrast passes for the auth screens live in
  [test-plan-crosscutting.md](test-plan-crosscutting.md).
- **Security inputs** (12): XSS/SQLi payloads on auth fields are covered by the crosscutting input
  sweep; this file covers enumeration (111), token tampering (113), and privilege bypass (E, M, O, P).
- **Non-functional** (13): skipped by design; auth load (token refresh storms, 100-centre concurrent
  sign-in) is flagged for the load pass, not this functional catalog.

Rows skipped with reason: theme picker in the account menu (pure display preference, T3; covered by
the dashboard/crosscutting plans); email-verification enforcement (no UI requires it yet; the
current not-required contract is pinned as TC-AUTH-105); invite expiry by clock (Better Auth expires
invitations via `expiresAt`; testing it requires editing the row in the DB, fold into TC-AUTH-126's
setup if the staging DB is available); Better Auth internals (session rotation, cookie flags) are
trusted upstream and only their observable contract is asserted.

Status-code observables are grounded in the real guards: no cookie -> middleware redirect to
`/sign-in`; no auth / no org / removed membership / teacher-on-operator-API / non-owner-on-owner-API
-> **401** with four distinct messages ("Not authenticated" / "No active organisation selected" /
"Not a member of this organisation" / "Forbidden: operators only" or "Forbidden: owner only");
teacher-not-teaching -> **403** (teacherBlocked); cross-tenant id and other-teacher payslip -> **404**;
operator pages -> redirect `/dashboard/attendance` (teacher); owner pages -> redirect
`/dashboard/billing` (staff); teacher pages -> redirect `/dashboard` (non-teacher).

**README finding #1 re-triage (2026-07-04)**: "staff is treated as an operator everywhere" is no
longer accurate. Owner-only gates now exist (requireOwner/requireOwnerContext) on the payment,
business, and invoicing settings pages/APIs, and member management is operator-only; staff keeping
the rest of the operational surface is now the documented role model (src/libs/auth-permissions.ts).
Residual, deliberate looseness pinned by TC-AUTH-033: route guards are coarse (teacher vs not,
owner vs not), so staff can still write taxonomy and run payroll even though the declared staff
statement lists `setting: ['read']`; treat any tightening as a deliberate, tested change.

Out of scope here (covered elsewhere): per-module field validation, XSS/SQLi on inputs, and PII
masking live in the relevant feature catalogs and `test-plan-crosscutting.md`; the public invoice
token surface lives in `test-plan-billing.md`.

**Total: 75 cases** (A:4, B:4, C:5, D:4, E:3, F:7, G:4, H:3, I:3, J:3, K:7, L:6, M:10, N:5, O:3, P:3, Q:1).
**@smoke subset (13): TC-AUTH-001, 002, 010, 012, 030, 032, 050, 061, 070, 100, 110, 121, 150.**
