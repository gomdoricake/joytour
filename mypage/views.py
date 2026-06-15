from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from guides.models import Guide
from guides.forms import GuideProfileForm
from guidereports.forms import GuideReportMainForm
from django.views import generic
from guidereports.models import GuideReport

@login_required
def login_redirect_view(request): 
    if request.user.username == 'admin': 
        return redirect('mypage:admin')
    else: 
        return redirect('mypage:mypage')

@login_required
def admin(request): 
    return render(request, 'mypage/admin.html')

@login_required
def mypage(request): 
    if request.user.username == 'admin': 
        return redirect('mypage:admin')
    try: 
        current_guide = request.user.guide_profile
        guide_reports = GuideReport.objects.filter(guide=current_guide).order_by('-id')
        context = {"guide": current_guide, "user": request.user, "guide_reports": guide_reports}
        return render(request, "mypage/index.html", context)
    except AttributeError: 
        if request.method == "POST": 
            form = GuideProfileForm(request.POST)
            if form.is_valid(): 
                new_guide = form.save(commit=False)
                new_guide.user = request.user
                new_guide.save()

                return redirect('mypage:mypage')
        else: 
            form = GuideProfileForm()
        
        return render(request, "mypage/create_profile.html", {"form": form})
       
@login_required
def create_report(request): 
    if request.method == "POST": 
        guide = Guide.objects.get(user=request.user)
        form = GuideReportMainForm(request.POST)
        if form.is_valid(): 
            new_report = form.save(commit=False)
            new_report.guide = guide
            new_report.save()
            return redirect('mypage:mypage')
    else: 
        guide = Guide.objects.get(user=request.user)
        form = GuideReportMainForm(initial={'guide': guide})
        return render(request, "mypage/create_report.html", {"form": form})
