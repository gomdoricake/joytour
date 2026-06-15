from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse
from .models import Guide, GuideReport, GuideExp, Event
from django.forms import inlineformset_factory
from .forms import GuideReportMainForm, GuideReportDayForm, GuideReportInboundForm

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
                return redirect('guidereports:guidereport_inbound')            

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
    
    return render(request, 'guidereports/guidereport_day.html', {'form': form})


ExpenseFormSet = inlineformset_factory(
    GuideReport, 
    GuideExp, 
    fields=['expense_type', 'expense'], 
    extra=1,             
    can_delete=True  
)

@login_required
def guidereport_day_guide_exp(request):


    day_data = request.session.get('day_data')
    if not day_data:
        return redirect('guidereports:guidereport_main')
    
    event = Event.objects.get(id=day_data['event_id'])


    final_instance = GuideReport(
        role=day_data['role'],
        day_inbound=day_data.get('day_inbound'), 
        guide=request.user.guide_profile,
    )

    if request.method == 'POST':
        formset = ExpenseFormSet(request.POST, instance=final_instance)
        
        if formset.is_valid():
            final_instance.final_guide_fee = final_instance.calculate_fee()
            
            today_str = day_data.get('today_str')
            if not today_str and event.report_date:
                from datetime import datetime
                today_str = datetime.strptime(day_data['report_date'], '%Y-%m-%d').strftime('%d%m%y')

            day_inbound_check = str(final_instance.day_inbound).upper().strip()
            if day_inbound_check == "DAY" and today_str and event.eventcode:
                final_instance.group_code = 'J' + today_str + event.eventcode
            
            
            final_instance.save()

            event.guidereport = final_instance

            event.save()

            expenses = formset.save(commit=False)
            for expense in expenses:
                if expense.expense and expense.expense > 0:
                    expense.guide_report = final_instance
                    expense.save()
            
            formset.save_m2m()
            for deleted_obj in formset.deleted_objects:
                deleted_obj.delete()

            if 'main_data' in request.session: del request.session['main_data']
            if 'day_data' in request.session: del request.session['day_data']
            
            return redirect('mypage:mypage') 


    else:
        formset = ExpenseFormSet(instance=final_instance)


    return render(request, 'guidereports/guidereport_day_guide_exp.html', {
        'formset': formset, 
        'final_instance': final_instance,
        'combined_eventcode': day_data.get('eventcode', ''),
    })

@login_required
def guidereport_inbound(request): 
    main_data = request.session.get('main_data')

    dummy_instance = GuideReport(
        role=main_data['role'], 
        day_inbound=main_data['day_inbound'],
    )
    
    if not main_data: 
        return redirect('mypage:guidereport_main')

    if request.method == 'POST': 
        form = GuideReportInboundForm(request.POST, instance=dummy_instance)
        if form.is_valid(): 

            guide_report = form.save(commit=False)

            guide_report.eventcode = form.cleaned_data.get('eventcode')
            print("eventcode: " + guide_report.eventcode)


            guide_report.day_inbound = main_data['day_inbound']
            guide_report.role = main_data['role']
            guide_report.guide = request.user.guide_profile

            guide_report.final_guide_fee = guide_report.calculate_fee()

            guide_report.save()
            del request.session['main_data']

            return redirect('mypage:mypage')
    else: 
        form = GuideReportDayForm(instance=dummy_instance)
    
    return render(request, 'guidereports/guidereport_day.html', {'form': form})


