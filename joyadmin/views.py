from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from guides.models import Guide
from guidereports.models import GuideReport
from datetime import date, timedelta

@login_required
def index(request): 
    admin = Guide.objects.get(user=request.user)
    return render(request, 'joyadmin/index.html', {'admin': admin})

from django.db.models import Sum, DecimalField
from django.db.models.functions import Cast, Coalesce

@login_required
def payable_reports(request): 
    all_reports = GuideReport.objects.all()
    today = date.today() 
    today_weekday = today.weekday()

    sub_days = 0

    guides = Guide.objects.annotate(
        max_amount=Coalesce(
            Sum(
                Cast('guidereports__final_amount_due', 
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                ), 
            ),
            0.0, 
            output_field=DecimalField(max_digits=12, decimal_places=2)
        )
    ).order_by('max_amount')

    # wednesday
    sub_days = -1 * today_weekday - 5
    last_wed = today + timedelta(days=sub_days)

    total_payable_fee = 0  

    # if today is wed/thurs/fri
    if 2<= today_weekday <= 4:
        # till this tuesday
        if today_weekday == 2: sub_days = -1
        if today_weekday == 3: sub_days = -2
        if today_weekday == 4: sub_days = -3
        
        this_tue= today + timedelta(days=sub_days)
        payable_reports = GuideReport.objects.filter(invoice_date__range=(str(last_wed), str(this_tue))).order_by('-id')
        
        for report in payable_reports: 
            if report.is_paid:
                report.pay_status = 'paid'
                report.save()
            else: 
                total_payable_fee += float(report.final_amount_due)
                report.pay_status = 'payable'
                report.save()

        return render(request, 'joyadmin/payable_reports.html', {'payable_reports': payable_reports, 
                    'last_wed': last_wed, 'until': this_tue, 'guides': guides, 'total_payable_fee': total_payable_fee})

    
    payable_reports = GuideReport.objects.filter(invoice_date__range=(str(last_wed), str(today))).order_by('-id')

    for report in payable_reports: 
        if report.is_paid: 
            report.pay_status = 'paid'
        else: 
            report.pay_status = 'payable'
        
        if report.final_amount_due: 
            total_payable_fee += float(report.final_amount_due)
            report.save()
        else: report.save()

    return render(request, 'joyadmin/payable_reports.html', {'payable_reports': payable_reports, 
                    'last_wed': last_wed, 'until': today, 'guides': guides, 'total_payable_fee': total_payable_fee})


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
