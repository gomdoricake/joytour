from django import template
from django.apps import apps
from datetime import datetime, date, timedelta

register = template.Library()


@register.filter(name='count_payable')
def count_payable(pay_status): 
    GuideReport = apps.get_model('guidereports', 'GuideReport')

    payable_guides = GuideReport.objects.filter(pay_status=pay_status)

    count = payable_guides.count()
    
    return count

    
@register.filter(name='sort_payable')
def sort_payable(guide, pay_status):

    today = date.today() 
    today_weekday = today.weekday()

    sub_days = 0

    # wednesday
    sub_days = -1 * today_weekday - 5
    last_wed = today + timedelta(days=sub_days)

    guidereports = guide.guidereports.all()

    # if today is wed/thurs/fri
    if 2<= today_weekday <= 4:
        # till this tuesday
        if today_weekday == 2: sub_days = -1
        if today_weekday == 3: sub_days = -2
        if today_weekday == 4: sub_days = -3
        
        this_tue= today + timedelta(days=sub_days)
        payable_reports = guidereports.filter(invoice_date__range=(str(last_wed), str(this_tue))).order_by('-id')

    else: 
        payable_reports = guidereports.filter(invoice_date__range=(str(last_wed), str(today))).order_by('-id')


    counts = payable_reports.count()

    return_list = []
    final_amount_due, final_events_fee, final_expenses_fee = 0, 0, 0

    for report in payable_reports: 
        if report.is_paid != 'paid': 
            if report.final_amount_due: 
                final_amount_due += float(report.final_amount_due)
            if report.final_expenses_fee: 
                final_expenses_fee += float(report.final_expenses_fee)
            if report.final_events_fee: 
                final_events_fee += float(report.final_events_fee)

    total_super = final_events_fee / 1.1 * 0.12
    final_amount_due += total_super

    return_list.append(
        (
        guide.name, 
        counts,
        f"${final_events_fee:.2f}",
        f"${final_expenses_fee:.2f}",
        f"${total_super:.2f}",
        f"${final_amount_due:.2f}",
        )
    )
    
    return return_list


@register.filter(name='sort_unpaid')
def sort_unpaid(guide, pay_status):
    unpaid_reports = guide.guidereports.filter(is_paid=False)
    counts = unpaid_reports.count()
    final_amount_due = 0

    return_list = []

    for report in unpaid_reports:
        if report.final_amount_due:  
            final_amount_due += float(report.final_amount_due)
        
    return_list.append(
        (
        guide.name, 
        counts,
        f"${final_amount_due:.2f}"
        )
    )
    
    return return_list

@register.filter(name='sort_paid')
def sort_paid(guide, pay_status): 
    paid_reports = guide.guidereports.filter(is_paid=True)
    counts = paid_reports.count()
    final_amount_due = 0

    return_list = []

    for report in paid_reports:
        if report.final_amount_due:  
            final_amount_due += float(report.final_amount_due)
        
    return_list.append(
        (
        guide.name, 
        counts,
        f"${final_amount_due:.2f}"
        )
    )
    
    return return_list


@register.filter(name='all_reports')
def all_reports(guide): 
    all_reports = guide.guidereports.all()
    counts = all_reports.count()
    final_amount_due = 0

    return_list = []

    for report in all_reports:
        if report.final_amount_due:  
            final_amount_due += float(report.final_amount_due)
        
    return_list.append(
        (
        guide.name, 
        counts,
        f"${final_amount_due:.2f}"
        )
    )

    return return_list

 


    
