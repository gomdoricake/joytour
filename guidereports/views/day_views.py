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
                'event_id': event.id,
                'role': main_data['role'],
                'day_inbound': main_data['day_inbound'], 
                'today_str': today_str     
            }
            return redirect('guidereports:guidereport_day_guide_exp')
    else: 
        form = GuideReportDayForm(instance=instance, initial=initial_data)
    
    return render(request, 'guidereports/day/guidereport_day.html', {'form': form})


GuideExpFormSet = inlineformset_factory(
    GuideReport, 
    GuideExp, 
    fields=['id', 'expense_type', 'expense'], 
    extra=1,             
    can_delete=True  
)

@login_required
def guidereport_day_guide_exp(request):
    day_data = request.session.get('day_data')
    if not day_data:
        return redirect('guidereports:guidereport_main')
    
    event = get_object_or_404(Event, id=day_data['event_id'])

    if request.method == 'POST':
        if event.guidereport:
            final_instance = event.guidereport
        else:
            final_instance = GuideReport(guide=request.user.guide_profile)
            
        final_instance.role = day_data['role']
        final_instance.day_inbound = day_data.get('day_inbound')

        formset = GuideExpFormSet(request.POST, instance=final_instance)
        
        if formset.is_valid():
            today_str = day_data.get('today_str')
            if not today_str and event.report_date:
                today_str = datetime.strptime(day_data['report_date'], '%Y-%m-%d').strftime('%d%m%y')

            day_inbound_check = str(final_instance.day_inbound).upper().strip()
            if day_inbound_check == "DAY" and today_str and event.eventcode:
                final_instance.group_code = 'J' + today_str + event.eventcode
            
            final_instance.save()

            GuideExp.objects.filter(guide_report=final_instance).delete()

            prefix = formset.prefix
            total_forms_count = int(request.POST.get(f'{prefix}-TOTAL_FORMS', 0))

            wash_added = False

            for i in range(total_forms_count):
                exp_type = request.POST.get(f'{prefix}-{i}-expense_type')
                exp_val_raw = request.POST.get(f'{prefix}-{i}-expense')
                memo = request.POST.get(f'{prefix}-{i}-memo')
                is_delete = request.POST.get(f'form-{i}-DELETE') 

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

            today = datetime.date.today()
            final_instance.invoice_date = today
            final_instance.save()

            if 'main_data' in request.session: del request.session['main_data']
            if 'day_data' in request.session: del request.session['day_data']
            
            return redirect('guidereports:detail', pk=final_instance.id) 
    else:
        final_instance = event.guidereport if event.guidereport else GuideReport(
            role=day_data['role'],
            day_inbound=day_data.get('day_inbound'),
            guide=request.user.guide_profile
        )
        formset = GuideExpFormSet(instance=final_instance)

    return render(request, 'guidereports/day/guidereport_day_guide_exp.html', {
        'formset': formset, 
        'final_instance': final_instance,
        'eventcode': event.eventcode,
        'report_date': event.report_date.strftime("%Y-%m-%d") if event.report_date else day_data.get('report_date')
    })


