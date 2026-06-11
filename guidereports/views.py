from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse
from .models import Guide, GuideReport
from .forms import GuideReportStep1Form

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

            guide_report = form.save(commit=False)
            guide_report.guide = request.user.guide_profile
            guide_report.save()

            return redirect('guidereports:guidereport_step2', pk=guide_report.pk)
    else: 
        form = GuideReportStep1Form()
    
    return render(request, 'guidereports/guidereport_step1.html', {'form': form})

@login_required
def guidereport_step2(request, pk): 
    guide_report = get_object_or_404(GuideReport, pk=pk)
    if request.method == 'POST': 
        form = GuideReportStep2Form(request.POST, instance=guide_report)
        if form.is_valid(): 
            guide_report = form.save(commit=False)
            guide_report.save()

            return redirect('mypage:mypage')
    else: 
        form = GuideReportStep2Form(instance=guide_report)
    
    return render(request, 'guidereports/guidereport_step2.html', {'form': form, 'report': guide_report})
