from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse
from ..models import *
from django.forms import inlineformset_factory
from ..forms import *

from datetime import datetime, date
from django.shortcuts import redirect

@login_required
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
                print("restuarant.expense: " + str(restaurant.expense))
                restaurant.save()
            
        guidereport.save()

    return redirect('guidereports:detail', guidereport.pk)    



@login_required
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
            guide_report.guide = request.user.guide_profile
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


EventFormSet = inlineformset_factory(
    GuideReport, 
    Event, 
    form=InboundEventForm, 
    extra=3,             
    can_delete=True  
)


@login_required
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

    if request.method == 'POST':
        formset = EventFormSet(request.POST, instance=guide_report)
        
        if formset.is_valid():            
            guide_report.save()

            main_data = request.session.get('main_data', {})
            main_data['guidereport_id'] = guide_report.id
            request.session['main_data'] = main_data

            inbound_data['guidereport_id'] = guide_report.id
            request.session['inbound_data'] = inbound_data 

            Event.objects.filter(guidereport_id=guide_report.id).delete()
            
            representative_date_str = ""
            representative_code = ""

            prefix = formset.prefix
            total_forms_count = int(request.POST.get(f'{prefix}-TOTAL_FORMS', 0))

            for i in range(total_forms_count): 
                report_date = request.POST.get(f'{prefix}-{i}-report_date')
                eventcode = request.POST.get(f'{prefix}-{i}-eventcode')
                hours_raw = request.POST.get(f'{prefix}-{i}-hours')
                overtime_raw = request.POST.get(f'{prefix}-{i}-overtime')
                is_delete = request.POST.get(f'{prefix}-{i}-DELETE')

                if is_delete or not report_date or not eventcode:
                    continue

                hours_value = None
                if hours_raw:
                    hours_raw = hours_raw.strip()
                    if hours_raw.upper() == 'AM/AS':
                        hours_value = 'AM/AS'  # CharField일 경우 문자열 그대로 저장
                    else:
                        try:
                            hours_value = hours_raw
                        except ValueError:
                            hours_value = 0
                else:
                    hours_value = 0
                
                overtime_value = 0
                if overtime_raw:
                    try:
                        overtime_value = float(overtime_raw.strip())
                    except ValueError:
                        overtime_value = 0

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
                        eventcode=eventcode,
                        hours=hours_value,
                        overtime=overtime_value
                    )
                except Exception as e:
                    print(f"이벤트 저장 중 에러 발생: {e}")
                    pass
                
            day_inbound_check = str(guide_report.day_inbound).upper().strip()
            if day_inbound_check == "INBOUND" and representative_date_str:
                if (guide_report.adt or 0) + (guide_report.tc or 0) + (guide_report.chd or 0) > 9: 
                    guide_report.group_code = f"{guide_report.agency_code}{representative_date_str}G"
                else: 
                    guide_report.group_code = f"{guide_report.agency_code}{representative_date_str}F"

            guide_report.save()

            request.session['inbound_events'] = {
                'guidereport_id': guide_report.id,
                'role': inbound_data['role'],
                'day_inbound': inbound_data.get('day_inbound'), 
                'agency_code': inbound_data['agency_code'],
                'adt': inbound_data['adt'],
                'tc': inbound_data['tc'],
                'chd': inbound_data['chd']
            }

            return redirect('guidereports:guidereport_inbound_restaurant_exp') 

    else:
        formset = EventFormSet(instance=guide_report)
    
    return render(request, 'guidereports/inbound/guidereport_inbound_events.html', {
        'formset': formset, 
        'guide_report': guide_report,
        'INBOUND_EVENTCODE': INBOUND_EVENTCODE
    })

RestaurantFormSet = inlineformset_factory(
    GuideReport, 
    RestaurantExp, 
    form=RestaurantExpForm, 
    extra=1,             
    can_delete=True  
)


@login_required
def guidereport_inbound_restaurant_exp(request): 
    inbound_events = request.session.get('inbound_events')

    if not inbound_events: 
        return redirect('guidereports:guidereport_inbound_events')
    
    report_id = inbound_events.get('guidereport_id')
    guide_report = get_object_or_404(GuideReport, id=report_id)

    if request.method == "POST": 
        formset = RestaurantFormSet(request.POST, instance=guide_report)

        if formset.is_valid(): 
            guide_report.save()

            main_data = request.session.get('main_data', {})
            main_data['guidereport_id'] = guide_report.id
            request.session['main_data'] = main_data

            RestaurantExp.objects.filter(guide_report_id=guide_report.id).delete()
            
            prefix = formset.prefix
            total_forms_count = int(request.POST.get(f'{prefix}-TOTAL_FORMS', 0))

            for i in range(total_forms_count): 
                report_date = request.POST.get(f'{prefix}-{i}-report_date')
                expense_type = request.POST.get(f'{prefix}-{i}-expense_type')  
                memo = request.POST.get(f'{prefix}-{i}-memo')
                is_delete = request.POST.get(f'{prefix}-{i}-DELETE') or request.POST.get(f'form-{i}-DELETE')

                print(f'---- RESTAURANT [Row {i}] Report Date: {report_date} ,Type: {expense_type}, Delete: {is_delete} ----')

                if expense_type and report_date and not is_delete: 
                    try: 
                        RestaurantExp.objects.create(
                            guide_report_id=guide_report.id,
                            report_date=report_date if report_date else None,
                            expense_type=expense_type, 
                            memo=memo
                        )
                        print(f"Restaurant 행 {i} 저장 성공")
                    except Exception as e: 
                        print(f"Restaurant 행 {i} 저장 실패: {e}")
                
            request.session['inbound_restaurant'] = inbound_events
            return redirect('guidereports:guidereport_inbound_attraction_exp') 

    else:
        formset = RestaurantFormSet(instance=guide_report)

    return render(request, 'guidereports/inbound/guidereport_inbound_restaurant_exp.html', {
        'formset': formset, 
        'guide_report': guide_report,
        'RESTAURANT_CHOICES': RESTAURANT_CHOICES
    })



AttractionFormSet = inlineformset_factory(
    GuideReport, 
    AttractionExp, 
    form=AttractionExpForm,
    extra=1,             
    can_delete=True  
)

@login_required
def guidereport_inbound_attraction_exp(request): 
    inbound_restaurant = request.session.get('inbound_restaurant')

    if not inbound_restaurant: 
        return redirect('guidereports:guidereport_inbound_restaurant_exp')
    
    report_id = inbound_restaurant.get('guidereport_id')
    guide_report = get_object_or_404(GuideReport, id=report_id)

    if request.method == "POST": 
        formset = AttractionFormSet(request.POST, instance=guide_report)
        guide_report.save()

        main_data = request.session.get('main_data', {})
        main_data['guidereport_id'] = guide_report.id
        request.session['main_data'] = main_data
        
        AttractionExp.objects.filter(guide_report_id=guide_report.id).delete()
        
        prefix = formset.prefix
        total_forms_count = int(request.POST.get(f'{prefix}-TOTAL_FORMS', 0))

        for i in range(total_forms_count): 
            report_date = request.POST.get(f'{prefix}-{i}-report_date')
            expense_type = request.POST.get(f'{prefix}-{i}-expense_type')
            memo = request.POST.get(f'{prefix}-{i}-memo') 
            is_delete = request.POST.get(f'{prefix}-{i}-DELETE') or request.POST.get(f'form-{i}-DELETE')

            if report_date and expense_type and not is_delete: 
                try: 
                    AttractionExp.objects.create(
                        guide_report_id=guide_report.id,
                        report_date=report_date if report_date else None,
                        expense_type=expense_type, 
                        memo = memo
                    )
                    print(f"Attraction 행 {i} 저장 성공")
                except Exception as e:
                    print(f"Attraction 행 {i} 저장 실패: {e}")
        
        request.session['inbound_attraction'] = inbound_restaurant
        
        
        if inbound_restaurant['role'] == 'GUIDE ONLY':
            return redirect('guidereports:guidereport_inbound_guide_exp')

        return redirect('guidereports:guidereport_inbound_fuel_exp') 

    else:
        formset = AttractionFormSet(instance=guide_report)

    return render(request, 'guidereports/inbound/guidereport_inbound_attraction_exp.html', {
        'formset': formset, 
        'guide_report': guide_report,
        'ATTRACTION_CHOICES': ATTRACTION_CHOICES
    })

FuelFormSet = inlineformset_factory(
    GuideReport, 
    FuelExp, 
    form=FuelExpForm,  
    extra=1,             
    can_delete=True  
)

@login_required
def guidereport_inbound_fuel_exp(request): 
    inbound_attraction = request.session.get('inbound_attraction')
    if not inbound_attraction: 
        return redirect('guidereports:guidereport_inbound_attraction_exp')
    
    report_id = inbound_attraction.get('guidereport_id')
    guide_report = get_object_or_404(GuideReport, id=report_id)

    if request.method == "POST": 
        formset = FuelFormSet(request.POST, instance=guide_report)

        if formset.is_valid():
            formset.save()
            
            request.session['inbound_fuel'] = inbound_attraction
            return redirect('guidereports:guidereport_inbound_guide_exp') 
        else:
            print("폼셋 유효성 검사 실패:", formset.errors)

    else:
        formset = FuelFormSet(instance=guide_report)

    return render(request, 'guidereports/inbound/guidereport_inbound_fuel_exp.html', {
        'formset': formset, 
        'guide_report': guide_report,
    })


GuideExpFormSet = inlineformset_factory(
    GuideReport, 
    GuideExp, 
    form=GuideExpForm,  
    extra=1,             
    can_delete=True  
)

@login_required
def guidereport_inbound_guide_exp(request): 

    inbound_fuel = request.session.get('inbound_fuel')
    print("inbound_fuel: " + str(inbound_fuel['role']))
    if not inbound_fuel: 
        return redirect('guidereports:guidereport_inbound_fuel_exp')
    
    report_id = inbound_fuel.get('guidereport_id')
    guide_report = get_object_or_404(GuideReport, id=report_id)
    if request.method == "POST":

        day_inbound_check = str(guide_report.day_inbound).upper().strip()
        first_event = guide_report.events.order_by('id').first()
        today_str = datetime.strptime(str(first_event.report_date), '%Y-%m-%d').strftime('%d%m%y')

        F_or_G = ""

        adt = guide_report.adt or 0
        chd = guide_report.chd or 0
        tc = guide_report.tc or 0

        if adt + chd + tc <= 9:
            F_or_G = "F"
        else: 
            F_or_G = "G"

        guide_report.group_code = f"{guide_report.agency_code}{today_str}{F_or_G}"

        prefix = 'expenses'
        
        total_forms_raw = request.POST.get(f'{prefix}-TOTAL_FORMS', '0')
        total_forms = int(total_forms_raw)

        GuideExp.objects.filter(guide_report=guide_report).delete()

        wash_added = False


        if total_forms > 0:
            
            for i in range(total_forms):
                e_type = request.POST.get(f'{prefix}-{i}-expense_type')
                e_val = request.POST.get(f'{prefix}-{i}-expense')
                memo = request.POST.get(f'{prefix}-{i}-memo')

                print("e_val: " + str(e_val))
                if e_val == '':
                    continue
                print("e_val2: " + str(e_val))


                if e_type == "WASH": 
                    if wash_added: 
                        continue
                    wash_added = True
                                    
                if e_type:
                    GuideExp.objects.create(
                        guide_report=guide_report,
                        expense_type=e_type,
                        expense=float(e_val) if e_val else 0.0, 
                        memo=memo
                    )
        today = date.today()
        guide_report.invoice_date = today

        guide_report.save()

        return redirect('guidereports:guidereport_inbound_summary')   
    else:
        formset = GuideExpFormSet(instance=guide_report)

    CHOICES = ""

    print("inbound_fuel['role']: " + str(inbound_fuel['role']))
    
    if inbound_fuel['role'] == 'GUIDE ONLY': 
        CHOICES = GUIDE_ONLY_EXPENSE_CHOICES
    else: 
        CHOICES = EXPENSE_CHOICES
    
    print("CHOICES: " + str(CHOICES))
    
    fuel_ids = list(FuelExp.objects.filter(guide_report=guide_report).values_list('id', flat=True))
    restaurant_ids = list(RestaurantExp.objects.filter(guide_report=guide_report).values_list('id', flat=True))
    attraction_ids = list(AttractionExp.objects.filter(guide_report=guide_report).values_list('id', flat=True))
    guide_exp_ids = list(GuideExp.objects.filter(guide_report=guide_report).values_list('id', flat=True))

    event = Event.objects.filter(guidereport=guide_report).first()
    event_id = event.id if event else None

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
        }
    }

    request.session.modified = True

    return render(request, 'guidereports/inbound/guidereport_inbound_guide_exp.html', {
        'formset': formset, 
        'guide_report': guide_report,
        'role': inbound_fuel['role'],
        'EXPENSE_CHOICES': CHOICES
    })

@login_required
def guidereport_inbound_summary(request): 
    session_data = request.session.get('guide_exp') or request.session.get('inbound_fuel')
    
    if not session_data:
        return redirect('guidereports:guidereport_inbound_agency')
        
    report_id = session_data.get('guidereport_id')
    guide_report = get_object_or_404(GuideReport, id=report_id)
    event = Event.objects.filter(guidereport=guide_report).first()
    events = Event.objects.filter(guidereport=guide_report)

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
    restaurant_expenses = RestaurantExp.objects.filter(guide_report=guide_report)  
    attraction_expenses = AttractionExp.objects.filter(guide_report=guide_report)  
    
    total_fuel = sum(item.expense for item in fuel_expenses if item.expense)
    total_guide = sum(item.expense for item in guide_expenses if item.expense)
    total_restaurant = sum(item.expense for item in restaurant_expenses if item.expense)  
    total_attraction = sum(item.expense for item in attraction_expenses if item.expense) 
    
    grand_total = total_fuel + total_guide + total_restaurant + total_attraction

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

    super_ann = event_fee * 0.115
    guide_report.super_ann = super_ann

    expense_fee = 0
    for expense in expenses: 
        fee = float(expense.expense)
        expense_fee += fee
        final_amount_due += fee

    guide_report.final_expenses_fee = expense_fee
    
    fuel_fee = 0
    for fuel in fuels:
        if fuel.expense: fee = float(fuel.expense)
        fuel_fee += fee

    guide_report.final_fuels_fee = fuel_fee
    final_amount_due += fuel_fee

    overtime = 0
    for event in guide_report.events.all(): 
        if event.overtime is not None:
            overtime += int(event.overtime)
    
    event_fee += (overtime * 30)

    final_expense += (overtime * 30)
    guide_report.final_amount_due = final_amount_due

    all_reports = GuideReport.objects.filter(guide=guide_report.guide).order_by('id')
    invoice_number = list(all_reports.values_list('id', flat=True)).index(guide_report.id) + 1

    guide_report.invoice_number = invoice_number
    guide_report.save()

    if request.method == 'POST':
        if 'main_data' in request.session: del request.session['main_data']
        if 'day_data' in request.session: del request.session['day_data']
        if 'day_fuel' in request.session: del request.session['day_fuel']
        if 'guide_exp' in request.session: del request.session['guide_exp']
        
        return redirect('guidereports:detail', pk=guide_report.id)

    overtimes = []
    for event in events:
        if event.overtime is not None:
            overtimes.append(event.overtime * 30)
        else: 
            overtimes.append(0)
    
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
        'event_data': event_data,
    }
    return render(request, 'guidereports/inbound/guidereport_inbound_summary.html', context)