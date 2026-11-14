# LabTrace Project Log

This log records the current workspace state and onboarding context. It is not
a claim that every route or feature has passed end-to-end testing. For setup,
the complete file tree, and implementation caveats, see [README.md](README.md).

## Workspace update - 2026-11-14

### Changes and technical updates present in the workspace

- The project is split into six Django apps: `authentication`, `users`,
  `access_logging`, `equipment`, `incidents`, and `dashboard`. Account,
  dashboard, user, visit, and equipment routes are included by
  `labtrace/urls.py`; incident routes are not yet connected.
- The authentication user model now includes optional `contact_number` and
  `department` fields, represented by
  `authentication/migrations/0003_user_contact_number_user_department.py`.
- Database settings use PostgreSQL via `psycopg`, with connection values read
  from environment variables through `python-dotenv`; `sslmode=require` is
  configured. `db.sqlite3` exists locally but is ignored and is not the active
  backend.
- Shared page templates are in the root `templates/` directory, configured
  through Django's template `DIRS`; `access_logging` and `users` also have
  app-local templates. The base template loads local CSS and JavaScript.
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
| `dashboard` | Role-specific home pages and admin user counts; no unified analytics implementation is present. |
| `incidents` | Package scaffold with placeholder model/view/test modules; no URL module or incident workflow is present, and root routing is commented out. |

### Important current limitations

- The project is not yet fully offline: `templates/base.html` loads
  `https://cdn.tailwindcss.com` even though local CSS and jQuery files exist.
- PostgreSQL must be configured and reachable. The `db.sqlite3` file does not
  indicate a SQLite fallback in settings.
- The equipment inventory view renders `equipment/inventory.html`, but the
  current shared template is named `templates/equipment/inventory.htm`. That
  mismatch must be resolved for the inventory page to render.
- `equipment` uses Django `ImageField` models, but `Pillow` is not listed in
  `requirements.txt`. Add/verify that dependency before relying on image
  uploads. `media/` is configured but does not currently exist in the tree.
- Settings currently enable `DEBUG` and contain a development placeholder
  `SECRET_KEY`. Do not deploy these settings as-is.
- Test modules exist, but most are placeholders. `users/tests.py` contains a
  small number of routing checks; this does not demonstrate end-to-end
  coverage of the application.
- There is no `seed_data` management command or documented/pre-seeded demo
  account set in the current workspace.

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
