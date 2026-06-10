from django.http import Http404, HttpResponseRedirect

from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from .models import Guide

class IndexView(generic.ListView):
    template_name = "guides/index.html"
    context_object_name = "latest_guides_list"

    def get_queryset(self):
        return Guide.objects.order_by("-init_training_date")

class DetailView(generic.DetailView):
    model = Guide
    template_name = "guides/detail.html"


