from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse
from .models import *
from django.forms import inlineformset_factory
from .forms import *

from django.shortcuts import redirect

@login_required
def index(request): 
    user = Guide.objects.get(name=request.user.username)
    return render(request, 'guidereports/index.html')

@login_required
def DetailView(request, pk):
    guide_report = get_object_or_404(GuideReport, pk=pk)
    events = guide_report.events.all() 
    
    for event in events: 
        print("event: ", event.eventcode)
        print('reportdate: ', event.report_date)
        
    return render(request, 'guidereports/detail.html', {
        'guide_report': guide_report,
        'events': events,                           
    })

@login_required
def guidereport_main(request): 
    if request.method == 'POST': 
        form = GuideReportMainForm(request.POST)
        if form.is_valid(): 
            
            request.session['main_data'] = {
                'day_inbound': form.cleaned_data['day_inbound'], 
                'role': form.cleaned_data['role'],
            }

            if form.cleaned_data['day_inbound'] == 'DAY': 
                return redirect('guidereports:guidereport_day')
            if form.cleaned_data['day_inbound'] == 'INBOUND': 
                return redirect('guidereports:guidereport_inbound_agency')            

    else: 
        form = GuideReportMainForm()
    
    return render(request, 'guidereports/guidereport_main.html', {'form': form})

@login_required
def guidereport_day(request): 
    main_data = request.session.get('main_data')

    dummy_instance = GuideReport(
        role=main_data['role'], 
        day_inbound=main_data['day_inbound'],
    )

    if not main_data: 
        return redirect('mypage:guidereport_main')

    if request.method == 'POST': 
        form = GuideReportDayForm(request.POST, instance=dummy_instance)
        if form.is_valid(): 

            guide_report = form.save(commit=False)

            eventcode = form.cleaned_data['eventcode']
            report_date = form.cleaned_data['report_date'].strftime('%Y-%m-%d')
            today_str = form.cleaned_data['report_date'].strftime('%d%m%y')

            guide_report.day_inbound = main_data['day_inbound']
            guide_report.role = main_data['role']
            guide_report.guide = request.user.guide_profile

            guide_report.save()

            event = Event.objects.create(eventcode=eventcode, report_date=report_date, guidereport=guide_report)

            
            request.session['day_data'] = {
                'event_id': event.id,
                'role': main_data['role'],
                'day_inbound': main_data['day_inbound'], 
                'today_str': today_str     
            }



            return redirect('guidereports:guidereport_day_guide_exp')
    else: 
        form = GuideReportDayForm(instance=dummy_instance)
    
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

            for i in range(total_forms_count):
                exp_type = request.POST.get(f'{prefix}-{i}-expense_type')
                exp_val_raw = request.POST.get(f'{prefix}-{i}-expense')
                is_delete = request.POST.get(f'form-{i}-DELETE') 

                print(f"--- [Form Row {i}] Type: {exp_type}, Value: {exp_val_raw}, Delete: {is_delete} ---")

                if exp_type and exp_val_raw and not is_delete:
                    try:
                        exp_val = float(exp_val_raw)
                        if exp_val > 0:
                            GuideExp.objects.create(
                                guide_report=final_instance,
                                expense_type=exp_type,
                                expense=exp_val,
                            )

                    except ValueError:
                        pass 

            event.guidereport = final_instance
            event.save()

            if 'main_data' in request.session: del request.session['main_data']
            if 'day_data' in request.session: del request.session['day_data']
            
            return redirect('mypage:mypage') 
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


def guidereport_inbound_agency(request): 
    main_data = request.session.get('main_data')

    dummy_instance = GuideReport(
        role=main_data['role'], 
        day_inbound=main_data['day_inbound'],
    )

    if not main_data: 
        return redirect('mypage:guidereport_main')

    if request.method == 'POST': 
        form = AgencyPaxForm(request.POST, instance=dummy_instance)
        if form.is_valid(): 

            guide_report = form.save(commit=False)
            
            request.session['inbound_data'] = {
                'role': main_data['role'],
                'day_inbound': main_data['day_inbound'], 
                'agency_code': form.cleaned_data['agency_code'],
                'adt': form.cleaned_data['adt'],
                'tc': form.cleaned_data['chd'], 
                'chd': guide_report.chd
            }

            return redirect('guidereports:guidereport_inbound_events')
    else: 
        form = AgencyPaxForm(instance=dummy_instance)
    
    return render(request, 'guidereports/inbound/guidereport_inbound_agency.html', {'form': form})


EventFormSet = inlineformset_factory(
    GuideReport, 
    Event, 
    form=InboundEventForm, 
    extra=1,             
    can_delete=True  
)


@login_required
def guidereport_inbound_events(request): 
    inbound_data = request.session.get('inbound_data')

    if not inbound_data:
        return redirect('guidereports:guidereport_main')
    
    report_id = inbound_data.get('guide_report_id')
    if report_id:
        guide_report = get_object_or_404(GuideReport, id=report_id)
    else:
        guide_report = GuideReport(
            role=inbound_data['role'],
            day_inbound=inbound_data.get('day_inbound'), 
            agency_code=inbound_data['agency_code'],
            guide=request.user.guide_profile,
            adt=inbound_data['adt'],
            tc=inbound_data['tc'],
            chd=inbound_data['chd']
        )

    if request.method == 'POST':
        formset = EventFormSet(request.POST, instance=guide_report)
        
        if formset.is_valid():            
            guide_report.save()

            inbound_data['guide_report_id'] = guide_report.id
            request.session['inbound_data'] = inbound_data 

            Event.objects.filter(guidereport_id=guide_report.id).delete()
            
            representative_date_str = ""
            representative_code = ""

            prefix = formset.prefix
            total_forms_count = int(request.POST.get(f'{prefix}-TOTAL_FORMS', 0))

            for i in range(total_forms_count): 
                report_date = request.POST.get(f'{prefix}-{i}-report_date')
                eventcode = request.POST.get(f'{prefix}-{i}-eventcode')
                is_delete = request.POST.get(f'{prefix}-{i}-DELETE')

                print(f'---- EVENT [Form Row {i}] Date: {report_date}, Code: {eventcode}, Delete: {is_delete} ----')

                if report_date and eventcode and not is_delete: 
                    if not representative_date_str and not representative_code:
                        try:
                            representative_date_str = datetime.strptime(report_date, '%Y-%m-%d').strftime('%d%m%y')
                            representative_code = str(eventcode).strip()
                        except Exception:
                            pass

                    try: 
                        Event.objects.create(
                            guidereport_id=guide_report.id,
                            report_date=report_date, 
                            eventcode=eventcode
                        )
                    except ValueError: 
                        pass
                
            day_inbound_check = str(guide_report.day_inbound).upper().strip()
            if day_inbound_check == "INBOUND" and representative_date_str:
                if guide_report.adt + guide_report.tc + guide_report.chd > 9: 
                    guide_report.group_code = f"{guide_report.agency_code}{representative_date_str}G"
                else: 
                    guide_report.group_code = f"{guide_report.agency_code}{representative_date_str}F"

            guide_report.save()

            return redirect('guidereports:guidereport_inbound_restaurant_exp') 

    else:
        formset = EventFormSet(instance=guide_report)

    return render(request, 'guidereports/inbound/guidereport_inbound_events.html', {
        'formset': formset, 
        'guide_report': guide_report,
    })

# RestaurantFormSet = inlineformset_factory(
#     GuideReport, 
#     RestaurantExp, 
#     form=RestaurantExpForm, 
#     extra=1,             
#     can_delete=True  
# )


# def guidereport_inbound_restaurant_exp(request): 
#     return render(request, 'guidereports/inbound/guidereport_inbound_restaurant_exp.html')