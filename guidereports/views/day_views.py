from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse
from ..models import *
from django.forms import inlineformset_factory
from ..forms import *

import datetime
from django.shortcuts import redirect


@login_required
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
            guide_report.guide = request.user.guide_profile
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


FuelFormSet = inlineformset_factory(
    GuideReport, 
    FuelExp, 
    form=FuelExpForm,  
    extra=1,             
    can_delete=True  
)

@login_required
def guidereport_day_fuel_exp(request): 
    day_data = request.session.get('day_data')
    if not day_data:
        return redirect('guidereports:guidereport_day')
    
    report_id = day_data.get('guidereport_id')
    guide_report = get_object_or_404(GuideReport, id=report_id)

    if request.method == "POST": 
        formset = FuelFormSet(request.POST, instance=guide_report)

        if formset.is_valid():
            formset.save()
            
            request.session['day_fuel'] = day_data
            return redirect('guidereports:guidereport_day_guide_exp') 
        else:
            print("폼셋 유효성 검사 실패:", formset.errors)

    else:
        formset = FuelFormSet(instance=guide_report)

    return render(request, 'guidereports/day/guidereport_day_fuel_exp.html', {
        'formset': formset, 
        'guide_report': guide_report,
    })


GuideExpFormSet = inlineformset_factory(
    GuideReport, 
    GuideExp, 
    fields=['id', 'expense_type', 'expense', 'memo'], 
    extra=1,             
    can_delete=True  
)


@login_required
def guidereport_day_guide_exp(request):
    day_fuel = request.session.get('day_fuel')
    if not day_fuel:
        return redirect('guidereports:guidereport_day')
    
    report_id = day_fuel.get('guidereport_id')
    guide_report = get_object_or_404(GuideReport, id=report_id)
    event = get_object_or_404(Event, guidereport=guide_report)

    if request.method == 'POST':
        final_instance = guide_report
        final_instance.role = day_fuel.get('role')
        final_instance.day_inbound = day_fuel.get('day_inbound')

        formset = GuideExpFormSet(request.POST, instance=final_instance)
        
        if formset.is_valid():
            today_str = day_fuel.get('today_str')
            if not today_str and event.report_date:
                if isinstance(event.report_date, str):
                    today_str = datetime.strptime(event.report_date, '%Y-%m-%d').strftime('%d%m%y')
                else:
                    today_str = event.report_date.strftime('%d%m%y')

            day_inbound_check = str(final_instance.day_inbound).upper().strip()
            if day_inbound_check == "DAY" and today_str and event.eventcode:
                final_instance.group_code = 'J' + today_str + event.eventcode
            
            final_instance.invoice_date = datetime.date.today()
            final_instance.save()

            GuideExp.objects.filter(guide_report=final_instance).delete()

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
                            GuideExp.objects.create(
                                guide_report=final_instance,
                                expense_type=exp_type,
                                expense=exp_val,
                                memo=memo
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
        report_date_str = day_data.get('report_date')

    return render(request, 'guidereports/day/guidereport_day_guide_exp.html', {
        'formset': formset, 
        'final_instance': final_instance,
        'eventcode': event.eventcode,
        'report_date': report_date_str
    })

@login_required
def guidereport_day_summary(request): 
    session_data = request.session.get('guide_exp') or request.session.get('day_fuel')
    
    if not session_data:
        return redirect('guidereports:guidereport_day')
        
    report_id = session_data.get('guidereport_id')
    guide_report = get_object_or_404(GuideReport, id=report_id)
    event = Event.objects.filter(guidereport=guide_report).first()

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
    
    fuel_expenses = FuelExp.objects.filter(guide_report=guide_report)
    guide_expenses = GuideExp.objects.filter(guide_report=guide_report)
    
    total_fuel = sum(item.expense for item in fuel_expenses if item.expense)
    total_guide = sum(item.expense for item in guide_expenses if item.expense)
    grand_total = total_fuel + total_guide

    if request.method == 'POST':
        if 'main_data' in request.session: del request.session['main_data']
        if 'day_data' in request.session: del request.session['day_data']
        if 'day_fuel' in request.session: del request.session['day_fuel']
        if 'guide_exp' in request.session: del request.session['guide_exp']
        
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
    }
    return render(request, 'guidereports/day/guidereport_day_summary.html', context)