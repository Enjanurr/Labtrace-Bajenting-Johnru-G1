from django import template


register = template.Library()


@register.inclusion_tag("equipment/_severity_badge.html")
def severity_badge(value, display=None):
    normalized = str(value).upper()
    display = display or str(value).replace("_", " ").title()

    if normalized in {"GOOD", "AVAILABLE", "LOW", "RESOLVED"}:
        classes = "bg-emerald-50 text-emerald-700 ring-emerald-600/10"
        dot = "bg-emerald-500"
    elif normalized in {
        "MALFUNCTIONING",
        "MAINTENANCE",
        "UNDER_MAINTENANCE",
        "MEDIUM",
        "REPORTED",
    }:
        classes = "bg-amber-50 text-amber-700 ring-amber-600/10"
        dot = "bg-amber-500"
    elif normalized in {"DAMAGED", "MISSING", "HIGH", "CRITICAL"}:
        classes = "bg-rose-50 text-rose-700 ring-rose-600/10"
        dot = "bg-rose-500"
    elif normalized in {"BORROWED", "INVESTIGATION"}:
        classes = "bg-blue-50 text-blue-700 ring-blue-600/10"
        dot = "bg-blue-500"
    else:
        classes = "bg-slate-100 text-slate-700 ring-slate-500/10"
        dot = "bg-slate-400"

    return {"display": display, "classes": classes, "dot": dot}
