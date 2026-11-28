from datetime import datetime

from django.db.models import Q
from django.urls import reverse

from access_logging.models import LabVisit
from equipment.models import EquipmentLog
from incidents.models import Incident, IncidentStatusHistory

from .fieldmap import *  # noqa: F401,F403
from .selectors import resolve

CAP = 500  # max rows pulled from each source, keeps the page fast


def _date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def parse_filters(get):
    status = get.get("incident_status", "")
    return {
        "user": get.get("user", "").strip(),
        "lab": get.get("lab", "").strip(),
        "asset": get.get("asset", "").strip(),
        "incident_status": status if status in Incident.Status.values else "",
        "date_from": _date(get.get("date_from")),
        "date_to": _date(get.get("date_to")),
    }


def lab_choices():
    values = LabVisit.objects.order_by().values_list(VISIT_LAB, flat=True).distinct()
    return sorted({str(v) for v in values if v not in (None, "")})


def _user_q(prefix, text):
    return (
        Q(**{f"{prefix}email__icontains": text})
        | Q(**{f"{prefix}first_name__icontains": text})
        | Q(**{f"{prefix}last_name__icontains": text})
    )


def _apply_dates(qs, field, f):
    if f["date_from"]:
        qs = qs.filter(**{f"{field}__date__gte": f["date_from"]})
    if f["date_to"]:
        qs = qs.filter(**{f"{field}__date__lte": f["date_to"]})
    return qs


def _visit_events(f, field, label):
    qs = LabVisit.objects.select_related(VISIT_USER).filter(**{f"{field}__isnull": False})
    if f["user"]:
        qs = qs.filter(_user_q(f"{VISIT_USER}__", f["user"]))
    if f["lab"]:
        qs = qs.filter(**{VISIT_LAB: f["lab"]})
    qs = _apply_dates(qs, field, f)
    return [
        {
            "when": getattr(v, field), "type": label, "user": getattr(v, VISIT_USER),
            "lab": resolve(v, VISIT_LAB), "asset": "", "status": "",
            "detail": str(resolve(v, VISIT_PURPOSE)), "url": "",
        }
        for v in qs.order_by(f"-{field}")[:CAP]
    ]


def _loan_events(f, field, label):
    qs = (
        EquipmentLog.objects
        .select_related(LOG_ASSET, f"{LOG_VISIT}__{VISIT_USER}")
        .filter(**{f"{field}__isnull": False})
    )
    if f["user"]:
        qs = qs.filter(_user_q(f"{LOG_VISIT}__{VISIT_USER}__", f["user"]))
    if f["lab"]:
        qs = qs.filter(**{f"{LOG_VISIT}__{VISIT_LAB}": f["lab"]})
    if f["asset"]:
        qs = qs.filter(**{f"{LOG_ASSET}__{ASSET_NAME}__icontains": f["asset"]})
    qs = _apply_dates(qs, field, f)
    return [
        {
            "when": getattr(log, field), "type": label,
            "user": resolve(log, f"{LOG_VISIT}__{VISIT_USER}"),
            "lab": resolve(log, f"{LOG_VISIT}__{VISIT_LAB}"),
            "asset": resolve(log, f"{LOG_ASSET}__{ASSET_NAME}"),
            "status": "", "detail": "", "url": "",
        }
        for log in qs.order_by(f"-{field}")[:CAP]
    ]


def _incident_events(f):
    qs = IncidentStatusHistory.objects.select_related(
        "changed_by", "incident__visit", f"incident__equipment_log__{LOG_ASSET}"
    )
    if f["incident_status"]:
        qs = qs.filter(to_status=f["incident_status"])
    if f["user"]:
        qs = qs.filter(_user_q("changed_by__", f["user"]))
    if f["lab"]:
        qs = qs.filter(**{f"incident__visit__{VISIT_LAB}": f["lab"]})
    if f["asset"]:
        qs = qs.filter(**{f"incident__equipment_log__{LOG_ASSET}__{ASSET_NAME}__icontains": f["asset"]})
    qs = _apply_dates(qs, "changed_at", f)

    labels = dict(Incident.Status.choices)
    events = []
    for h in qs.order_by("-changed_at")[:CAP]:
        inc = h.incident
        events.append({
            "when": h.changed_at, "type": "Incident", "user": h.changed_by,
            "lab": resolve(inc.visit, VISIT_LAB) if inc.visit_id else "",
            "asset": resolve(inc.equipment_log, f"{LOG_ASSET}__{ASSET_NAME}") if inc.equipment_log_id else "",
            "status": labels.get(h.to_status, h.to_status),
            "detail": f"{inc.reference}: {inc.title}",
            "url": reverse("incidents:detail", args=[inc.pk]),
        })
    return events


def build_events(f):
    """
    Filter rules:
    - incident status set  -> only incident events (transitions INTO that status)
    - asset set            -> check-in/out events are skipped (they have no asset)
    """
    events = []
    if not f["incident_status"]:
        if not f["asset"]:
            events += _visit_events(f, VISIT_IN, "Check-in")
            events += _visit_events(f, VISIT_OUT, "Check-out")
        events += _loan_events(f, LOG_BORROWED, "Borrowed")
        events += _loan_events(f, LOG_RETURNED, "Returned")
    events += _incident_events(f)
    events.sort(key=lambda e: e["when"], reverse=True)
    return events

def serialize_event(e):
    user = e["user"]
    if user and hasattr(user, "get_full_name"):
        user_label = user.get_full_name() or user.email
    else:
        user_label = str(user or "")
    return {
        "when": e["when"].isoformat(),
        "type": e["type"],
        "user": user_label,
        "lab": str(e["lab"] or ""),
        "asset": str(e["asset"] or ""),
        "status": e["status"],
        "detail": e["detail"],
        "url": e["url"],
    }