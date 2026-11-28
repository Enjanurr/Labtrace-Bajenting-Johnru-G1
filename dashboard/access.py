from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

STAFF_ROLES = ("INSTRUCTOR", "ADMIN")


def staff_required(view):
    """Logged-out -> login page. Logged-in but not instructor/admin -> 403."""
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if getattr(request.user, "role", None) not in STAFF_ROLES:
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return login_required(wrapper)