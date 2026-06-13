from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse
from .models import Guide, GuideReport, GuideExp
from django.forms import inlineformset_factory
from .forms import GuideReportMainForm, GuideReportDayForm, GuideReportInboundForm

from django.shortcuts import redirect

@login_required
def index(request): 
    user = Guide.objects.get(name=request.user.username)
    return render(request, 'guidereports/index.html')

def DetailView(request, pk): 
    guide_report = GuideReport.objects.get(pk=pk)
    return render(request, 'guidereports/detail.html', {'guide_report': guide_report})

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

            guide_report.eventcode = form.cleaned_data.get('eventcode')
            print("eventcode: " + guide_report.eventcode)

            guide_report.day_inbound = main_data['day_inbound']
            guide_report.role = main_data['role']
            guide_report.guide = request.user.guide_profile

            request.session['day_data'] = {
                'role': main_data['role'],
                'day_inbound': main_data['day_inbound'], 
                'eventcode': form.cleaned_data['eventcode'], 
                'report_date': form.cleaned_data['report_date'].strftime('%Y-%m-%d')            
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

    final_instance = GuideReport(
        role=day_data['role'],
        day_inbound=day_data.get('day_inbound'), 
        eventcode=day_data['eventcode'],
        report_date=day_data['report_date'], 
        guide=request.user.guide_profile
    )

    if request.method == 'POST':
        formset = ExpenseFormSet(request.POST, instance=final_instance)
        
        if formset.is_valid():
            final_instance.guide_fee = final_instance.calculate_fee()
            final_instance.save()
            
            instances = formset.save(commit=False)

            for instance in instances: 
                if instance.expense and instance.expense > 0: 
                    print('exp: ' , instance.expense)
                    instance.guide_report = final_instance
                    instance.id = None
                    instance.save()

            formset.save()

            if 'main_data' in request.session: del request.session['main_data']
            if 'day_data' in request.session: del request.session['day_data']

            return redirect('mypage:mypage')
    
    else:
        formset = ExpenseFormSet(instance=final_instance)

    return render(request, 'guidereports/guidereport_day_guide_exp.html', {
        'formset': formset, 'final_instance': final_instance
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

            guide_report.guide_fee = guide_report.calculate_fee()

            guide_report.save()
            del request.session['main_data']

            return redirect('mypage:mypage')
    else: 
        form = GuideReportDayForm(instance=dummy_instance)
    
    return render(request, 'guidereports/guidereport_day.html', {'form': form})
