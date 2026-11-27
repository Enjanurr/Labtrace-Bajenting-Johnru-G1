# LabTrace Workspace Map

For app architecture and environment details, see
[project-overview.md](project-overview.md). Route/form and workflow maps are in
[api-routes-and-forms.md](api-routes-and-forms.md) and
[domain-and-workflows.md](domain-and-workflows.md).

## Project and shared assets

```text
labtrace/
  settings.py, urls.py, asgi.py, wsgi.py
authentication/
  models.py, forms.py, views.py, urls.py, tests.py, migrations/
users/
  middleware.py, permissions.py, decorators.py
  forms.py, views.py, urls.py, tests.py, migrations/
access_logging/
  models.py, forms.py, views.py, room_picker.py, urls.py
  tests.py, tests_room_checkin.py, migrations/
equipment/
  models.py, forms.py, views.py, room_views.py, room_scope.py, filters.py
  urls.py, tests.py, templatetags/severity_tags.py, migrations/
incidents/
  models.py, forms.py, services.py, views.py, urls.py, tests.py, migrations/
dashboard/
  views.py, central.py, selectors.py, audit.py, access.py
  fieldmap.py, choices.py, urls.py, tests.py
  tests_performance.py, tests_seed.py, migrations/
  management/commands/seed_demo_data.py
templates/
  base.html, 403.html
  authentication/, registration/, users/, access_logging/
  equipment/, incidents/, dashboard/
static/
  css/tailwind.css
  js/jquery.min.js, main.js, live_refresh.js
  img/favicon.svg
tailwind/
  input.css
context/
  README.md, project-overview.md, domain-and-workflows.md
  api-routes-and-forms.md, testing-and-ops.md
  improvements.md, pd3-hardening-context.md, WBS_STATUS.md, LOG.md, FILETREE.md
```

## Important template groups

- `templates/authentication/`: registration page and shared field partial.
- `templates/registration/`: login and password-reset pages/partials.
- `templates/users/`: profile, user management, password change/reset.
- `templates/access_logging/`: check-in, personal history, staff active visits.
- `templates/equipment/`: inventory, loan, return, asset and room forms,
  severity badge partial.
- `templates/incidents/`: incident list/detail/form and status badge partial.
- `templates/dashboard/`: role dashboards, central dashboard, audit page.

## Notes

- This is a package-level map, not an exhaustive listing of migrations,
  generated files, or every template. Check the filesystem before relying on
  completeness.
- `incidents` is implemented and routed; do not describe it as a scaffold.
- The central dashboard/audit files and `equipment/templatetags/` are omitted
  from older README/file-tree snapshots but present in the current workspace.
- Context docs are indexed in [README.md](README.md).
