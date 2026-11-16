from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from users.secure_files import serve_private_file

from .models import IncidentAttachment
from .services import can_view


@login_required
def attachment_download(request, pk):
    attachment = get_object_or_404(IncidentAttachment.objects.select_related("incident"), pk=pk)
    if not can_view(request.user, attachment.incident):   # reporter, instructor, admin
        raise PermissionDenied
    return serve_private_file(attachment.file, attachment.original_name)