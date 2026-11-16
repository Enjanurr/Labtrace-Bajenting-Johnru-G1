from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import Incident, IncidentStatusHistory

ROLE_ADMIN = "ADMIN"
ROLE_INSTRUCTOR = "INSTRUCTOR"

S = Incident.Status

# Every legal move. Anything not listed here is rejected server-side.
TRANSITIONS = {
    S.REPORTED: [S.INVESTIGATION],
    S.INVESTIGATION: [S.RESOLVED],
    S.RESOLVED: [S.CLOSED, S.INVESTIGATION],  # INVESTIGATION = reopen
    S.CLOSED: [],
}


def is_staff(user):
    return user.is_authenticated and user.role in (ROLE_ADMIN, ROLE_INSTRUCTOR)


def can_view(user, incident):
    return is_staff(user) or incident.reporter_id == user.id


def allowed_next_statuses(incident, user):
    nxt = TRANSITIONS.get(incident.status, [])
    if user.role == ROLE_ADMIN:
        return list(nxt)
    if user.role == ROLE_INSTRUCTOR:
        # Instructors may only start an investigation.
        return [s for s in nxt if incident.status == S.REPORTED and s == S.INVESTIGATION]
    return []


def open_incident(incident, user):
    IncidentStatusHistory.objects.create(
        incident=incident, from_status="", to_status=S.REPORTED, changed_by=user,
        note="Incident reported.",
    )


@transaction.atomic
def change_status(incident, user, new_status, note=""):
    if new_status not in allowed_next_statuses(incident, user):
        raise ValidationError("That status change is not allowed.")
    if new_status == S.RESOLVED and not note.strip():
        raise ValidationError("Resolution notes are required to resolve an incident.")

    old = incident.status
    incident.status = new_status
    now = timezone.now()

    if new_status == S.INVESTIGATION:
        incident.resolved_at = None
        if incident.assigned_to_id is None:
            incident.assigned_to = user
    elif new_status == S.RESOLVED:
        incident.resolution_notes = note.strip()
        incident.resolved_at = now
    elif new_status == S.CLOSED:
        incident.closed_at = now

    incident.save()
    IncidentStatusHistory.objects.create(
        incident=incident, from_status=old, to_status=new_status,
        changed_by=user, note=note.strip(),
    )
    return incident