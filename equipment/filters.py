from django.db.models import Q

from .models import Room
from .room_scope import BorrowScope, scope_assets


def filter_assets(request, qs, scope=None):
    room = request.GET.get("room", "").strip()
    q = request.GET.get("q", "").strip()
    if room.isdigit() and (scope is None or not scope.restricted):
        qs = qs.filter(room_id=int(room))
    if q:
        qs = qs.filter(
            Q(name__icontains=q) | Q(asset_code__icontains=q)
            | Q(room__name__icontains=q) | Q(room__code_prefix__icontains=q)
        )
    if scope is not None:
        qs = scope_assets(scope, qs)
    return qs.select_related("room")


def filter_context(request, scope: BorrowScope):
    return {
        "rooms": (
            Room.objects.filter(is_active=True)
            if not scope.restricted
            else Room.objects.none()
        ),
        "selected_room": (
            str(scope.room.pk)
            if scope.restricted and scope.room
            else request.GET.get("room", "") if not scope.restricted else ""
        ),
        "q": request.GET.get("q", ""),
    }