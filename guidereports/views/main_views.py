from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse
from ..models import *
from django.forms import inlineformset_factory
from ..forms import *

import datetime
from django.shortcuts import redirect

@login_required
def index(request): 
    guidereports = GuideReport.objects.all().order_by('-id')
    return render(request, 'guidereports/index.html', {'guidereports': guidereports})

@login_required
def DetailView(request, pk):
    guide_report = get_object_or_404(GuideReport, pk=pk)
    events = guide_report.events.all()
    expenses = guide_report.expenses.all()
    fuels = guide_report.fuels.all()

    final_amount_due = 0 

    event_fee = 0
    for event in events: 
        fee = float(event.guide_fee)
        event_fee += fee
        final_amount_due += fee
    
    guide_report.final_events_fee = event_fee

    super_ann = event_fee * 0.12
    guide_report.super_ann = super_ann

    expense_fee = 0
    for expense in expenses: 
        fee = float(expense.expense)
        expense_fee += fee
        final_amount_due += fee

    guide_report.final_expenses_fee = expense_fee
    
    fuel_fee = 0
    for fuel in fuels: 
        fee = float(fuel.expense)
        fuel_fee += fee

    guide_report.final_fuels_fee = fuel_fee
    guide_report.final_amount_due = final_amount_due

    all_reports = GuideReport.objects.filter(guide=guide_report.guide).order_by('id')
    invoice_number = list(all_reports.values_list('id', flat=True)).index(guide_report.id) + 1

    guide_report.invoice_number = invoice_number
    guide_report.save()
        
    return render(request, 'guidereports/detail.html', {
        'guide_report': guide_report,
        'events': events,
        'event_fee': event_fee, 
        'expense_fee': expense_fee, 
        'fuel_fee': fuel_fee,
        'final_amount_due': final_amount_due, 
        'super_ann': super_ann,         
        'invoice_number': invoice_number       
    })


@login_required
def guidereport_confirm(request, pk): 
    if request.method == 'POST': 
        guide_report = get_object_or_404(GuideReport, id=pk)
        guide_report.is_confirmed = not guide_report.is_confirmed
        guide_report.save()

    return redirect('guidereports:detail', pk=pk)
    

@login_required
def update_guidereport(request, pk): 
    guidereport = get_object_or_404(GuideReport, pk=pk)
    
    request.session['main_data'] = {
        'guidereport_id': guidereport.id, 
        'day_inbound': guidereport.day_inbound,
        'role': guidereport.role,
    }
    
    if guidereport.day_inbound == 'INBOUND': 
        request.session['inbound_data'] = {
            'guidereport_id': guidereport.id,
            'role': guidereport.role,
            'day_inbound': guidereport.day_inbound, 
            'agency_code': guidereport.agency_code,
            'adt': guidereport.adt,
            'tc': guidereport.tc, 
            'chd': guidereport.chd
        }
    return redirect('guidereports:guidereport_main')


@login_required
def guidereport_main(request): 
    if request.method == 'POST': 
        form = GuideReportMainForm(request.POST)
        if form.is_valid(): 
            existing_data = request.session.get('main_data', {})

            existing_data['day_inbound'] = form.cleaned_data['day_inbound']
            existing_data['role'] = form.cleaned_data['role']

            request.session['main_data'] = existing_data

            if form.cleaned_data['day_inbound'] == 'DAY': 
                return redirect('guidereports:guidereport_day')
            if form.cleaned_data['day_inbound'] == 'INBOUND': 
                return redirect('guidereports:guidereport_inbound_agency')            

    else: 
        saved_main_data = request.session.get('main_data')

        if saved_main_data:
            form = GuideReportMainForm(initial=saved_main_data)
        else:
            form = GuideReportMainForm()
    
    return render(request, 'guidereports/guidereport_main.html', {'form': form})


