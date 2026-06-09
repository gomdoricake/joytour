from django.http import Http404, HttpResponseRedirect

from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from .models import Guide

def index(request):
    latest_guides_list = Guide.objects.order_by("-init_training_date")
    context = {"latest_guides_list": latest_guides_list}
    return render(request, "guides/index.html", context)

def create_guide(request):
    if request.method == "POST":
        name = request.POST.get("name")
        init_training_date = request.POST.get("init_training_date")
        birth_date = request.POST.get("birth_date")
        abn = request.POST.get("abn")
        contact_info = request.POST.get("contact_info")
        address = request.POST.get("address")
        bank_account_name = request.POST.get("bank_account_name")
        bsb = request.POST.get("bsb")
        account_number = request.POST.get("account_number")
        guide = Guide.objects.create(
            name=name, 
            init_training_date=init_training_date,
            birth_date=birth_date,
            abn=abn,
            contact_info=contact_info,
            address=address,
            bank_account_name=bank_account_name,
            bsb=bsb,
            account_number=account_number
            )
        return HttpResponseRedirect(reverse("guides:guide_detail"), args=guide.id)
    else:
        return render(request, "guides/create.html")

def guide_detail(request, guide_id):
    try:
        guide = Guide.objects.get(id=guide_id)
        context = {"guide": guide}
    except Guide.DoesNotExist:
        raise Http404("Guide does not exist")
    return render(request, "guides/detail.html", context)

