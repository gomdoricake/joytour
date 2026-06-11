from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse
from .models import Guide, GuideReport
from .forms import GuideReportStep1Form, GuideReportStep2Form

from django.shortcuts import redirect

@login_required
def index(request): 
    user = Guide.objects.get(name=request.user.username)
    return render(request, 'guidereports/index.html')

def DetailView(request, pk): 
    guide_report = GuideReport.objects.get(pk=pk)
    return render(request, 'guidereports/detail.html', {'guide_report': guide_report})

@login_required
def guidereport_step1(request): 
    if request.method == 'POST': 
        form = GuideReportStep1Form(request.POST)
        if form.is_valid(): 
            
            report_date_obj = form.cleaned_data.get('report_date')
            request.session['step1_data'] = {
                'day_inbound': form.cleaned_data['day_inbound'], 
                'role': form.cleaned_data['role'],
                'report_date': report_date_obj.isoformat() if report_date_obj else None,            
            }
            return redirect('guidereports:guidereport_step2')
    else: 
        form = GuideReportStep1Form()
    
    return render(request, 'guidereports/guidereport_step1.html', {'form': form})

@login_required
def guidereport_step2(request): 
    step1_data = request.session.get('step1_data')

    dummy_instance = GuideReport(
        role=step1_data['role'], 
        day_inbound=step1_data['day_inbound'],
        report_date=step1_data['report_date']
    )
    
    if not step1_data: 
        return redirect('mypage:guidereport_step1')

    if request.method == 'POST': 
        form = GuideReportStep2Form(request.POST, instance=dummy_instance)
        if form.is_valid(): 

            guide_report = form.save(commit=False)

            guide_report.eventcode = form.cleaned_data.get('eventcode')
            print("eventcode: " + guide_report.eventcode)


            guide_report.day_inbound = step1_data['day_inbound']
            guide_report.role = step1_data['role']
            guide_report.report_date = step1_data['report_date']
            guide_report.guide = request.user.guide_profile

            guide_report.guide_fee = guide_report.calculate_fee()

            guide_report.save()
            del request.session['step1_data']

            return redirect('mypage:mypage')
    else: 
        form = GuideReportStep2Form(instance=dummy_instance)
    
    return render(request, 'guidereports/guidereport_step2.html', {'form': form})
