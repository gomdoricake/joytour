from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from django.shortcuts import render
from django.urls import reverse
from django.views import generic

from .models import Guide
from guidereports.models import GuideReport
from mypage.views  import review_grade

from datetime import datetime, date, timedelta


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

from django.db.models import Sum, FloatField
from django.db.models.functions import Cast

@login_required
def guide_payable(request, pk): 
    guide = Guide.objects.get(pk=pk)
    
    today = date.today()
    today_weekday = today.weekday()

    sub_days = -1 * today_weekday - 5
    last_wed = today + timedelta(days=sub_days)

    if 2 <= today_weekday <= 4:
        sub_days = 2 - today_weekday - 1
        until_date = today + timedelta(days=sub_days)
    else:
        until_date = today

    start_date_str = str(last_wed)
    end_date_str = str(until_date)

    guidereports = GuideReport.objects.filter(guide=guide, invoice_date__range=(start_date_str, end_date_str))
    
    total_payable_fee = 0.0

    for report in guidereports:
        if report.is_paid == 'payable': continue
        if report.is_paid:
            report.pay_status = 'paid'
        else:
            report.pay_status = 'payable'
            if report.final_amount_due:
                total_payable_fee += float(report.final_amount_due)
        report.save()
    
    payable_reports = guidereports.filter(pay_status="payable").order_by('-invoice_date')

    guide_fee = payable_reports.aggregate(total_fee=Sum(Cast('final_events_fee', output_field=FloatField())))
    total_guide_fee = guide_fee['total_fee']

    expense_fee = payable_reports.aggregate(total_fee=Sum(Cast('final_expenses_fee', output_field=FloatField())))
    total_expense_fee = expense_fee['total_fee']

    super_ann_fee = payable_reports.aggregate(total_fee=Sum(Cast('super_ann', output_field=FloatField())))
    total_super_ann_fee = super_ann_fee['total_fee']

    context = {'guide': guide, 
               'payable_reports': payable_reports, 
               'total_payable_fee': total_payable_fee,
                'total_guide_fee': total_guide_fee,
                'total_expense_fee': total_expense_fee,
                'total_super_ann_fee': total_super_ann_fee,
                'last_wed': last_wed,
                'until': until_date}
    return render(request, 'guides/guide_payable.html', context)



def guide_unpaid(request, pk): 
    guide = Guide.objects.get(pk=pk)
    unpaid_reports = GuideReport.objects.filter(guide=guide, is_paid=False)
    context = {'guide': guide, 'unpaid_reports': unpaid_reports}

    return render(request, 'guides/guide_unpaid.html', context)


def guide_paid(request, pk): 
    guide = Guide.objects.get(pk=pk)
    paid_reports = GuideReport.objects.filter(guide=guide, is_paid=True)
    context = {'guide': guide, 'paid_reports': paid_reports}

    return render(request, 'guides/guide_paid.html', context)


def guide_all(request, pk): 
    guide = Guide.objects.get(pk=pk)
    all_reports = GuideReport.objects.filter(guide=guide)
    context = {'guide': guide, 'all_reports': all_reports}

    return render(request, 'guides/guide_all.html', context)