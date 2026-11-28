from functools import wraps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import RoomForm
from .models import Room


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapper(request, *args, **kwargs):
        u = request.user
        if not (u.is_superuser or getattr(u, "role", None) == "ADMIN"):
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapper


@admin_required
def room_list(request):
    q = request.GET.get("q", "").strip()
    rooms = Room.objects.annotate(asset_count=Count("assets"))
    if q:
        rooms = rooms.filter(Q(name__icontains=q) | Q(code_prefix__icontains=q))
    return render(request, "equipment/room_list.html", {"rooms": rooms, "q": q})


@admin_required
def room_create(request):
    form = RoomForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        room = form.save()
        messages.success(request, f"Room {room.name} created with prefix {room.code_prefix}.")
        return redirect("equipment:room_list")
    return render(request, "equipment/room_form.html", {"form": form, "title": "Add Room"})


@admin_required
def room_edit(request, pk):
    room = get_object_or_404(Room, pk=pk)
    form = RoomForm(request.POST or None, instance=room)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Room {room.name} updated.")
        return redirect("equipment:room_list")
    return render(request, "equipment/room_form.html", {"form": form, "title": f"Edit {room.name}"})