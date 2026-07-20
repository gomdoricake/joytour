from django import template
from guidereports.models import GuideReport
from datetime import datetime, date, timedelta

register = template.Library()

@register.filter(name='sort_payable')
def sort_payable(guide, pay_status):

    today = date.today() 
    today_weekday = today.weekday()

    sub_days = 0

    # wednesday
    sub_days = -1 * today_weekday - 5
    last_wed = today + timedelta(days=sub_days)

    payable_reports = guide.guidereports.filter(invoice_date__range=(str(last_wed), str(today)))
    counts = payable_reports.count()
    final_amount_due = 0

    return_list = []

    for report in payable_reports: 
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

    print("final_amount_due: " + str(final_amount_due))
    
    return return_list



    
