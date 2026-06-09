from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from django.shortcuts import render
from django.urls import reverse
from .models import Guide

from .forms import GuideProfileForm

@login_required
def index(request):
    latest_guides_list = Guide.objects.order_by("-init_training_date")
    context = {"latest_guides_list": latest_guides_list}
    return render(request, "guides/index.html", context)

@login_required
def create_guide(request):
    if request.method == "POST":
        form = GuideProfileForm(request.POST)
        if form.is_valid(): 
            form.save(commit=False)
        return HttpResponseRedirect(reverse("guides:guide_detail"), args=guide.id)
    else:
        return render(request, "guides/create.html")

@login_required
def guide_detail(request, guide_id):
    try:
        guide = Guide.objects.get(id=guide_id)
        context = {"guide": guide}
    except Guide.DoesNotExist:
        raise Http404("Guide does not exist")
    return render(request, "guides/detail.html", context)

