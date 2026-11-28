from django.db.models import Count

from access_logging.models import LabVisit
from equipment.models import Asset, EquipmentLog
from incidents.models import Incident

from .fieldmap import *  # noqa: F401,F403

from datetime import timedelta

from django.db.models import Avg, DurationField, ExpressionWrapper, F
from django.utils import timezone

OPEN_INCIDENT_STATUSES = [Incident.Status.REPORTED, Incident.Status.INVESTIGATION]


def resolve(obj, lookup):
    """Follow 'visit__user' style paths on an instance; '' if anything is missing."""
    for part in lookup.split("__"):
        if obj is None:
            return ""
        obj = getattr(obj, part, None)
    return obj if obj is not None else ""


def active_visits():
    return (
        LabVisit.objects.filter(**{f"{VISIT_OUT}__isnull": True})
        .select_related(VISIT_USER)
        .order_by(VISIT_IN)
    )


def active_visit_rows():
    rows = []
    for v in active_visits():
        display = getattr(v, f"get_{VISIT_PURPOSE}_display", None)
        rows.append({
            "user": getattr(v, VISIT_USER),
            "lab": resolve(v, VISIT_LAB),
            "since": getattr(v, VISIT_IN),
            "purpose": display() if callable(display) else resolve(v, VISIT_PURPOSE),
        })
    return rows


def occupancy():
    rows = (
        active_visits().order_by()
        .values(VISIT_LAB).annotate(count=Count("pk")).order_by(VISIT_LAB)
    )
    return [{"lab": r[VISIT_LAB], "count": r["count"]} for r in rows]


def asset_summary():
    labels = dict(getattr(Asset._meta.get_field(ASSET_STATUS), "flatchoices", []))
    rows = (
        Asset.objects.order_by()
        .values(ASSET_STATUS).annotate(count=Count("pk")).order_by(ASSET_STATUS)
    )
    return [
        {"status": r[ASSET_STATUS], "label": labels.get(r[ASSET_STATUS], r[ASSET_STATUS]), "count": r["count"]}
        for r in rows
    ]


def current_borrowers():
    qs = (
        EquipmentLog.objects.filter(**{f"{LOG_RETURNED}__isnull": True})
        .select_related(LOG_ASSET, f"{LOG_VISIT}__{VISIT_USER}")
        .order_by(LOG_BORROWED)
    )
    return [
        {
            "asset_name": resolve(log, f"{LOG_ASSET}__{ASSET_NAME}"),
            "borrower": resolve(log, f"{LOG_VISIT}__{VISIT_USER}"),
            "lab": resolve(log, f"{LOG_VISIT}__{VISIT_LAB}"),
            "since": getattr(log, LOG_BORROWED),
        }
        for log in qs
    ]


def incident_summary():
    """Unresolved = Reported + Under Investigation."""
    qs = Incident.objects.filter(status__in=OPEN_INCIDENT_STATUSES)
    by = {r["status"]: r["count"] for r in qs.order_by().values("status").annotate(count=Count("pk"))}
    return {
        "total": sum(by.values()),
        "reported": by.get(Incident.Status.REPORTED, 0),
        "investigation": by.get(Incident.Status.INVESTIGATION, 0),
        "latest": qs.select_related("reporter").order_by("-created_at")[:5],
    }
    
def _label_map(model, field):
    return dict(model._meta.get_field(field).flatchoices)


def _grouped(qs, field, labels):
    rows = qs.order_by().values(field).annotate(count=Count("pk")).order_by(field)
    return [
        {"value": r[field], "label": labels.get(r[field], r[field]), "count": r["count"]}
        for r in rows if r[field] not in (None, "")
    ]


def equipment_metrics(days=30):
    """Usage and condition numbers for the dashboard."""
    now = timezone.now()
    today = timezone.localtime(now).replace(hour=0, minute=0, second=0, microsecond=0)
    since = now - timedelta(days=days)

    out_now = EquipmentLog.objects.filter(**{f"{LOG_RETURNED}__isnull": True})
    returned = EquipmentLog.objects.filter(**{f"{LOG_RETURNED}__gte": since})
    avg = returned.aggregate(
        avg=Avg(ExpressionWrapper(F(LOG_RETURNED) - F(LOG_BORROWED), output_field=DurationField()))
    )["avg"]
    name_key = f"{LOG_ASSET}__{ASSET_NAME}"
    top = (
        EquipmentLog.objects.filter(**{f"{LOG_BORROWED}__gte": since})
        .order_by().values(name_key).annotate(count=Count("pk")).order_by("-count", name_key)[:5]
    )
    return {
        "days": days,
        "active_loans": out_now.count(),
        "borrowed_today": EquipmentLog.objects.filter(**{f"{LOG_BORROWED}__gte": today}).count(),
        "returned_today": EquipmentLog.objects.filter(**{f"{LOG_RETURNED}__gte": today}).count(),
        "avg_loan_minutes": round(avg.total_seconds() / 60) if avg else None,
        "top_assets": [{"name": r[name_key], "count": r["count"]} for r in top],
        "on_loan_condition": _grouped(out_now, LOG_PRE, _label_map(EquipmentLog, LOG_PRE)),
        "returned_condition": _grouped(returned, LOG_POST, _label_map(EquipmentLog, LOG_POST)),
    }


def _name(user):
    if not user:
        return ""
    return (user.get_full_name() or user.email) if hasattr(user, "get_full_name") else str(user)


def _fmt(dt):
    return timezone.localtime(dt).strftime("%b %d, %H:%M") if dt else ""


def live_snapshot():
    """Everything the dashboard needs, JSON-serialisable, in one payload."""
    occ = occupancy()
    inc = incident_summary()
    assets = asset_summary()
    return {
        "generated_at": timezone.now().isoformat(),
        "total_inside": sum(r["count"] for r in occ),
        "occupancy": occ,
        "visits": [
            {"user": _name(v["user"]), "lab": str(v["lab"]), "purpose": str(v["purpose"]),
             "since": v["since"].isoformat(), "since_display": _fmt(v["since"])}
            for v in active_visit_rows()
        ],
        "equipment": {
            "assets": assets,
            "total_assets": sum(a["count"] for a in assets),
            **equipment_metrics(),
        },
        "borrowers": [
            {"asset": b["asset_name"], "borrower": _name(b["borrower"]), "lab": str(b["lab"]),
             "since": b["since"].isoformat(), "since_display": _fmt(b["since"])}
            for b in current_borrowers()
        ],
        "incidents": {"total": inc["total"], "reported": inc["reported"],
                      "investigation": inc["investigation"]},
        "unresolved": inc["total"],
    }