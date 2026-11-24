from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import IncidentForm, StatusUpdateForm
from .models import Incident
from .services import can_view, change_status, is_staff, open_incident


def _get_visible(request, pk):
    incident = get_object_or_404(
        Incident.objects.select_related("reporter", "visit", "equipment_log", "assigned_to"), pk=pk
    )
    if not can_view(request.user, incident):
        raise PermissionDenied
    return incident


@login_required
def incident_list(request):
    qs = Incident.objects.select_related("reporter")
    if not is_staff(request.user):
        qs = qs.filter(reporter=request.user)
    status = request.GET.get("status", "")
    if status in Incident.Status.values:
        qs = qs.filter(status=status)
    return render(request, "incidents/incident_list.html", {
        "incidents": qs,
        "status_choices": Incident.Status.choices,
        "current_status": status,
        "staff": is_staff(request.user),
    })


@login_required
def incident_create(request):
    initial = {}
    if request.method == "GET":
        visit_id = request.GET.get("visit")
        log_id = request.GET.get("log")
        asset_id = request.GET.get("asset")
        condition = request.GET.get("condition", "")

        from equipment.models import Asset

        asset = Asset.objects.filter(pk=asset_id).first() if asset_id else None
        if visit_id:
            initial["visit"] = visit_id
        if log_id:
            initial["equipment_log"] = log_id
        if condition == "DAMAGED":
            initial.update({
                "title": f"Damaged equipment: {asset.asset_code}" if asset else "Damaged equipment",
                "category": Incident.Category.DAMAGE,
                "severity": Incident.Severity.HIGH,
                "description": f"{asset.asset_code} was reported Damaged in room {asset.room.name if asset.room else 'Unassigned'}." if asset else "Equipment was reported Damaged.",
            })
        elif condition == "MALFUNCTIONING":
            initial.update({
                "title": f"Malfunctioning equipment: {asset.asset_code}" if asset else "Malfunctioning equipment",
                "category": Incident.Category.MALFUNCTION,
                "severity": Incident.Severity.MEDIUM,
                "description": f"{asset.asset_code} was reported Malfunctioning in room {asset.room.name if asset.room else 'Unassigned'}." if asset else "Equipment was reported Malfunctioning.",
            })
        elif condition == "MISSING":
            initial.update({
                "title": f"Missing equipment: {asset.asset_code}" if asset else "Missing equipment",
                "category": Incident.Category.LOSS,
                "severity": Incident.Severity.HIGH,
                "description": f"{asset.asset_code} was reported Missing in room {asset.room.name if asset.room else 'Unassigned'}." if asset else "Equipment was reported Missing.",
            })

    form = IncidentForm(
        request.POST or None,
        user=request.user,
        initial=initial if request.method == "GET" else None,
    )
    if request.method == "POST" and form.is_valid():
        incident = form.save(commit=False)
        incident.reporter = request.user
        incident.save()
        open_incident(incident, request.user)
        messages.success(request, f"Incident {incident.reference} submitted.")
        return redirect("incidents:detail", pk=incident.pk)
    return render(request, "incidents/incident_form.html", {"form": form})


@login_required
def incident_detail(request, pk):
    incident = _get_visible(request, pk)
    status_form = StatusUpdateForm(incident=incident, user=request.user)
    return render(request, "incidents/incident_detail.html", {
        "incident": incident,
        "history": incident.history.select_related("changed_by"),
        "status_form": status_form,
        "can_update_status": is_staff(request.user),
    })


@login_required
@require_POST
def incident_status(request, pk):
    incident = _get_visible(request, pk)
    if not is_staff(request.user):
        raise PermissionDenied
    form = StatusUpdateForm(request.POST, incident=incident, user=request.user)
    if form.is_valid():
        try:
            change_status(incident, request.user, form.cleaned_data["status"], form.cleaned_data["note"])
            messages.success(request, f"Status changed to {incident.get_status_display()}.")
        except ValidationError as e:
            messages.error(request, e.messages[0])
    else:
        for errors in form.errors.values():
            messages.error(request, errors[0])
    return redirect("incidents:detail", pk=incident.pk)

