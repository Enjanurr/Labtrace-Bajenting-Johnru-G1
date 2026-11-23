# LabTrace Workspace Map

The complete current file tree and setup instructions live in
[README.md](README.md). This companion map is intentionally concise; it was
updated with the README on 2026-11-14.

## Project layout

- `labtrace/` - Django settings, root URL configuration, ASGI and WSGI entry
  points.
- `authentication/` - custom `authentication.User`, role choices, institutional
  email validation, registration, login and logout.
- `users/` - profile management, administrator user controls, role access
  helpers, and password reset.
- `access_logging/` - lab visit model, check-in/check-out, visit history, and
  active occupancy views.
- `equipment/` - assets, visit-linked equipment loans, and condition records
  recording.
- `incidents/` - current scaffold only; no incident URLs or workflow yet.
- `dashboard/` - role-specific landing pages and limited admin user counts.
- `templates/` - shared templates, including account, dashboard, equipment,
  registration, and profile pages.
- `static/` and `tailwind/` - local CSS/JavaScript assets and Tailwind source.
- `sent_emails/` - local file-email output for password-reset messages.

## Onboarding cautions

- PostgreSQL is the configured backend. The ignored `db.sqlite3` is not used by
  the current settings.
- `.env` and `db.sqlite3` are ignored local files; never publish credentials or
  database contents.
- The application has a remaining Tailwind CDN reference, and the equipment
  inventory template currently has an `.htm`/`.html` name mismatch. See the
  README and [LOG.md](LOG.md) for precise details and other known limitations.
