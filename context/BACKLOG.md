# LabTrace Backlog

## Project Progress — WBS Scope-Adjusted

**Overall WBS completion: 100% (15/15 deliverables complete).**

Calculation: 15 completed WBS deliverables divided by 15 in-scope deliverables,
with equal weight per deliverable.

This estimate treats equipment/incident image uploads as intentionally
out-of-scope, per the current project decision, and counts the implemented,
searchable staff audit trail as complete. The condition-check deliverable is
complete for recording condition/status without image evidence. This is a
feature-scope estimate, not a claim that all tests pass, that audit history is
unbounded, or that deployment hardening is complete. Fresh test results remain
unverified; the audit event sources currently have a 500-row cap.

| WBS phase | Deliverables complete | Completion |
|---|---:|---:|
| 1.1 Authentication | 3/3 | 100% |
| 1.2 User Management | 3/3 | 100% |
| 1.3 Access & Visit Logging | 3/3 | 100% |
| 1.4 Equipment Management | 3/3 | 100% |
| 1.5 Incident & Accountability Tracking | 3/3 | 100% |
| **Overall** | **15/15** | **100%** |

## 1. Snapshot / Audit Context

**Audit date:** 2026-11-27

**Current scope-adjusted WBS status:** 15/15 complete (100%). Image uploads
are intentionally excluded from the accepted scope; the searchable audit trail
is treated as delivered. See the progress summary above for the calculation
and verification caveats.

**Repository state**

- Current branch: `feature/enhanced-ui`
- HEAD: `570c11a` (`pd3`)
- Branches found: `master`, `develop`, `feature/enhanced-ui`
- No `main` branch exists.
- Local working tree is not clean: deleted `progress/*.md` files and untracked
  `context/` and `docs/` files are present. These documentation changes do not
  alter application code.
- `origin/master` and local `master` point to `adca3a0`.
- `origin/develop` and local `develop` point to `c785648`.
- `develop` and `master` have no reported file differences in this audit.
- `feature/enhanced-ui` has no merge base with `master` or `develop`, so a
  normal merge-base diff could not be used. Status is based on the inspected
  working-tree source and relevant commits on `feature/enhanced-ui`.
- Relevant active revisions include:
  - Room-centered `Room`/`Asset`/`LabVisit` changes.
  - Room-scoped Student/Researcher equipment borrowing.
  - Shared Good/Damaged/Malfunctioning/Missing conditions.
  - Logout blocking for active visits/open loans.
  - Removal of equipment/incident picture and file uploads.

**WBS sources**

- Primary WBS source: `context/WBS_STATUS.md`, an audit snapshot dated
  2026-11-17.
- Supporting notes: `context/pd3-hardening-context.md`,
  `context/improvements.md`, `context/domain-and-workflows.md`, and
  `README.md`.
- A separate slide/PDF exists at `docs/Labtrace-Bajenting-Johnru-G1-PD1.pdf`,
  but no additional Markdown WBS table was found. `[VERIFY]` whether the PDF
  has the same deliverable breakdown or additional acceptance criteria.

**Historical audit snapshot (2026-11-17; not the current scope-adjusted status)**

- WBS items implemented with supporting code: **13 of 15**
- WBS items only partially implemented: **2 of 15**
- WBS items with no implementation found: **0 of 15**
- Historical weighted estimate: **93.3%**, counting both condition evidence
  uploads and audit performance/completeness as partial requirements.
- Current scope-adjusted estimate: **100%**, counting condition recording
  without images and the searchable audit trail as complete.
- Current test pass status: **[VERIFY]** — no full fresh test run is recorded
  in this backlog audit.
- Historical full-suite result: 64 tests, 55 passed, 3 failed, 6 errored.
  It predates some active revisions and must not be treated as current.

## 2. Done (Implemented & Aligned with WBS)

### 1.1 Authentication

- **1.1.1 Login** — Implemented in `authentication/urls.py`,
  `authentication/views.py`, `authentication/forms.py`, and
  `templates/registration/login.html`.
  - Login accepts username or email.
  - Django session authentication is used.
  - Inactive users are rejected.
  - Logout is guarded for active visits/open equipment loans.
  - Evidence: `authentication/tests.py` (`LoginBehaviorTests`).

- **1.1.2 Register** — Implemented in `authentication/views.py`,
  `authentication/forms.py`, `authentication/models.py`, and
  `templates/authentication/register.html`.
  - Uses Django `UserCreationForm`.
  - Validates institutional email domain and unique email.
  - Requires first name and last name.
  - Passwords are Django-hashed.
  - Public registration is forced to `STUDENT`.
  - `[VERIFY]` registration behavior test coverage.

- **1.1.3 Change/Reset Password** — Implemented in `users/urls.py`,
  `users/templates/users/password_reset_form.html`, and reset email
  templates. Password change is routed through Django's
  `PasswordChangeView` to `templates/users/password_change.html`.
  - Evidence: `users/tests.py` routing and password-change tests.
  - `[VERIFY]` complete email/token/deep-link/new-password flow.

### 1.2 User Management

- **1.2.1 Update Profile** — Implemented in `users/views.py`,
  `users/forms.py`, `templates/users/profile.html`, and
  `templates/users/profile_edit.html`.
  - The update view uses `request.user`; no public object ID is accepted.
  - Evidence: `users/tests.py` profile behavior tests.

- **1.2.2 User Management & RBAC** — Implemented across
  `authentication/models.py`, `users/middleware.py`,
  `users/decorators.py`, `users/permissions.py`, and `dashboard/views.py`.
  - Roles: Student, Instructor, Researcher, and Admin.
  - Server-side role mixins/decorators/middleware exist.
  - Role-specific dashboard views are routed.
  - Evidence: role and dashboard tests.
  - `[VERIFY]` direct-URL/IDOR coverage for every mutating route.

- **1.2.3 Deactivate Account** — Implemented in `users/views.py`,
  `users/urls.py`, and `templates/users/user_list.html`.
  - Uses inherited `is_active=False` as soft deactivation.
  - Inactive users cannot log in.
  - Evidence: `authentication/tests.py`
    `test_inactive_user_cannot_log_in`.

### 1.3 Access & Visit Logging

- **1.3.1 Digital Check-In** — Implemented in
  `access_logging/models.py`, `forms.py`, `views.py`, `room_picker.py`,
  `urls.py`, and `templates/access_logging/check_in.html`.
  - Timestamps, room, purpose, and active-status creation are implemented.
  - A database constraint permits at most one active visit per user.
  - Evidence: `access_logging/tests.py` and
    `access_logging/tests_room_checkin.py`.

- **1.3.2 Digital Check-Out** — Implemented in
  `access_logging/views.py` and `LabVisit.check_out()`.
  - Records exit time and whole-minute duration.
  - Rejects checkout when unreturned equipment exists.
  - Evidence: `access_logging/tests.py`.

- **1.3.3 Centralized Laboratory Dashboard** — Implemented in
  `dashboard/central.py`, `dashboard/selectors.py`,
  `templates/dashboard/central.html`, `dashboard/urls.py`, and
  `static/js/live_refresh.js`.
  - Staff-only active visits and occupancy.
  - Live JSON endpoint.
  - Equipment availability/current borrowers and usage/condition metrics.
  - Unresolved incident totals.
  - Evidence: `dashboard/tests.py`.

### 1.4 Equipment Management

- **1.4.1 Borrow Equipment** — Implemented in `equipment/urls.py`,
  `equipment/views.py`, `equipment/forms.py`, `equipment/models.py`,
  `equipment/room_scope.py`, and `equipment/tests.py`.
  - Requires an active visit.
  - Links an open loan to the visit.
  - Student/Researcher borrowing is room-scoped.
  - Staff borrowing is unrestricted.

- **1.4.2 Pre/Post Condition Check** — Complete for the accepted scope in
  `equipment/models.py`, `equipment/forms.py`, `equipment/views.py`, and the
  borrow/return templates.
  - Pre/post conditions are recorded using Good, Damaged, Malfunctioning, and
    Missing values.
  - Image/file uploads were intentionally removed and are out of scope; they
    are not counted as a remaining deliverable.
  - `[VERIFY]` Fresh focused test results; condition and equipment behavior
    test coverage exists in `equipment/tests.py`.

- **1.4.3 Return Equipment** — Implemented in `equipment/views.py`,
  `equipment/forms.py`, `equipment/models.py`, and
  `templates/equipment/return.html`.
  - Sets return timestamp, post-condition, and availability.
  - Unlinks the asset operationally through the returned EquipmentLog.
  - Evidence: `equipment/tests.py`.

- **Room-centered enhancements aligned to active revisions**
  - `equipment/models.py` defines `Room`, sequential room-prefixed asset codes,
    and availability/condition choices.
  - `equipment/room_views.py` provides room add/edit/list administration.
  - `access_logging/models.py` and `CheckInForm` include the room relationship.
  - Evidence: `equipment/tests.py`,
    `access_logging/tests_room_checkin.py`.

### 1.5 Incident & Accountability Tracking

- **1.5.1 Report Incident** — Implemented in `incidents/models.py`,
  `forms.py`, `views.py`, `urls.py`, and
  `templates/incidents/incident_form.html`.
  - Links to the reporter and optionally the visit/equipment loan.
  - Restricts visit/loan choices to the reporter's records.
  - Evidence: `incidents/tests.py`.
  - Picture/file evidence uploads were intentionally removed and are
    excluded from the accepted scope.

- **1.5.2 Incident Status Engine** — Implemented in
  `incidents/models.py`, `incidents/services.py`, `incidents/views.py`,
  and `templates/incidents/incident_detail.html`.
  - Reported, Under Investigation, Resolved, and Closed states exist.
  - Staff-only updates and append-only status history are implemented.
  - Resolution notes and timestamps are maintained.
  - Evidence: `incidents/tests.py`.

- **1.5.3 Searchable Audit Trail** — Complete in `dashboard/central.py`,
  `dashboard/audit.py`, `templates/dashboard/audit.html`, and the dashboard
  audit API.
  - Admins and Instructors can search/filter events by user, lab, asset name,
    incident status, and date range; results are paginated.
  - Server-side access is enforced by the staff access policy.
  - `[VERIFY]` Fresh tests and completeness/performance over large histories.
    Each event source is capped at 500 rows before merge and pagination.

## 3. Not Done / Remaining (Active Backlog)

### High priority

- **Verify searchable audit trail at target data volume**
  - Search/filter UI and API are implemented and counted as a completed WBS
    deliverable.
  - Fresh tests and large-history behavior remain unverified; each source is
    capped at 500 records before merged pagination.
  - Next: run dashboard audit/performance tests against PostgreSQL and assess
    whether the cap is sufficient for the expected deployment.

- **Replace insecure deployment settings**
  - `labtrace/settings.py` has `DEBUG=True`, a hard-coded development
    `SECRET_KEY`, and localhost-only `ALLOWED_HOSTS`.
  - Next: add environment-specific secrets and deployment settings, disable
    debug, configure real hosts, HTTPS and secure cookies.

- **Remove external and offline-compliance violations**
  - `templates/base.html` loads Google Fonts and Tailwind CDN URLs even though
    local assets exist.
  - Next: remove external requests or update offline claims/documentation.

- **Rerun and repair the automated test suite**
  - The last historical complete run recorded failures/errors involving audit
    queries, stale reset heading, dashboard fixture data, and seed command.
  - Next: run Django checks and the full suite against reachable PostgreSQL,
    repair actual failures, and publish fresh totals.

- **Verify and repair demo seeding**
  - `dashboard/management/commands/seed_demo_data.py` exists.
  - `dashboard/tests_seed.py` exists.
  - The historical WBS snapshot says it failed due to an unsupported user field,
    but the active model has `institutional_id` and the current command appears
    to use it.
  - Next: `[VERIFY]` by running the command/tests in an isolated database.

### Medium priority

- **Confirm complete password-reset behavior**
  - Reset routes/templates exist and routing tests exist.
  - No fresh test proves a full emailed token/deep-link/new-password workflow.
  - Next: run a manual and/or automated end-to-end reset test.

- **Complete authorization and IDOR review**
  - Role and ownership checks exist for profiles, incidents, equipment,
    check-in/check-out, rooms, and staff dashboards.
  - Direct-ID tests are incomplete for all object routes.
  - Next: add/execute tests changing visit, loan, incident, profile, asset, and
    room IDs under Student, Instructor, Researcher, and Admin sessions.

- **Confirm room-centered active revisions**
  - Room migrations, room UI, room-prefixed asset codes, and room check-in
    code exist on `feature/enhanced-ui`.
  - `[VERIFY]` whether the same behavior is merged into `master`/`develop`
    and whether room migration state is consistent with deployments.

- **Correct release/documentation drift**
  - Root `README.md` and older context/WBS notes contain stale dashboard,
    incident, upload, and test claims.
  - Next: update only after fresh code/test verification. This backlog does not
    authorize application code changes.

- **Confirm public role-selection scope**
  - Registration intentionally forces `STUDENT`.
  - Instructor/Researcher assignment is administrative.
  - `[VERIFY]` whether the accepted PD3 scope requires self-selected
    Instructor/Student roles or approval/invite logic.

- **Complete evidence/branch status for the PD3 report**
  - The selected/created PD3 draft contains `[placeholder]` fields and needs
    screenshot, branch, PR, and test evidence.
  - `[VERIFY]` actual branch/PRs and submission details.

### Low priority

- **Audit git hygiene and generated files**
  - `.gitignore` covers `.env`, `.venv`, `db.sqlite3`, caches, `media/`, and
    `sent_emails/`.
  - Ignore rules do not remove already tracked files.
  - Next: `[VERIFY]` tracked files with `git ls-files` and remove generated
    secrets/email output if present.

- **Refresh WBS verification notes after fresh tests**
  - The current 100% figure is a scope-adjusted feature-completion estimate,
    not a test-pass or production-readiness score.
  - Next: rerun a code-based WBS audit and update test evidence/status when
    results are available; retain the scope decision excluding image uploads.

- **Improve incident status transition strictness**
  - Current service permits staff to move to any different status, rather than
    implementing a strict Reported -> Investigation -> Resolved -> Closed
    graph.
  - `[VERIFY]` whether the WBS requires strict transitions or permits reopening
    and direct staff transitions.

## 4. Suggested Next Execution Order

1. Run `python manage.py check`, `python manage.py makemigrations --check --dry-run`,
   and focused/full Django tests against PostgreSQL. This establishes the
   current truth for all remaining WBS items.
2. Clarify with the PD1/PD2/PD3 materials whether incident/equipment evidence
   attachments are mandatory. The active branch intentionally removed them.
3. Verify audit trail behavior/performance at target data volume; address the
   500-row source cap if it does not meet operational needs.
4. Repair or verify demo seeding and full password-reset behavior.
5. Perform the authorization/IDOR test pass across profile, visit, loan,
   incident, room, and admin routes.
6. Remove CDN/font external requests or formally document a network dependency.
7. Move deployment secrets out of source and disable debug for release.
8. Reconcile branch `feature/enhanced-ui` into the target integration/release
   branch after tests pass and migration compatibility is confirmed.
9. Refresh README, WBS status, PD3 evidence, and this backlog with final
   command/test/PR results.
