from django.db.models import Q
from .models import Room


def filter_assets(request, qs):
    room = request.GET.get("room", "").strip()
    q = request.GET.get("q", "").strip()
    if room.isdigit():
        qs = qs.filter(room_id=int(room))
    if q:
        qs = qs.filter(
            Q(name__icontains=q) | Q(asset_code__icontains=q)
            | Q(room__name__icontains=q) | Q(room__code_prefix__icontains=q)
        )
    return qs.select_related("room")


def filter_context(request):
    return {
        "rooms": Room.objects.filter(is_active=True),
        "selected_room": request.GET.get("room", ""),
        "q": request.GET.get("q", ""),
    }