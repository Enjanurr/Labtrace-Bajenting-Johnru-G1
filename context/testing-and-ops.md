# LabTrace Testing and Operations

This is the operational reference as of source inspection on 2026-11-27.
No tests or database commands were run for this documentation reorganization.

## Test map

| Module | Main areas represented in tests |
|---|---|
| `authentication/tests.py` | Login by email, inactive-user rejection, logout guard |
| `users/tests.py` | Reset routing, user management route names, profile rendering/update, password change |
| `access_logging/tests.py` | Check-in, active visit uniqueness behavior, checkout, staff active visits |
| `access_logging/tests_room_checkin.py` | Active-room picker, room/building data, valid/inactive/missing room cases, active visit room filter |
| `equipment/tests.py` | Borrow/return, active visit requirement, conditions, defective assets, room scope and asset codes |
| `incidents/tests.py` | Incident ownership, staff access, submission, status updates/history/lifecycle |
| `dashboard/tests.py` | Staff dashboard access/data and audit filters |
| `dashboard/tests_performance.py` | Audit pagination, query counts, response time, index checks |
| `dashboard/tests_seed.py` | Demo seed command repeat/reset/data behavior |

These module descriptions summarize test code and names, not fresh passing
results.

## Commands

Run from the repository root with the project's configured Python environment
and a reachable PostgreSQL instance/test database:

```powershell
python -m pip install -r requirements.txt
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py test
```

For iterative focused tests, use Django labels, for example:

```powershell
python manage.py test equipment
python manage.py test access_logging
python manage.py test incidents
python manage.py test dashboard.tests_performance
```

Reuse a local test DB only when safe and intentional:

```powershell
python manage.py test --keepdb
```

Tailwind:

```powershell
npm install
npm run build:css
npm run watch:css
```

`npm test` is a placeholder script and intentionally exits with an error; it
does not run Django tests.

## Configuration and local operation

1. Create a virtual environment. The root README recommends Python 3.11+;
   `requirements.txt` does not itself pin a Python version.
2. Install `requirements.txt`.
3. Set `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT` in a local
   ignored `.env`. Settings default database name to `postgres`, port to
   `5432`, and use `sslmode=require`.
4. Apply migrations with `python manage.py migrate`.
5. Run `python manage.py runserver`.

Never copy actual `.env` values, reset email contents, or test credentials into
context files. PostgreSQL is the only configured backend; do not assume the
local `db.sqlite3` artifact is active.

The `seed_demo_data` management command exists at
`dashboard/management/commands/seed_demo_data.py`. It supports `--reset`,
`--password`, and `--force`; it refuses to run with `DEBUG` disabled unless
`--force` is provided. It prints demo credentials to command output, so use
only in an isolated non-production database and do not paste that output into
shared documentation. Its tests exist, but the command/test result has not
been freshly verified in this documentation task.

## Known verification snapshot

`context/WBS_STATUS.md` records an older full-suite run dated 2026-11-17:
64 tests, 55 passed, 3 failed, and 6 errored. The report lists audit
performance/filter, dashboard fixture, reset-heading, and seed-command issues.
Treat these as historical observations only. The current source has since
changed (including the custom user's `institutional_id` field); rerun the suite
before reporting present failures or success.

The WBS document also reports successful `manage.py check` and
`makemigrations --check --dry-run` on that historical snapshot. These commands
were not rerun here.

## Deployment and operational risks

- Do not deploy current settings unchanged: `DEBUG=True`, a hard-coded
  development `SECRET_KEY`, and localhost-only `ALLOWED_HOSTS` are configured.
- The current templates request `https://fonts.googleapis.com`,
  `https://fonts.gstatic.com`, and `https://cdn.tailwindcss.com`. The project
  is not fully offline; remove/replace these requests or qualify offline
  claims.
- Email reset output is file-based under `sent_emails/`; provision and protect
  that directory if used.
- No media storage settings or evidence-upload fields are present in the
  current models/forms inspected. This is intentional: migrations remove the
  equipment condition image fields and incident attachment model. Do not
  assume upload/download behavior is implemented or restore it unless the
  approved WBS/PD3 scope requires it.
- The audit UI/API are available to both Instructor and Admin roles. Filters
  include user name/email, lab, asset name, incident status, and date range;
  pagination is supported. Asset-code searching is not implemented in the
  current filter logic, and each event source is capped at 500 records before
  merged pagination.
- Audit event builders cap each underlying source at 500 rows before merged
  in-memory sorting and pagination. Older matching events can be omitted.
- `.gitignore` currently ignores `.env`, `db.sqlite3`, `venv/`, `.venv/`,
  Python caches/bytecode, `media/`, and `sent_emails/`. Ignore rules do not
  remove files that were already tracked; check Git tracking separately when
  doing repository hygiene work.

## Branch / pull request process

No authoritative branch naming, commit, or PR workflow was established from
the inspected source/context. Follow the instructor/team process. Record
actual branch and PR details in the PD3 report; do not infer them from
`context/improvements.md`.
