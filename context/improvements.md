# Feature Improvements: Implementation Cross-Check

This backlog was reconciled with current source on 2026-11-27. “Implemented”
means source paths and behavior are present; it does not certify fresh test or
manual results. Resolve the [VERIFY] items against PD2 feedback/PD3 acceptance
criteria before treating them as closed.

## 1. Room-aware visits and asset codes — IMPLEMENTED IN SOURCE

- `equipment.Room` is a model with a unique name/prefix, building, capacity,
  active flag, and asset sequence counter.
- `Asset.room` and `LabVisit.room` link equipment and visits to rooms.
- `Asset.save()` generates sequential room-prefixed codes when creating an
  asset without a code. `RoomForm` derives a prefix when blank.
- Check-in lists only active rooms; `RoomCheckInTests` covers picker,
  successful check-in, inactive/missing-room rejection, and active-visit room
  filtering.
- Student/Researcher equipment inventory and borrowing are limited to the
  active visit's room; staff has unrestricted room scope.
- Incidents link optionally to a visit and equipment loan, so room context is
  indirect; there is no direct `Incident.room` field.

**[VERIFY]** Compare against the original PD2 issue and test similar room
prefixes/creation concurrency on the target PostgreSQL environment.

## 2. Defective equipment restrictions and incident redirect — PARTIAL

Implemented:

- Borrowing only permits assets in `AVAILABLE` state and rechecks status
  inside a transaction with a row lock.
- A defective pre-borrow condition changes asset availability to Maintenance
  or Missing and redirects to incident creation with context.
- Returning Damaged/Malfunctioning items sets Maintenance; Missing sets
  Missing; Good sets Available.
- `equipment.tests.EquipmentBehaviorTests` includes defect/unavailable cases.

Remaining:

- No invariant requires an incident to be created before an asset can later be
  changed to Available. Incident creation is prompted by redirect, not enforced
  as a prerequisite.
- [VERIFY] Confirm the borrow UI prevents users from assuming the defective
  item was loaned and confirm incident prefill/association in a manual flow.

## 3. Shared borrow/return condition options — IMPLEMENTED IN SOURCE

- `equipment.models.CONDITION_CHOICES` defines Good, Damaged,
  Malfunctioning, and Missing.
- `BorrowForm` and `ReturnForm` use the shared options.
- `equipment.tests.EquipmentBehaviorTests.test_borrow_and_return_forms_use_the_shared_condition_choices`
  checks the form choices.

**[VERIFY]** Capture a fresh focused test result before reporting this as
verified in the final PD3 report.

## 4. Logout guard for active operations — IMPLEMENTED IN SOURCE

- `authentication.views.LabTraceLogoutView` blocks logout if the current user
  has an active visit or any unreturned equipment.
- The warning includes links to visit history/check-out and equipment loans.
- `authentication.tests.LoginBehaviorTests.test_logout_is_blocked_for_active_visit_or_unreturned_equipment`
  exercises the block.

**[VERIFY]** Confirm expected role scope. Current code applies the guard to all
authenticated roles, not only students/instructors.

## 5. Status/condition badges — IMPLEMENTED IN TEMPLATES

- `equipment.templatetags.severity_tags.severity_badge` maps condition,
  availability, incident severity, and incident status values to badge colors.
- It is used in equipment inventory, personal equipment, return, and incident
  list/detail templates.
- Colors include emerald (good/available/low/resolved), amber
  (malfunctioning/maintenance/medium/reported), rose
  (damaged/missing/high/critical), and blue (borrowed/investigation).

**[VERIFY]** Review visual contrast and ensure every requested role/view shows
the intended badge; source references alone do not prove accessibility or
visual consistency.

## 6. Audit trail filtering for staff — IMPLEMENTED IN SOURCE

- `/dashboard/audit/` and `/dashboard/audit/api/` are guarded by
  `dashboard.access.staff_required`, which allows Instructors and Admins.
- `templates/dashboard/audit.html` provides filters for user name/email, lab,
  asset, incident status, and date range.
- `dashboard/audit.py` applies the filters across visit, equipment loan, and
  incident status-history events; the API uses the same filters and pagination.
- The current asset filter matches equipment name, not asset code, even though
  the UI's placeholder text mentions both.
- Event retrieval remains capped at 500 rows per source before merged
  pagination.

**[VERIFY]** Freshly run dashboard audit tests/performance tests. Admin access
is present in the shared staff policy; it is not restricted to Admin alone.

## 7. Image/file upload removal — INTENTIONALLY REMOVED

- Equipment image fields and incident attachments are absent from current
  models/forms and media settings.
- `equipment/migrations/0002_remove_equipmentlog_post_condition_img_and_more.py`
  removes pre/post condition image fields.
- `incidents/migrations/0002_delete_incidentattachment.py` removes the
  attachment model.
- The historical removal commit is `4b2e483` (`removed Image upload feature`).

Treat uploads as deliberately removed, not an unfinished feature, unless the
approved WBS or PD3 acceptance criteria explicitly require them.

## 8. Role choice during registration — NOT IMPLEMENTED AS SELF-SERVICE

- `RegistrationForm.save()` forces newly registered users to `STUDENT`.
- Admin user management can change a user's role; superuser role is controlled
  by the user model/admin path.
- `dashboard.views.home()` redirects each authenticated role to its dashboard.
- The optional Student/Instructor selector or instructor invite/approval
  workflow is not present.

Decision needed: [VERIFY] whether PD3 requires role self-selection. If added,
do not expose Admin assignment to public registration; use an approved
Instructor verification or admin approval policy.
