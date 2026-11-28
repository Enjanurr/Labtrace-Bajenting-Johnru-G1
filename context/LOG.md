# LabTrace Context Handoff Log

## Current workspace snapshot — 2026-11-27

This handoff is a navigation aid, not a release log or a claim that tests pass.
Use [README.md](README.md) as the context index and the four focused references
for implementation details.

### Current implementation highlights

- Six Django apps are mounted from `labtrace/urls.py`: authentication, users,
  access logging, equipment, incidents, and dashboard.
- PostgreSQL is the configured database. Credentials are environment-based;
  email is file-based. Current settings still use `DEBUG=True` and a
  development `SECRET_KEY`.
- Users have Student, Instructor, Researcher, and Admin roles. Registration
  assigns Student; role home redirects and server-side restrictions exist.
- Room-aware check-in and equipment scoping, sequential room-prefixed asset
  codes, condition checks, incident reporting/status history, staff dashboard,
  and audit UI/API are implemented in source.
- The logout view blocks sign-out when a user has an active visit or
  unreturned loan.
- Audit aggregation is limited to 500 records per source before merged
  in-memory sorting/pagination. Performance needs fresh verification.
- Audit search/filter is available to both Admin and Instructor roles: user,
  lab, asset name, incident status, and date range. Asset code is not searched
  by the current backend despite the UI placeholder. Performance needs fresh
  verification.
- Image/file uploads were intentionally removed: equipment image fields and
  incident attachments are removed by migrations; current models/forms have
  no upload fields and settings have no media configuration. Do not describe
  uploads as merely pending unless the approved WBS explicitly requires them.
- `templates/base.html` still requests Google Fonts and Tailwind CDN, so
  “fully offline” claims are not accurate.

### Documentation consolidation

- Added `project-overview.md`, `domain-and-workflows.md`,
  `api-routes-and-forms.md`, and `testing-and-ops.md`.
- Updated `FILETREE.md` and `improvements.md` to reflect current source.
- Kept `WBS_STATUS.md` as a historical 2026-11-17 audit and
  `pd3-hardening-context.md` as a report starter. Do not copy their test
  totals or issue statuses without rechecking.

### Historical verification note

`WBS_STATUS.md` records a 2026-11-17 test run of 64 tests (55 passed, 3 failed,
6 errored) and successful Django system/migration checks. Those results are
historical, not freshly rerun. In particular, its seed-command failure note
predates the current `authentication.User.institutional_id` field.

### Source of truth

Prefer current models, forms, views, URLconfs, settings, templates, migrations,
and tests. Update the canonical context references when behavior changes.
Do not treat the root README or older dated notes as authoritative where they
conflict with current source.
