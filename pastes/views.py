from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404, render
from django.db import transaction
from datetime import timedelta

from .models import Paste
from .utils import generate_id, get_now


@api_view(['GET'])
def healthz(request):
    try:
        Paste.objects.first()
        return Response({"ok": True})
    except Exception:
        return Response({"ok": False}, status=500)


@api_view(['POST'])
def create_paste(request):
    data = request.data

    content = data.get("content")
    ttl_seconds = data.get("ttl_seconds")
    max_views = data.get("max_views")

    if not content or not isinstance(content, str):
        return Response({"error": "Invalid content"}, status=400)

    if ttl_seconds is not None:
        try:
            ttl_seconds = int(ttl_seconds)
            if ttl_seconds < 1:
                raise ValueError()
        except:
            return Response({"error": "Invalid ttl_seconds"}, status=400)

    if max_views is not None:
        try:
            max_views = int(max_views)
            if max_views < 1:
                raise ValueError()
        except:
            return Response({"error": "Invalid max_views"}, status=400)

    now = get_now(request)
    expires_at = None

    if ttl_seconds:
        expires_at = now + timedelta(seconds=ttl_seconds)

    pid = generate_id()

    paste = Paste.objects.create(
        id=pid,
        content=content,
        expires_at=expires_at,
        max_views=max_views
    )

    return Response({
        "id": paste.id,
        "url": f"{request.scheme}://{request.get_host()}/p/{paste.id}"
    }, status=201)


@api_view(['GET'])
def fetch_paste(request, id):
    now = get_now(request)

    with transaction.atomic():
        paste = get_object_or_404(Paste.objects.select_for_update(), id=id)

        if paste.expires_at and paste.expires_at <= now:
            return Response({"error": "Paste expired"}, status=404)

        if paste.max_views is not None and paste.views >= paste.max_views:
            return Response({"error": "View limit exceeded"}, status=404)

        paste.views += 1
        paste.save()

        remaining_views = None
        if paste.max_views is not None:
            remaining_views = max(paste.max_views - paste.views, 0)

        return Response({
            "content": paste.content,
            "remaining_views": remaining_views,
            "expires_at": paste.expires_at
        })


def view_paste_html(request, id):
    now = get_now(request)

    paste = get_object_or_404(Paste, id=id)

    if paste.expires_at and paste.expires_at <= now:
        return render(request, "404.html", status=404)

    if paste.max_views is not None and paste.views >= paste.max_views:
        return render(request, "404.html", status=404)

    return render(request, "paste.html", {"content": paste.content})
