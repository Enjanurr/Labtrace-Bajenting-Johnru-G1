from django.http import JsonResponse
from django.shortcuts import render

from . import selectors
from .access import staff_required


@staff_required
def central_dashboard(request):
    occ = selectors.occupancy()
    return render(request, "dashboard/central.html", {
        "visits": selectors.active_visit_rows(),
        "occupancy": occ,
        "total_inside": sum(r["count"] for r in occ),
        "asset_summary": selectors.asset_summary(),
        "metrics": selectors.equipment_metrics(),
        "borrowers": selectors.current_borrowers(),
        "incidents": selectors.incident_summary(),
    })


@staff_required
def central_data(request):
    """JSON polled by live_refresh.js."""
    return JsonResponse(selectors.live_snapshot())