import mimetypes
import os

from django.http import FileResponse, Http404

INLINE_TYPES = {"image/jpeg", "image/png", "application/pdf"}


def serve_private_file(field_file, display_name=None):
    """Stream a stored file. Callers must check permissions BEFORE calling this."""
    if not field_file:
        raise Http404("No file.")
    try:
        handle = field_file.open("rb")
    except (FileNotFoundError, ValueError, OSError):
        raise Http404("File not found.")

    content_type = mimetypes.guess_type(field_file.name)[0] or "application/octet-stream"
    response = FileResponse(
        handle,
        as_attachment=content_type not in INLINE_TYPES,
        filename=display_name or os.path.basename(field_file.name),
        content_type=content_type,
    )
    response["X-Content-Type-Options"] = "nosniff"
    response["Cache-Control"] = "private, no-store"
    return response