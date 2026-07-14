from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from django.shortcuts import render
from django.urls import reverse
from django.views import generic

from .models import Guide
from mypage.views  import review_grade

class IndexView(generic.ListView):
    template_name = "guides/index.html"
    context_object_name = "latest_guides_list"

    def get_queryset(self):
        return Guide.objects.order_by("-init_training_date")

class DetailView(generic.DetailView):
    model = Guide
    template_name = "guides/detail.html"

    def get_context_data(self, **kwargs): 
        context = super().get_context_data(**kwargs)
        guide = context['guide']
        if guide.init_training_date: 
            grade = review_grade(guide.pk)
        else: 
            grade = 0
        guide.grade = grade
        guide.save()

        context['guide'] = guide

        return context
        



