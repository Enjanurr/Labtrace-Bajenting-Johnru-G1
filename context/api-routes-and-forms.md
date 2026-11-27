# LabTrace Routes, Views, Forms, and UI

Routes are mounted by `labtrace/urls.py`. Paths below are relative to the
prefix shown. Confirm template names in the view before changing or moving
templates.

## Root and dashboard

Root `""` redirects to `dashboard:home`; authenticated role selection happens
in `dashboard.views.home`.

| Prefix and path | URL name | View | Access / response |
|---|---|---|---|
| `/dashboard/` | `dashboard:home` | `dashboard.views.home` | Login required; redirects by role |
| `/dashboard/admin/` | `dashboard:admin` | `AdminDashboardView` | Admin; `dashboard/admin.html` |
| `/dashboard/instructor/` | `dashboard:instructor` | `InstructorDashboardView` | Instructor; `dashboard/instructor.html` |
| `/dashboard/researcher/` | `dashboard:researcher` | `ResearcherDashboardView` | Researcher; `dashboard/researcher.html` |
| `/dashboard/student/` | `dashboard:student` | `StudentDashboardView` | Student; `dashboard/student.html` |
| `/dashboard/central/` | `dashboard:central` | `dashboard.central.central_dashboard` | Instructor/Admin; `dashboard/central.html` |
| `/dashboard/central/data/` | `dashboard:central_data` | `dashboard.central.central_data` | Instructor/Admin; JSON snapshot |
| `/dashboard/audit/` | `dashboard:audit` | `dashboard.central.audit_trail` | Instructor/Admin; `dashboard/audit.html`; GET filters and pagination |
| `/dashboard/audit/api/` | `dashboard:audit_api` | `dashboard.central.audit_api` | Instructor/Admin; same filters with paginated JSON |

Audit access is shared by Instructor and Admin roles (`dashboard.access.staff_required`).
The UI supports filtering by user name/email, laboratory, asset name, incident
status, and date range. The API accepts the same filters plus `page` and
`page_size` (maximum 100). The current backend asset filter matches equipment
name; asset-code matching is not implemented despite the UI placeholder text.
Each event source is capped at 500 rows before merge and pagination.

## Authentication and user management

| Prefix and path | URL name | View | Form/template behavior |
|---|---|---|---|
| `/accounts/register/` | `authentication:register` | `register_view` | `RegistrationForm`; `authentication/register.html`; public registrations are Student-only |
| `/accounts/login/` | `authentication:login` | `LabTraceLoginView` | `LoginForm`; `registration/login.html`; username or email |
| `/accounts/logout/` | `authentication:logout` | `LabTraceLogoutView` | Blocks logout if the user has an active visit or open equipment loan |
| `/users/me/` | `users:profile` | `ProfileDetailView` | Signed-in user's `users/profile.html` |
| `/users/me/edit/` | `users:profile_edit` | `ProfileUpdateView` | `ProfileForm`; updates only `request.user`; `users/profile_edit.html` |
| `/users/manage/` | `users:manage_list` | `user_list_view` | Admin; search by identity, role/status filters, pagination; `users/user_list.html` |
| `/users/manage/<pk>/role/` | `users:manage_role` | `change_role_view` | POST-only Admin action; `UserRoleForm` |
| `/users/manage/<pk>/toggle-active/` | `users:manage_toggle` | `toggle_active_view` | POST-only Admin action; toggles `is_active` |
| `/users/password-change/` | `users:password_change` | Django `PasswordChangeView` | `users/password_change.html`; success -> profile |
| `/users/password-reset/` | `users:password_reset` | Django `PasswordResetView` | `users/password_reset_form.html`; file-based email |
| `/users/password-reset/done/` | `users:password_reset_done` | Django `PasswordResetDoneView` | `users/password_reset_done.html` |
| `/users/password-reset/confirm/<uidb64>/<token>/` | `users:password_reset_confirm` | Django `PasswordResetConfirmView` | `users/password_reset_confirm.html` |
| `/users/password-reset/complete/` | `users:password_reset_complete` | Django `PasswordResetCompleteView` | `users/password_reset_complete.html` |

Password reset uses Django's default URL token mechanism and writes messages
under `sent_emails/`; no SMTP service is configured.

## Visits

| Prefix and path | URL name | View | Form/template/response |
|---|---|---|---|
| `/visits/check-in/` | `access_logging:check_in` | `check_in_view` | `CheckInForm`; `access_logging/check_in.html`; active rooms only |
| `/visits/<pk>/check-out/` | `access_logging:check_out` | `check_out_view` | POST-only JSON; owner or Instructor/Admin; blocks while loans are open |
| `/visits/mine/` | `access_logging:my_visits` | `my_visits_view` | Own current/history visits; `access_logging/my_visits.html` |
| `/visits/active/` | `access_logging:active` | `active_visits_view` | Instructor/Admin; `active_visits.html`; AJAX request returns rows HTML + count JSON |

## Equipment and room administration

| Prefix and path | URL name | View | Form/template/access |
|---|---|---|---|
| `/equipment/` | `equipment:inventory` | `inventory_view` | Search/status/room scope; `equipment/inventory.html` |
| `/equipment/borrow/` | `equipment:borrow` | `borrow_view` | `BorrowForm`; active visit required; room/server-side scope |
| `/equipment/logs/<pk>/return/` | `equipment:return` | `return_view` | `ReturnForm`; owner or staff; `equipment/return.html` |
| `/equipment/mine/` | `equipment:mine` | `my_equipment_view` | Own active loans/history; `equipment/my_equipment.html` |
| `/equipment/manage/new/` | `equipment:asset_new` | `asset_form_view` | Instructor/Admin; `AssetForm`; `equipment/asset_form.html` |
| `/equipment/manage/<pk>/edit/` | `equipment:asset_edit` | `asset_form_view` | Instructor/Admin; edit asset |
| `/equipment/rooms/` | `equipment:room_list` | `room_list` | Admin/superuser; `equipment/room_list.html` |
| `/equipment/rooms/add/` | `equipment:room_create` | `room_create` | Admin/superuser; `RoomForm`; `equipment/room_form.html` |
| `/equipment/rooms/<pk>/edit/` | `equipment:room_edit` | `room_edit` | Admin/superuser; `RoomForm` |

Forms:

- `AssetForm` requires a room on creation; room prefix/code generation is
  server-side. Borrowed asset availability cannot be edited in this form.
- `RoomForm` trims the room name, derives/normalizes a prefix, and checks for
  duplicate prefixes.
- `BorrowForm` and `ReturnForm` use the shared condition options.

## Incidents

| Prefix and path | URL name | View | Form/template/access |
|---|---|---|---|
| `/incidents/` | `incidents:list` | `incident_list` | Reporter sees own; staff sees all; `incidents/incident_list.html` |
| `/incidents/new/` | `incidents:new` | `incident_create` | `IncidentForm`; own visits/loans only; `incidents/incident_form.html` |
| `/incidents/<pk>/` | `incidents:detail` | `incident_detail` | Reporter or staff; `incidents/incident_detail.html` |
| `/incidents/<pk>/status/` | `incidents:status` | `incident_status` | POST-only; Instructor/Admin; `StatusUpdateForm` |

The new-incident GET accepts `visit`, `log`, `asset`, and `condition` query
parameters for prefill from the equipment flow. Incident status history is
created through `incidents.services`.

## Removed file/image uploads

Equipment condition images and incident evidence attachments were removed in
the current implementation. The active models/forms have no upload fields,
media settings are absent from `labtrace/settings.py`, and migrations remove
the earlier equipment image fields and `IncidentAttachment` model:
`equipment/migrations/0002_remove_equipmentlog_post_condition_img_and_more.py`
and `incidents/migrations/0002_delete_incidentattachment.py`. Treat upload
support as out of scope unless an approved WBS/PD3 requirement says otherwise.

## Shared template and JavaScript conventions

- Most pages extend `templates/base.html`; shared UI is organized by feature
  under `templates/<app>/`.
- Use Django `{% url %}` names and `{% csrf_token %}` for forms. CSRF
  middleware is configured; verify each state-changing form when modifying it.
- `static/js/main.js` configures CSRF for same-origin jQuery AJAX, polls the
  active-visits view, handles checkout, field styling, password visibility,
  and institutional email hints.
- `static/js/live_refresh.js` is dedicated to the central dashboard.
- Equipment status badges use `equipment/templatetags/severity_tags.py` and
  `templates/equipment/_severity_badge.html` (included via the template tag
  library); incident templates also render severity/status badges.
- The root `templates/base.html` currently contains external Google Fonts and
  Tailwind CDN references even though local assets are bundled.
