from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404

from users.secure_files import serve_private_file

from .models import EquipmentLog

FIELDS = {"pre": "pre_condition_img", "post": "post_condition_img"}
STAFF_ROLES = ("INSTRUCTOR", "ADMIN")


@login_required
def condition_image(request, pk, kind):
    field = FIELDS.get(kind)
    if field is None:
        raise Http404
    log = get_object_or_404(EquipmentLog.objects.select_related("visit"), pk=pk)
    if request.user.role not in STAFF_ROLES and log.visit.user_id != request.user.id:
        raise PermissionDenied
    return serve_private_file(getattr(log, field))