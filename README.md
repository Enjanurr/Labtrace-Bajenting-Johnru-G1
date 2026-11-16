
# Johnru I. Bajenting CSIT327-G1

# LabTrace

LabTrace is a Django application for laboratory user accounts, lab visits, and
equipment loans. The repository is organized as modular Django apps, with
shared project templates and locally stored static files.


## What is implemented

- **Authentication (`authentication`)** — custom `AbstractUser` model, role
  field, institutional email validation, registration, login, and logout.
- **User management (`users`)** — profile editing, administrator role changes
  and activation controls, role-based access helpers, and password reset.
- **Lab visits (`access_logging`)** — check-in, visit history, check-out, and a
  staff active-visits/occupancy view with an AJAX refresh and checkout action.
- **Equipment (`equipment`)** — inventory, borrowing and returning, condition
  recording, optional/required proof photos, and staff asset editing.
- **Dashboards (`dashboard`)** — role-specific landing pages; the admin page
  currently displays user counts.
- **Incidents (`incidents`)** — incident reporting, status transitions, history,
  and staff audit views are implemented and routed.

## Architecture and current file layout

This tree reflects the workspace files as inspected on 2026-11-14. It excludes
`.git`, Python cache files, dependency directories, and the generated contents
of `sent_emails/`. `.env` and `db.sqlite3` are present locally and ignored by
Git; do not commit local credentials or database data.

```text
lab/
├── .env                              # Local settings; not tracked
├── .gitignore
├── README.md
├── LOG.md                            # Status and AI/developer onboarding notes
├── FILETREE.md                       # Companion workspace map
├── manage.py                         # Django command entry point
├── db.sqlite3                        # Local artifact; not the configured backend
├── requirements.txt                  # Django, psycopg, python-dotenv
├── package.json                      # Tailwind CSS development dependency
├── package-lock.json
├── tailwind.config.js
├── tailwindcss.exe                   # Local Tailwind executable
├── sent_emails/                      # File-based password-reset output
├── labtrace/                         # Django project configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py                   # Apps, PostgreSQL, auth, email, static/media
│   ├── urls.py                       # Root routes and app includes
│   └── wsgi.py
├── authentication/                   # Custom user model and authentication
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   │   ├── __init__.py
│   │   ├── 0001_initial.py
│   │   ├── 0002_alter_user_options_alter_user_email_and_more.py
│   │   └── 0003_user_contact_number_user_department.py
│   └── templates/                     # Present, currently empty
├── users/                             # Profiles, role controls, password reset
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── decorators.py
│   ├── forms.py
│   ├── middleware.py
│   ├── models.py                      # No app-specific model yet
│   ├── permissions.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   │   └── __init__.py
│   └── templates/
│       └── users/
│           ├── deactivate.html
│           ├── password_change.html
│           ├── password_reset_complete.html
│           ├── password_reset_confirm.html
│           ├── password_reset_done.html
│           ├── password_reset_email.txt
│           ├── password_reset_form.html
│           ├── password_reset_subject.txt
│           ├── profile.html
│           └── user_list.html
├── access_logging/                    # Visit check-in/out and occupancy
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   └── templates/
│       └── access_logging/
│           ├── _active_rows.html
│           ├── active_visits.html
│           ├── check_in.html
│           └── my_visits.html
├── equipment/                         # Asset inventory and loan records
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   └── templates/                     # Present, currently empty
├── incidents/                         # Incident reporting and lifecycle
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── dashboard/                         # Role-specific dashboard views
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                      # No app-specific model yet
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   │   └── __init__.py
│   └── templates/                     # Present, currently empty
├── templates/                         # Shared/project-level Django templates
│   ├── 403.html
│   ├── base.html
│   ├── authentication/
│   │   ├── _field.html
│   │   └── register.html
│   ├── dashboard/
│   │   ├── admin.html
│   │   ├── instructor.html
│   │   ├── researcher.html
│   │   └── student.html
│   ├── equipment/
│   │   ├── asset_form.html
│   │   ├── borrow.html
│   │   ├── inventory.html
│   │   ├── my_equipment.html
│   │   └── return.html
│   ├── registration/
│   │   ├── _field.html
│   │   ├── login.html
│   │   ├── password_reset_complete.html
│   │   ├── password_reset_confirm.html
│   │   ├── password_reset_form.html
│   │   └── register.html
│   └── users/
│       ├── profile.html
│       └── profile_edit.html
├── static/                            # Locally stored static assets
│   ├── css/
│   │   └── tailwind.css
│   ├── js/
│   │   ├── jquery.min.js
│   │   └── main.js
│   └── src/                           # Present, currently empty
└── tailwind/
    └── input.css                      # Tailwind source stylesheet
```

### How the pieces fit together

- `labtrace/settings.py` installs the six project apps and selects
  `authentication.User` as `AUTH_USER_MODEL`. `labtrace/urls.py` mounts the
  admin, account, dashboard, user, visit, and equipment routes. Incident
  routing is currently commented out.
- `authentication.User` extends Django's `AbstractUser`. Roles are `STUDENT`,
  `INSTRUCTOR`, `RESEARCHER`, and `ADMIN`; new registrations are assigned the
  student role. `@cit.edu` is the configured allowed email domain. The profile
  form also sets the username to the saved email; login accepts username or
  email.
- `access_logging.LabVisit` records visits and permits at most one active visit
  per user. `equipment.EquipmentLog` links a loan to a visit and records
  pre-/post-return condition. An active visit cannot be checked out while it
  has unreturned equipment.
- The project-level `templates/` directory is configured in Django settings;
  apps may also provide templates under their own `templates/` directories.
- Password-reset emails use Django's file-based email backend and are written
  to `sent_emails/`. Uploaded equipment condition images are configured to use
  local `MEDIA_ROOT` (`media/`), which is not currently present in the tree.

## Requirements and local setup

Requirements are listed in `requirements.txt`: Django 5.2, `psycopg` 3,
`python-dotenv`, and Pillow. A PostgreSQL server that accepts SSL connections
is required by the current settings; the checked-in/local `db.sqlite3` is
**not** selected as the application database.

1. Use Python 3.11 or newer and create/activate a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   On macOS/Linux, activate with `source .venv/bin/activate`.

2. Install Python requirements:

   ```shell
   python -m pip install -r requirements.txt
   ```

3. Configure the PostgreSQL connection in the ignored local `.env` file:

   ```dotenv
   DB_NAME=your_database
   DB_USER=your_database_user
   DB_PASSWORD=your_database_password
   DB_HOST=your_database_host
   DB_PORT=5432
   ```

   `DB_NAME` and `DB_PORT` have settings defaults, but provide all connection
   values appropriate to your PostgreSQL instance. The connection is set to
   `sslmode=require`. Keep real credentials out of source control.

4. Apply migrations and start the development server:

   ```shell
   python manage.py migrate
   python manage.py runserver
   ```

   Open `http://127.0.0.1:8000/`. The project has no `seed_data` command or
   guaranteed demo accounts; create accounts through registration or Django
   admin as appropriate.

When changing models, create and review migrations with `python manage.py
makemigrations` before applying them. Tests cover login, profile changes,
visits, equipment borrowing/returning, and incident behavior. Run
`python manage.py test --keepdb` against a configured, reachable test database
before relying on a change.

## Offline and deployment caveats

- jQuery and a compiled Tailwind stylesheet are stored under `static/`.
  Templates use these local assets and do not load Tailwind from a CDN.
- Tailwind is compiled locally with the bundled v3.4.17 executable. After
  changing utility classes in templates or forms, run `npm run build:css`;
  Django serves the generated `static/css/tailwind.css`.
- The database is configured for PostgreSQL, which may be local but must be
  provisioned separately. File-based email and media storage are local.
- `DEBUG` is enabled and `SECRET_KEY` has a development placeholder in the
  current settings. Configure secure deployment settings before exposing the
  application.
- Equipment templates are in the shared template directory; the inventory
  view and template both use `equipment/inventory.html`.
- `requirements.txt` declares Pillow for the equipment `ImageField` models.
