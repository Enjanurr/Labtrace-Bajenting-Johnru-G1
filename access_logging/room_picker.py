from equipment.models import Room


def active_rooms():
    return Room.objects.filter(is_active=True).order_by("building", "name")


def room_picker_context(form):
    rooms = active_rooms()
    data = [
        {
            "id": r.pk,
            "name": r.name,
            "code_prefix": r.code_prefix,
            "lab_type": r.lab_type,
            "lab_type_display": r.get_lab_type_display(),
            "building": r.building or "",
        }
        for r in rooms
    ]
    buildings = list(
        Room.objects.filter(is_active=True)
        .exclude(building="")
        .order_by("building")
        .values_list("building", flat=True)
        .distinct()
    )
    selected = form["room"].value() or ""
    return {
        "rooms_data": data,
        "buildings": buildings,
        "selected_room": str(selected),
    }