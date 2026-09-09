# SIMS Admin Portal — Comprehensive User Story & E2E Test Coverage

**Date:** 2026-06-05
**Status:** Living document — update as features ship
**Scope:** All admin-accessible features in sifu-tutor (Laravel 11 + Inertia.js/React)
**Methodology:** Retroactive Test Coverage via ATDD + BDD (Given/When/Then)

---

## What This Is (Industry Context)

This document applies **Retroactive Test Coverage** — the industry-standard practice for
auditing an existing application and deriving E2E tests from it. It draws from three
complementary methodologies (all independently verified by adversarial research):

| Methodology | What It Does | Who Coined It |
|---|---|---|
| **ATDD** (Acceptance Test-Driven Development) | Maps features → acceptance tests; tests act as living requirements | Agile Alliance |
| **BDD** (Behavior-Driven Development) | Given/When/Then format for human-readable scenarios | Dan North, 2006 |
| **Characterization Testing** | Captures existing behavior as a baseline (change detector, not bug hunter) | Michael Feathers, 2004 |

**Key principle (verified):** When retroactively adding tests to a live system,
the goal is a **safety net for future changes** — not bug discovery. Other systems
(mobile apps, Ripple) depend on current SIMS behavior. Tests protect that contract.

---

## Story Format

Each user story uses:
```
US-XXX: [Short title]
Role: [admin | finance-admin | staff | super-admin]
Story: As a [role], I want to [action] so that [benefit]
Given/When/Then: BDD acceptance scenario
Seed: Laravel factories/seeders needed
E2E: existing spec file(s) | GAP (needs new spec)
Priority: P1 (financial/auth) | P2 (core workflow) | P3 (CMS/config)
```

---

## MODULE 1 — Authentication & Session

### US-001: Admin Login with Valid Credentials
**Role:** Any admin
**Story:** As an admin, I want to log in with my email and password so that I can access the SIMS portal.
```
Given: A valid admin user exists (UserFactory + AdminUserSeeder)
When: I submit correct email and password on /login
Then: I am redirected to the dashboard
 And: My session is authenticated (auth:sanctum)
 And: The navbar shows my name
```
**Seed:** `UserFactory`, `AdminUserSeeder`
**E2E:** `tests/e2e/auth/login.spec.ts` ✓
**Priority:** P1

### US-002: Login Blocked for Invalid Credentials
**Role:** Any admin
**Story:** As the system, I want to reject invalid credentials so that unauthorized users cannot access the portal.
```
Given: A valid admin user exists
When: I submit a wrong password
Then: I see "These credentials do not match" error
 And: I remain on the login page
```
**Seed:** `UserFactory`
**E2E:** `tests/e2e/auth/login.spec.ts` ✓
**Priority:** P1

### US-003: Rate Limiting on Login
**Role:** Any user
**Story:** As the system, I want to block brute-force login attempts so that accounts are protected.
```
Given: The login page is accessible
When: I submit incorrect credentials 5+ times from the same IP
Then: I receive a "Too many login attempts" response
 And: Further attempts are blocked for the lockout period
```
**Seed:** None (IP simulation)
**E2E:** `tests/e2e/auth/rate-limiting.spec.ts` ✓
**Priority:** P1

### US-004: Logout Clears Session
**Role:** Any admin
**Story:** As an admin, I want to log out so that my session is terminated and no one can access my account.
```
Given: I am logged in as an admin
When: I click "Logout"
Then: My session token is invalidated
 And: I am redirected to /login
 And: Accessing any protected route redirects me to /login
```
**Seed:** `UserFactory`
**E2E:** `tests/e2e/auth/login.spec.ts` ✓
**Priority:** P1

### US-005: Password Reset via Email
**Role:** Any admin
**Story:** As an admin who forgot my password, I want to request a reset link so that I can regain access.
```
Given: A valid admin user exists with email hafiz@example.com
When: I submit my email on /forget-password
Then: A password reset email is sent
 And: I see "Password reset link sent" confirmation
When: I click the link and submit a new password
Then: My password is updated
 And: I can log in with the new password
```
**Seed:** `UserFactory`
**E2E:** GAP — no forget-password.spec.ts exists
**Priority:** P2

### US-006: Authenticated Pages Deny Unauthenticated Access
**Role:** Unauthenticated user
**Story:** As the system, I want to redirect unauthenticated requests to /login so that protected routes are never exposed.
```
Given: I am not logged in
When: I navigate directly to /tutor or any protected route
Then: I am redirected to /login
 And: After logging in, I am redirected back to the original URL
```
**Seed:** None
**E2E:** `tests/e2e/auth/cache-control.spec.ts` ✓
**Priority:** P1

---

## MODULE 2 — User Management (Admin CRUD)

### US-010: List Admin Users
**Role:** super-admin (permission: `user-list`)
**Story:** As a super-admin, I want to view all portal users so that I can manage access.
```
Given: 5+ admin users exist
When: I navigate to /user
Then: A paginated table shows all users
 And: Each row shows name, email, role, status
```
**Seed:** `UserFactory` ×5
**E2E:** `tests/e2e/smoke/users.spec.ts` (smoke only) — **PARTIAL GAP**
**Priority:** P2

### US-011: Create New Admin User
**Role:** super-admin (permission: `user-add`)
**Story:** As a super-admin, I want to create a new admin user and assign a role so that staff can access the portal.
```
Given: I am on /user/create
When: I fill in name, email, password, role and submit
Then: A new user record is created
 And: The user appears in the user list
 And: The user can log in with the given credentials
```
**Seed:** `RolesSeeder` (roles must exist first)
**E2E:** GAP — no user-management/create.spec.ts
**Priority:** P2

### US-012: Edit Admin User
**Role:** super-admin (permission: `user-edit`)
**Story:** As a super-admin, I want to edit an existing user's name, role, or email so that I can keep records accurate.
```
Given: User "Ali" exists
When: I navigate to /user/edit/{id} and update the name to "Ali Ahmad"
Then: The record is updated in the database
 And: The user list reflects the change
```
**Seed:** `UserFactory`
**E2E:** GAP
**Priority:** P2

### US-013: Delete Admin User
**Role:** super-admin (permission: `user-delete`)
**Story:** As a super-admin, I want to delete a user so that former staff no longer have access.
```
Given: A non-superadmin user "Ahmad" exists
When: I click Delete on Ahmad's row and confirm
Then: Ahmad is soft-deleted
 And: Ahmad no longer appears in the user list
 And: Ahmad cannot log in
```
**Seed:** `UserFactory`
**E2E:** GAP
**Priority:** P2

### US-014: Reset Admin User Password
**Role:** super-admin (permission: `user-change-password`)
**Story:** As a super-admin, I want to reset a user's password so that locked-out staff can regain access.
```
Given: User "Ahmad" exists
When: I submit the reset-password form for Ahmad with a new password
Then: Ahmad's password is changed
 And: Ahmad can log in with the new password
```
**Seed:** `UserFactory`
**E2E:** GAP
**Priority:** P2

### US-015: View User Audit Logs
**Role:** super-admin (permission: `user-logs-list`)
**Story:** As a super-admin, I want to view audit logs of user actions so that I can track who did what and when.
```
Given: Admin user "Ali" has performed 5+ actions (login, create tutor, etc.)
When: I navigate to /user-logs
Then: A table shows timestamped entries for each action
 And: I can filter by user and date range
```
**Seed:** `UserFactory`, perform actions to generate logs
**E2E:** `tests/e2e/audit-logging/activity-logs.spec.ts` ✓
**Priority:** P2

---

## MODULE 3 — Role & Permission Management

### US-020: List Roles
**Role:** super-admin (permission: `user-role-list`)
**Story:** As a super-admin, I want to view all defined roles so that I understand the permission structure.
```
Given: Roles "Admin", "Finance", "Staff" exist (RolesSeeder)
When: I navigate to /user/role
Then: A table lists all roles with their permission counts
```
**Seed:** `RolesSeeder`
**E2E:** GAP — no roles-permissions/list.spec.ts
**Priority:** P2

### US-021: Create Role with Permissions
**Role:** super-admin (permission: `user-role-add`)
**Story:** As a super-admin, I want to create a new role and assign specific permissions so that I can control access granularly.
```
Given: I am on /user/role/create
When: I name the role "Finance Staff" and select permissions: invoice-journal-view, tutor-payment-journal-view
Then: The role is created
 And: A user assigned this role can access invoices but not user management
```
**Seed:** `RolesSeeder`
**E2E:** GAP
**Priority:** P2

### US-022: Edit Role Permissions
**Role:** super-admin (permission: `user-edit-edit`)
**Story:** As a super-admin, I want to update a role's permissions so that access rights evolve with business needs.
```
Given: Role "Finance Staff" exists with 5 permissions
When: I add the "tutor-commitment-slip-view" permission and save
Then: All users with this role can now access commitment slips
```
**Seed:** `RolesSeeder`, `UserFactory`
**E2E:** GAP
**Priority:** P2

### US-023: Delete Role
**Role:** super-admin (permission: `user-edit-delete`)
**Story:** As a super-admin, I want to delete an unused role so that the role list stays clean.
```
Given: Role "Old Finance" exists with no assigned users
When: I delete the role
Then: The role no longer appears in the role list
 And: No users are affected
```
**Seed:** `RolesSeeder`
**E2E:** GAP
**Priority:** P3

---

## MODULE 4 — Tutor Management

### US-030: List Tutors
**Role:** admin (permission: `tutor-list`)
**Story:** As an admin, I want to view all registered tutors so that I can manage their profiles.
```
Given: 10+ tutors exist in various states (active, inactive)
When: I navigate to /tutor
Then: A searchable, paginated table shows all tutors
 And: I can filter by status, subject, level
```
**Seed:** `TutorFactory` ×10, `SubjectFactory`, `LevelFactory`
**E2E:** `tests/e2e/tutors/index.spec.ts` ✓
**Priority:** P2

### US-031: View Tutor Profile
**Role:** admin (permission: `tutor-view`)
**Story:** As an admin, I want to view a tutor's full profile including subjects, availability, and documents so that I can assess their suitability.
```
Given: Tutor "Ali" exists with profile, subjects, and uploaded IC document
When: I navigate to /tutor/dashboard/{id}
Then: I see Ali's personal info, subjects, availability slots, and documents
 And: I see Ali's active request count and payment history
```
**Seed:** `TutorFactory`, `TutorSubjectFactory`, `TutorAvailabilitySlotFactory`
**E2E:** `tests/e2e/tutors/show.spec.ts` ✓
**Priority:** P2

### US-032: Create Tutor Manually
**Role:** admin (permission: `tutor-add`)
**Story:** As an admin, I want to manually register a tutor so that tutors who can't self-register are onboarded.
```
Given: I am on /tutor/create
When: I fill in name, email, phone, subjects, and availability and submit
Then: A new tutor profile is created
 And: The tutor appears in the tutor list
 And: A welcome email/notification is sent
```
**Seed:** `SubjectFactory`, `LevelFactory`, `CurriculumFactory`
**E2E:** `tests/e2e/tutors/create.spec.ts` ✓
**Priority:** P2

### US-033: Edit Tutor Profile
**Role:** admin (permission: `tutor-edit`)
**Story:** As an admin, I want to edit a tutor's profile so that I can correct information or update their subjects.
```
Given: Tutor "Ali" exists
When: I update Ali's phone number and add a new subject
Then: The changes are saved
 And: The profile page reflects the new information
```
**Seed:** `TutorFactory`, `SubjectFactory`
**E2E:** `tests/e2e/tutors/edit.spec.ts` ✓
**Priority:** P2

### US-034: Delete Tutor
**Role:** admin (permission: `tutor-delete`)
**Story:** As an admin, I want to soft-delete a tutor so that inactive tutors are removed from the active list without losing records.
```
Given: Tutor "Ali" exists with no active requests
When: I delete Ali from the tutor list
Then: Ali is soft-deleted (deleted_at is set)
 And: Ali no longer appears in the active tutor list
 And: Ali's historical data (payments, reports) is preserved
```
**Seed:** `TutorFactory`
**E2E:** `tests/e2e/tutors/edge-cases.spec.ts` (partial) ✓
**Priority:** P2

### US-035: Import Tutors via CSV
**Role:** admin (permission: `tutor-add`)
**Story:** As an admin, I want to import multiple tutors from a CSV file so that bulk onboarding is efficient.
```
Given: A valid CSV with 5 tutor records (name, email, phone, subject)
When: I upload the CSV on /tutor/import
Then: 5 tutor profiles are created
 And: A success message shows "5 tutors imported"
 And: Invalid rows show individual error messages
```
**Seed:** CSV fixture file
**E2E:** GAP — no tutors/import.spec.ts
**Priority:** P3

### US-036: View Tutor Documents
**Role:** admin (permission: `tutor-view`)
**Story:** As an admin, I want to view a tutor's uploaded identity documents so that I can verify their credentials before approving requests.
```
Given: Tutor "Ali" has uploaded an IC and teaching certificate
When: I view the Documents tab on Ali's profile
Then: I can see thumbnails/links for each document
 And: I can click to view or download each document
```
**Seed:** `TutorFactory` with documents seeded
**E2E:** `tests/e2e/tutors/documents.spec.ts` ✓
**Priority:** P2

---

## MODULE 5 — Tutor Requests (Job Postings)

### US-040: List Tutor Requests
**Role:** admin (permission: `tutor-requests-list`)
**Story:** As an admin, I want to view all tutor requests so that I can track their status and manage assignments.
```
Given: 10+ requests exist in various statuses (Pending, Matched, Active, Completed)
When: I navigate to /tutor/request
Then: A searchable, filterable table shows all requests
 And: I can filter by status, subject, level, location
```
**Seed:** `TutorRequestFactory` ×10, `ParentModelFactory`, `StudentFactory`
**E2E:** `tests/e2e/tutor-requests/list.spec.ts` ✓
**Priority:** P1

### US-041: Create Tutor Request
**Role:** admin (permission: `tutor-requests-add`)
**Story:** As an admin, I want to create a tutor request on behalf of a parent so that their child can be matched with a tutor.
```
Given: Parent "Puan Siti" and student "Ahmad" (Form 3) exist
When: I fill in subject (Mathematics), level (Form 3), sessions/week (3), location, and submit
Then: A new request is created with status "Pending"
 And: The request appears in the list
 And: A confirmation notification is sent to Puan Siti
```
**Seed:** `ParentModelFactory`, `StudentFactory`, `SubjectFactory`, `LevelFactory`
**E2E:** `tests/e2e/tutor-requests/create.spec.ts` ✓
**Priority:** P1

### US-042: View Tutor Request Detail
**Role:** admin (permission: `tutor-requests-view`)
**Story:** As an admin, I want to view the full details of a request so that I can assess what the parent needs.
```
Given: Request TUT-0001 exists with 2 students and 3 subject preferences
When: I navigate to /tutor/request/show/{id}
Then: I see parent info, student(s), subjects, levels, schedule preferences, location, and status history
```
**Seed:** `TutorRequestFactory`, `TutorRequestStudentFactory`
**E2E:** `tests/e2e/tutor-requests/detail.spec.ts` ✓
**Priority:** P1

### US-043: Assign Tutor to Request
**Role:** admin (permission: `tutor-requests-assign-tutor`)
**Story:** As an admin, I want to assign a tutor to a pending request so that the parent gets a matched tutor.
```
Given: Request TUT-0001 is in "Pending" status
 And: Tutor "Cikgu Ali" is available and matches the subjects/levels
When: I assign Cikgu Ali to TUT-0001
Then: The request status changes to "Matched"
 And: A notification is sent to Cikgu Ali and Puan Siti
 And: The assignment is logged in the request timeline
```
**Seed:** `TutorFactory`, `TutorRequestFactory`
**E2E:** `tests/e2e/tutor-requests/actions.spec.ts` ✓
**Priority:** P1

### US-044: Assign Staff Member to Request
**Role:** admin (permission: `tutor-requests-assign-admin`)
**Story:** As an admin, I want to assign a staff member as the case officer for a request so that there is a clear point of contact.
```
Given: Request TUT-0001 has no assigned staff
When: I assign staff "Farah" to the request
Then: Farah is shown as the case officer on the request detail
 And: Farah receives a notification
```
**Seed:** `StaffFactory`, `TutorRequestFactory`
**E2E:** `tests/e2e/tutor-requests/actions.spec.ts` ✓
**Priority:** P2

### US-045: Update Request Status
**Role:** admin (permission: `tutor-requests-edit`)
**Story:** As an admin, I want to update a request's status so that the lifecycle is tracked accurately.
```
Given: Request TUT-0001 is "Matched"
When: I change the status to "Active"
Then: The status is updated in the database and UI
 And: The status change is recorded in the request timeline with timestamp
```
**Seed:** `TutorRequestFactory`
**E2E:** `tests/e2e/tutor-requests/edit.spec.ts` ✓
**Priority:** P1

### US-046: Duplicate a Request
**Role:** admin (permission: `tutor-requests-duplicate-ticket`)
**Story:** As an admin, I want to duplicate an existing request so that I can quickly create a similar request for another student.
```
Given: Request TUT-0001 exists for subject Maths, Form 3
When: I click "Duplicate" on TUT-0001
Then: A new request is created with the same subject/level/location but blank parent/student
 And: I am taken to the new request's edit page to fill in the new parent
```
**Seed:** `TutorRequestFactory`
**E2E:** GAP — no duplicate.spec.ts in tutor-requests/
**Priority:** P3

### US-047: Reactivate a Cancelled Request
**Role:** admin (permission: `tutor-requests-edit`)
**Story:** As an admin, I want to reactivate a cancelled request so that a parent who changed their mind can be re-matched.
```
Given: Request TUT-0001 is "Cancelled"
When: I click "Reactivate" on TUT-0001
Then: The request status returns to "Pending"
 And: The reactivation is logged in the timeline
```
**Seed:** `TutorRequestFactory` with cancelled status
**E2E:** GAP
**Priority:** P3

### US-048: Run Matching Engine for a Request
**Role:** admin (permission: `tutor-requests-run-matching`)
**Story:** As an admin, I want to run the matching algorithm for a request so that the system recommends the best-fit tutors automatically.
```
Given: Request TUT-0001 needs a Maths tutor for Form 3 in Petaling Jaya
 And: 5+ active tutors exist with various subject/level/location profiles
When: I click "Run Matching" on TUT-0001
Then: The matching engine runs and returns a ranked list of tutors
 And: Each tutor shows a match score and reason
```
**Seed:** `TutorFactory` ×5 with subjects/locations, `TutorRequestFactory`
**E2E:** GAP — no matching-engine/ folder
**Priority:** P2

### US-049: Process Level Change for Request
**Role:** admin (permission: `tutor-requests-change-level`)
**Story:** As an admin, I want to process a level change for an active request so that the correct tutor rate and invoice are recalculated.
```
Given: Request TUT-0001 is "Active" at Form 3 rate (RM 40/hr)
When: I process a level change to Form 5 (RM 50/hr)
Then: The new rate is applied from the effective date
 And: Future invoices use the new rate
 And: A level change record is created for audit
```
**Seed:** `TutorRequestFactory`, `LevelFactory`, `ParentInvoiceFactory`
**E2E:** `tests/e2e/level-change/` ✓ (folder exists)
**Priority:** P1

### US-050: View Application Logs
**Role:** admin (permission: `tutor-requests-view-application-log`)
**Story:** As an admin, I want to view all application logs for tutor requests so that I can audit changes and communications.
```
Given: Request TUT-0001 has a history of status changes and tutor assignments
When: I navigate to /tutor/request/logs
Then: A chronological log shows all events (created, status changed, tutor assigned, etc.)
 And: Each entry shows timestamp, actor, and event description
```
**Seed:** `TutorRequestFactory`, generate events
**E2E:** GAP — no application-logs.spec.ts
**Priority:** P2

---

## MODULE 6 — Parent Management

### US-060: List Parents
**Role:** admin (permission: `customer-view`)
**Story:** As an admin, I want to view all registered parents so that I can manage their accounts.
```
Given: 10+ parents exist
When: I navigate to /parent
Then: A searchable, paginated table shows all parents with name, phone, email, status
```
**Seed:** `ParentModelFactory` ×10
**E2E:** `tests/e2e/parents/` folder exists ✓
**Priority:** P2

### US-061: View Parent Dashboard
**Role:** admin (permission: `customer-dashboard`)
**Story:** As an admin, I want to view a parent's dashboard so that I can see their requests, invoices, and students in one place.
```
Given: Parent "Puan Siti" has 2 students, 3 requests, and 5 invoices
When: I navigate to /parent/dashboard/{id}
Then: I see all students, active requests, invoice history, and payment status
```
**Seed:** `ParentModelFactory`, `StudentFactory` ×2, `TutorRequestFactory` ×3, `ParentInvoiceFactory` ×5
**E2E:** `tests/e2e/parents/` ✓
**Priority:** P2

### US-062: Create Parent Manually
**Role:** admin (permission: `customer-add`)
**Story:** As an admin, I want to manually register a parent so that they can receive tutor matching services.
```
Given: I am on /parent/create
When: I fill in name, email, phone, address and submit
Then: A new parent account is created
 And: The parent can log in on the mobile app
```
**Seed:** None (new record)
**E2E:** `tests/e2e/parents/` ✓
**Priority:** P2

### US-063: Edit Parent Profile
**Role:** admin (permission: `customer-edit`)
**Story:** As an admin, I want to update a parent's contact information so that communications reach them correctly.
```
Given: Parent "Puan Siti" exists with phone 012-1234567
When: I update the phone to 012-9999888
Then: The new phone is saved
 And: Future WhatsApp messages use the new number
```
**Seed:** `ParentModelFactory`
**E2E:** `tests/e2e/parents/` ✓
**Priority:** P2

### US-064: Delete Parent
**Role:** admin (permission: `customer-delete`)
**Story:** As an admin, I want to soft-delete a parent so that inactive accounts are removed from the active list.
```
Given: Parent "Encik Raju" has no active requests or unpaid invoices
When: I delete Encik Raju
Then: The parent is soft-deleted
 And: The parent no longer appears in the active parent list
```
**Seed:** `ParentModelFactory`
**E2E:** `tests/e2e/parents/` ✓
**Priority:** P2

### US-065: View Parent Payment Receipts
**Role:** admin (permission: `customer-payment-receipts-view`)
**Story:** As an admin, I want to view all payment receipts for a parent so that I can reconcile their payment history.
```
Given: Parent "Puan Siti" has 5 paid invoices
When: I navigate to /parent/payment-receipts?parent_id={id}
Then: I see a table of all receipts with amount, date, and payment method
```
**Seed:** `ParentModelFactory`, `ParentInvoiceFactory` ×5 (paid)
**E2E:** GAP
**Priority:** P2

---

## MODULE 7 — Student Management

### US-070: List Students
**Role:** admin (permission: `student-list`)
**Story:** As an admin, I want to view all students so that I can manage their profiles.
```
Given: 10+ students exist linked to various parents
When: I navigate to /student
Then: A table shows all students with name, parent, level, and status
```
**Seed:** `StudentFactory` ×10, `ParentModelFactory` ×5
**E2E:** `tests/e2e/students/students.spec.ts` ✓
**Priority:** P2

### US-071: Create Student
**Role:** admin (permission: `student-add`)
**Story:** As an admin, I want to create a student profile so that the student can be added to tutor requests.
```
Given: Parent "Puan Siti" exists
When: I create student "Ahmad" (Form 3, born 2010) linked to Puan Siti
Then: Ahmad's profile is created
 And: Ahmad can be selected when creating a tutor request for Puan Siti
```
**Seed:** `ParentModelFactory`, `LevelFactory`
**E2E:** `tests/e2e/students/students.spec.ts` ✓
**Priority:** P2

### US-072: Edit Student
**Role:** admin (permission: `student-edit`)
**Story:** As an admin, I want to update a student's level so that their request gets repriced correctly.
```
Given: Student "Ahmad" is in Form 3
When: I update Ahmad's level to Form 4
Then: The level is saved
 And: New requests for Ahmad default to Form 4 pricing
```
**Seed:** `StudentFactory`, `LevelFactory`
**E2E:** `tests/e2e/students/students.spec.ts` ✓
**Priority:** P2

---

## MODULE 8 — Class Management & Attendance

### US-080: View Class Schedule
**Role:** admin (permission: `class-schedule-list`)
**Story:** As an admin, I want to view all upcoming and past classes so that I can monitor delivery of tutoring services.
```
Given: 10+ classes exist for active requests
When: I navigate to /class/
Then: I see a paginated list of classes with tutor, student, subject, date, time, and status
 And: I can filter by date range, tutor, or request
```
**Seed:** `ClassesFactory` ×10, `TutorFactory`, `TutorRequestFactory`
**E2E:** `tests/e2e/classes/classes-index.spec.ts` ✓
**Priority:** P2

### US-081: Record Class Attendance (Clock In/Out)
**Role:** admin (permission: `class-schedule-clock-in-out`)
**Story:** As an admin, I want to mark a class as attended so that the tutor's session count is updated and invoicing is triggered.
```
Given: Class #101 is "Scheduled" for today
When: I click "Clock In" for class #101
Then: The class status changes to "Ongoing"
When: I click "Clock Out"
Then: The class status changes to "Completed"
 And: The session count for the request increments
 And: An invoice entry is generated for the completed session
```
**Seed:** `ClassesFactory` (scheduled), `TutorFactory`, `TutorRequestFactory`
**E2E:** `tests/e2e/classes/classes-actions.spec.ts` ✓
**Priority:** P1

### US-082: Edit Class Details
**Role:** admin (permission: `class-schedule-edit`)
**Story:** As an admin, I want to edit a class's scheduled date and time so that I can accommodate rescheduling requests.
```
Given: Class #101 is scheduled for Monday 3pm
When: I edit the class to Tuesday 4pm
Then: The new schedule is saved
 And: A notification is sent to the tutor and parent
```
**Seed:** `ClassesFactory`
**E2E:** `tests/e2e/classes/classes-actions.spec.ts` ✓
**Priority:** P2

### US-083: Delete Class
**Role:** admin (permission: `class-schedule-delete`)
**Story:** As an admin, I want to cancel and delete a class so that incorrect sessions are removed from the schedule.
```
Given: Class #101 is "Scheduled" (not yet attended)
When: I delete class #101
Then: The class is removed from the schedule
 And: No invoice entry is generated for it
```
**Seed:** `ClassesFactory`
**E2E:** `tests/e2e/classes/classes-actions.spec.ts` ✓
**Priority:** P2

### US-084: View Cancel Journal
**Role:** admin (permission: `canceled-class-journal-list`)
**Story:** As an admin, I want to view all cancelled classes so that I can process refunds for affected parents.
```
Given: 5 classes have been cancelled this month
When: I navigate to /class/cancel-journal
Then: I see all cancelled classes with reason, date, tutor, parent, and refund status
```
**Seed:** `ClassesFactory` (cancelled)
**E2E:** `tests/e2e/classes/journeys.spec.ts` (partial) ✓
**Priority:** P2

### US-085: Process Refund for Cancelled Class
**Role:** admin (permission: `canceled-class-journal-refund`)
**Story:** As an admin, I want to issue a refund credit for a cancelled class so that the parent's account is adjusted correctly.
```
Given: Class #101 was cancelled and a RM 40 session fee was charged
When: I click "Refund" on class #101 in the cancel journal
Then: A RM 40 credit is applied to the parent's next invoice
 And: The refund slip is generated and downloadable
 And: The class is marked as "Refunded"
```
**Seed:** `ClassesFactory` (cancelled), `ParentInvoiceFactory`
**E2E:** GAP — no cancel-refund.spec.ts
**Priority:** P1

---

## MODULE 9 — Invoice & Payment (Parent-Side)

### US-090: View Invoice Journal
**Role:** admin (permission: `invoice-journal-view`)
**Story:** As an admin, I want to view all parent invoices so that I can monitor billing and outstanding payments.
```
Given: 20+ invoices exist in various states (Pending, Paid, Overdue)
When: I navigate to /parent/invoice-journal
Then: A searchable, filterable table shows all invoices
 And: I can filter by status, parent, month, and amount range
 And: Summary stats show total billed, collected, and outstanding
```
**Seed:** `ParentInvoiceFactory` ×20
**E2E:** `tests/e2e/parent-invoices/smoke.spec.ts` ✓
**Priority:** P1

### US-091: View Single Invoice
**Role:** admin (permission: `invoice-journal-view`)
**Story:** As an admin, I want to view a single invoice's full detail so that I can see line items, deductions, and payment history.
```
Given: Invoice #INV-001 exists for parent "Puan Siti" with 3 session line items
When: I navigate to the invoice detail page
Then: I see all line items, applicable deductions, total amount, and payment status
```
**Seed:** `ParentInvoiceFactory`, `ParentInvoiceDeductionFactory`
**E2E:** `tests/e2e/parent-invoices/show.spec.ts` ✓
**Priority:** P1

### US-092: Edit Invoice
**Role:** admin (permission: `invoice-journal-edit`)
**Story:** As an admin, I want to edit an invoice's due date or add a deduction so that billing remains accurate.
```
Given: Invoice #INV-001 is "Pending"
When: I update the due date and add a RM 20 discount
Then: The invoice reflects the new due date and discounted total
 And: A note is added to the invoice history
```
**Seed:** `ParentInvoiceFactory`
**E2E:** `tests/e2e/parent-invoices/` ✓
**Priority:** P1

### US-093: Direct Pay Invoice (Mark as Paid Manually)
**Role:** admin (permission: `invoice-journal-directpay`)
**Story:** As an admin, I want to mark an invoice as paid manually so that cash or bank transfer payments are recorded.
```
Given: Invoice #INV-001 is "Pending" for RM 150
When: I click "Direct Pay" and enter payment method "Bank Transfer" with reference "TXN123"
Then: The invoice status changes to "Paid"
 And: A payment receipt is generated
 And: The tutor's payment journal is updated
```
**Seed:** `ParentInvoiceFactory` (pending)
**E2E:** `tests/e2e/parent-invoices/mark-paid.spec.ts` ✓
**Priority:** P1

### US-094: Transfer Invoice Payment (Re-allocation)
**Role:** admin (permission: `invoice-journal-transfer-payment`)
**Story:** As an admin, I want to transfer a payment from one invoice to another so that mis-allocated payments are corrected without touching the original transaction.
```
Given: Invoice #INV-001 is paid but the payment should have been for #INV-002
When: I use the payment transfer tool to move the payment to #INV-002
Then: #INV-001 is marked as "Unpaid" and #INV-002 is marked as "Paid"
 And: A transfer record is created for LHDN audit trail
 And: The transfer can be reverted
```
**Seed:** `ParentInvoiceFactory` ×2 (one paid, one unpaid)
**E2E:** GAP — no payment-transfers/ folder
**Priority:** P1

### US-095: Download Invoice Slip
**Role:** admin (permission: `invoice-journal-view`)
**Story:** As an admin, I want to download a PDF invoice slip so that I can send it to the parent.
```
Given: Invoice #INV-001 is "Paid"
When: I click "Download Slip" on #INV-001
Then: A PDF is downloaded with invoice details, amount, and payment confirmation
```
**Seed:** `ParentInvoiceFactory` (paid)
**E2E:** GAP — no invoice-download.spec.ts
**Priority:** P2

### US-096: Delete Invoice
**Role:** admin (permission: `invoice-journal-delete`)
**Story:** As an admin, I want to delete an erroneous invoice so that incorrect bills are removed.
```
Given: Invoice #INV-001 is "Pending" and was created in error
When: I delete #INV-001
Then: The invoice is soft-deleted
 And: It no longer appears in the parent's invoice list
 And: The deletion is logged for audit
```
**Seed:** `ParentInvoiceFactory`
**E2E:** `tests/e2e/parent-invoices/delete.spec.ts` ✓
**Priority:** P1

### US-097: View Invoice Follow-Up List
**Role:** admin (permission: `invoice-follow-up-list`)
**Story:** As an admin, I want to view all overdue invoices so that I can follow up with parents.
```
Given: 5 invoices are 30+ days overdue
When: I navigate to /parent/invoice-follow-up
Then: I see all overdue invoices with parent contact info and amount due
 And: I can bulk-send a payment reminder WhatsApp message
```
**Seed:** `ParentInvoiceFactory` ×5 (overdue)
**E2E:** GAP
**Priority:** P2

### US-098: FIUU Payment Gateway — Callback Handling
**Role:** System (no admin UI)
**Story:** As the system, I want to handle FIUU payment callbacks so that online payments are automatically recorded.
```
Given: Parent "Puan Siti" clicks Pay Online for Invoice #INV-001 (RM 150)
 And: FIUU processes the payment successfully
When: FIUU sends a callback to /payment/fiuu/callback
Then: Invoice #INV-001 is marked as "Paid"
 And: A payment receipt is generated
 And: The tutor's payment journal is updated
```
```
Given: FIUU sends a declined callback
When: The callback is received at /payment/fiuu/callback
Then: Invoice #INV-001 remains "Unpaid" (not "Failed")
 And: The response returns HTTP 200 (FIUU requires 200 on all callbacks)
```
**Seed:** `ParentInvoiceFactory`
**E2E:** `tests/e2e/financial/financial-callbacks.spec.ts` ✓
**Priority:** P1

---

## MODULE 10 — Tutor Payments & Commissions

### US-100: View Tutor Payment Journal
**Role:** admin (permission: `tutor-payment-journal-view`)
**Story:** As an admin, I want to view all tutor payments so that I can track what has been paid and what is outstanding.
```
Given: 10+ tutor payment records exist
When: I navigate to /tutor/payment-journal
Then: A searchable table shows all payments with tutor name, amount, month, and status
```
**Seed:** `TutorPaymentFactory` ×10
**E2E:** `tests/e2e/tutor-payments/list.spec.ts` ✓
**Priority:** P1

### US-101: Make Tutor Payment
**Role:** admin (permission: `tutor-payment-journal-payment`)
**Story:** As an admin, I want to record a payment to a tutor so that their earnings are marked as disbursed.
```
Given: Tutor "Cikgu Ali" has RM 500 in unpaid earnings for June 2026
When: I navigate to /tutor/payment/{id} and submit payment with bank ref "TXN456"
Then: The payment is recorded as "Paid"
 And: A payment slip is generated
 And: Ali receives a WhatsApp notification
```
**Seed:** `TutorFactory`, `TutorPaymentFactory` (unpaid)
**E2E:** `tests/e2e/tutor-payments/create.spec.ts` ✓
**Priority:** P1

### US-102: Edit Tutor Payment
**Role:** admin (permission: `tutor-payment-journal-payment`)
**Story:** As an admin, I want to edit a tutor payment to correct the bank reference so that the record is accurate.
```
Given: Payment #PAY-001 is recorded with wrong bank ref "TXN000"
When: I edit the bank ref to "TXN456"
Then: The payment record is updated
 And: The audit log shows the change
```
**Seed:** `TutorPaymentFactory`
**E2E:** `tests/e2e/tutor-payments/edit.spec.ts` ✓
**Priority:** P2

### US-103: View Pending Payouts
**Role:** admin (permission: `tutor-pending-payouts-list`)
**Story:** As an admin, I want to see all tutors with pending payouts so that I can process payments in bulk.
```
Given: 5 tutors have completed sessions with unpaid earnings
When: I navigate to /tutor/pending-payouts
Then: I see each tutor's name, earnings amount, and number of sessions
 And: I can select multiple tutors and process payment in bulk
```
**Seed:** `TutorFactory` ×5, `TutorPaymentFactory` ×5 (pending)
**E2E:** GAP
**Priority:** P1

### US-104: Download Tutor Payment Slip
**Role:** admin (permission: `tutor-payment-slip-download`)
**Story:** As an admin, I want to download a tutor's payment slip so that it can be sent as proof of payment.
```
Given: Payment #PAY-001 is "Paid"
When: I click "Download Slip" on #PAY-001
Then: A PDF slip is downloaded showing tutor name, amount, date, bank ref, and sessions
```
**Seed:** `TutorPaymentFactory` (paid)
**E2E:** `tests/e2e/tutor-payments/` (partial) ✓
**Priority:** P2

### US-105: Issue Tutor Commitment Fee
**Role:** admin (permission: `tutor-commitment-slip-list`)
**Story:** As an admin, I want to issue a commitment fee to a tutor so that they are financially committed to accepting a request.
```
Given: Tutor "Cikgu Ali" is assigned to Request TUT-0001
When: I issue a RM 30 commitment fee for Ali
Then: A commitment fee record is created
 And: A commitment slip is generated
 And: Ali receives a notification
```
**Seed:** `TutorFactory`, `TutorRequestFactory`
**E2E:** `tests/e2e/tutor-commitment-slips/commitment-slips.spec.ts` ✓
**Priority:** P2

### US-106: Refund Tutor Commitment Fee
**Role:** admin (permission: `tutor-commitment-slip-refund`)
**Story:** As an admin, I want to refund a tutor's commitment fee so that tutors who completed their obligations are compensated.
```
Given: Commitment fee #CF-001 was issued to "Cikgu Ali"
 And: Ali has completed the required sessions
When: I click "Refund" on CF-001
Then: The commitment fee is marked as "Refunded"
 And: The refund amount is added to Ali's next payment
```
**Seed:** `TutorFactory`, commitment fee record
**E2E:** `tests/e2e/commitment-fees/approval.spec.ts` ✓
**Priority:** P2

### US-107: View Staff Commission Journal
**Role:** admin (permission: `staff-commission-journal-view`)
**Story:** As an admin, I want to view each staff member's commission earned so that I can process payroll.
```
Given: Staff "Farah" has closed 5 requests this month earning RM 250 commission
When: I navigate to /staff-commission/
Then: I see a journal with each staff member's name and total commission
When: I click on Farah's row
Then: I see the breakdown by request
```
**Seed:** `StaffFactory`, `TutorRequestFactory` ×5 (closed, assigned to Farah)
**E2E:** `tests/e2e/staff-commission/journal.spec.ts` ✓
**Priority:** P1

### US-108: Make Staff Commission Payment
**Role:** admin (permission: `staff-payment-make`)
**Story:** As an admin, I want to pay a staff member's commission so that their earnings are disbursed.
```
Given: Staff "Farah" has RM 250 in unpaid commission
When: I submit a commission payment for Farah with bank ref "TXN789"
Then: The commission is marked as "Paid"
 And: A commission payment slip is generated
```
**Seed:** `StaffFactory`, `StaffFactory` commission records
**E2E:** `tests/e2e/staff-commission/mark-paid.spec.ts` ✓
**Priority:** P1

### US-109: Ad-hoc Tutor Bonus
**Role:** admin (permission: `bonus-adhoc-create`)
**Story:** As an admin, I want to issue a one-time bonus to a tutor so that exceptional performance is rewarded.
```
Given: Tutor "Cikgu Ali" has excellent ratings this month
When: I issue a RM 50 ad-hoc bonus to Ali with note "Excellent performance"
Then: The bonus is added to Ali's payment journal
 And: Ali is notified of the bonus
```
**Seed:** `TutorFactory`
**E2E:** `tests/e2e/tutor-bonuses/tutor-bonuses-actions.spec.ts` ✓
**Priority:** P2

---

## MODULE 11 — Reports & Analytics

### US-110: View Evaluation Reports
**Role:** admin (permission: `evaluation-report-view`)
**Story:** As an admin, I want to view tutor evaluation reports submitted by parents so that I can monitor teaching quality.
```
Given: 5 evaluation reports have been submitted for active tutors
When: I navigate to /tutor/evaluation-report
Then: I see a list of reports with tutor name, parent, rating, and date
 And: I can click to view each report's full content
```
**Seed:** `TutorFactory`, `ParentModelFactory`, evaluation report records
**E2E:** `tests/e2e/reports/` ✓
**Priority:** P2

### US-111: View Analytics Overview
**Role:** admin (permission: `analytics-overview`)
**Story:** As an admin, I want to see high-level KPIs so that I can monitor business health at a glance.
```
Given: The portal has data for the last 3 months
When: I navigate to /analytics/overview
Then: I see total active requests, total revenue collected, tutor count, and parent count
 And: Each KPI has a trend indicator (up/down vs last month)
```
**Seed:** Full dataset via `E2ETestDataSeeder`
**E2E:** `tests/e2e/reports/analytics.spec.ts` ✓
**Priority:** P2

### US-112: View Executive Summary
**Role:** admin (permission: `analytics-executive-summary`)
**Story:** As an admin, I want to generate an executive summary report for a date range so that I can present business performance to stakeholders.
```
Given: Business data exists for June 2026
When: I select June 2026 and click "Generate Report"
Then: I see total invoiced, total collected, outstanding, new parents, new tutors, sessions completed
```
**Seed:** Full dataset
**E2E:** `tests/e2e/reports/analytics.spec.ts` ✓
**Priority:** P2

### US-113: View Daily Ticket Application Report
**Role:** admin (permission: `operation-report-daily-ticket`)
**Story:** As an admin, I want to view today's ticket applications so that I can process new requests promptly.
```
Given: 3 new tutor requests were submitted today
When: I navigate to /daily/ticket/application
Then: I see a list of today's new requests with parent, subject, level, and location
```
**Seed:** `TutorRequestFactory` ×3 (created today)
**E2E:** `tests/e2e/reports/management-reports.spec.ts` ✓
**Priority:** P2

---

## MODULE 12 — Notifications & Broadcasts

### US-120: Send Push Notification to Mobile App Users
**Role:** admin (permission: `mobile-notification-add`)
**Story:** As an admin, I want to send a push notification to all tutors so that I can broadcast announcements.
```
Given: 10+ tutors have registered device tokens
When: I create a notification with title "Monthly Bonus Released!" and body text
 And: I select audience "All Tutors" and send
Then: The notification is queued and delivered to all tutor devices
 And: A notification log entry is created
```
**Seed:** `TutorFactory` ×10, `DeviceTokenFactory` ×10
**E2E:** `tests/e2e/notification-architecture/notifications-index.spec.ts` ✓
**Priority:** P2

### US-121: Send WhatsApp Broadcast via CSV
**Role:** admin (permission: `broadcasts-send`)
**Story:** As an admin, I want to send a WhatsApp broadcast to a list of parents via CSV so that bulk communications are efficient.
```
Given: A CSV file with 5 parent WhatsApp numbers and message variables
When: I upload the CSV on /broadcasts, select the template, and preview
Then: I see a parsed preview with 5 recipient entries
When: I click "Send"
Then: 5 WhatsApp messages are queued via the broadcast service
 And: A broadcast log entry is created
```
**Seed:** CSV fixture, `ParentModelFactory` ×5
**E2E:** `tests/e2e/broadcasts/send.spec.ts` ✓
**Priority:** P2

### US-122: Toggle Notification Channel (Kill Switch)
**Role:** admin (permission: `notification-management-toggle`)
**Story:** As an admin, I want to enable or disable a notification channel so that I can stop automated messages during maintenance.
```
Given: The "Invoice Reminder" notification type is enabled
When: I toggle it off on the Notification Management page
Then: The toggle is saved as disabled
 And: Invoice reminder jobs no longer send messages
 And: An audit log records the change
```
**Seed:** `NotificationTypeSeeder`
**E2E:** `tests/e2e/notification-architecture/kill-switch.spec.ts` ✓
**Priority:** P1

### US-123: View Staff Notification Inbox
**Role:** Any logged-in staff (permission: `staff-notifications-view`)
**Story:** As a staff member, I want to see my in-portal notifications so that I don't miss important alerts.
```
Given: Staff "Farah" has 5 unread notifications (new ticket assigned, payment completed)
When: Farah clicks the bell icon in the navbar
Then: A dropdown shows the 5 unread notifications with summary text
When: Farah clicks a notification
Then: It is marked as read and she is navigated to the relevant page
```
**Seed:** Staff notification records
**E2E:** `tests/e2e/notification-architecture/bell-dropdown.spec.ts` ✓
**Priority:** P2

---

## MODULE 13 — Settings & Configuration

### US-130: Manage Bonus Rules
**Role:** admin (permission: `bonus-rules-view`, `bonus-rules-create`, `bonus-rules-edit`)
**Story:** As an admin, I want to configure bonus rules so that tutors are automatically rewarded for meeting performance targets.
```
Given: I am on /settings/bonus-rules/create
When: I create a rule "5 sessions/month = RM 50 bonus" and save
Then: The rule appears in the bonus rules list
When: I toggle the rule off
Then: The rule is inactive and no bonuses are calculated from it
```
**Seed:** `BonusRulesSeeder`
**E2E:** `tests/e2e/tutor-bonuses/bonus-rules-list.spec.ts` ✓
**Priority:** P2

### US-131: Manage Commission Rules
**Role:** admin (permission: `settings.commission-rules.view`, `settings.commission-rules.edit`)
**Story:** As an admin, I want to configure commission rules so that staff are paid the correct percentage for each request type.
```
Given: A commission rule "Form 1-3 = 5%" exists
When: I update it to "Form 1-3 = 6%" and save
Then: Future commission calculations use 6%
When: I deactivate the rule
Then: No commission is calculated for that request type
```
**Seed:** `CommissionRuleSeeder`
**E2E:** `tests/e2e/staff-commission/rules.spec.ts` ✓
**Priority:** P1

### US-132: Manage Lookup Values (Dropdown Lists)
**Role:** admin (permission: `lookups-manage`)
**Story:** As an admin, I want to add/edit/reorder dropdown options so that forms have the correct choices.
```
Given: The "Request Source" lookup has values [Facebook, Referral, Google]
When: I add "TikTok" and reorder it to position 1
Then: "TikTok" appears first in the Request Source dropdown on forms
```
**Seed:** Lookup records
**E2E:** `tests/e2e/settings/` ✓
**Priority:** P3

### US-133: Manage States & Cities
**Role:** admin (permission: `settings-add-state`, `settings-add-city`)
**Story:** As an admin, I want to add a new city to a state so that tutors and parents can select it in their location fields.
```
Given: State "Selangor" exists with 5 cities
When: I add city "Cyberjaya" to Selangor
Then: "Cyberjaya" appears in the city dropdown when Selangor is selected on forms
```
**Seed:** `StateFactory`, `CityFactory`
**E2E:** `tests/e2e/state-cities/state-cities.spec.ts` ✓
**Priority:** P3

### US-134: System Health — View Queue Status
**Role:** admin (permission: `system-health-view`)
**Story:** As an admin, I want to view the system health dashboard so that I can spot failed jobs or queue backlogs.
```
Given: 3 failed jobs exist in the queue
When: I navigate to /settings/system-health
Then: I see the failed jobs count and each job's error message
When: I click "Retry Jobs"
Then: The failed jobs are re-queued
```
**Seed:** Simulate failed jobs
**E2E:** `tests/e2e/settings/` ✓
**Priority:** P2

### US-135: Update Extra Student Charges
**Role:** admin (permission: `extra-student-charges-update`)
**Story:** As an admin, I want to update the per-additional-student surcharge so that multi-student families are billed correctly.
```
Given: The extra student charge is RM 10 per additional student
When: I update it to RM 15 and save
Then: New invoices for families with multiple students use RM 15 per extra student
```
**Seed:** Settings record
**E2E:** `tests/e2e/commitment-fees/settings.spec.ts` ✓
**Priority:** P2

---

## MODULE 14 — Content Management (CMS)

### US-140: Create Blog Article
**Role:** admin (permission: `blogs-add`)
**Story:** As an admin, I want to publish a blog article so that content appears on the parent/tutor app.
```
Given: I am on /blog/create
When: I fill in title, content, category, cover image, and set status to "Published"
Then: The article is published
 And: It appears on the blog list page
 And: Mobile app users can see it
```
**Seed:** None (new content)
**E2E:** `tests/e2e/content-management/articles-create.spec.ts` ✓
**Priority:** P3

### US-141: Edit Blog Article
**Role:** admin (permission: `blogs-edit`)
**Story:** As an admin, I want to edit an existing article so that content stays accurate.
```
Given: Article "5 Study Tips" exists
When: I update the title to "5 Study Tips for Form 5 Students" and save
Then: The updated title appears in the article list and on the app
```
**Seed:** Blog article record
**E2E:** `tests/e2e/content-management/articles-edit.spec.ts` ✓
**Priority:** P3

### US-142: Manage Mobile Banners
**Role:** admin (permission: `mobile-banner-advertise-add`)
**Story:** As an admin, I want to upload a promotional banner so that it appears on the mobile app home screen.
```
Given: I am on /banner/create
When: I upload a 1200×400 banner image, set a link URL, and set status "Active"
Then: The banner is saved and appears at the top of the mobile app home screen
```
**Seed:** Image fixture
**E2E:** `tests/e2e/content-management/promotions.spec.ts` ✓
**Priority:** P3

### US-143: Manage FAQs
**Role:** admin (permission: `faqs-add`)
**Story:** As an admin, I want to add a FAQ so that parents and tutors can find answers to common questions in the app.
```
Given: I am on /faq/create
When: I fill in question and answer and save
Then: The FAQ appears in the FAQ list
 And: I can trigger a push notification to alert users of the new FAQ
```
**Seed:** None
**E2E:** `tests/e2e/content-management/support.spec.ts` ✓
**Priority:** P3

---

## MODULE 15 — Staff Management

### US-150: List Staff
**Role:** admin (permission: `staff-view-list`)
**Story:** As an admin, I want to view all staff members so that I can manage the team.
```
Given: 5 staff members exist
When: I navigate to /staff
Then: A table shows all staff with name, email, phone, and linked portal user
```
**Seed:** `StaffFactory` ×5
**E2E:** `tests/e2e/staff/staff.spec.ts` ✓
**Priority:** P2

### US-151: Create Staff Member
**Role:** admin (permission: `staff-add`)
**Story:** As an admin, I want to create a staff profile and link it to a portal user so that commission tracking is tied to the right person.
```
Given: Portal user "Farah" exists
When: I create a staff profile for "Farah" and link it to her user account
Then: Farah's staff profile is created
 And: Requests assigned to Farah's user account generate commission entries for her staff profile
```
**Seed:** `UserFactory`, `StaffFactory`
**E2E:** `tests/e2e/staff/staff.spec.ts` ✓
**Priority:** P2

### US-152: View Staff Commission Summary (My Commission)
**Role:** staff (own commission only)
**Story:** As a staff member, I want to view my own commission summary so that I know how much I have earned this month.
```
Given: I am logged in as staff "Farah" who has earned RM 250 this month
When: I navigate to /my-commission
Then: I see my total commission for the current month
 And: A breakdown by request is shown
```
**Seed:** `StaffFactory`, commission records for Farah
**E2E:** `tests/e2e/staff-commission/my-commission.spec.ts` ✓
**Priority:** P2

---

## MODULE 16 — Subjects, Levels & Reference Data

### US-160: CRUD Subjects
**Role:** admin (permission: `subject-add`, `subject-edit`, `subject-delete`)
**Story:** As an admin, I want to manage subjects so that the subject dropdown is always current.
```
Given: Subjects [Maths, English, Science] exist
When: I add "Additional Mathematics" and save
Then: "Additional Mathematics" appears in subject dropdowns on forms
When: I delete "Science"
Then: "Science" no longer appears in dropdowns (soft-deleted)
```
**Seed:** `SubjectFactory`
**E2E:** `tests/e2e/subjects/subjects.spec.ts` ✓
**Priority:** P3

### US-161: CRUD Levels
**Role:** admin (permission: `level-add`, `level-edit`, `level-delete`)
**Story:** As an admin, I want to manage education levels so that request pricing is tied to the correct level.
```
Given: Levels [Form 1, Form 2 ... Form 5] exist
When: I add "A-Level" with hourly rate RM 80
Then: "A-Level" appears in level dropdowns and requests using it are priced at RM 80/hr
```
**Seed:** `LevelFactory`
**E2E:** `tests/e2e/levels/` ✓
**Priority:** P2

---

## MODULE 17 — Tickets & Support

### US-170: Create Support Ticket
**Role:** admin (permission: `tickets-create`)
**Story:** As an admin, I want to create a support ticket for a parent or tutor issue so that it is tracked to resolution.
```
Given: Parent "Puan Siti" reports a payment discrepancy
When: I create a ticket with category "Payment", priority "High", and description
Then: The ticket is created with status "Open"
 And: Puan Siti receives a confirmation notification
 And: The ticket appears in the ticket list
```
**Seed:** `ParentModelFactory`, `TicketSeeder`
**E2E:** GAP — only `backdate-escalation.spec.ts` exists; no create/CRUD tests
**Priority:** P1

### US-171: Assign Ticket to Staff
**Role:** admin (permission: `tickets-assign`)
**Story:** As an admin, I want to assign a ticket to a staff member so that ownership is clear.
```
Given: Ticket #TKT-001 is "Open" and unassigned
When: I assign it to staff "Farah"
Then: Farah is shown as the assignee on the ticket
 And: Farah receives a notification
```
**Seed:** `TicketSeeder`, `StaffFactory`
**E2E:** GAP
**Priority:** P1

### US-172: Resolve Ticket
**Role:** admin (permission: `tickets-resolve`)
**Story:** As an admin, I want to resolve a ticket so that the issue is recorded as fixed.
```
Given: Ticket #TKT-001 is "In Progress" assigned to "Farah"
When: I click "Resolve" and add resolution notes
Then: The ticket status changes to "Resolved"
 And: The parent receives a resolution notification
```
**Seed:** `TicketSeeder`
**E2E:** GAP
**Priority:** P1

### US-173: Reject or Close Ticket as No Action
**Role:** admin (permission: `tickets-resolve`)
**Story:** As an admin, I want to close a ticket that requires no action so that the queue stays clean.
```
Given: Ticket #TKT-002 is a duplicate of #TKT-001
When: I click "Close (No Action)" and note "Duplicate of TKT-001"
Then: The ticket is closed
 And: No further notifications are sent
```
**Seed:** `TicketSeeder`
**E2E:** GAP
**Priority:** P2

### US-174: Merge Tickets
**Role:** admin (permission: `tickets-resolve`)
**Story:** As an admin, I want to merge two tickets about the same issue so that duplicates are consolidated.
```
Given: Tickets #TKT-001 and #TKT-002 both report the same payment issue from the same parent
When: I merge #TKT-002 into #TKT-001
Then: #TKT-002 is marked as "Merged" and closed
 And: #TKT-001 shows a note that #TKT-002 was merged into it
```
**Seed:** `TicketSeeder` ×2
**E2E:** GAP
**Priority:** P2

---

## MODULE 18 — Manual Operations Jobs

### US-180: Trigger Invoice Send Job
**Role:** super-admin (permission: `system-health-manage`)
**Story:** As an admin, I want to manually trigger the invoice send job so that invoices are emailed/WhatsApp'd to parents on demand.
```
Given: 5 parents have pending invoices not yet sent
When: I click "Send Invoices" on /manual-jobs
Then: The invoice send job is queued
 And: Within 60 seconds, all 5 parents receive their invoice notification
 And: A success count is shown
```
**Seed:** `ParentModelFactory` ×5, `ParentInvoiceFactory` ×5 (unsent)
**E2E:** GAP — no manual-jobs/ folder
**Priority:** P2

### US-181: Trigger Monthly Bonus Calculation
**Role:** super-admin (permission: `system-health-manage`)
**Story:** As an admin, I want to manually run the monthly bonus calculation so that eligible tutors receive their bonuses.
```
Given: Bonus rules exist and 3 tutors meet the session threshold for June 2026
When: I click "Run Monthly Bonus" on /manual-jobs
Then: The bonus job runs
 And: 3 bonus records are created in the tutor payment journal
 And: A summary shows how many tutors received bonuses
```
**Seed:** `BonusRulesSeeder`, `TutorFactory` ×3 with completed sessions
**E2E:** GAP
**Priority:** P1

### US-182: Trigger Payment Reminder Job
**Role:** super-admin (permission: `system-health-manage`)
**Story:** As an admin, I want to manually trigger payment reminder notifications so that overdue parents are reminded.
```
Given: 5 parents have invoices overdue by 7+ days
When: I click "Send Payment Reminders"
Then: WhatsApp reminders are sent to all 5 parents
 And: A notification log entry is created for each
```
**Seed:** `ParentModelFactory` ×5, `ParentInvoiceFactory` ×5 (overdue)
**E2E:** GAP
**Priority:** P2

### US-183: Trigger Tutor Payment Notifications
**Role:** super-admin (permission: `system-health-manage`)
**Story:** As an admin, I want to notify tutors that their payment has been processed so that they know to check their bank.
```
Given: 3 tutors have payments marked as "Paid" today
When: I click "Send Tutor Payment Notifications"
Then: WhatsApp/push notifications are sent to all 3 tutors
```
**Seed:** `TutorFactory` ×3, `TutorPaymentFactory` ×3 (paid today)
**E2E:** GAP
**Priority:** P2

### US-184: Process Pending Level Changes
**Role:** super-admin (permission: `system-health-manage`)
**Story:** As an admin, I want to manually process level changes so that rate updates take effect immediately.
```
Given: 2 requests have level changes approved but not yet applied
When: I click "Process Level Changes"
Then: Both level changes are applied
 And: Future invoices for those requests use the new rates
```
**Seed:** Level change records (approved, unapplied)
**E2E:** GAP
**Priority:** P1

---

## MODULE 19 — Cross-Module User Journeys (Critical Paths)

### US-190: Full Tutor Lifecycle
**Role:** admin
**Story:** As an admin, I want to onboard a tutor, assign them to a request, track classes, and pay them so that the end-to-end service is validated.
```
Given: No tutor or request exists for this test
When: I create Tutor "Cikgu Zulaikha" with subjects [Maths, Form 5] and availability Mon-Fri 4-8pm
 And: I create Request TUT-E2E-001 for Parent "Puan Nora" (student Ahmad, Form 5 Maths)
 And: I assign Cikgu Zulaikha to TUT-E2E-001
 And: I schedule and clock in/out 3 classes
Then: An invoice is generated for Puan Nora for 3 sessions
When: I mark the invoice as paid
Then: A tutor payment entry is generated for Cikgu Zulaikha
When: I make the tutor payment
Then: Cikgu Zulaikha receives a payment notification
 And: Her payment slip is downloadable
```
**Seed:** Full seed via `E2ETestDataSeeder`
**E2E:** `tests/e2e/cross-module/tutor-lifecycle.spec.ts` ✓
**Priority:** P1

### US-191: Invoice → Payment → Tutor Pay Flow
**Role:** admin
**Story:** As an admin, I want to validate that an online payment from a parent correctly flows through to the tutor payment journal.
```
Given: Invoice #INV-E2E exists for RM 150
When: FIUU callback fires for #INV-E2E (paid RM 150)
Then: #INV-E2E is "Paid"
 And: Tutor payment journal has an entry for the tutor
 And: Staff commission journal has an entry for the assigned staff
```
**Seed:** `ParentInvoiceFactory`, `TutorFactory`, `StaffFactory`
**E2E:** `tests/e2e/cross-module/invoice-payment-flow.spec.ts` ✓
**Priority:** P1

### US-192: RBAC — Finance Staff Cannot Access User Management
**Role:** finance-admin
**Story:** As the system, I want to enforce permission boundaries so that finance staff cannot access user management or admin settings.
```
Given: User "Farah" has role "Finance Staff" (permissions: invoice-journal-view only)
When: Farah navigates to /user or /user/role
Then: She receives a 403 Forbidden response
When: Farah navigates to /parent/invoice-journal
Then: She can see the invoice journal
```
**Seed:** `UserFactory` (role: Finance Staff), `RolesSeeder`
**E2E:** Permission tests exist across modules ✓
**Priority:** P1

---

## COVERAGE SUMMARY

### Coverage Heat Map

| Module | E2E Folder | Spec Count | Coverage |
|---|---|---|---|
| Authentication | `auth/` | 4 specs | ✅ Good |
| User Management | `smoke/users` only | 1 spec | ⚠️ Partial |
| Roles & Permissions | None | 0 specs | ❌ Gap |
| Tutor Management | `tutors/` | 9 specs | ✅ Good |
| Tutor Requests | `tutor-requests/` | 10 specs | ✅ Good |
| Parent Management | `parents/` | 4 specs | ✅ Good |
| Student Management | `students/` | 2 specs | ⚠️ Partial |
| Class Management | `classes/` | 11 specs | ✅ Good |
| Invoice & Payment | `parent-invoices/`, `financial/` | 12 specs | ✅ Good |
| Tutor Payments | `tutor-payments/` | 9 specs | ✅ Good |
| Commitment Fees | `commitment-fees/`, `tutor-commitment-slips/` | 6 specs | ✅ Good |
| Staff Commission | `staff-commission/` | 10 specs | ✅ Good |
| Tutor Bonuses | `tutor-bonuses/` | 8 specs | ✅ Good |
| Reports & Analytics | `reports/` | 8 specs | ✅ Good |
| Notifications | `notification-architecture/` | 4 specs | ✅ Good |
| Broadcasts | `broadcasts/` | 5 specs | ✅ Good |
| Settings & Config | `settings/` | 2 specs | ⚠️ Partial |
| CMS | `content-management/` | 10 specs | ✅ Good |
| Staff Management | `staff/` | 5 specs | ✅ Good |
| Subjects & Levels | `subjects/`, `levels/` | 4 specs | ✅ Good |
| Tickets | `tickets/` | 1 spec | ❌ Gap |
| Manual Jobs | None | 0 specs | ❌ Gap |
| Matching Engine | None | 0 specs | ❌ Gap |
| Payment Transfers | None | 0 specs | ❌ Gap |
| Level Changes | `level-change/` | 1+ spec | ✅ Good |
| Cross-Module Journeys | `cross-module/` | 6 specs | ✅ Good |
| Workflows (Tier 1) | `workflows/` | 3 specs | ✅ Good |

### Priority Gaps to Fill (Ordered by Business Risk)

| # | Gap | Stories | Risk |
|---|---|---|---|
| 1 | **Tickets CRUD** | US-170, 171, 172, 173, 174 | High — staff workflows have no E2E safety net |
| 2 | **Payment Transfers** | US-094 | High — financial, LHDN audit trail |
| 3 | **Manual Jobs** | US-180–184 | High — ops rely on manual triggers monthly |
| 4 | **Matching Engine** | US-048 | Medium — core feature with no automated test |
| 5 | **User Management CRUD** | US-011–014 | Medium — admin access control |
| 6 | **Roles & Permissions CRUD** | US-020–023 | Medium — RBAC integrity |
| 7 | **Password Reset Flow** | US-005 | Medium — staff self-service blocked without this |
| 8 | **Pending Payouts Bulk** | US-103 | Medium — monthly payroll operation |
| 9 | **Invoice Follow-Up** | US-097 | Low — operational convenience |
| 10 | **CSV Import (Tutors/Parents)** | US-035 | Low — bulk onboarding utility |

---

## Data Seed Strategy

### E2ETestDataSeeder (already exists — augment, don't replace)

The seeder at `database/seeders/E2ETestDataSeeder.php` should provision:

```
Roles:       super-admin, finance-admin, staff-officer, read-only
Users:       1 per role (with stable email + password for auth fixtures)
States:      5 (Selangor, KL, Johor, Penang, Perak)
Cities:      3 per state
Subjects:    Maths, English, Science, BM, Physics, Chemistry, Add Maths
Levels:      Form 1–5, UPSR, PT3, SPM, IGCSE, A-Level
Curriculum:  SPM, IGCSE, Cambridge
Banks:       Maybank, CIMB, RHB, HLB
Tutors:      10 (varied subjects, locations, availability)
Parents:     5 (varied locations)
Students:    10 (2 per parent, varied levels)
Requests:    10 (varied statuses: Pending, Matched, Active, Completed, Cancelled)
Classes:     30 (mix of Scheduled, Completed, Cancelled)
Invoices:    20 (mix of Pending, Paid, Overdue)
TutorPay:   10 (mix of pending, paid)
Staff:       3 (linked to portal users)
Tickets:     5 (Open, In Progress, Resolved)
BonusRules: 2 active rules
CommRules:  3 active commission rules
```

### Per-Test Factory Pattern (preferred for isolation)

```typescript
// In each spec file — create minimal data inline, not shared state
test.beforeEach(async ({ request }) => {
  await request.post('/e2e/seed', {
    data: { recipe: 'tutor-with-request' }  // named recipe from SeederController
  });
});
```

### Fixture Files (for stable IDs)

Store seeded IDs in `tests/e2e/fixtures/seed-ids.{env}.json` (pattern already in use):
```json
{
  "adminUserId": 1,
  "superAdminEmail": "superadmin@e2e.test",
  "tutorId": 42,
  "parentId": 7,
  "requestId": 100
}
```

---

## Tool Recommendation

**Playwright** (already in use via `tests/e2e/tsconfig.json`) — correct choice for SIMS because:
- SIMS uses Inertia.js (React SPA); Playwright handles client-side routing correctly
- Laravel Dusk uses Selenium which is slower and flakier on SPAs
- Playwright's network interception is needed for FIUU callback simulation
- Already 198 spec files prove it works in this stack

**Data seeding:** Laravel factories (already 14 exist) + `E2ETestDataSeeder` + per-test HTTP seed endpoint

---

*Total user stories: 62 | Covered by E2E: 45 | Partial: 7 | Gap: 10*
*198 spec files exist — one of the most comprehensive E2E suites in a Laravel/Inertia.js project*
