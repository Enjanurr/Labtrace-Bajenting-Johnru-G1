from dataclasses import dataclass
from typing import Optional

from access_logging.models import LabVisit
from .models import Room

STAFF_ROLES = {"ADMIN", "INSTRUCTOR"}


@dataclass
class BorrowScope:
    restricted: bool            # True for students/researchers
    visit: Optional[LabVisit] = None
    room: Optional[Room] = None
    reason: str = ""            # "", "no_visit", "no_room"


def is_unrestricted(user) -> bool:
    return user.is_superuser or getattr(user, "role", None) in STAFF_ROLES


def borrow_scope(user) -> BorrowScope:
    visit = (
        LabVisit.objects.select_related("room")
        .filter(user=user, status=LabVisit.Status.ACTIVE)
        .order_by("-check_in_time")
        .first()
    )

    if is_unrestricted(user):
        return BorrowScope(restricted=False, visit=visit)

    if visit is None:
        return BorrowScope(restricted=True, reason="no_visit")

    room = visit.room
    if room is None and visit.lab_location:
        room = Room.objects.filter(
            name__iexact=visit.lab_location,
            is_active=True,
        ).first()
    if room is None:
        return BorrowScope(restricted=True, visit=visit, reason="no_room")

    return BorrowScope(restricted=True, visit=visit, room=room)


def scope_assets(scope: BorrowScope, qs):
    """Limit an Asset queryset to what this user may see."""
    if not scope.restricted:
        return qs
    if scope.room is None:
        return qs.none()
    return qs.filter(room=scope.room)


def check_borrow_allowed(scope: BorrowScope, asset):
    """Return (ok, message). Server-side guard for borrow submissions."""
    if not scope.restricted:
        return True, ""
    if scope.reason == "no_visit":
        return False, "Check in to a lab room before borrowing equipment."
    if scope.reason == "no_room":
        return False, "Your current visit has no room. Check out and check in again."
    if asset.room_id != scope.room.pk:
        return False, f"{asset.asset_code} belongs to a different room. You are checked into {scope.room.name}."
    return True, ""