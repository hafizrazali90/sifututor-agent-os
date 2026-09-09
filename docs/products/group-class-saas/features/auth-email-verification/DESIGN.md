# Kelasapp Auth Email Verification And Transactional Email UX

Status: Draft for Hafiz review before implementation  
Date: 2026-07-07  
Project: Kelasapp  
GitHub issue: Learnest-Lab/kelasapp#17  
Owner: Hafiz  
Implementation branch: `feat/strict-email-verification`

## Why This Exists

Kelasapp already sends password reset and verification emails through the
Better Auth and Resend path, but verification is not strict yet. The app also
has a WhatsApp-first invite pattern, so organization invites do not currently
send email.

This design note captures the agreed product decisions before code changes so
the auth flow, admin UX, email copy, and tests move together.

## Source Of Truth

Use this Markdown file as the build source for this feature. HTML review files
are optional only if Hafiz wants a visual review board later.

Related design references:

- `docs/products/group-class-saas/features/onboarding-activation/DESIGN.md`
- `docs/products/group-class-saas/UI-CONVENTIONS.md`
- `docs/products/group-class-saas/DESIGN-AUDIT.md`
- `docs/products/group-class-saas/FLOWS.md`
- `kelas/docs/products/group-class-saas/SATNAING-MATCH-AUDIT.md`
- `sifu-tutor/docs/ui-ux/page-patterns.md`
- `sifu-tutor/docs/ui-ux/component-patterns.md`
- `sifu-tutor/docs/ui-ux/content-style-guide.md`
- `sifu-tutor/docs/ui-ux/accessibility-and-states.md`

## Locked Decisions

| Area | Decision | Meaning |
| --- | --- | --- |
| Verification rollout | C | Require verification going forward, but protect trusted existing users before production rollout with a one-time verified mark. No permanent code exceptions. |
| Email language | A | Locale-aware emails. Send English or BM based on current locale, with English fallback. |
| Verification completion | A | After a user verifies, auto sign in and continue to the intended destination. |
| Welcome email | B | Send welcome email only after first successful onboarding or centre creation. |
| Invite resend | A | Add `Resend email` for pending invites in the admin panel. |
| Member verification UI | A | Show a verification badge only in this batch. No filters, bulk actions, or blocking admin tools yet. |

## Product Principle

Strict verification should feel like a normal SaaS safety step, not a wall.

The user should always know:

- why the app needs verification
- which email address to check
- what action is available now
- how to resend the email
- how to change direction without being trapped

## Target User Flows

### 1. New Owner Sign Up

1. User creates an account from the localized sign-up page.
2. Kelasapp sends a verification email in the current locale.
3. The app shows a focused "check your email" screen.
4. User cannot continue to organization selection or dashboard until verified.
5. User clicks the verification link.
6. Better Auth verifies the email, signs the user in, and returns the user to
   the intended localized destination.
7. User completes onboarding and creates the first centre.
8. Kelasapp sends the welcome email after the centre exists.

### 2. Returning Unverified User

1. User signs in with correct credentials.
2. The app detects that the email is not verified.
3. The user is sent to the check-email screen instead of dashboard.
4. The user can resend the verification email.
5. After clicking the verification link, the user continues to dashboard or the
   original requested destination.

### 3. Invited Member

1. Admin invites a member from organization settings.
2. Kelasapp keeps the current invite-link and WhatsApp helper workflow.
3. Kelasapp also sends an invite email to the invited address.
4. Pending invite rows include `Resend email`.
5. If the invited person is new, they sign up and must verify before joining.
6. After verification, the invite acceptance continues without losing context.
7. If the invited person is already verified and signed in with the invited
   email, accepting the invite continues directly.

### 4. Existing Active Session That Is Unverified

1. If an existing session reaches dashboard while unverified, dashboard access
   is stopped.
2. The user is redirected to the check-email screen.
3. The redirect preserves the intended localized return path where safe.

### 5. Admin Member List

1. Current organization member UI remains the same.
2. Each member row can show a small verified or unverified badge.
3. The badge must use existing `StatusBadge` semantics where possible.
4. No admin override, force verify, or resend-to-member bulk tool in this batch.

## UI Rules

### Auth And Account Access

Follow the existing auth card pattern:

- centered auth card, current `max-w-sm` pattern is allowed
- one primary action per screen
- visible labels on form fields
- helpful error copy, not raw Better Auth exception text
- mobile-safe layout
- no account existence leaks beyond approved auth behavior
- no em dashes in UI copy
- all user-facing text must be in `next-intl`

### Check Email Screen

The check-email screen should include:

- short title: "Check your email"
- email address shown if safely available
- one primary action to resend verification
- secondary path back to sign in or change email
- success state after resend
- rate-limit or generic failure state without exposing internals

Recommended BM tone:

- "Semak e-mel anda"
- "Kami sudah hantar pautan pengesahan..."
- "Hantar semula e-mel"

### Admin Panel

Admin screens should stay dense, calm, and operational:

- no marketing hero layout
- no big explanatory cards
- use existing card/table density
- use existing badge tones
- avoid long equal-weight action rows
- keep destructive actions visually separate

For pending invites, `Resend email` should be easy to find but should not make
the row noisy. If row width becomes tight, keep common actions visible and move
rare or destructive actions into a compact overflow menu.

## Email Rules

All emails should be plain, branded, and practical:

- subject is short and action-led
- first line explains why the recipient got the email
- main CTA appears early
- fallback link is included
- support/help line is included
- English and BM templates are both available
- text fallback is sent together with HTML
- no dependency on external images
- no secret or sensitive payload in the email body

### Verification Email

Purpose: prove the user owns the email address before access.

Content:

- product name: Kelasapp
- action: verify email
- reason: secure access to the centre
- CTA: verify email
- fallback link
- short expiry line if Better Auth exposes expiry cleanly

### Invite Email

Purpose: notify invited staff that a centre invited them.

Content:

- centre or organization name
- inviter name or safe fallback if available
- role label
- CTA: accept invite
- fallback link
- mention that verification may be required before joining

### Welcome Email

Purpose: confirm successful first centre setup.

Send after:

- first organization or centre creation succeeds
- active organization context is available

Content:

- welcome to Kelasapp
- centre name
- next useful action: invite team, add classes, or explore dashboard
- support/help line

### Password Reset Email

Purpose: existing forgot password journey.

Update direction:

- keep current functionality
- polish copy and bilingual templates
- preserve current reset link behavior
- keep existing E2E coverage passing

### Other Standard Email

Password changed or security alert email is desirable, but only if Better Auth
exposes a clean hook without fragile auth patching. If not clean, defer it as a
separate task instead of risking the core auth flow.

## Implementation Contracts

### Better Auth

Expected auth settings:

- `emailAndPassword.requireEmailVerification`
- `emailVerification.sendOnSignUp`
- `emailVerification.sendOnSignIn`
- `emailVerification.autoSignInAfterVerification`
- `organization.requireEmailVerificationOnInvitation`
- `organization.sendInvitationEmail`

The implementation must confirm the exact installed Better Auth API from local
Node dependencies before editing.

### Routes

Recommended user-facing route:

- `/:locale/check-email`

This page can serve sign-up, sign-in, resend, and invite verification wait
states.

Callback URLs must remain localized and must not allow unsafe external
redirects.

### Existing Trusted Users

Before production rollout, trusted existing users can be marked verified once:

- `hafizrazali@live.com`
- `hafiz.razali@sifututor.my`

This must be a production data operation with explicit Hafiz approval before it
is run. The app code should not hardcode these addresses.

## Edge Cases To Handle

- User clicks an expired verification link.
- User clicks the same verification link twice.
- User resends verification multiple times.
- User signs in before verifying.
- User signs up from an invite and verifies after sign-up.
- User accepts an invite while signed in as a different email.
- Pending invite is cancelled before the email link is used.
- Existing verified users are not slowed down by the new gate.
- Existing password reset flow still works.

## Evidence Plan

Use local Node 24 checks and live smoke evidence where relevant. Do not use
GitHub Actions as evidence.

Permanent E2E coverage should include:

- new signup cannot enter onboarding before email verification
- verification link signs in and continues to onboarding
- returning unverified user lands on check-email and can resend
- invite email is sent when admin invites a member
- pending invite row can resend invite email
- invited new user verifies before joining organization
- member list shows verification badge
- welcome email sends after first centre creation
- forgot password and reset password still pass end to end

Expected local commands after implementation:

- `npm ci` if dependencies are not installed in the worktree
- `npm run check:types`
- `npm run lint`
- `npm run check:i18n`
- `npm run check:deps`
- focused Playwright auth and onboarding specs
- relevant smoke or T1/T2 specs touched by the sign-up helper
- `npm run build-local`
- `git diff --check`
- `../scripts/agent-checks/pre-commit-guard.sh`

Browser evidence after implementation:

- check-email screen screenshot
- admin pending invite row screenshot
- successful local outbox evidence for verification, invite, welcome, and reset

## Rollout Gates

1. Hafiz approves this design direction.
2. Implement on `feat/strict-email-verification`.
3. Verify locally with Node 24 and permanent E2E.
4. Stop before production data update.
5. With explicit approval, mark trusted existing production users verified.
6. With explicit approval, deploy.
7. Run live smoke without GitHub Actions.

## Out Of Scope For This Batch

- admin force-verify controls
- verification filters or bulk actions
- custom email design system builder
- full security-alert email suite if Better Auth has no clean hook
- permanent email exceptions in code
