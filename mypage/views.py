from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from guides.models import Guide
from guides.forms import GuideProfileForm
from guidereports.forms import GuideReportMainForm
from django.views import generic
from guidereports.models import GuideReport
import datetime
from dateutil.relativedelta import relativedelta
    

@login_required
def login_redirect_view(request): 
    if request.user.username == 'admin':
        return redirect('joyadmin:index')
    else: 
        return redirect('mypage:index')

def review_grade(guide_id):
    guide = Guide.objects.get(id=guide_id)
    current_grade = guide.grade
    init_training_date = guide.init_training_date
        
    months, today = 0, datetime.date.today()

    if guide.is_sponsored: 
        guide.grade = 1
        guide.save()
        return 1

    while True: 
        if init_training_date + relativedelta(months=months) > today: 
            break
        months += 1

    if months <= 9: 
        guide.grade = 1
    else: 
        months -= 10
        guide.grade = int(months / 12) + 2

    guide.save()
    return guide.grade

@login_required
def index(request): 
    if request.user.username == 'admin': 
        return redirect('joyadmin:index')
    try: 
        current_guide = request.user.guide_profile
        guide_reports = GuideReport.objects.filter(guide=current_guide).order_by('-id')
        review_grade(current_guide.id)
        context = {"guide": current_guide, "user": request.user, "guide_reports": guide_reports}
        return render(request, "mypage/index.html", context)
    except AttributeError: 
        if request.method == "POST": 
            form = GuideProfileForm(request.POST)
            if form.is_valid(): 
                new_guide = form.save(commit=False)
                new_guide.user = request.user
                new_guide.save()

                return redirect('mypage:index')
        else: 
            form = GuideProfileForm()
        
        return render(request, "mypage/create_profile.html", {"form": form})

@login_required 
def update_mypage(request, pk):
    guide = get_object_or_404(Guide, pk=pk)
    if request.method == 'POST': 
        form = GuideProfileForm(request.POST, instance=guide)
        
        if form.is_valid(): 
            form.save()
            return redirect('mypage:index')
    else: 
        form = GuideProfileForm(instance=guide)
    
    return render(request, 'mypage/create_profile.html', {'form': form})        

@login_required
def create_report(request): 
    if request.method == "POST": 
        guide = Guide.objects.get(user=request.user)
        form = GuideReportMainForm(request.POST)
        if form.is_valid(): 
            new_report = form.save(commit=False)
            new_report.guide = guide
            new_report.save()
            return redirect('mypage:index')
    else: 
        guide = Guide.objects.get(user=request.user)
        form = GuideReportMainForm(initial={'guide': guide})
        return render(request, "mypage/create_report.html", {"form": form})
