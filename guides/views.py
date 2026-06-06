from django.http import Http404

from django.shortcuts import get_object_or_404, render
from .models import Guide

def index(request):
    latest_guides_list = Guide.objects.order_by("-init_training_date")
    context = {"latest_guides_list": latest_guides_list}
    return render(request, "guides/index.html", context)

def guide_detail(request, guide_id):
    print("guide_id: ", guide_id)
    try:
        guide = Guide.objects.get(id=guide_id)
        context = {"guide": guide}
    except Guide.DoesNotExist:
        raise Http404("Guide does not exist")
    return render(request, "guides/detail.html", context)

