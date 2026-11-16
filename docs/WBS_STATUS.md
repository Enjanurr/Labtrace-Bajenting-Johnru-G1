# LabTrace WBS Audit Status

## 1. Summary

- **DONE:** 12 of 15 WBS items (**80% of items**)
- **PARTIAL:** 3 of 15 WBS items (**20% of items**)
- **NOT DONE:** 0
- **UNVERIFIED:** 0
- **Weighted WBS completion estimate:** 90% (DONE = 100%, PARTIAL = 50%, NOT DONE/UNVERIFIED = 0%)

This report reflects the current working tree as of 2026-11-15. The central
dashboard and cross-module audit trail are now implemented, but remain PARTIAL:
the dashboard's live JSON refresh does not cover all displayed data, and the
audit trail lacks a retrieval API and performance test. The latest dashboard
test run had 13 passing tests and 3 errors. The 80% figure is WBS feature
fully-complete-item share; the weighted completion estimate is 90%. Neither
figure represents production readiness.

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
| 1.3.3 | Centralized Laboratory Dashboard | PARTIAL | `dashboard/central.py` (`central_dashboard`, `central_data`); `dashboard/selectors.py` (`active_visit_rows`, `occupancy`, `asset_summary`, `current_borrowers`, `incident_summary`); `templates/dashboard/central.html`; `dashboard/tests.py` | Staff dashboard aggregates active visits, occupancy, asset statuses/current borrowers, and unresolved incidents. JSON refresh covers occupancy and unresolved count, not the full dashboard/equipment data. A dashboard test covering asset setup errors because its fixture creates assets with a blank unique `asset_code`. |
| 1.4.1 | Borrow Equipment | DONE | `equipment/urls.py` (`borrow`); `equipment/views.py` (`borrow_view`); `equipment/forms.py` (`BorrowForm`); `equipment/models.py` (`EquipmentLog`) | Borrow flow is implemented and linked to the active visit. |
| 1.4.2 | Pre/Post Condition Check | PARTIAL | `equipment/models.py` (`Condition`, image fields); `equipment/forms.py` (`BorrowForm`, `ReturnForm`); `equipment/views.py` (`return_view`); `templates/equipment/borrow.html`; `templates/equipment/return.html` | Condition and evidence collection are present, but file validation is shallow and there are no real equipment tests. |
| 1.4.3 | Return Equipment | DONE | `equipment/urls.py` (`return`); `equipment/views.py` (`return_view`); `equipment/models.py` (`EquipmentLog`); `templates/equipment/return.html` | Return handling updates asset availability and logs the post-condition. |
| 1.5.1 | Report Incident | DONE | `incidents/urls.py` (`new`, `list`, `detail`, `status`); `incidents/views.py` (`incident_create`, `incident_list`, `incident_detail`); `incidents/forms.py` (`IncidentForm`); `incidents/models.py` (`Incident`, `IncidentAttachment`) | Reporting is implemented, routed, and backed by real tests. |
| 1.5.2 | Incident Status Engine | DONE | `incidents/services.py` (`TRANSITIONS`, `allowed_next_statuses`, `change_status`); `incidents/views.py` (`incident_status`); `incidents/tests.py` | Status transitions, admin enforcement, and lifecycle tests are implemented. |
| 1.5.3 | Searchable Audit Trail | PARTIAL | `dashboard/central.py` (`audit_trail`); `dashboard/audit.py` (`parse_filters`, `build_events`); `templates/dashboard/audit.html`; `dashboard/tests.py` | Unified paginated UI combines access, equipment, and incident status-history events and supports user, lab, asset, incident-status, and date-range filters. No separate retrieval API or performance test exists; queries cap each event source at 500 rows. Two user-filter tests currently error because a test helper argument named `user` collides with the filter parameter. |

## 3. Cross-cutting findings

### Offline compliance — FAIL
- `templates/base.html` still loads `https://cdn.tailwindcss.com` at line 11. Local CSS and JavaScript are present, but the CDN remains an active external dependency.
- `static/css/tailwind.css` contains a Tailwind project URL in its generated license comment; that string is not itself a browser request.

### Database — PASS
- `labtrace/settings.py` configures PostgreSQL only (`django.db.backends.postgresql`) and reads DB settings from `.env` using `python-dotenv`.
- There is no SQLite fallback in the app settings.
- `.env` is ignored by Git in `.gitignore`.

### Requirements — PASS
- `requirements.txt` declares Pillow for the `ImageField` fields in `equipment/models.py`.

### Template/route integrity — PASS
- Login, profile, access-logging, and equipment views resolve their templates from the shared `templates/` directory, including `equipment/inventory.html`.
- `users:password_change` is routed to the existing password-change template and linked from the profile page.

### Security — FAIL
- `labtrace/settings.py` sets `DEBUG = True` and uses a hard-coded development `SECRET_KEY`.
- `ALLOWED_HOSTS` is limited to localhost-only settings, which is acceptable for local development but not production.
- File upload validation is limited to type/size checks in various forms; it does not inspect actual file content.
- Media files are exposed during debug mode through the default static/media route; private evidence should be served through an authorization-aware download endpoint.

### Tests — PARTIAL
| `tests.py` | Meaningful cases | Audit result |
|---|---:|---|
| `authentication/tests.py` | 2 | Login by email and inactive-user rejection |
| `users/tests.py` | 6 | Routing, profile update, template resolution, and password change |
| `access_logging/tests.py` | 5 | Check-in, checkout, template resolution, and staff access control |
| `equipment/tests.py` | 4 | Template resolution, borrowing/returning, and active-visit requirement |
| `dashboard/tests.py` | 16 | Current targeted run: 13 passed and 3 errored |
| `incidents/tests.py` | 13 | Real status, access, and lifecycle coverage |

The dashboard tests exercise staff access, occupancy, API counts, incident
aggregation, audit event types and filters. Three test errors remain: two
audit user-filter cases hit a helper argument collision, and the equipment
summary case creates two assets with an empty value for a unique asset code.
The complete suite was not rerun as part of this update.

### Seed/demo data — FAIL
- No management command or fixture was found to seed campuses, equipment, users, or incidents.

### Git hygiene — FAIL
- `sent_emails/*.log` files are tracked by Git and may contain generated reset email output.
- `.gitignore` now includes `.env`, `db.sqlite3`, `venv/`, `.venv/`,
  `__pycache__/`, `media/`, and `sent_emails/`. The ignore rule does not
  untrack the existing email logs; review and remove those tracked generated
  files from version control as appropriate.

## 4. README/LOG contradictions

- `README.md:259` says templates do not load Tailwind from a CDN, but
  `templates/base.html:11` still loads `https://cdn.tailwindcss.com`.
- `README.md` and `LOG.md` describe the central dashboard and audit trail as
  implemented; current code supports that, but both remain PARTIAL against
  WBS requirements because the live JSON endpoint is incomplete and audit
  retrieval/performance testing is absent.

## 5. Bugs and risks found

### Critical
- None identified in the current working tree.

### High
- **Insecure deployment settings** — `labtrace/settings.py` still uses a hard-coded development secret and `DEBUG = True`.
- **Sensitive evidence access** — media is served in debug mode, without a dedicated authorization-aware download view.

### Medium
- **Production security settings** — `DEBUG = True` and a development `SECRET_KEY` remain in the source settings.
- **No seed data** — operations cannot be demoed or reproduced by a standard management command.

### Low
- **No strong file-content validation** — uploads are checked only superficially.

## 6. Recommended next steps

1. Fix the three dashboard test errors and rerun the full suite.
2. Remove the Tailwind CDN reference and reconcile README offline-compliance claims.
3. Extend the central dashboard JSON endpoint/refresh to cover all required live data, including equipment usage and condition.
4. Add a retrieval API and a performance test for the unified audit trail.
5. Move production security settings out of source and provide authorization-aware access to private evidence.
6. Remove generated email logs from Git tracking and add a reproducible demo-data seed command.

## 7. Commands run

| Command | Result |
|---|---|
| `python manage.py check` | Passed: no system-check issues. |
| `python manage.py makemigrations --check --dry-run` | Passed: no model changes detected. |
| `python manage.py test dashboard.tests` | Could not create the test database because `test_postgres` already exists. |
| `python manage.py test dashboard.tests --keepdb` | 16 tests run; 13 passed and 3 errored (two audit test-helper collisions and one missing unique asset-code fixture value). |
