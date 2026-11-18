# LabTrace Project Log

This log records the current workspace state and onboarding context. It is not
a claim that every route or feature has passed end-to-end testing. For setup,
the complete file tree, and implementation caveats, see [README.md](README.md).

## Workspace update - 2026-11-15

### Changes since the previous log entry

- Added a staff-only central operations dashboard at `/dashboard/central/`
  and a JSON endpoint at `/dashboard/central/data/`. Both allow instructors
  and admins only.
- The central dashboard summarizes active visits and occupancy by lab,
  equipment availability/current borrowers, equipment usage and condition
  summaries, and unresolved incidents (reported or under investigation).
  `dashboard/selectors.py` provides a full JSON snapshot that the local
  `static/js/live_refresh.js` refreshes every 15 seconds, including the active
  visits, occupancy, equipment, borrowers, and incident counts.
- Added a unified audit trail at `/dashboard/audit/` for check-in/out,
  equipment borrow/return, and incident status-history events. It supports
  user, lab, asset, incident-status, and date-range filters, combines filters,
  sorts newest first, and paginates results. Added `/dashboard/audit/api/` for
  paginated JSON results with the same filters and a page-size cap of 100.
  Event collection remains capped at 500 rows per source.
- Added `dashboard/central.py`, `dashboard/selectors.py`, `dashboard/audit.py`,
  `dashboard/access.py`, `dashboard/fieldmap.py`, and `dashboard/choices.py`,
  with routes in `dashboard/urls.py` and pages in
  `templates/dashboard/central.html` and `templates/dashboard/audit.html`.
  The dashboard now reports asset totals/status, borrowing activity, average
  loan time, most-borrowed assets, and pre-/post-condition summaries.
- Added indexes in `dashboard/migrations/0001_audit_indexes.py`, audit
  performance/pagination tests, and tests for authorized incident-evidence
  and equipment-condition image downloads.
- Added `dashboard/management/commands/seed_demo_data.py` to generate demo
  users, visits, assets, loans, and incidents. Its current tests fail because
  the command passes `institutional_id`, which is not a field on the current
  user model; it needs correction before treating the seed command as usable.
- Updated local setup dependencies to include Pillow and added ignore rules
  for uploaded media and generated file-based email output. The inventory
  template is now named `templates/equipment/inventory.html`, and the
  password-change route is present.

### Verification and remaining issues

- Latest verification: `python manage.py test dashboard --keepdb` ran 34
  tests; 26 passed, 2 failed, and 6 errored. The two failures are audit query
  performance assertions (query count varies by page size and a filtered query
  exceeds the configured budget). Errors are two audit tests whose helper's
  `user` argument conflicts with the user filter, one dashboard test whose
  second asset has a blank unique `asset_code`, and three seed-command tests
  that hit the unsupported `institutional_id` argument. Fix these before
  treating dashboard, audit performance, or seeding as fully verified.
- A normal `python manage.py test dashboard` attempt could not create the
  database because `test_postgres` already exists; `--keepdb` used that
  existing test database.
- `templates/base.html` still loads `https://cdn.tailwindcss.com`; the project
  is therefore not fully offline despite having bundled CSS.
- `labtrace/settings.py` still uses `DEBUG = True` and a hard-coded development
  `SECRET_KEY`. Do not deploy these settings as-is.
- The audit trail aggregates existing access, equipment, and incident
  history; it is not a separate immutable audit log. Each event source is
  limited to 500 records before the API/page pagination is applied.
- `docs/WBS_STATUS.md` predates these additions and should be refreshed: an
  audit API and performance tests now exist, although the performance
  assertions fail; a demo-data command also exists but currently fails.
- Authorized download views now exist for incident attachments and equipment
  condition images and return private/no-store responses. However,
  `templates/incidents/incident_detail.html` and `templates/equipment/return.html`
  still contain direct `file.url` links; switch these to the authorized routes
  so the UI does not bypass the new permission checks when media is served.

## Workspace update - 2026-11-14

### Changes and technical updates present in the workspace

- The project is split into six Django apps: `authentication`, `users`,
  `access_logging`, `equipment`, `incidents`, and `dashboard`. Account,
  dashboard, user, visit, equipment, and incident routes are included by
  `labtrace/urls.py`.
- The authentication user model now includes optional `contact_number` and
  `department` fields, represented by
  `authentication/migrations/0003_user_contact_number_user_department.py`.
- Database settings use PostgreSQL via `psycopg`, with connection values read
  from environment variables through `python-dotenv`; `sslmode=require` is
  configured. `db.sqlite3` exists locally but is ignored and is not the active
  backend.
- Shared page templates are in the root `templates/` directory, configured
  through Django's template `DIRS`. The base template loads local CSS and
  JavaScript.
- The settings configure local media storage and file-based email. Password
  reset messages are written to `sent_emails/`, not sent through an SMTP
  service.
- Role-specific dashboard endpoints/templates have been added. The admin
  dashboard currently reports user totals by role; the other dashboards are
  role-specific template pages.

### Current implementation status

| Component | Current state |
| --- | --- |
| `authentication` | Custom `AbstractUser` with `STUDENT`, `INSTRUCTOR`, `RESEARCHER`, and `ADMIN` roles; `@cit.edu` validation; registration, login by username/email, logout. |
| `users` | Self-service profile view/edit, admin user search/role/active controls, role-based access helpers, and file-based password-reset flow. Deactivation sets Django's `is_active=False`, preserving related records. |
| `access_logging` | Visit check-in, personal history, checkout, staff active-visit listing, occupancy counts, and AJAX refresh/checkout. A database constraint permits at most one active visit per user. |
| `equipment` | Asset inventory, borrowing/returning, condition records and photo fields, staff asset create/edit. Loans link to visits; checkout is blocked while items remain unreturned. |
| `dashboard` | Role-specific pages, staff-only central dashboard with live equipment/condition metrics, searchable cross-module audit UI/API, audit indexes, and demo-data command. The latest dashboard test run has 2 failures and 6 errors; see the verification notes above. |
| `incidents` | Incident reporting, status lifecycle, history, and staff audit views are routed and tested. |

### Important current limitations

- The base template includes locally bundled CSS and JavaScript, but still
  loads Tailwind from `https://cdn.tailwindcss.com`; offline operation is not
  yet complete.
- PostgreSQL must be configured and reachable. The `db.sqlite3` file does not
  indicate a SQLite fallback in settings.
- Equipment inventory now uses the matching `equipment/inventory.html`
  template, and a password-change route is configured to render
  `users/password_change.html`.
- `Pillow` is declared in `requirements.txt` for equipment image fields.
- Settings currently enable `DEBUG` and contain a development placeholder
  `SECRET_KEY`. Do not deploy these settings as-is.
- Other app tests have been expanded, but only the dashboard test run was
  repeated for the 2026-11-15 update. The centralized dashboard and unified
  audit-trail code now exist; the latest dashboard test run is not fully
  passing.
- A `seed_demo_data` management command exists, but currently errors because
  it supplies an unsupported `institutional_id` user field. No pre-seeded
  accounts should be assumed until that command is repaired and verified.

## Onboarding context for a new developer or AI

1. **Start with the configured project, not the database artifact.** Django
   loads `labtrace.settings`; the database engine is PostgreSQL. Read
   `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT` in local
   environment configuration. `DB_NAME` and `DB_PORT` have defaults, and
   PostgreSQL SSL mode is required. Do not read, expose, or commit `.env`
   credentials.
2. **Preserve the custom user model.** `AUTH_USER_MODEL` is
   `authentication.User`; use `get_user_model()` or `settings.AUTH_USER_MODEL`
   for new model relations. Registration assigns the student role and email
   validation is controlled by `ALLOWED_EMAIL_DOMAINS`. Profile updates
   normalize email and set the username to that email.
3. **Use role checks consistently.** Global `users.middleware` requires login
   outside its exempt URL prefixes and applies path-prefix restrictions.
   `users.decorators.role_required` and `users.permissions.RoleRequiredMixin`
   are the existing per-view patterns. Keep role policy consistent between
   middleware, decorators/mixins, templates, and tests.
4. **Preserve operational history.** A `LabVisit` is owned by a user, and
   `EquipmentLog` links a loan to a visit. Both use `PROTECT` for historical
   relations; user deactivation is a soft-delete. Existing conditional
   uniqueness constraints enforce one active visit per user and one open loan
   per asset.
5. **Keep offline behavior honest.** Email is file-based and static assets
   are bundled, but a CDN is still referenced. Uploaded files use local media
   storage; verify local directory permissions and image dependencies.
6. **Keep docs and routing in sync.** The README contains the workspace tree,
   setup requirements, and known gaps. Do not assume a scaffold is a completed
   feature; inspect app URLs, views, templates, migrations, and tests before
   extending it.

## Setup and verification notes

- Install Python dependencies from `requirements.txt`, configure PostgreSQL
  environment variables, then run `python manage.py migrate` and
  `python manage.py runserver`.
- The package's `npm test` command is only a placeholder; Django tests are
  invoked with `python manage.py test` and require a configured test database.
- Review generated migrations and apply them to the intended PostgreSQL
  database. Do not treat the ignored SQLite file as migration/test state.
