from django.http import Http404

from django.shortcuts import get_object_or_404, render
from .models import Guide

def index(request):
    latest_guides_list = Guide.objects.order_by("-init_training_date")
    context = {"latest_guides_list": latest_guides_list}
    return render(request, "guides/index.html", context)

def create_guide(request):
    if request.method == "POST":
        name = request.POST.get("name")
        init_training_date = request.POST.get("init_training_date")
        guide = Guide.objects.create(name=name, init_training_date=init_training_date)
        return render(request, "guides/detail.html", {"guide": guide})
    else:
        return render(request, "guides/create.html")

def guide_detail(request, guide_id):
    print("guide_id: ", guide_id)
    try:
        guide = Guide.objects.get(id=guide_id)
        context = {"guide": guide}
    except Guide.DoesNotExist:
        raise Http404("Guide does not exist")
    return render(request, "guides/detail.html", context)

