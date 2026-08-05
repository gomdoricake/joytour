from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from guides.models import Guide
from guidereports.models import GuideReport
from datetime import date, timedelta

@login_required
def index(request): 
    admin = Guide.objects.get(user=request.user)
    return render(request, 'joyadmin/index.html', {'admin': admin})

from django.db.models import Sum, DecimalField, Q
from django.db.models.functions import Cast, Coalesce


@login_required
def payable_reports(request):
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


    guides = Guide.objects.annotate(
        payable_sum=Coalesce(
            Sum(
                Cast('guidereports__final_amount_due', 
                     output_field=DecimalField(max_digits=12, decimal_places=2)),
                filter=Q(
                    guidereports__invoice_date__range=(start_date_str, end_date_str),
                    guidereports__is_paid=False
                )
            ),
            0.0,
            output_field=DecimalField(max_digits=12, decimal_places=2)
        )
    ).filter(payable_sum__gt=0).order_by('-payable_sum')

    payable_reports = GuideReport.objects.filter(
        invoice_date__range=(start_date_str, end_date_str)
    ).annotate(
        amount_num=Cast('final_amount_due', output_field=DecimalField(max_digits=12, decimal_places=2)),
        guide_payable_sum=Coalesce(
            Sum(
                Cast('guide__guidereports__final_amount_due', 
                     output_field=DecimalField(max_digits=12, decimal_places=2)),
                filter=Q(
                    guide__guidereports__invoice_date__range=(start_date_str, end_date_str),
                    guide__guidereports__is_paid=False
                )
            ),
            0.0,
            output_field=DecimalField(max_digits=12, decimal_places=2)
        )
    ).order_by('-guide_payable_sum', '-amount_num')

    total_payable_fee = 0.0
    total_guide_fee = 0.0
    total_expense_fee = 0.0
    total_super_ann = 0.0

    for report in payable_reports:
        if report.is_paid:
            report.pay_status = 'paid'
        else:
            report.pay_status = 'payable'
            if report.final_amount_due:
                total_payable_fee += float(report.final_amount_due)
            if report.final_events_fee: 
                total_guide_fee += float(report.final_events_fee)
            if report.final_expenses_fee: 
                total_expense_fee += float(report.final_expenses_fee)
            if report.super_ann: 
                total_super_ann += float(report.super_ann)
        report.save()

    return render(request, 'joyadmin/payable_reports.html', {
        'payable_reports': payable_reports,
        'last_wed': last_wed,
        'until': until_date,
        'guides': guides,
        'total_payable_fee': total_payable_fee,
        'total_guide_fee': total_guide_fee,
        'total_expense_fee': total_expense_fee,
        'total_super_ann': total_super_ann
    })


@login_required
def unpaid_reports(request): 

    unpaid_reports = GuideReport.objects.filter(is_paid=False).order_by('-id')

    total_unpaid_fee = 0

    for report in unpaid_reports: 
        report.pay_status = 'unpaid'
        if report.final_amount_due:
            total_unpaid_fee += float(report.final_amount_due)
            report.save()
            
    guides = Guide.objects.all()

    return render(request, 'joyadmin/unpaid_reports.html', {'unpaid_reports': unpaid_reports, 'total_unpaid_fee': total_unpaid_fee, 'guides': guides})

@login_required
def paid_reports(request): 
    paid_reports = GuideReport.objects.filter(is_paid=True).order_by('-id')

    total_paid_fee = 0

    guides = Guide.objects.all()

    for report in paid_reports: 
        report.pay_status = 'paid'
        if report.final_amount_due: 
            total_paid_fee += float(report.final_amount_due)
            report.save()
    
    return render(request, 'joyadmin/paid_reports.html', {'paid_reports': paid_reports, 'guides': guides ,'total_paid_fee': total_paid_fee})


@login_required
def all_reports(request): 
    guidereports = GuideReport.objects.all().order_by('-id')

    guides = Guide.objects.all()

    total_all_fee = 0

    for report in guidereports: 
        if report.final_amount_due: 
            total_all_fee += float(report.final_amount_due)
            report.save()

    return render(request, 'joyadmin/all_reports.html', {'guidereports': guidereports, 'guides': guides, 'total_all_fee': total_all_fee})
