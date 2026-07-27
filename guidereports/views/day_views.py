from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.http import HttpResponse
from ..models import *
from django.forms import inlineformset_factory
from ..forms import *

import datetime
from datetime import date
from django.shortcuts import redirect


@login_required
@never_cache
def guidereport_day(request): 
    main_data = request.session.get('main_data')
    if not main_data: 
        return redirect('guidereports:guidereport_main') 

    report_id = main_data.get('guidereport_id')
    
    initial_data = {}

    role = main_data['role']
    if role == '12 SEAT':
        DAY_EVENTCODE = DAY_EVENTCODE_12SEAT
    if role == '21 SEAT': 
        DAY_EVENTCODE = DAY_EVENTCODE_21SEAT
    if role == '53 SEAT': 
        DAY_EVENTCODE = DAY_EVENTCODE_53SEAT
    elif role == 'GUIDE ONLY': 
        DAY_EVENTCODE = DAY_EVENTCODE_GUIDE_ONLY


    if report_id:
        instance = get_object_or_404(GuideReport, id=report_id)
        event_instance = Event.objects.filter(guidereport=instance).first()
        
        if event_instance:
            initial_data['eventcode'] = event_instance.eventcode
            
            if event_instance.report_date:
                initial_data['report_date'] = event_instance.report_date.strftime('%Y-%m-%d')
    else:
        instance = GuideReport(role=main_data['role'], day_inbound=main_data['day_inbound'])

    if request.method == 'POST': 
        form = GuideReportDayForm(request.POST, instance=instance)
        if form.is_valid(): 
            guide_report = form.save(commit=False)
            guide_report.day_inbound = main_data['day_inbound']
            guide_report.role = main_data['role']
            guide_report.guide = guide_report.guide  if request.user.username == 'admin' else request.user.guide_profile
            guide_report.save()

            eventcode = form.cleaned_data['eventcode']
            report_date = form.cleaned_data['report_date'].strftime('%Y-%m-%d')
            today_str = form.cleaned_data['report_date'].strftime('%d%m%y')

            event, created = Event.objects.update_or_create(
                guidereport=guide_report,
                defaults={'eventcode': eventcode, 'report_date': report_date}
            )

            main_data['guidereport_id'] = guide_report.id
            request.session['main_data'] = main_data

            request.session['day_data'] = {
                'guidereport_id': guide_report.id,
                'event_id': event.id,
                'role': main_data['role'],
                'day_inbound': main_data['day_inbound'], 
                'today_str': today_str     
            }
            return redirect('guidereports:guidereport_day_fuel_exp')
    else: 
        form = GuideReportDayForm(instance=instance, initial=initial_data)
    
    return render(request, 'guidereports/day/guidereport_day.html', {'form': form, 'DAY_EVENTCODE': DAY_EVENTCODE})


@login_required
@never_cache
def guidereport_day_fuel_exp(request): 
    day_data = request.session.get('day_data')

    if not day_data:
        return redirect('guidereports:guidereport_day')
    
    report_id = day_data.get('guidereport_id')
    guide_report = get_object_or_404(GuideReport, id=report_id)

    events = guide_report.events.all()
    
    initial_data = []
    for event in events: 
        initial_data.append({'report_date': event.report_date})
    
    if guide_report.fuels.count() == 0:
        extra = 1
    else: 
        extra = 0

    FuelFormSet = inlineformset_factory(
        GuideReport, 
        FuelExp, 
        form=FuelExpForm,  
        extra=extra,             
        can_delete=True  
    )

    if request.method == "POST": 
        formset = FuelFormSet(request.POST, instance=guide_report, initial=initial_data)

        if formset.is_valid():
            formset.save()
            
            request.session['day_fuel'] = day_data
            return redirect('guidereports:guidereport_day_guide_exp') 
        else:
            print("폼셋 유효성 검사 실패:", formset.errors)

    else:
        formset = FuelFormSet(instance=guide_report, initial=initial_data)

    return render(request, 'guidereports/day/guidereport_day_fuel_exp.html', {
        'formset': formset, 
        'guide_report': guide_report,
    })

from django.db import transaction


@login_required
@never_cache
def guidereport_day_guide_exp(request):
    day_fuel = request.session.get('day_fuel')
    if not day_fuel:
        return redirect('guidereports:guidereport_day')
    
    report_id = day_fuel.get('guidereport_id')
    guide_report = get_object_or_404(GuideReport, id=report_id)
    event = get_object_or_404(Event, guidereport=guide_report)

    if guide_report.expenses.count() == 0:
        extra = 1
    else:
        extra = 0

    GuideExpFormSet = inlineformset_factory(
        GuideReport, 
        GuideExp, 
        fields=['id', 'expense_type', 'expense', 'memo'], 
        extra=extra,             
        can_delete=True  
    )

    if request.method == 'POST':
        final_instance = guide_report
        final_instance.role = day_fuel.get('role')
        final_instance.day_inbound = day_fuel.get('day_inbound')

        formset = GuideExpFormSet(request.POST, request.FILES, instance=final_instance)
        
        if formset.is_valid():
            today_str = day_fuel.get('today_str')
            if not today_str and event.report_date:
                if isinstance(event.report_date, str):
                    today_str = datetime.datetime.strptime(event.report_date, '%Y-%m-%d').strftime('%d%m%y')
                else:
                    today_str = event.report_date.strftime('%d%m%y')

            day_inbound_check = str(final_instance.day_inbound).upper().strip()
            if day_inbound_check == "DAY" and today_str and event.eventcode:
                final_instance.group_code = 'J' + today_str + event.eventcode
            
            final_instance.invoice_date = datetime.date.today()

            with transaction.atomic(): 
                final_instance.save()

                existing_expenses = GuideExp.objects.filter(guide_report=final_instance)

                for old_exp in existing_expenses: 
                    for old_img in old_exp.receipt_images.all():
                        old_img.image_file.delete(save=False) 
                    old_exp.delete()

                prefix = formset.prefix
                total_forms_count = int(request.POST.get(f'{prefix}-TOTAL_FORMS', 0))
                wash_added = False

                for i in range(total_forms_count):
                    exp_type = request.POST.get(f'{prefix}-{i}-expense_type')
                    exp_val_raw = request.POST.get(f'{prefix}-{i}-expense')
                    memo = request.POST.get(f'{prefix}-{i}-memo')
                    is_delete = request.POST.get(f'{prefix}-{i}-DELETE') 

                    if exp_type and exp_val_raw and not is_delete:
                        try:
                            if exp_type == 'WASH':
                                if wash_added:
                                    continue
                                wash_added = True

                            exp_val = float(exp_val_raw)
                            if exp_val > 0:
                                new_exp = GuideExp.objects.create(
                                    guide_report=final_instance,
                                    expense_type=exp_type,
                                    expense=exp_val,
                                    memo=memo
                                )

                                receipt_files = request.FILES.getlist(f'receipt_images_{i}')

                                for file in receipt_files: 
                                    ReceiptImage.objects.create(
                                        guide_exp=new_exp, 
                                        image_file=file
                                    )
                        except ValueError:
                            pass 

                event.guidereport = final_instance
                event.save()

                request.session['guide_exp'] = {
                    'guidereport_id': guide_report.id,
                    'event_id': event.id,
                    'role': day_fuel['role'],
                    'day_inbound': day_fuel['day_inbound'], 
                    'today_str': today_str     
                }
            
            return redirect('guidereports:guidereport_day_summary') 
            
    else:
        final_instance = guide_report
        formset = GuideExpFormSet(instance=final_instance)

    if event.report_date:
        report_date_str = event.report_date if isinstance(event.report_date, str) else event.report_date.strftime("%Y-%m-%d")
    else:
        report_date_str = day_fuel.get('report_date')

    if day_fuel.get('role') == 'GUIDE ONLY':
        CHOICES = GUIDE_ONLY_EXPENSE_CHOICES
    else:
        CHOICES = EXPENSE_CHOICES
    
    return render(request, 'guidereports/day/guidereport_day_guide_exp.html', {
        'formset': formset, 
        'final_instance': final_instance,
        'eventcode': event.eventcode,
        'report_date': report_date_str, 
        'EXPENSE_CHOICES': CHOICES,
    })


@login_required
@never_cache
def guidereport_day_summary(request): 
    session_data = (
        request.session.get('guide_exp') or 
        request.session.get('day_fuel') or
        request.session.get('day_data')
    )
    
    if not session_data:
        return redirect('guidereports:guidereport_day')
        
    report_id = session_data.get('guidereport_id')
    guide_report = get_object_or_404(GuideReport, id=report_id)
    
    event = guide_report.events.first()  
    fuel_expenses = guide_report.fuels.all()  
    guide_expenses = guide_report.expenses.all()

    report_date_str = "-"
    if event and event.report_date:
        if isinstance(event.report_date, str):
            report_date_str = event.report_date
        else:
            report_date_str = event.report_date.strftime("%Y-%m-%d")
    elif session_data.get('today_str'):
        try:
            report_date_str = datetime.strptime(session_data.get('today_str'), '%d%m%y').strftime('%Y-%m-%d')
        except ValueError:
            pass
    
    total_fuel = float(sum(item.expense for item in fuel_expenses if item.expense))
    total_guide = float(sum(item.expense for item in guide_expenses if item.expense))
    
    
    base_fee = float(event.guide_fee) if (event and event.guide_fee) else 0.0
    
    grand_total = base_fee + total_guide

    guide_report.super_ann = base_fee / 1.1 * 0.12
    guide_report.final_events_fee = str(base_fee)
    guide_report.final_fuels_fee = str(total_fuel)
    guide_report.final_expenses_fee = str(total_guide)  
    guide_report.final_amount_due = str(grand_total)
    guide_report.invoice_number = GuideReport.objects.filter(invoice_number__isnull=False).count() + 1
    
    guide_report.invoice_date = date.today()
    guide_report.save()

    if request.method == 'POST':
        session_keys_to_delete = [
            'main_data', 'day_data', 'day_fuel', 'guide_exp', 'inbound_data'
        ]
        for key in session_keys_to_delete:
            if key in request.session: 
                del request.session[key]
        
        return redirect('guidereports:detail', pk=guide_report.id)

    context = {
        'guide_report': guide_report,
        'event': event,
        'report_date': report_date_str,
        'fuel_expenses': fuel_expenses,
        'guide_expenses': guide_expenses,
        'total_fuel': total_fuel,
        'total_guide': total_guide,
        'grand_total': grand_total,
        'invoice_number': guide_report.invoice_number,
        'super_ann': guide_report.super_ann,
        'invoice_date': guide_report.invoice_date,
    }
    return render(request, 'guidereports/day/guidereport_day_summary.html', context)