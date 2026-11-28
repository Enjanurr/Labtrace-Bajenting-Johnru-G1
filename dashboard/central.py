from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render

from incidents.models import Incident

from . import selectors
from .access import staff_required
from .audit import build_events, lab_choices, parse_filters, serialize_event

MAX_PAGE_SIZE = 100


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


@staff_required
def audit_trail(request):
    filters = parse_filters(request.GET)
    events = build_events(filters)
    page_obj = Paginator(events, 25).get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    return render(request, "dashboard/audit.html", {
        "page_obj": page_obj,
        "total": len(events),
        "filters": filters,
        "labs": lab_choices(),
        "incident_statuses": Incident.Status.choices,
        "querystring": params.urlencode(),
    })


@staff_required
def audit_api(request):
    """
    GET /dashboard/audit/api/?user=&lab=&asset=&incident_status=&date_from=&date_to=&page=&page_size=
    Same filters as the audit page; page_size is capped at 100.
    """
    filters = parse_filters(request.GET)
    try:
        page_size = min(max(int(request.GET.get("page_size", 25)), 1), MAX_PAGE_SIZE)
    except ValueError:
        page_size = 25

    paginator = Paginator(build_events(filters), page_size)
    page = paginator.get_page(request.GET.get("page"))
    return JsonResponse({
        "count": paginator.count,
        "page": page.number,
        "num_pages": paginator.num_pages,
        "page_size": page_size,
        "has_next": page.has_next(),
        "has_previous": page.has_previous(),
        "filters": {
            "user": filters["user"], "lab": filters["lab"], "asset": filters["asset"],
            "incident_status": filters["incident_status"],
            "date_from": filters["date_from"].isoformat() if filters["date_from"] else "",
            "date_to": filters["date_to"].isoformat() if filters["date_to"] else "",
        },
        "results": [serialize_event(e) for e in page.object_list],
    })