# CSIT327 PD3 Hardening Report — Starter Draft

> **Draft status:** Initial context only. Confirm all details against the PD2
> issue list, current branch, manual testing, and the final PD3 report template
> before submission. Code presence is not proof of successful deployment or
> manual verification.
>
> For current technical references, see [context/README.md](README.md),
> [project-overview.md](project-overview.md),
> [domain-and-workflows.md](domain-and-workflows.md), and
> [testing-and-ops.md](testing-and-ops.md).

## Project Information

| Field | Draft |
|---|---|
| System Name | LabTrace |
| Student Name | Johnru I. Bajenting [confirm spelling and official format] |
| Section | CSIT327-G1 [confirm] |
| Increment | PD3 — Hardening [confirm increment number/title] |
| Core Feature Hardened | Room-aware laboratory access and equipment borrowing, with role-based access and operational accountability [confirm scope] |
| GitHub Repository | [repository URL] — repository name observed as `Enjanurr/Labtrace`; add the exact URL |
| Date Submitted | [submission date] |

## 1. PD2 Issues Resolved

The following are candidate resolutions based on implementation currently
present in the workspace. Match each item to the actual PD2 issue or instructor
feedback before marking it resolved.

| Candidate issue / improvement | Current implementation evidence | Verification |
|---|---|---|
| Equipment and visits need to be associated with a lab room. | `equipment.models.Room`; `Asset.room`; `access_logging.models.LabVisit.room`; room-aware check-in in `access_logging`; `access_logging.tests_room_checkin.RoomCheckInTests`. The visit model synchronizes the legacy `lab_location` text when a room is assigned. | Implemented in code; compare with the original PD2 issue and verify on the target database. |
| Asset codes need to be identifiable and generated consistently. | `equipment.models.Asset.save()` and `derive_room_prefix()` generate sequential room-prefixed codes; `equipment.tests.RoomAndAssetCodeTests` covers generation and room filtering. | Implemented in code; add manual result / screenshot. |
| Borrowing needs to respect active visits and room scope. | `equipment.room_scope.borrow_scope`; `equipment.views.borrow_view`; `equipment.tests.EquipmentBehaviorTests` and `RoomAndAssetCodeTests` cover active-visit requirement, room-restricted inventory, and rejecting assets from another room. | Implemented in code; confirm all relevant roles and edge cases manually. |
| Defective or unavailable items should not be borrowed. | `equipment.models.Asset.Availability`; `equipment.views.borrow_view` blocks non-available assets and redirects defective pre-condition reports to incident creation; `EquipmentBehaviorTests.test_defective_asset_is_blocked_and_return_defect_updates_status` covers this flow. | Implemented in code; verify the UI flow and incident association manually. |
| Condition values should be consistent between borrowing and return. | Shared `equipment.models.CONDITION_CHOICES`; `EquipmentBehaviorTests.test_borrow_and_return_forms_use_the_shared_condition_choices`. | Implemented in code; record a fresh focused test result. |
| Logout should be blocked while a user has an active visit or unreturned equipment. | `authentication.views.LabTraceLogoutView.dispatch()` blocks logout and shows links to resolve active visits or open loans; `LoginBehaviorTests.test_logout_is_blocked_for_active_visit_or_unreturned_equipment`. | Implemented in code; verify message and links for each role manually. |
| Active visits and open equipment loans need data-integrity protection. | Conditional unique constraints `one_active_visit_per_user` in `access_logging.models.LabVisit` and `one_open_log_per_asset` in `equipment.models.EquipmentLog`. | Implemented in model definitions; confirm migrations are applied to the intended database. |

**PD2 issue references and final disposition:** [Add issue IDs / feedback
references, resolution dates, and any items still open.]

## 2. Hardening Checklist

### 2.1 Validation and Error Handling

- [x] Institutional email domain validation is implemented by
  `authentication.models.validate_institutional_email` and used by
  `authentication.forms.RegistrationForm`.
- [x] Registration uses Django `UserCreationForm`; the form assigns the
  `STUDENT` role instead of accepting a public self-selected role.
- [x] Email uniqueness is enforced by the custom user model and checked by
  `RegistrationForm.clean_email()`.
- [x] Equipment condition forms share `CONDITION_CHOICES`; see
  `equipment/forms.py` and `equipment.tests`.
- [x] Room and asset forms validate room data and support generated asset
  codes; see `equipment/forms.py`, `equipment/models.py`, and `equipment/tests.py`.
- [x] Borrow and return forms share the same four condition choices, including
  `Missing`; see `equipment.models.CONDITION_CHOICES` and
  `EquipmentBehaviorTests.test_borrow_and_return_forms_use_the_shared_condition_choices`.
- [x] Borrowing rejects unavailable equipment and redirects defective
  condition reports to incident creation; see `equipment.views.borrow_view`
  and `EquipmentBehaviorTests.test_defective_asset_is_blocked_and_return_defect_updates_status`.
- [x] The incident view pre-fills visit/loan and defective-condition details
  from query parameters; `IncidentForm` limits visit/loan options to the
  signed-in user's records. See `incidents.views.incident_create` and
  `incidents.forms.IncidentForm`. [Manual flow still needs verification.]
- [ ] Confirm user-facing validation and error messages for invalid,
  duplicate, and missing form values. [Manual verification]
- [x] Picture/file uploads were intentionally removed from the current
  implementation: equipment condition image fields and incident attachments
  are removed by migrations
  `equipment/migrations/0002_remove_equipmentlog_post_condition_img_and_more.py`
  and `incidents/migrations/0002_delete_incidentattachment.py`. Active
  models/forms do not expose uploads, and settings have no media configuration.
  Treat this as an intentional scope decision unless approved WBS/PD3
  acceptance criteria require uploads.
- [ ] Confirm database and unexpected application errors are handled without
  exposing sensitive details to users.

### 2.2 Security and Access Control

- [x] Django CSRF middleware is enabled in `labtrace/settings.py`.
- [x] The custom user model defines Student, Instructor, Researcher, and Admin
  roles in `authentication/models.py`.
- [x] Role-based access middleware and view-level access helpers exist in
  `users/middleware.py`, `users/decorators.py`, and `users/permissions.py`.
- [x] Self-service profile views operate on the signed-in user; profile
  update behavior is covered in `users/tests.py`.
- [x] Incident tests cover student ownership restrictions and staff access in
  `incidents/tests.py`.
- [x] Equipment room-scope tests verify that a student cannot borrow an asset
  from another room in `equipment/tests.py`.
- [x] Logout is blocked when the signed-in user has an active visit or
  unreturned equipment; see `authentication.views.LabTraceLogoutView` and
  `LoginBehaviorTests.test_logout_is_blocked_for_active_visit_or_unreturned_equipment`.
- [ ] Verify every POST form includes a CSRF token and every mutating endpoint
  rejects unauthorized methods/roles. [Manual/code review]
- [ ] Replace the hard-coded development `SECRET_KEY` and disable `DEBUG`
  before any deployment; `labtrace/settings.py` currently has
  `DEBUG = True` and a development placeholder key.
- [ ] Set deployment-appropriate `ALLOWED_HOSTS` and review HTTPS, secure
  cookie, and proxy settings before deployment.
- [ ] If media/file handling is added or enabled, verify authorization on
  downloads. Current `labtrace/settings.py` has no `MEDIA_ROOT` or
  `MEDIA_URL` configuration.
- [x] Audit UI/API is available to Instructor and Admin roles at
  `/dashboard/audit/` and `/dashboard/audit/api/`. It supports filters for
  user, lab, asset name, incident status, and date range. Access is enforced by
  `dashboard.access.staff_required`. The asset filter matches equipment name,
  not asset code, and results are capped at 500 per source.
- [ ] Freshly verify audit search/filter behavior and query performance.
- [ ] Check for IDOR across visit, equipment loan, incident, and profile
  routes by changing object IDs while signed in as another user.
- [ ] Confirm password reset email delivery and reset-link behavior in the
  configured environment. The project is configured for file-based email in
  `labtrace/settings.py`.

### 2.3 Data Integrity and Database

- [x] The configured database engine is PostgreSQL
  (`django.db.backends.postgresql`) in `labtrace/settings.py`; credentials are
  read from environment variables loaded through `python-dotenv`.
- [x] `LabVisit` protects user history with `PROTECT` and enforces at most one
  active visit per user through a conditional unique constraint.
- [x] `EquipmentLog` protects visit/asset history and enforces at most one
  unreturned loan per asset through a conditional unique constraint.
- [x] `Incident` and `IncidentStatusHistory` retain incident state and
  transition history; see `incidents/models.py` and `incidents/services.py`.
- [ ] Run and record `python manage.py check`,
  `python manage.py makemigrations --check --dry-run`, and migration status
  against the intended PostgreSQL environment.
- [ ] Verify transaction behavior for concurrent check-in, borrowing, and
  return operations.
- [ ] Confirm backups, restore procedure, and retention policy. [Operations
  evidence needed]

## 3. Automated Tests

The following test modules are present. Record the actual command, environment,
date, and results from a fresh run; do not treat older report results as
current.

| Test module | Coverage indicated by test names/content | Result |
|---|---|---|
| `authentication/tests.py` | Login by email, inactive-user rejection, logout guard for active visits/open equipment | [Run result] |
| `users/tests.py` | Password-reset routing, profile access/update, password change, management route names | [Run result] |
| `access_logging/tests.py` | Visit check-in/history/checkout and staff active-visits access | [Run result] |
| `access_logging/tests_room_checkin.py` | Active-room picker, room/building data, valid check-in, inactive/missing-room rejection, room-filtered active visits | [Run result] |
| `equipment/tests.py` | Borrow/return, active visit, room scope, asset-code generation, defective item handling, shared condition choices | [Run result] |
| `incidents/tests.py` | Incident ownership, staff access, submission validation, status transitions and lifecycle | [Run result] |
| `dashboard/tests.py` | Central dashboard access/data and audit filtering | [Run result] |
| `dashboard/tests_performance.py` | Audit pagination, query counts, response time, and index coverage | [Run result] |
| `dashboard/tests_seed.py` | Demo seed command creates roles/data, avoids duplicates, and resets data | [Run result; verify command passes] |

**Commands and results**

```text
python manage.py check
[Paste concise output/result]

python manage.py makemigrations --check --dry-run
[Paste concise output/result]

python manage.py test
[Paste test count, pass/fail/error totals, and relevant failure summary]
```

**Automated test limitations / known failures:** [List current failures,
environment/database limitations, and follow-up issue references.
`context/WBS_STATUS.md` is a historical snapshot; rerun tests before copying
its results.]

## 4. Branches and Pull Requests

| Work item | Branch | Pull request | Status / review evidence |
|---|---|---|---|
| PD3 hardening increment | [branch name] | [PR URL or N/A] | [Open / merged / reviewed; add date and review notes] |
| Additional related changes | [branch name] | [PR URL or N/A] | [Status] |

## 5. Evidence Screenshots

Add dated screenshots or evidence links. Avoid exposing real credentials,
personal data, or secret configuration values.

1. Registration validation and successful account creation — [screenshot/link]
2. Role-appropriate dashboard and denied access for an unauthorized role —
   [screenshot/link]
3. Room selection, visit check-in, and active visit — [screenshot/link]
4. Equipment inventory and rejected borrow attempt for an unavailable item —
   [screenshot/link]
5. Equipment return and updated condition/availability — [screenshot/link]
6. Incident report and status-history workflow — [screenshot/link]
7. Automated test run / terminal results — [screenshot/link]
8. Database or migration verification with secrets redacted — [screenshot/link]

## 6. Remaining Tasks

- [ ] Compare every item in `context/improvements.md` with the current
  implementation; update its pending/implemented labels only after
  verification.
- [ ] Update `context/improvements.md`: room-aware check-in, defective-item
  borrowing restrictions, shared condition choices, and the logout guard now
  have implementation evidence in the workspace; independently verify the
  remaining suggestions before changing their status.
- [ ] Confirm whether self-service role selection is required. Registration
  currently assigns `STUDENT` in `authentication.forms.RegistrationForm`;
  do not allow public assignment of privileged roles.
- [ ] Implement and verify the proposed standardized condition/status badges
  if they are within the approved PD3 scope.
- [ ] Finish deployment hardening: secret management, production debug
  settings, allowed hosts, and secure transport/cookie settings.
- [ ] Verify owner/staff authorization on object-detail and mutation routes.
  If media handling is later added/enabled, verify download authorization too.
- [ ] Run the complete test suite against a reachable PostgreSQL test
  database, resolve failures, and attach results.
- [ ] Verify migration consistency and document database backup/restore
  procedures.
- [ ] Complete manual checks and add screenshots/evidence links above.
- [ ] [Add remaining PD3 acceptance criteria and owner/target date.]

## 7. Outstanding Issues

| Issue | Severity | Evidence / impact | Next action |
|---|---|---|---|
| Development secret and `DEBUG = True` are in `labtrace/settings.py`. | High before deployment | Unsafe deployment defaults if exposed beyond local development. | Use environment-specific settings and secret configuration; verify production settings. |
| Full test-suite status is not freshly recorded in this draft. | Medium | Historical results may not represent the current workspace. | Run tests on the target PostgreSQL environment and record exact output. |
| Picture/file uploads were intentionally removed from incident and equipment flows. | Scope-dependent | Current forms/models do not accept evidence files; removal migrations are present. | Confirm approved WBS/PD3 requirements; restore only if uploads are explicitly required. |
| Public registration always assigns the Student role. | Scope-dependent | Applicants cannot select Student/Instructor during self-registration; this is a security restriction in the current form, not a role-approval workflow. | Confirm approved registration policy; retain admin-controlled privileged role assignment. |
| [Add issue] | [Severity] | [Impact] | [Action / owner] |

## 8. Test Accounts

Use only dedicated, non-production accounts. Do not put real passwords,
recovery tokens, or personal data in this report.

| Role | Username/email | Password handling | Verification |
|---|---|---|---|
| Student | [create dedicated test account] | [store outside this report; provide through approved channel if needed] | [Not yet verified] |
| Instructor | [create dedicated test account] | [store outside this report; provide through approved channel if needed] | [Not yet verified] |
| Researcher | [create dedicated test account] | [store outside this report; provide through approved channel if needed] | [Not yet verified] |
| Admin | [create dedicated test account] | [store outside this report; provide through approved channel if needed] | [Not yet verified] |

## 9. Declaration

I declare that the information and evidence in the final report accurately
represent the implemented and tested LabTrace PD3 increment. Any limitations,
known defects, or unverified behavior are disclosed in the report.

- **Student Name:** [official name]
- **Signature:** [signature]
- **Date:** [date]
