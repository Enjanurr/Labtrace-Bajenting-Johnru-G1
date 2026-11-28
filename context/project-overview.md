# LabTrace Project Overview

**Workspace source review:** 2026-11-27. This is a source-grounded reference,
not a claim that the current test suite passes or that the app is production
ready.

## Purpose and architecture

LabTrace is a Django application for institutional user accounts, laboratory
room visits, equipment inventory/loans, incidents, and staff operations.
The project is split into six Django apps. Root URL configuration is in
`labtrace/urls.py`; shared Django templates live in the root `templates/`
directory, configured by `TEMPLATES[0]["DIRS"]`.

Request path at a glance:

1. Django project settings and middleware are loaded from `labtrace/settings.py`.
2. `labtrace/urls.py` mounts each app URLconf.
3. App views validate requests with forms, permission helpers, and model logic.
4. Views render shared templates or return JSON for AJAX/dashboard clients.
5. Django ORM persistence uses PostgreSQL; password-reset email output is
   written to local files.

## App boundaries

| App | Responsibility | Main source |
|---|---|---|
| `authentication` | Custom user model, institutional email validation, registration, login, guarded logout | `models.py`, `forms.py`, `views.py`, `urls.py` |
| `users` | Self-profile, administrator user controls, role/access helpers, password change/reset | `views.py`, `forms.py`, `middleware.py`, `permissions.py`, `urls.py` |
| `access_logging` | Room-aware check-in, checkout, personal visit history, staff active-visit board | `models.py`, `forms.py`, `views.py`, `room_picker.py`, `urls.py` |
| `equipment` | Rooms, assets, condition values, visit-linked loans, room scope, room/asset administration | `models.py`, `forms.py`, `views.py`, `room_views.py`, `room_scope.py`, `urls.py` |
| `incidents` | Incident reporting, owner/staff visibility, status changes, status history | `models.py`, `forms.py`, `services.py`, `views.py`, `urls.py` |
| `dashboard` | Role-specific home pages, staff operations snapshot, audit UI/API, demo-data command | `views.py`, `central.py`, `selectors.py`, `audit.py`, `urls.py` |

There are no app-specific model declarations in `users/models.py` or
`dashboard/models.py` in the current workspace; those apps use models from the
other modules.

## Stack and dependencies

- Python/Django: `requirements.txt` specifies Django `>=5.2,<6.0`.
- Database driver: `psycopg[binary]`; environment loading: `python-dotenv`.
- UI: Django templates, locally stored jQuery (`static/js/jquery.min.js`),
  generated Tailwind CSS (`static/css/tailwind.css`), and Tailwind CSS 3.4.17
  development dependency in `package.json`.
- JavaScript: `static/js/main.js` handles AJAX/check-out and common form UI;
  `static/js/live_refresh.js` updates the central dashboard.
- The project manifest's `npm test` script is a placeholder that exits with
  an error. Django tests use `python manage.py test`.
- No Pillow dependency is present in `requirements.txt`; image/file uploads
  were intentionally removed from the active equipment and incident flows.
  See the removal migrations listed in
  [api-routes-and-forms.md](api-routes-and-forms.md).

## Configuration and local operation

- `AUTH_USER_MODEL = "authentication.User"`.
- PostgreSQL is the only configured Django database backend. Values are read
  from `.env` using `load_dotenv`: `DB_NAME` (default `postgres`), `DB_USER`,
  `DB_PASSWORD`, `DB_HOST`, and `DB_PORT` (default `5432`). `sslmode=require`
  is configured. A local `db.sqlite3` file is not selected by settings.
- Institutional email domains come from `ALLOWED_EMAIL_DOMAINS`, currently
  `["cit.edu"]`.
- `TIME_ZONE` is `Asia/Manila`, with timezone-aware datetimes enabled.
- Email uses Django's file-based backend at `sent_emails/`; it does not send
  via SMTP in this configuration.
- Static files are served from `static/` in development. There is no
  `MEDIA_ROOT` or `MEDIA_URL` in the current settings.
- Tailwind CSS build script: `npm run build:css`; watch script:
  `npm run watch:css`.

## Security and deployment caveats

- Current settings set `DEBUG = True`, use a hard-coded development
  `SECRET_KEY`, and limit `ALLOWED_HOSTS` to localhost. Do not expose this
  configuration as production settings.
- `CsrfViewMiddleware` is enabled. Verify individual forms/mutating endpoints
  and deployment cookie/HTTPS settings before release.
- `RoleBasedAccessMiddleware` globally requires authentication except for its
  explicit exempt URL prefixes and applies a small set of path-prefix role
  rules. Many views also enforce roles/ownership directly; consult
  [domain-and-workflows.md](domain-and-workflows.md).
- The code includes locally generated CSS, but `templates/base.html` still
  requests Google Fonts and `https://cdn.tailwindcss.com`. The application is
  therefore not fully offline despite the local stylesheet and the contrary
  settings comment/README claim.
- Keep `.env`, local databases, generated email files, and test account
  credentials out of documentation and source control. `.gitignore` ignores
  `.env`, `db.sqlite3`, virtual environments, caches, `media/`, and
  `sent_emails/`.

## Working conventions

- For user relations in new models, use `settings.AUTH_USER_MODEL`; at runtime
  use `get_user_model()`.
- Preserve historical visit/loan/incident relationships and conditional
  uniqueness constraints; see
  [domain-and-workflows.md](domain-and-workflows.md).
- Use named URL patterns with Django's `reverse()` / `{% url %}` rather than
  hard-coding route paths in application links.
- No branch naming, review, or pull-request convention was verified in the
  inspected project files. Follow the course/team process and update the
  applicable report placeholder.

## Known source/documentation drift

- The root `README.md` tree and status descriptions are stale. It describes
  the dashboard as limited, says there is no CDN, and omits current room,
  audit, and template files.
- The root README's listed Python packages match `requirements.txt`, but it
  still describes equipment image uploads; these were intentionally removed
  and are absent from current models/forms.
- The root README's feature overview/tree is stale: it describes dashboards as
  limited and omits current room-aware check-in, central dashboard, audit, and
  template files.
- Older context notes also describe incidents as unrouted or the seed command
  as broken. Current `labtrace/urls.py` includes incidents, and the current
  user model has `institutional_id`; nevertheless, run the seed tests before
  treating the command as verified.
- See [testing-and-ops.md](testing-and-ops.md) for historical test results
  and current verification limits.
