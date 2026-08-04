from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from guides.models import Guide
from guides.forms import GuideProfileForm
from guidereports.forms import GuideReportMainForm
from django.views import generic
from guidereports.models import GuideReport
import datetime
from dateutil.relativedelta import relativedelta
from django.http import HttpResponseBadRequest

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
    
    if not init_training_date: 
        guide.grade = 0
        guide.save()
        return 0

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
    if request.session.get('guidereport_id', '') != '':
        del request.session['guidereport_id']
    if request.session.get('main_data', '') != '': 
        del request.session['main_data']
    if request.session.get('inbound_data', '') != '':
        del request.session['inbound_data']
    if request.session.get('day_data', '') != '':  
        del request.session['day_data']
    if request.session.get('fuel_temp_list', '') != '': 
        del request.session['fuel_temp_list']
    if request.session.get('s3_fuel_temp_list', '') != '': 
        del request.session['s3_fuel_temp_list']
    if request.session.get('exp_temp_list', '') != '': 
        del request.session['exp_temp_list']
    if request.session.get('s3_exp_temp_list', '') != '': 
        del request.session['s3_exp_temp_list']


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

@login_required
def confirmed_reports(request, pk): 

    guide = Guide.objects.get(pk=pk)
    guidereports = guide.guidereports
    not_paid_reports = guidereports.filter(is_paid=False)
    confirmed_reports = not_paid_reports.filter(is_confirmed=True)

    return render(request, 'mypage/confirmed_reports.html', {'confirmed_reports': confirmed_reports, 'guide': guide})
    

@login_required
def unpaid_reports(request, pk): 
    
    guide = Guide.objects.get(pk=pk)
    unpaid_reports = guide.guidereports.filter(is_paid=False)

    return render(request, 'mypage/unpaid_reports.html', {'unpaid_reports': unpaid_reports, 'guide': guide})


@login_required
def paid_reports(request, pk): 
    guide = Guide.objects.get(pk=pk)
    paid_reports = guide.guidereports.filter(is_paid=True)

    return render(request, 'mypage/paid_reports.html', {'paid_reports': paid_reports, 'guide': guide})