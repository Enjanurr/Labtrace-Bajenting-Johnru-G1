# LabTrace WBS Audit Status

## 1. Summary

- **DONE:** 13 of 15 WBS items (**86.7% fully completed**)
- **PARTIAL:** 2 of 15 WBS items (**13.3% partial**)
- **NOT DONE:** 0
- **UNVERIFIED:** 0
- **Weighted WBS completion estimate:** 93.3% (DONE = 100%, PARTIAL = 50%, NOT DONE/UNVERIFIED = 0%)

This report reflects the current working tree as of 2026-11-17. Phase estimates
use equal weighting within each phase; overall weighted completion counts each
DONE item as 100% and each PARTIAL item as 50%. The full test run found 64 tests:
55 passed, 3 failed, and 6 errored. The completion estimate describes WBS
implementation, not production readiness.

| Phase | WBS items | DONE / PARTIAL | Weighted completion |
|---|---:|---:|---:|
| 1.1 Authentication | 3 | 3 / 0 | 100% |
| 1.2 User Management | 3 | 3 / 0 | 100% |
| 1.3 Access & Visit Logging | 3 | 3 / 0 | 100% |
| 1.4 Equipment Management | 3 | 2 / 1 | 83.3% |
| 1.5 Incident & Accountability Tracking | 3 | 2 / 1 | 83.3% |

## 2. WBS status table

| WBS code | Work package | Status | Evidence (file:name) | Missing / notes |
|---|---|---|---|---|
| 1.1.1 | Login | DONE | `authentication/urls.py` (`login`); `authentication/views.py` (`LabTraceLoginView`); `authentication/forms.py` (`LoginForm`); `templates/registration/login.html`; `authentication/tests.py` (`LoginBehaviorTests`) | Login by email/session creation and inactive-user rejection have behavioral tests. Invalid-credential messaging does not have a dedicated test. |
| 1.1.2 | Register | DONE | `authentication/urls.py` (`register`); `authentication/views.py` (`register_view`); `authentication/forms.py` (`RegistrationForm`); `authentication/models.py` (`validate_institutional_email`); `templates/authentication/register.html` | Registration is routed, validates institutional email, enforces unique credentials, and stores hashed passwords via Django auth. No registration behavior test was found. |
| 1.1.3 | Change/Reset Password | DONE | `users/urls.py` (`password_reset`, `password_reset_done`, `password_reset_confirm`, `password_reset_complete`); `users/templates/users/password_reset_form.html`; `users/templates/users/password_reset_email.txt`; `users/tests.py` (`PasswordResetRoutingTests`) | Reset routes, templates, and file-based email are present; tests cover reset-page routing but not a full email/token/deep-link/new-password reset cycle. The password-change flow has a behavior test. |
| 1.2.1 | Update Profile | DONE | `users/views.py` (`ProfileDetailView`, `ProfileUpdateView`); `users/forms.py` (`ProfileForm`); `templates/users/profile.html`; `templates/users/profile_edit.html` | Users can view and update their own profile; ownership is enforced by `get_object()`. |
| 1.2.2 | User Management & RBAC | DONE | `authentication/models.py` (`User.Role`); `users/middleware.py` (`RoleBasedAccessMiddleware`); `users/permissions.py` (`RoleRequiredMixin`); `dashboard/views.py` (`AdminDashboardView`, `InstructorDashboardView`, `ResearcherDashboardView`, `StudentDashboardView`) | Role-specific dashboards and server-side access checks are implemented. |
| 1.2.3 | Deactivate Account | DONE | `users/urls.py` (`manage_toggle`); `users/views.py` (`toggle_active_view`); `templates/users/user_list.html`; `authentication/forms.py` (`LoginForm` inactive-account error); `authentication/tests.py` (`test_inactive_user_cannot_log_in`) | Admin UI toggles `is_active` as a soft deactivation, and inactive-user login is rejected. The admin toggle action itself does not have a dedicated behavior test. |
| 1.3.1 | Digital Check-In | DONE | `access_logging/urls.py` (`check_in`); `access_logging/views.py` (`check_in_view`); `access_logging/forms.py` (`CheckInForm`); `access_logging/models.py` (`LabVisit`); `templates/access_logging/check_in.html` | Check-in is implemented, routed, and has a working view/template. |
| 1.3.2 | Digital Check-Out | DONE | `access_logging/urls.py` (`check_out`); `access_logging/views.py` (`check_out_view`); `access_logging/models.py` (`LabVisit.check_out`); `templates/access_logging/my_visits.html` | Checkout updates duration and prevents checkout while equipment is still borrowed. |
| 1.3.3 | Centralized Laboratory Dashboard | DONE | `dashboard/central.py` (`central_dashboard`, `central_data`); `dashboard/selectors.py` (`live_snapshot`, `equipment_metrics`, `occupancy`, `incident_summary`); `templates/dashboard/central.html`; `static/js/live_refresh.js` | Staff dashboard aggregates active visits, occupancy, equipment availability, current borrowers, usage/condition metrics, and unresolved incidents. JSON refresh updates the displayed metrics. One dashboard test errors because its fixture creates an asset with a blank unique `asset_code`; feature code is routed and implemented. |
| 1.4.1 | Borrow Equipment | DONE | `equipment/urls.py` (`borrow`); `equipment/views.py` (`borrow_view`); `equipment/forms.py` (`BorrowForm`); `equipment/models.py` (`EquipmentLog`) | Borrow flow is implemented and linked to the active visit. |
| 1.4.2 | Pre/Post Condition Check | PARTIAL | `equipment/models.py` (`Condition`); `equipment/forms.py` (`BorrowForm`, `ReturnForm`); `equipment/views.py` (`return_view`); `templates/equipment/borrow.html`; `templates/equipment/return.html` | Condition recording is present; no photo/evidence upload workflow remains. |
| 1.4.3 | Return Equipment | DONE | `equipment/urls.py` (`return`); `equipment/views.py` (`return_view`); `equipment/models.py` (`EquipmentLog`); `templates/equipment/return.html` | Return handling updates asset availability and logs the post-condition. |
| 1.5.1 | Report Incident | DONE | `incidents/urls.py` (`new`, `list`, `detail`, `status`); `incidents/views.py` (`incident_create`, `incident_list`, `incident_detail`); `incidents/forms.py` (`IncidentForm`); `incidents/models.py` (`Incident`) | Reporting is implemented, routed, and backed by real tests without file attachments. |
| 1.5.2 | Incident Status Engine | DONE | `incidents/services.py` (`TRANSITIONS`, `allowed_next_statuses`, `change_status`); `incidents/views.py` (`incident_status`); `incidents/tests.py` | Status transitions, admin enforcement, and lifecycle tests are implemented. |
| 1.5.3 | Searchable Audit Trail | PARTIAL | `dashboard/central.py` (`audit_trail`, `audit_api`); `dashboard/audit.py` (`parse_filters`, `build_events`, `serialize_event`); `templates/dashboard/audit.html`; `dashboard/tests_performance.py` | Filtered UI and JSON API cover access, equipment, and incident-history events with pagination. Remains partial because query-count/performance assertions fail and event collection is capped at 500 rows per source before pagination. Two filter tests also error due to a test-helper argument collision. |

## 3. Cross-cutting findings

### Offline compliance — FAIL
- `templates/base.html` loads Tailwind from `https://cdn.tailwindcss.com` and Google Fonts from `fonts.googleapis.com` / `fonts.gstatic.com`. These are active external requests despite the bundled CSS and JavaScript.
- `static/css/tailwind.css` contains a Tailwind project URL in its generated license comment; that string is not itself a browser request.

### Database — PASS
- `labtrace/settings.py` configures PostgreSQL only (`django.db.backends.postgresql`) and reads DB settings from `.env` using `python-dotenv`.
- There is no SQLite fallback in the app settings.
- `.env` is ignored by Git in `.gitignore`.

### Requirements — PASS

### Template/route integrity — PASS
- Login, profile, access-logging, and equipment views resolve their templates from the shared `templates/` directory, including `equipment/inventory.html`.
- `users:password_change` is routed to the existing password-change template and linked from the profile page. The reset page renders, though a test still expects its previous heading text.

### Security — FAIL
- `labtrace/settings.py` sets `DEBUG = True` and uses a hard-coded development `SECRET_KEY`.
- `ALLOWED_HOSTS` is limited to localhost-only settings, which is acceptable for local development but not production.
- File upload validation is limited to type/size checks in various forms; it does not inspect actual file content.
- Authorization-aware download views exist, but `templates/incidents/incident_detail.html` and `templates/equipment/return.html` still link directly to `.url` media paths. With debug media serving enabled, these links bypass download-view permission checks.

### Tests — PARTIAL
| `tests.py` | Meaningful cases | Audit result |
|---|---:|---|
| `authentication/tests.py` | 2 | Login by email and inactive-user rejection |
| `users/tests.py` | 6 | Routing, profile update, template resolution, and password change; one stale reset-heading assertion fails |
| `access_logging/tests.py` | 5 | Check-in, checkout, template resolution, and staff access control |
| `equipment/tests.py` | 4 | Template resolution, borrowing/returning, and active-visit requirement |
| `dashboard/tests.py` | 16 | 13 passed; 3 errored (two filter-helper collisions and one asset fixture) |
| `dashboard/tests_downloads.py` | 7 | Authorized private download, response headers, missing file and invalid image path coverage |
| `dashboard/tests_performance.py` | 8 | Pagination/index checks; 2 query-performance assertions fail |
| `dashboard/tests_seed.py` | 3 | All 3 error because the seed command passes an unsupported user field |
| `incidents/tests.py` | 13 | Real status, access, and lifecycle coverage |

`python manage.py test --keepdb` discovered 64 tests: 55 passed, 3 failed, and
6 errored. The failures are one stale password-reset heading assertion and two
audit query-count/performance assertions. The errors are two audit filter
helper collisions, one asset fixture with an empty unique code, and three seed
command tests failing on unsupported `institutional_id`.

### Seed/demo data — FAIL
- `dashboard/management/commands/seed_demo_data.py` exists and defines demo users, assets, visits, loans, and incidents. It is not currently usable: it passes `institutional_id` to the custom user model, which has no such field; all three seed tests error.

### Git hygiene — FAIL
- `sent_emails/*.log` files are tracked by Git and may contain generated reset email output.
- `.gitignore` now includes `.env`, `db.sqlite3`, `venv/`, `.venv/`,
  `__pycache__/`, `media/`, and `sent_emails/`. The ignore rule does not
  untrack the existing email logs; review and remove those tracked generated
  files from version control as appropriate.

## 4. README/LOG contradictions

- `README.md` says there is no Tailwind CDN and describes the dashboard as role-specific pages/admin counts only; current `templates/base.html` still requests Tailwind and Google Fonts, and the central dashboard is now implemented.
- `README.md` says no demo-data command exists; a seed command is present, though currently broken by an unsupported user field.
- `README.md` and `docs/FILETREE.md` have stale trees/status: `docs/FILETREE.md` calls incidents a scaffold and omits the current central dashboard/audit API, private-download handlers, and added dashboard test/management-command files.
- `docs/LOG.md` describes current dashboard features, but its test totals and limitations predate the latest full run. Its warning about direct media links remains supported by current templates.

## 5. Bugs and risks found

### Critical
- None identified in the current working tree.

### High
- **Insecure deployment settings** — `labtrace/settings.py` still uses a hard-coded development secret and `DEBUG = True`.

### Medium
- **Broken seed command** — `dashboard/management/commands/seed_demo_data.py` uses a nonexistent `institutional_id` user field, so demo setup fails.
- **Audit performance** — two performance assertions fail, and source caps truncate event history before API pagination.

### Low
- **No strong file-content validation** — uploads are checked only superficially.

## 6. Recommended next steps

1. Replace direct media URLs in templates with the existing authorized download routes.
2. Remove Tailwind/Google Fonts external requests and correct the README's offline status.
3. Fix the dashboard filter/asset test fixtures, seed command, and stale reset-heading assertion; rerun the suite.
4. Optimize audit query counts and ensure API pagination covers all matching records rather than a fixed per-source slice.
5. Move production security settings out of source and remove generated email logs from Git tracking.
6. Refresh README, LOG, and FILETREE claims that no longer match the implemented dashboard, audit API, and seed command.

## 7. Commands run

| Command | Result |
|---|---|
| `python manage.py check` | Passed: no system-check issues. |
| `python manage.py makemigrations --check --dry-run` | Passed: no model changes detected. |
| `python manage.py test --keepdb` | 64 tests run; 55 passed, 3 failed, and 6 errored. Existing PostgreSQL test DB was reused. |
