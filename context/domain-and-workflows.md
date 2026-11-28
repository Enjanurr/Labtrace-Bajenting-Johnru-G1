# LabTrace Domain and Workflows

Source reviewed 2026-11-27. Statuses below describe current model/view logic;
test pass status is documented separately and should be refreshed before a
release.

## Roles and access policy

`authentication.User.Role` defines:

| Stored role | Display label | Main access |
|---|---|---|
| `STUDENT` | Student | Own profile, visits, equipment loans, and reported incidents |
| `INSTRUCTOR` | Instructor | Staff operations, active visits, incident management, asset management |
| `RESEARCHER` | Researcher | Own profile, visits, equipment loans, and reported incidents |
| `ADMIN` | Admin | Staff operations plus user and room administration |

Registration in `authentication.forms.RegistrationForm` always sets the role
to `STUDENT`; applicants cannot choose a role. Admins can update non-superuser
roles and activation through `users` management. Superusers are forced to the
`ADMIN` role by `User.save()`.

Access is enforced in more than one place:

- `users.middleware.RoleBasedAccessMiddleware` requires authentication outside
  exempt prefixes and restricts `/users/manage/` to Admin,
  `/visits/active/` to Instructor/Admin, and `/equipment/manage/` to
  Instructor/Admin.
- Role-specific dashboards use `RoleRequiredMixin`.
- Central dashboard/audit endpoints use `dashboard.access.staff_required`.
- Room management uses its local `admin_required` decorator.
- Incident visibility allows the reporter or staff (Instructor/Admin);
  non-staff incident lists are filtered to their own reports.
- Equipment return allows the loan owner or staff. Student/Researcher borrow
  inventory and submissions are scoped to the room of their active visit;
  Instructor/Admin are unrestricted by this room scope.
- Checkout allows the visit owner or staff and is POST-only.

Middleware path-prefix rules are not the only authorization boundary. When
adding endpoints, preserve view-level role/ownership checks and add tests for
direct URL access.

## Entity model

| Entity | Important fields/state | Relationships and integrity |
|---|---|---|
| `authentication.User` | Django `AbstractUser`; unique institutional `email`; `contact_number`, `department`, `institutional_id`, `role`, inherited `is_active` | User deletion is treated as soft deactivation for historical records; deactivated users cannot authenticate. |
| `equipment.Room` | Unique `name` and `code_prefix`; `lab_type`, `building`, `capacity`, `is_active`, `last_asset_number` | Related to assets and visits. Prefix derives from name if omitted. |
| `equipment.Asset` | Unique `asset_code`, `name`, `availability_status` | Optional `Room` FK with `PROTECT`; new room-linked assets receive sequential room-prefixed codes when created without a code. Direct model creation without a room uses an `EQ-NNN` fallback. |
| `access_logging.LabVisit` | `lab_location`, `purpose`, check-in/out times, duration, `status` | User FK and optional Room FK; user deletion `PROTECT`; DB constraint permits at most one `ACTIVE` visit per user. Assigning a room syncs `lab_location`. |
| `equipment.EquipmentLog` | borrow/return timestamps, pre-/post-condition | Links one visit and one asset with `PROTECT`; DB constraint permits at most one unreturned log per asset. |
| `incidents.Incident` | title, description, category, severity, status, assignee, resolution notes/timestamps | Reporter FK; optional visit and equipment-loan FKs; incident can be linked indirectly to room through the visit/loan/asset relationships. No direct Room FK or upload field is declared. |
| `incidents.IncidentStatusHistory` | from/to status, actor, note, timestamp | Related to incident; changes are created by the service layer. Incident deletion cascades history; changed-by user uses `PROTECT`. |

### Visit values

- Purpose: `CLASS`, `RESEARCH`, `PROJECT`, `TESTING`.
- Visit status: `ACTIVE`, `COMPLETED`.
- `LabVisit.check_out()` sets checkout time, whole-minute duration (minimum
  zero), and status `COMPLETED`.

### Equipment values

- Condition: `GOOD`, `DAMAGED`, `MALFUNCTIONING`, `MISSING`. Borrow and return
  forms share `CONDITION_CHOICES`.
- Availability: `AVAILABLE`, `BORROWED`, `MAINTENANCE`, `MISSING`.
- Return mapping in `equipment.views`: Good -> Available; Damaged or
  Malfunctioning -> Maintenance; Missing -> Missing.
- A defective pre-borrow condition is not accepted as a normal loan: the
  asset is set to Maintenance or Missing and the user is redirected to
  incident creation with visit/asset/condition context.
- The incident is prompted through a redirect; current code does not enforce
  that an incident must be filed before a staff member can later mark an asset
  available.

### Incident values and transitions

- Categories: Damage, Malfunction, Loss/Missing item, Safety concern,
  Misconduct, Other.
- Severity: Low, Medium, High, Critical.
- Status: Reported, Under Investigation, Resolved, Closed.
- `incidents.services.change_status()` permits staff to select any different
  defined status; this is not a strict sequential transition graph.
- Resolution requires non-empty notes. The service records actor, old/new
  status, and note in history; timestamps/notes are maintained as status
  changes occur.

## End-to-end workflows

### Account creation and login

1. Registration validates required identity fields, Django password rules,
   institutional email domain, and unique email.
2. Django `UserCreationForm` hashes the password; registration assigns
   `STUDENT`.
3. Login accepts username or email and uses Django session authentication.
   `dashboard:home` redirects to the role-specific dashboard.
4. Logout is blocked for any authenticated user with an active visit or
   unreturned equipment; the warning includes links to visit/equipment pages.

### Room visit

1. Check-in selects an active `Room` and purpose using `CheckInForm`.
2. The view locks/rechecks the room as active and writes the visit; a race that
   creates a second active visit is handled via the DB constraint.
3. The user sees current visit and history; only one active visit per user is
   allowed.
4. Checkout is POST-only, authorized for the owner or staff, and rejected if
   the visit is no longer active or contains unreturned equipment. Successful
   checkout records duration.
5. Staff can filter active visits by room; the view has an AJAX partial/count
   response.

### Equipment borrow and return

1. Borrowing requires an active visit. Student/Researcher assets are filtered
   to the checked-in room and revalidated server-side.
2. The borrow view locks the selected asset and permits only `AVAILABLE`
   assets. A DB constraint also prevents concurrent open loans for one asset.
3. Successful borrow creates `EquipmentLog` and sets asset availability to
   `BORROWED`.
4. Only the owner or staff can return a loan. The post-return condition is
   stored, return time is set, and availability follows the mapping above.
5. Non-Good return conditions warn and redirect to prefilled incident
   reporting.

### Incident reporting and review

1. An authenticated user submits title/category/severity/description, with
   optional visit/equipment-loan associations restricted to their own
   records.
2. The incident is assigned the reporter, starts as `REPORTED`, and an initial
   status-history entry is created.
3. Reporter and staff can view the incident; only Instructor/Admin may update
   status.
4. Status changes use the service layer and append status history; resolution
   needs a note.

### Dashboard and audit

- `/dashboard/central/` and its data endpoint are Instructor/Admin-only.
- Dashboard selectors aggregate active visits/occupancy, equipment
  availability and current borrowers, loan/condition metrics, and unresolved
  incidents (Reported + Under Investigation).
- `static/js/live_refresh.js` polls the central JSON endpoint every 15 seconds
  by default, skips hidden documents and concurrent requests, and updates
  status/error text.
- The audit UI (`/dashboard/audit/`) and API
  (`/dashboard/audit/api/`) are available to both Admins and Instructors via
  `dashboard.access.staff_required`; they are not Admin-exclusive.
- The audit UI provides GET filters for user name/email, lab, asset name,
  incident status, and date range. The API accepts the same filters and
  pagination parameters.
- Audit events combine check-in/out, equipment borrow/return, and incident
  status-history events. The asset filter currently matches the equipment
  name, despite the UI placeholder also mentioning asset code.
- Each source is capped at 500 rows before in-memory merge/sort/pagination;
  this can omit older matching events.
- `[VERIFY]` Current query/performance test results; the historical WBS audit
  documented failures, and no new test run is recorded here.
