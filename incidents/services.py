from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import Incident, IncidentStatusHistory

ROLE_ADMIN = "ADMIN"
ROLE_INSTRUCTOR = "INSTRUCTOR"

S = Incident.Status

def is_staff(user):
    return user.is_authenticated and user.role in (ROLE_ADMIN, ROLE_INSTRUCTOR)


def can_view(user, incident):
    return is_staff(user) or incident.reporter_id == user.id


def allowed_next_statuses(incident, user):
    if not is_staff(user):
        return []
    return [status.value for status in Incident.Status]


def open_incident(incident, user):
    IncidentStatusHistory.objects.create(
        incident=incident, from_status="", to_status=S.REPORTED, changed_by=user,
        note="Incident reported.",
    )


@transaction.atomic
def change_status(incident, user, new_status, note=""):
    if new_status not in allowed_next_statuses(incident, user):
        raise ValidationError("That status change is not allowed.")
    if new_status == incident.status:
        raise ValidationError("Select a different status.")
    if new_status == S.RESOLVED and not note.strip():
        raise ValidationError("Resolution notes are required to resolve an incident.")

    old = incident.status
    incident.status = new_status
    now = timezone.now()

    if new_status == S.INVESTIGATION:
        incident.resolved_at = None
        incident.resolution_notes = ""
        if incident.assigned_to_id is None:
            incident.assigned_to = user
    elif new_status == S.RESOLVED:
        incident.resolution_notes = note.strip()
        incident.resolved_at = now
    elif old != S.RESOLVED:
        incident.resolved_at = None
        incident.resolution_notes = ""

    if new_status == S.CLOSED:
        incident.closed_at = now
    else:
        incident.closed_at = None

    incident.save()
    IncidentStatusHistory.objects.create(
        incident=incident, from_status=old, to_status=new_status,
        changed_by=user, note=note.strip(),
    )
    return incident