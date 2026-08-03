from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.http import HttpResponse
from ..models import *
from django.forms import inlineformset_factory
from ..forms import *

from django.views.decorators.csrf import csrf_exempt

import datetime
from datetime import date
from django.shortcuts import redirect

import boto3
from botocore.config import Config
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

@login_required
@never_cache
def guidereport_day(request): 
    main_data = request.session.get('main_data')
    if not main_data: 
        return redirect('guidereports:guidereport_main') 

    report_id = request.session.get('guidereport_id', '')
    role = main_data.get('role', '')

    DAY_EVENTCODE = None
    if role == '12 SEAT':
        DAY_EVENTCODE = DAY_EVENTCODE_12SEAT
    if role == '21 SEAT': 
        DAY_EVENTCODE = DAY_EVENTCODE_21SEAT
    if role == '53 SEAT': 
        DAY_EVENTCODE = DAY_EVENTCODE_53SEAT
    elif role == 'GUIDE ONLY': 
        DAY_EVENTCODE = DAY_EVENTCODE_GUIDE_ONLY


    initial_data = {}

    if report_id:
        instance = get_object_or_404(GuideReport, id=report_id)
        event_instance = Event.objects.filter(guidereport=instance).first()
        
        if event_instance:
            if event_instance.eventcode: 
                initial_data['eventcode'] = event_instance.eventcode
            if event_instance.report_date:
                initial_data['report_date'] = event_instance.report_date.strftime('%Y-%m-%d')
    else:
        day_data = request.session.get('day_data', {})
        
        if day_data: 
            initial_data['report_date'] = day_data.get('report_date', '')
            initial_data['eventcode'] = day_data.get('eventcode', '')
    
    event_instance = Event(
        report_date=initial_data.get('report_date') or None, 
        eventcode=initial_data.get('eventcode', '')
    )

    if request.method == 'POST': 
        form = GuideReportDayForm(request.POST, instance=event_instance)
        if form.is_valid(): 
            eventcode = form.cleaned_data['eventcode']
            report_date = form.cleaned_data['report_date'].strftime('%Y-%m-%d')
            today_str = form.cleaned_data['report_date'].strftime('%d%m%y')

            request.session['day_data'] = {
                'report_date': report_date, 
                'today_str': today_str, 
                'group_code': 'J' + today_str + eventcode, 
                'eventcode': eventcode
            }
            
            return redirect('guidereports:guidereport_day_fuel_exp')
    else: 
        form = GuideReportDayForm(initial=initial_data, instance=event_instance)
    
    return render(request, 'guidereports/day/guidereport_day.html', {'form': form, 'DAY_EVENTCODE': DAY_EVENTCODE})


import uuid
import mimetypes
from django.http import JsonResponse

def get_image_path(request, client_file_name): 
    group_code = request.session.get('day_data')['group_code']
        
    return f'{group_code}/{client_file_name}'


def guidereport_day_fuel_s3_url(request):
    client_file_name = request.GET.get('file_name', 'receipt.jpg')
    
    content_type, _ = mimetypes.guess_type(client_file_name)
    if not content_type:
        content_type = 'application/octet-stream'

    ext = os.path.splitext(client_file_name)[1]
    unique_name = get_image_path(request, client_file_name)
    s3_key = f"day/bp/{unique_name}"

    bp_s3_client = default_storage.connection.meta.client
    bucket_name = default_storage.bucket_name

    presigned_url = bp_s3_client.generate_presigned_url(
        ClientMethod='put_object', 
        Params={
            'Bucket': bucket_name, 
            'Key': s3_key, 
            'ContentType': content_type
        },
        ExpiresIn=600
    )

    return JsonResponse({
        'upload_url': presigned_url,
        's3_key': s3_key,
        'content_type': content_type
    })


import mimetypes
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.forms import formset_factory

@login_required
@never_cache
@csrf_exempt
def guidereport_day_fuel_exp(request): 
    day_data = request.session.get('day_data')
    if not day_data: 
        return redirect('guidereports:guidereport_day')
        
    serialized_fuel_data = request.session.get('fuel_temp_list', '[]')
    try:
        fuel_data_list = json.loads(serialized_fuel_data)
    except json.JSONDecodeError: 
        fuel_data_list = []

    serialized_s3_data = request.session.get('s3_fuel_temp_list', '[]')
    try: 
        s3_data_list = json.loads(serialized_s3_data)
    except json.JSONDecodeError: 
        s3_data_list = []

    for i, fuel_item in enumerate(fuel_data_list): 
        if i < len(s3_data_list): 
            fuel_item['file_key'] = s3_data_list[i]

    
    FuelFormSet = formset_factory(
        FuelExpForm,
        extra=1,
        can_delete=True
    )

    day_data = request.session.get('day_data') or {}
    report_date = day_data.get('report_date', '')

    if request.method == 'POST': 
        formset = FuelFormSet(request.POST, request.FILES)

        if formset.is_valid(): 
            fuel_temp_list, s3_fuel_temp_list = [], []

            for form in formset.forms: 
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    data = form.cleaned_data.copy()
                    
                    s3_key_value = data.get('file_key') or request.POST.get(f'{form.prefix}-file_key') 
                    
                    fuel_temp_list.append(data)
                    s3_fuel_temp_list.append(str(s3_key_value))

            request.session['fuel_temp_list'] = json.dumps(fuel_temp_list, cls=DjangoJSONEncoder)
            request.session['s3_fuel_temp_list'] = json.dumps(s3_fuel_temp_list, cls=DjangoJSONEncoder)
            
            return redirect('guidereports:guidereport_day_guide_exp')
        else: 
            print('폼셋 유효성 검사 실패: ', formset.errors)
        
    else: 
        if not fuel_data_list: 
            fuel_data_list = [{'report_date': report_date}]
        else: 
            for item in fuel_data_list: 
                item['report_date'] = report_date

        formset = FuelFormSet(
            initial=fuel_data_list,
        )

    return render(request, 'guidereports/day/guidereport_day_fuel_exp.html', {
        'formset': formset, 
    })


from django.db import transaction
from django.core.files.storage import default_storage


def guidereport_day_exp_s3_url(request): 

    client_file_name = request.GET.get('file_name') or 'receipt.jpg'
    content_type, _ = mimetypes.guess_type(client_file_name)

    if not content_type: 
        content_type = 'application/octet-stream'
    
    ext = os.path.splitext(client_file_name)[1]

    unique_name = get_image_path(request, client_file_name)
    s3_key = f"day/guide_exp/{unique_name}"


    exp_s3_client = default_storage.connection.meta.client
    bucket_name = default_storage.bucket_name

    presigned_url = exp_s3_client.generate_presigned_url(
        ClientMethod = 'put_object', 
        Params = {
            'Bucket': bucket_name,
            'Key': s3_key, 
            'ContentType': content_type
        },
        ExpiresIn = 600
    )

    return JsonResponse({
        'upload_url': presigned_url, 
        's3_key': s3_key, 
        'content_type': content_type
    })


@login_required
@never_cache
@csrf_exempt
def guidereport_day_guide_exp(request):
    
    day_data = request.session.get('day_data')  
    fuel_temp_list = request.session.get('fuel_temp_list')
    if not fuel_temp_list or not day_data:
        return redirect('guidereports:guidereport_day')
    
    serialized_exp_data = request.session.get('exp_temp_list', '[]')
    try: 
        exp_data_list = json.loads(serialized_exp_data)
    except json.JSONDecodeError: 
        exp_data_list = []

    serialized_s3_data = request.session.get('s3_exp_temp_list', '[]')
    try:
        s3_data_list = json.loads(serialized_s3_data)
    except json.JSONDecodeError: 
        s3_data_list = []

    formatted_initial_list = []
    for i, item in enumerate(exp_data_list):
        if isinstance(item, list) and len(item) >= 2:
            data_dict = {'expense_type': item[0], 'expense': item[1]}
        elif isinstance(item, dict):
            data_dict = item.copy()
        else:
            continue
            
        if i < len(s3_data_list): 
            data_dict['file_key'] = s3_data_list[i]
        formatted_initial_list.append(data_dict)

    GuideExpFormSet = formset_factory(
        GuideExpForm, 
        extra=1,              
        can_delete=True  
    )

    if request.method == 'POST':
        formset = GuideExpFormSet(request.POST, request.FILES)
        
        if formset.is_valid():
            wash_added = False
            exp_temp_list = []
            s3_exp_temp_list = []
            
            for form in formset.forms: 
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    exp_type = form.cleaned_data.get('expense_type')
                    exp_val = form.cleaned_data.get('expense')
                    memo = form.cleaned_data.get('memo', '')

                    if exp_type and exp_val and exp_val > 0: 
                        if exp_type == 'WASH': 
                            if wash_added: 
                                continue
                            wash_added = True
                        
                        s3_key_value = form.cleaned_data.get('file_key') or request.POST.get(f'{form.prefix}-file_key')
                        
                        exp_temp_list.append({
                            'expense_type': exp_type,
                            'expense': exp_val, 
                            'memo': memo
                        })
                        s3_exp_temp_list.append(str(s3_key_value))                        
                
            request.session['exp_temp_list'] = json.dumps(exp_temp_list, cls=DjangoJSONEncoder)
            request.session['s3_exp_temp_list'] = json.dumps(s3_exp_temp_list, cls=DjangoJSONEncoder)

            return redirect('guidereports:guidereport_day_summary') 
        else:
            print('폼셋 유효성 검사 실패: ', formset.errors)
            
    else:
        formset = GuideExpFormSet(
            initial=formatted_initial_list
        )

    report_date_str = day_data.get('report_date', '')
    
    if day_data.get('role') == 'GUIDE ONLY':
        CHOICES = request.resolver_match.namespace + "_GUIDE_ONLY_CHOICES"  
    else:
        CHOICES = "DEFAULT_EXPENSE_CHOICES"
    
    return render(request, 'guidereports/day/guidereport_day_guide_exp.html', {
        'formset': formset, 
        'report_date': report_date_str, 
        'CHOICES': CHOICES
    })

from django.db.models import Sum
from decimal import Decimal


def safe_decimal(value, default='0.00'):
    if value is None or str(value).strip() == '':
        return Decimal(default)
    try:
        return Decimal(str(value))
    except (ValueError, TypeError, decimal.InvalidOperation):
        return Decimal(default)

@login_required
@never_cache
def guidereport_day_summary(request): 
    day_data = request.session.get('day_data')  
    fuel_temp_list = request.session.get('fuel_temp_list')
    exp_temp_list = request.session.get('exp_temp_list')
    main_data = request.session.get('main_data')

    if not fuel_temp_list or not day_data or not exp_temp_list or not main_data:
        return redirect('guidereports:guidereport_day')

    day_inbound = main_data.get('day_inbound')
    role = main_data.get('role')
    report_date = day_data.get('report_date')
    group_code = day_data.get('group_code')
    eventcode = day_data.get('eventcode')
    report_id = request.session.get('guidereport_id', '')

    fuel_list = json.loads(request.session.get('fuel_temp_list', '[]'))
    s3_fuel_list = json.loads(request.session.get('s3_fuel_temp_list', '[]'))
    exp_list = json.loads(request.session.get('exp_temp_list', '[]'))
    s3_exp_list = json.loads(request.session.get('s3_exp_temp_list', '[]'))

    if report_id:
        guide_report = get_object_or_404(GuideReport, pk=report_id)
        event = Event.objects.filter(guide_report=guide_report).first()
        if not event:
            event = Event(guide_report=guide_report, eventcode=eventcode, report_date=report_date)
        
        guide_report.day_inbound = day_inbound
        guide_report.role = role
        guide_report.group_code = group_code
        event.eventcode = eventcode

        invoice_number = guide_report.invoice_number
        invoice_date = guide_report.invoice_date
    else:
        guide = request.user.guide_profile
        invoice_number = guide.guidereports.count() + 1
        invoice_date = date.today()
        
        guide_report = GuideReport(
            guide=guide,
            invoice_date=invoice_date,
            invoice_number=invoice_number,
            day_inbound=day_inbound, 
            role=role,
            group_code=group_code,
        )
        
        event = Event(
            guide_report=guide_report,
            eventcode=eventcode,
            report_date=report_date,
        )

    computed_fee = event.calculate_guide_fee()
    event.guide_fee = computed_fee 
    
    guide_fee_decimal = safe_decimal(computed_fee)
    total_fuel = sum(safe_decimal(f.get('expense')) for f in fuel_list)
    total_guide_exp = sum(safe_decimal(e.get('expense')) for e in exp_list)
    
    super_ann = guide_fee_decimal / Decimal('1.1') * Decimal('0.12')
    grand_total = guide_fee_decimal + total_guide_exp

    if request.method == 'POST':
        with transaction.atomic():
            if report_id:
                guide_report.day_inbound = day_inbound
                guide_report.role = role
                guide_report.report_date = report_date
                guide_report.group_code = group_code
                guide_report.save()

                Event.objects.filter(guide_report=guide_report).delete()
                FuelExp.objects.filter(guide_report=guide_report).delete()
                GuideExp.objects.filter(guide_report=guide_report).delete()
            else:
                guide_report.save()

            event.guide_report = guide_report  
            event.save()

            for i, fuel in enumerate(fuel_list): 
                
                if i < len(s3_fuel_list):
                    s3_key_value = s3_fuel_list[i]
                    
                FuelExp.objects.create(
                    guide_report=guide_report,
                    report_date=fuel.get('report_date') or report_date,
                    expense=safe_decimal(fuel.get('expense')),
                    memo=fuel.get('memo', ''),
                    file_key=s3_key_value  
                )

            for i, exp in enumerate(exp_list): 

                if i < len(s3_exp_list):
                    s3_key_value = s3_exp_list[i]

                GuideExp.objects.create(
                    guide_report=guide_report,
                    expense_type=exp.get('expense_type'), 
                    expense=safe_decimal(exp.get('expense')),
                    memo=exp.get('memo', ''),
                    file_key=s3_key_value
                )

            guide_report.final_events_fee = event.guide_fee
            guide_report.final_fuels_fee = total_fuel
            guide_report.final_expenses_fee = total_guide_exp
            guide_report.super_ann = super_ann
            guide_report.final_amount_due = grand_total
            guide_report.save()

            return redirect('guidereports:detail', pk=guide_report.id)

    context = {
        'guide_report': guide_report,
        'event': event,                 
        'report_date': report_date,
        'fuel_expenses': fuel_list,
        'guide_expenses': exp_list,
        'total_fuel': total_fuel,
        'total_guide': total_guide_exp,
        'grand_total': grand_total,
        'invoice_number': invoice_number,
        'super_ann': super_ann,
        'invoice_date': invoice_date,
    }
    return render(request, 'guidereports/day/guidereport_day_summary.html', context)
