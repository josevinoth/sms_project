
import os
import mimetypes

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404


@login_required(login_url='/SMS/login_page')
def protected_media(request, path):
    media_root = os.path.realpath(settings.MEDIA_ROOT)
    file_path = os.path.realpath(os.path.join(media_root, path))

    # Prevent access outside the media folder
    if os.path.commonpath([media_root, file_path]) != media_root:
        raise Http404

    if not os.path.isfile(file_path):
        raise Http404

    content_type, _ = mimetypes.guess_type(file_path)

    response = FileResponse(
        open(file_path, 'rb'),
        content_type=content_type or 'application/octet-stream'
    )
    response['X-Content-Type-Options'] = 'nosniff'

    return response
