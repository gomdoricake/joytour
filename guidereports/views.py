from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse
from .models import Guide
from .forms import GuideReportForm

from django.shortcuts import redirect

@login_required
def index(request): 
    user = Guide.objects.get(name=request.user.username)
    return render(request, 'guidereports/index.html')

@login_required
def create_guidereport(request): 
    if request.method == 'POST': 
        form = GuideReportForm(request.POST)
        if form.is_valid(): 

            guide_report = form.save(commit=False)
            guide_report.guide = request.user
            guide_report.save()

            return redirect('mypage:mypage')
    else: 
        form = GuideReportForm()
    
    return render(request, 'guidereports/create_guidereport.html')
