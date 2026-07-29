from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.http import HttpResponse
from ..models import *
from django.forms import inlineformset_factory
from ..forms import *

from datetime import datetime, date
from django.shortcuts import redirect

@login_required
@never_cache
def update_attraction(request, pk): 
    guidereport = get_object_or_404(GuideReport, pk=pk)
    
    if request.user.username != 'admin':
        return HttpResponseForbidden("권한이 없습니다.")

    if request.method == 'POST': 
        for attraction in guidereport.attractions.all():
            adt_val = request.POST.get(f'adt_{attraction.pk}')
            chd_val = request.POST.get(f'chd_{attraction.pk}')
            tc_val = request.POST.get(f'tc_{attraction.pk}')
            tg_val = request.POST.get(f'tg_{attraction.pk}')
            tod_val = request.POST.get(f'tod_{attraction.pk}')

            if adt_val is not None:
                attraction.adt = int(adt_val) if adt_val else 0
                attraction.chd = int(chd_val) if chd_val else 0
                attraction.tc = int(tc_val) if tc_val else 0
                attraction.tg = int(tg_val) if tg_val else 0
                attraction.tod = int(tod_val) if tod_val else 0
                
                attraction.expense = 30 * attraction.adt + 20 * attraction.chd + 10 * attraction.tc + 5 * attraction.tg

                attraction.save()

        guidereport.save()
            
    return redirect('guidereports:detail', guidereport.pk)    


@login_required
@never_cache
def update_restaurant(request, pk): 
    guidereport = get_object_or_404(GuideReport, pk=pk)
    
    if request.user.username != 'admin':
        return HttpResponseForbidden("권한이 없습니다.")

    if request.method == 'POST': 
        for restaurant in guidereport.restaurants.all():
            adt_val = request.POST.get(f'adt_{restaurant.pk}')
            chd_val = request.POST.get(f'chd_{restaurant.pk}')
            tc_val = request.POST.get(f'tc_{restaurant.pk}')
            tg_val = request.POST.get(f'tg_{restaurant.pk}')
            dr_val = request.POST.get(f'dr_{restaurant.pk}')

            if adt_val is not None:
                restaurant.adt = int(adt_val) if adt_val else 0
                restaurant.chd = int(chd_val) if chd_val else 0
                restaurant.tc = int(tc_val) if tc_val else 0
                restaurant.tg = int(tg_val) if tg_val else 0
                restaurant.dr = int(dr_val) if dr_val else 0
                
                restaurant.expense = 25 * restaurant.adt + 20 * restaurant.chd + 10 * restaurant.tc + 5 * restaurant.tg
                restaurant.save()
            
        guidereport.save()

    return redirect('guidereports:detail', guidereport.pk)    



@login_required
@never_cache
def guidereport_inbound_agency(request): 
    main_data = request.session.get('main_data')
    if not main_data: 
        return redirect('guidereports:guidereport_main') 

    report_id = main_data.get('guidereport_id')
    if report_id:
        instance = get_object_or_404(GuideReport, id=report_id)
    else:
        instance = GuideReport(role=main_data['role'], day_inbound=main_data['day_inbound'])

    if request.method == 'POST': 
        form = AgencyPaxForm(request.POST, instance=instance)
        if form.is_valid(): 
            guide_report = form.save(commit=False)
            guide_report.guide = guide_report.guide if request.user.username == 'admin' else request.user.guide_profile
            guide_report.save()

            main_data['guidereport_id'] = guide_report.id
            request.session['main_data'] = main_data
            
            request.session['inbound_data'] = {
                'guidereport_id': guide_report.id,
                'role': main_data['role'],
                'day_inbound': main_data['day_inbound'], 
                'agency_code': form.cleaned_data['agency_code'],
                'adt': form.cleaned_data['adt'],
                'tc': form.cleaned_data['tc'], 
                'chd': form.cleaned_data['chd']
            }
            return redirect('guidereports:guidereport_inbound_events')
    else: 
        form = AgencyPaxForm(instance=instance)
    
    return render(request, 'guidereports/inbound/guidereport_inbound_agency.html', {'form': form, 'AGENCY_CHOICES': AGENCY_CHOICES})


@login_required
@never_cache
def guidereport_inbound_events(request): 
    inbound_data = request.session.get('inbound_data')

    if not inbound_data:
        return redirect('guidereports:guidereport_main')
    
    report_id = inbound_data.get('guidereport_id')
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
     
    if guide_report.events.count() == 0:
        extra = 3
    else: 
        extra = 0
    
    EventFormSet = inlineformset_factory(
        GuideReport, 
        Event, 
        form=InboundEventForm, 
        extra=extra,             
        can_delete=True  
    )

    if request.method == 'POST':
        formset = EventFormSet(request.POST, instance=guide_report)
        
        if formset.is_valid():            
            guide_report.save()

            events = formset.save()

            first_event = guide_report.events.order_by('id').first()
            if first_event and first_event.report_date:
                try:
                    if isinstance(first_event.report_date, str):
                        representative_date_str = datetime.strptime(first_event.report_date, '%Y-%m-%d').strftime('%d%m%y')
                    else:
                        representative_date_str = first_event.report_date.strftime('%d%m%y')
                    
                    day_inbound_check = str(guide_report.day_inbound).upper().strip()
                    if day_inbound_check == "INBOUND":
                        pax_count = (guide_report.adt or 0) + (guide_report.tc or 0) + (guide_report.chd or 0)
                        suffix = "G" if pax_count > 9 else "F"
                        guide_report.group_code = f"{guide_report.agency_code}{representative_date_str}{suffix}"
                        guide_report.save()
                except Exception as e:
                    print(f"Group Code 생성 실패: {e}")

            inbound_data['guidereport_id'] = guide_report.id
            request.session['inbound_data'] = inbound_data 
            request.session['inbound_events'] = inbound_data

            return redirect('guidereports:guidereport_inbound_restaurant_exp') 
    else:
        formset = EventFormSet(instance=guide_report)
    
    return render(request, 'guidereports/inbound/guidereport_inbound_events.html', {
        'formset': formset, 
        'guide_report': guide_report,
        'INBOUND_EVENTCODE': INBOUND_EVENTCODE
    })


@login_required
@never_cache
def guidereport_inbound_restaurant_exp(request): 
    inbound_events = request.session.get('inbound_events')

    if not inbound_events: 
        return redirect('guidereports:guidereport_inbound_events')
    
    report_id = inbound_events.get('guidereport_id')
    guide_report = get_object_or_404(GuideReport, id=report_id)

    events = guide_report.events.all()
    initial_data = []
    for event in events:
        initial_data.append({'report_date': event.report_date}) 
        initial_data.append({'report_date': event.report_date}) 

    if guide_report.restaurants.count() == 0:
        extra = events.count() * 2
    else:
        extra = 0

    RestaurantFormSet = inlineformset_factory(
        GuideReport, 
        RestaurantExp, 
        form=RestaurantExpForm, 
        extra=extra,             
        can_delete=True  
    )

    if request.method == "POST": 
        formset = RestaurantFormSet(request.POST, instance=guide_report, initial=initial_data)

        if formset.is_valid(): 
            guide_report.save()
            formset.save() 
            
            request.session['inbound_restaurant'] = inbound_events
            return redirect('guidereports:guidereport_inbound_attraction_exp') 
    else:
        formset = RestaurantFormSet(instance=guide_report, initial=initial_data)

    return render(request, 'guidereports/inbound/guidereport_inbound_restaurant_exp.html', {
        'formset': formset, 
        'guide_report': guide_report,
        'RESTAURANT_CHOICES': RESTAURANT_CHOICES
    })


@login_required
@never_cache  
def guidereport_inbound_attraction_exp(request): 
    inbound_restaurant = request.session.get('inbound_restaurant')

    if not inbound_restaurant: 
        return redirect('guidereports:guidereport_inbound_restaurant_exp')
    
    report_id = inbound_restaurant.get('guidereport_id')
    guide_report = get_object_or_404(GuideReport, id=report_id)

    events = guide_report.events.all()
    initial_data = []
    for event in events: 
        initial_data.append({'report_date': event.report_date})
    
    if guide_report.attractions.count() == 0:
        extra = events.count()
    else:
        extra = 0

    AttractionFormSet = inlineformset_factory(
        GuideReport, 
        AttractionExp, 
        form=AttractionExpForm,
        extra=extra,             
        can_delete=True  
    )

    if request.method == "POST": 
        formset = AttractionFormSet(request.POST, instance=guide_report, initial=initial_data)
        
        if formset.is_valid():
            guide_report.save()
            formset.save()

            main_data = request.session.get('main_data', {})
            main_data['guidereport_id'] = guide_report.id
            request.session['main_data'] = main_data
            
            request.session['inbound_attraction'] = inbound_restaurant
            
            return redirect('guidereports:guidereport_inbound_fuel_exp') 
        else:
            print("Attraction 폼셋 유효성 검사 실패:", formset.errors)

    else:
        formset = AttractionFormSet(instance=guide_report, initial=initial_data)

    return render(request, 'guidereports/inbound/guidereport_inbound_attraction_exp.html', {
        'formset': formset, 
        'guide_report': guide_report,
        'ATTRACTION_CHOICES': ATTRACTION_CHOICES
    })


@login_required
@never_cache  
def guidereport_inbound_fuel_exp(request): 
    inbound_attraction = request.session.get('inbound_attraction')

    if not inbound_attraction: 
        return redirect('guidereports:guidereport_inbound_attraction_exp')
        
    report_id = inbound_attraction.get('guidereport_id')
    guide_report = get_object_or_404(GuideReport, id=report_id)

    events = guide_report.events.all()
    initial_data = []
    for event in events:
        if event.report_date:
            initial_data.append({'report_date': event.report_date})

    FuelFormSet = inlineformset_factory(
        GuideReport, 
        FuelExp, 
        form=FuelExpForm,  
        extra=events.count(),             
        can_delete=True  
    )


    if request.method == "POST": 
        formset = FuelFormSet(request.POST, instance=guide_report, initial=initial_data)

        if formset.is_valid():
            guide_report.save()
            
            formset.save()
            
            request.session['inbound_fuel'] = inbound_attraction
            return redirect('guidereports:guidereport_inbound_guide_exp') 
        else:
            print("Fuel 폼셋 유효성 검사 실패:", formset.errors)

    else:
        formset = FuelFormSet(instance=guide_report, initial=initial_data)

    return render(request, 'guidereports/inbound/guidereport_inbound_fuel_exp.html', {
        'formset': formset, 
        'guide_report': guide_report,
    })


@login_required
@never_cache
def guidereport_inbound_guide_exp(request): 
    inbound_fuel = request.session.get('inbound_fuel') or request.session.get('inbound_attraction')
    
    if not inbound_fuel: 
        return redirect('guidereports:guidereport_inbound_attraction_exp')
    
    report_id = inbound_fuel.get('guidereport_id')
    guide_report = get_object_or_404(GuideReport, id=report_id)

    if guide_report.expenses.count() == 0:
        extra = 1
    else: 
        extra = 0
    
    GuideExpFormSet = inlineformset_factory(
        GuideReport, 
        GuideExp, 
        form=GuideExpForm,  
        extra=extra,             
        can_delete=True  
    )

    if request.method == "POST":
        formset = GuideExpFormSet(request.POST, instance=guide_report)
        
        if formset.is_valid():
            instances = formset.save(commit=False)
            
            for obj in formset.deleted_objects:
                if obj.pk:
                    obj.delete()

            wash_exists_in_db = guide_report.expenses.filter(expense_type="WASH").exists()

            for instance in instances:
                if not instance.expense:
                    continue
                
                if instance.expense_type == "WASH" and not instance.pk:
                    if wash_exists_in_db:
                        continue
                    wash_exists_in_db = True
                
                instance.guide_report = guide_report
                instance.save()

            formset.save_m2m()

            first_event = guide_report.events.order_by('id').first()
            if first_event and first_event.report_date:
                try:
                    if isinstance(first_event.report_date, str):
                        today_str = datetime.strptime(first_event.report_date, '%d-%m-%y').strftime('%d%m%y')
                    else:
                        today_str = first_event.report_date.strftime('%d%m%y')
                    
                    adt = guide_report.adt or 0
                    chd = guide_report.chd or 0
                    tc = guide_report.tc or 0
                    F_or_G = "F" if (adt + chd + tc) <= 9 else "G"
                    
                    guide_report.group_code = f"{guide_report.agency_code}{today_str}{F_or_G}"
                except Exception as e:
                    print(f"Group Code 변환 에러: {e}")
                    
            guide_report.invoice_date = date.today()
            guide_report.save()

            return redirect('guidereports:guidereport_inbound_summary')
        else:
            print("GuideExp 폼셋 유효성 검사 실패:", formset.errors)
            
    else:
        formset = GuideExpFormSet(instance=guide_report)

    fuel_ids = list(guide_report.fuels.values_list('id', flat=True))
    restaurant_ids = list(guide_report.restaurants.values_list('id', flat=True))
    source_attractions = guide_report.attractions.values_list('id', flat=True) if hasattr(guide_report, 'attractions') else []
    attraction_ids = list(source_attractions)
    guide_exp_ids = list(guide_report.expenses.values_list('id', flat=True))

    first_event = guide_report.events.order_by('id').first()
    event_id = first_event.id if first_event else None

    request.session['guide_exp'] = {
        'guidereport_id': guide_report.id,
        'role': inbound_fuel.get('role', guide_report.role),
        'day_inbound': inbound_fuel.get('day_inbound', guide_report.day_inbound), 
        'event_id': event_id,
        'fuel_ids': fuel_ids,
        'restaurant_ids': restaurant_ids,
        'attraction_ids': attraction_ids,
        'guide_exp_ids': guide_exp_ids,
        'summary_snapshot': {
            'group_code': guide_report.group_code,
            'has_fuel': len(fuel_ids) > 0,
            'has_restaurant': len(restaurant_ids) > 0,
            'has_attraction': len(attraction_ids) > 0,
            'has_guide_exp': len(guide_exp_ids) > 0,
        },
        'GUIDE_ONLY_EXPENSE_CHOICES': GUIDE_ONLY_EXPENSE_CHOICES,
        'EXPENSE_CHOICES': EXPENSE_CHOICES
    }
    request.session.modified = True

    return render(request, 'guidereports/inbound/guidereport_inbound_guide_exp.html', {
        'formset': formset, 
        'guide_report': guide_report,
        'role': inbound_fuel.get('role'),
        'EXPENSE_CHOICES': EXPENSE_CHOICES,
        'GUIDE_ONLY_EXPENSE_CHOICES': GUIDE_ONLY_EXPENSE_CHOICES
    })


@login_required
@never_cache
def guidereport_inbound_summary(request): 
    session_data = (
        request.session.get('guide_exp') or 
        request.session.get('inbound_fuel') or 
        request.session.get('inbound_attraction')
    )
    
    if not session_data:
        return redirect('guidereports:guidereport_inbound_agency')
        
    report_id = session_data.get('guidereport_id')
    guide_report = get_object_or_404(GuideReport, id=report_id)
    
    events = guide_report.events.all()
    expenses = guide_report.expenses.all()
    fuels = guide_report.fuels.all()
    
    fuel_expenses = fuels
    guide_expenses = expenses
    restaurant_expenses = guide_report.restaurants.all()
    attraction_expenses = guide_report.attractions.all()

    event = events.first()
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
    
    total_fuel = sum(item.expense for item in fuel_expenses if item.expense)
    total_guide = sum(item.expense for item in guide_expenses if item.expense)
    total_restaurant = sum(item.expense for item in restaurant_expenses if item.expense)  
    total_attraction = sum(item.expense for item in attraction_expenses if item.expense) 
    
    grand_total = total_fuel + total_guide + total_restaurant + total_attraction

    final_amount_due = 0 
    event_fee = 0
    expense_fee = 0
    fuel_fee = 0
    overtime = 0

    for e in events: 
        fee = float(e.guide_fee or 0)
        event_fee += fee
    guide_report.final_events_fee = event_fee
    guide_report.super_ann = (event_fee / 1.1) * 0.12
    


    for exp in expenses: 
        fee = float(exp.expense or 0)
        expense_fee += fee

    for e in events: 
        if e.overtime is not None:
            overtime += int(e.overtime)
    
    expense_fee += (overtime * 30)
    guide_report.final_expenses_fee = expense_fee
    
    for fuel in fuels:
        if fuel.expense: 
            fuel_fee += float(fuel.expense)
    guide_report.final_fuels_fee = fuel_fee

    final_amount_due = event_fee + expense_fee + fuel_fee
    guide_report.final_amount_due = final_amount_due

    all_reports = GuideReport.objects.filter(guide=guide_report.guide).order_by('id')
    guide_report.invoice_number = GuideReport.objects.filter(invoice_number__isnull=False).count() + 1
    guide_report.save()

    print("super_ann: " + str(guide_report.super_ann))


    if request.method == 'POST':
        session_keys_to_delete = [
            'main_data', 'day_data', 'day_fuel', 'guide_exp', 
            'inbound_data', 'inbound_events', 'inbound_restaurant', 'inbound_attraction', 'inbound_fuel'
        ]
        for key in session_keys_to_delete:
            if key in request.session: 
                del request.session[key]

        return redirect('guidereports:detail', pk=guide_report.id)

    overtimes = []
    for e in events:
        if e.overtime is not None and e.overtime > 0:
            overtimes.append({
                'report_date': e.report_date, 
                'hours': e.overtime, 
                'amount': f"{float(e.overtime * 30):.1f}"
            })
    
    context = {
        'guide_report': guide_report,
        'event': event,
        'events': events,
        'report_date': report_date_str,
        'fuel_expenses': fuel_expenses,
        'guide_expenses': guide_expenses,
        'restaurant_expenses': restaurant_expenses,  
        'attraction_expenses': attraction_expenses,  
        'total_fuel': total_fuel,
        'total_guide': total_guide,
        'total_restaurant': total_restaurant,          
        'total_attraction': total_attraction,          
        'grand_total': grand_total,
        'event_fee': event_fee, 
        'expense_fee': expense_fee, 
        'fuel_fee': fuel_fee,
        'final_amount_due': final_amount_due, 
        'overtimes': overtimes,
    }
    return render(request, 'guidereports/inbound/guidereport_inbound_summary.html', context)