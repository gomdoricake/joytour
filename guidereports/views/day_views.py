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

    if report_id:
        if isinstance(report_id, list): 
            report_id = report_id[0] if report_id else None
    
    try: 
        report_id = int(report_id)
        request.session['guidereport_id'] = report_id
    except (ValueError, TypeError): 
        report_id = ''

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
        event_instance = Event.objects.filter(guide_report=instance).first()
        
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
    client_prefix = request.GET.get('prefix', '').strip()
    client_index_raw = request.GET.get('index', '')

    session_data_raw = request.session.get('s3_fuel_temp_list', '{}')

    try:
        serialized_s3_data = json.loads(session_data_raw)
        if not isinstance(serialized_s3_data, dict):
            serialized_s3_data = {}
    except json.JSONDecodeError:
        serialized_s3_data = {}
    
    content_type, _ = mimetypes.guess_type(client_file_name)
    if not content_type:
        content_type = 'application/octet-stream'

    ext = os.path.splitext(client_file_name)[1]
    unique_name = get_image_path(request, client_file_name)
    s3_key = f"day/bp/temp/{unique_name}"


    if client_prefix and client_prefix != '': 
        if 'id_' in client_prefix:
            client_prefix = client_prefix.replace('id_', '')
        if '-file_key' in client_prefix:
            client_prefix = client_prefix.replace('-file_key', '')

        serialized_s3_data[client_prefix] = s3_key

    else: 
        client_index_raw = request.GET.get('index', '0')
        serialized_s3_data[f'form-{client_index_raw}'] = s3_key

    request.session['s3_fuel_temp_list'] = json.dumps(serialized_s3_data, cls=DjangoJSONEncoder)
    request.session.modified = True

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
    report_id = request.session.get('guidereport_id', None)
    day_data = request.session.get('day_data')
    if not day_data: 
        return redirect('guidereports:guidereport_day')
        
    serialized_fuel_data = request.session.get('fuel_temp_list', '[]')
    try:
        fuel_data_list = json.loads(serialized_fuel_data)
        if not isinstance(fuel_data_list, list):
            fuel_data_list = []
    except json.JSONDecodeError: 
        fuel_data_list = []

    serialized_s3_data = request.session.get('s3_fuel_temp_list', '{}')
    try: 
        s3_data_dict = json.loads(serialized_s3_data)
        if not isinstance(s3_data_dict, dict):
            s3_data_dict = {}
    except json.JSONDecodeError: 
        s3_data_dict = {}
    
    FuelFormSet = formset_factory(FuelExpForm, extra=1, can_delete=True)
    day_data = request.session.get('day_data') or {}
    report_date = day_data.get('report_date', '')

    if request.method == 'POST': 
        formset = FuelFormSet(request.POST, request.FILES)

        if formset.is_valid(): 
            fuel_temp_list = []
            new_s3_dict = {}
            saved_index = 0 

            for form in formset.forms: 
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    cleaned = form.cleaned_data
                    
                    fuel_temp_list.append({
                        'report_date': cleaned.get('report_date').strftime('%Y-%m-%d') if cleaned.get('report_date') else report_date,
                        'expense': float(cleaned.get('expense')) if cleaned.get('expense') is not None else 0.0,
                        'memo': str(cleaned.get('memo') or '').strip(),
                    })

                    hidden_s3_val = request.POST.get(f'{form.prefix}-s3_key', '').strip()
                    
                    if not hidden_s3_val:
                        hidden_s3_val = s3_data_dict.get(form.prefix, '')

                    if hidden_s3_val:
                        new_s3_dict[f'form-{saved_index}'] = hidden_s3_val
                    
                    saved_index += 1

            request.session['fuel_temp_list'] = json.dumps(fuel_temp_list, cls=DjangoJSONEncoder)
            request.session['s3_fuel_temp_list'] = json.dumps(new_s3_dict, cls=DjangoJSONEncoder)
            request.session.modified = True
            
            return redirect('guidereports:guidereport_day_guide_exp')
        else: 
            print('폼셋 검증 실패 원인:', formset.errors)
        
    else: 
        if report_id and not s3_data_dict: 
            db_fuels = FuelExp.objects.filter(guide_report_id=report_id).order_by('-id')
        
            for idx, fuel_obj in enumerate(db_fuels): 
                if fuel_obj.file_key: 
                    s3_data_dict[f'form-{idx}'] = fuel_obj.file_key
            
            request.session['s3_fuel_temp_list'] = json.dumps(s3_data_dict, cls=DjangoJSONEncoder)
            request.session.modified = True

        if not fuel_data_list: 
            fuel_data_list = [{'report_date': report_date, 'expense': 0.0, 'memo': ''}]
        else: 
            for item in fuel_data_list: 
                item['report_date'] = report_date

        formset = FuelFormSet(initial=fuel_data_list)
    
    zipped_forms = []
    for form in formset.forms: 
        receipt_url = s3_data_dict.get(form.prefix, None)
        zipped_forms.append((form, receipt_url))
        
    return render(request, 'guidereports/day/guidereport_day_fuel_exp.html', {
        'formset': formset, 
        'zipped_forms': zipped_forms
    })


from django.db import transaction
from django.core.files.storage import default_storage


def guidereport_day_exp_s3_url(request): 
    client_file_name = request.GET.get('file_name', 'receipt.jpg')
    client_prefix = request.GET.get('prefix', '').strip()
    client_index_raw = request.GET.get('index', '')
    
    sessoin_data_raw = request.session.get('s3_exp_temp_list', '[]')

    try: 
        serialized_s3_data = json.loads(sessoin_data_raw)
        if not isinstance(serialized_s3_data, dict):
            serialized_s3_data = {}
    except json.JSONDecodeError:
        serialized_s3_data = {}

    content_type, _ = mimetypes.guess_type(client_file_name)
    if not content_type: 
        content_type = 'application/octet-stream'
    
    ext = os.path.splitext(client_file_name)[1]
    unique_name = get_image_path(request, client_file_name)
    s3_key = f"day/guide_exp/temp/{unique_name}"

    if client_prefix and client_prefix != '': 
        if 'id_' in client_prefix:
            client_prefix = client_prefix.replace('id_', '')
        if '-file_key' in client_prefix:
            client_prefix = client_prefix.replace('-file_key', '')
        
        serialized_s3_data[client_prefix] = s3_key
    
    else:
        client_index_raw = request.GET.get('index', '0')
        serialized_s3_data[f'form-{client_index_raw}'] = s3_key
    
    request.session['s3_exp_temp_list'] = json.dumps(serialized_s3_data, cls=DjangoJSONEncoder)
    request.session.modified = True

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
    report_id = request.session.get('guidereport_id', None)
    day_data = request.session.get('day_data')  
    fuel_temp_list = request.session.get('fuel_temp_list')
    if not fuel_temp_list or not day_data:
        return redirect('guidereports:guidereport_day')
    
    serialized_exp_data = request.session.get('exp_temp_list', '[]')
    try: 
        exp_data_list = json.loads(serialized_exp_data)
        if not isinstance(exp_data_list, list):
            exp_data_list = []
    except json.JSONDecodeError: 
        exp_data_list = []

    serialized_s3_data = request.session.get('s3_exp_temp_list', '{}')
    try:
        s3_data_dict = json.loads(serialized_s3_data)
        if not isinstance(s3_data_dict, dict):
            s3_data_dict = {}
    except json.JSONDecodeError: 
        s3_data_dict = {}

    GuideExpFormSet = formset_factory(
        GuideExpForm, 
        extra=0,        
        can_delete=True  
    )

    day_data = request.session.get('day_data') or {}
    report_date_str = day_data.get('report_date', '')

    if request.method == 'POST':
        formset = GuideExpFormSet(request.POST, request.FILES)
        
        if formset.is_valid():
            wash_added = False
            exp_temp_list = []
            new_s3_dict = {}
            saved_index = 0 
            
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
                        
                        exp_temp_list.append({
                            'expense_type': exp_type,
                            'expense': float(exp_val), 
                            'memo': str(memo or '').strip()
                        })
                        
                        hidden_s3_val = request.POST.get(f'{form.prefix}-s3_key', '').strip()
                        
                        if not hidden_s3_val and isinstance(s3_data_dict, dict):
                            hidden_s3_val = s3_data_dict.get(form.prefix, '')

                        if hidden_s3_val:
                            new_s3_dict[f'form-{saved_index}'] = hidden_s3_val
                        
                        saved_index += 1                       
                
            request.session['exp_temp_list'] = json.dumps(exp_temp_list, cls=DjangoJSONEncoder)
            request.session['s3_exp_temp_list'] = json.dumps(new_s3_dict, cls=DjangoJSONEncoder)
            request.session.modified = True

            return redirect('guidereports:guidereport_day_summary') 
        else:
            print('폼셋 유효성 검사 실패: ', formset.errors)
            
    else:
        if report_id:
            from ..models import GuideExp
            db_exps = GuideExp.objects.filter(guide_report_id=report_id).order_by('id')
            
            if not exp_data_list and db_exps.exists():
                for exp_obj in db_exps:
                    exp_data_list.append({
                        'expense_type': exp_obj.expense_type,
                        'expense': float(exp_obj.expense) if exp_obj.expense is not None else 0.0,
                        'memo': exp_obj.memo or ''
                    })
                request.session['exp_temp_list'] = json.dumps(exp_data_list, cls=DjangoJSONEncoder)
            
            if not s3_data_dict and db_exps.exists():
                for idx, exp_obj in enumerate(db_exps):
                    if exp_obj.file_key:
                        s3_data_dict[f'form-{idx}'] = exp_obj.file_key
                request.session['s3_exp_temp_list'] = json.dumps(s3_data_dict, cls=DjangoJSONEncoder)
            
            request.session.modified = True

        if not exp_data_list: 
            exp_data_list = [{'expense_type': '', 'expense': 0.0, 'memo': ''}]

        formset = GuideExpFormSet(initial=exp_data_list)

    zipped_forms = []
    for form in formset.forms:
        receipt_url = s3_data_dict.get(form.prefix, None)
        zipped_forms.append((form, receipt_url))
    
    if day_data.get('role') == 'GUIDE ONLY':
        CHOICES = request.resolver_match.namespace + "_GUIDE_ONLY_CHOICES"  
    else:
        CHOICES = "DEFAULT_EXPENSE_CHOICES"
    
    return render(request, 'guidereports/day/guidereport_day_guide_exp.html', {
        'formset': formset, 
        'zipped_forms': zipped_forms, 
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


    is_same_event = Event.objects.filter(report_date=report_date, eventcode=eventcode, guide_report__guide__user=request.user).order_by('-id')

    if is_same_event.exists() and (not report_id or is_same_event.first().guide_report.id != report_id):
        print("같은 날짜와 이벤트코드로 이미 가이드 리포트가 존재합니다.")
        alert_message = "같은 날짜와 이벤트코드로 이미 가이드 리포트가 존재합니다. "
        return render(request, 'guidereports/day/guidereport_day_summary.html', { 'alert_message': alert_message, **context })


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

            bp_s3_client = default_storage.connection.meta.client
            bucket_name = default_storage.bucket_name

            for i, fuel in enumerate(fuel_list):
                s3_key_value = None

                if isinstance(s3_fuel_list, dict): 
                    s3_key_value = s3_fuel_list.get(f'form-{i}')

                if not s3_key_value: 
                    s3_key_value = request.POST.get(f'form-{i}-s3_key', None)

                if s3_key_value and 'temp/' in s3_key_value:
                    old_key = s3_key_value
                    new_key = old_key.replace('temp/', '')
                    try:
                        bp_s3_client.copy_object(
                            Bucket=bucket_name,
                            CopySource={'Bucket': bucket_name, 'Key': old_key},
                            Key=new_key
                        )
                        bp_s3_client.delete_object(Bucket=bucket_name, Key=old_key)
                        s3_key_value = new_key
                    except Exception as e:
                        print(f"S3 파일 이동 실패: {e}")

                FuelExp.objects.create(
                    guide_report=guide_report,
                    report_date=fuel.get('report_date'),
                    expense=safe_decimal(fuel.get('expense')),
                    memo=fuel.get('memo', ''),
                    file_key=s3_key_value
                )

            for i, exp in enumerate(exp_list):
                s3_key_value = None
                
                if isinstance(s3_exp_list, dict): 
                    s3_key_value = s3_exp_list.get(f'form-{i}')
                elif isinstance(s3_exp_list, list) and i < len(s3_exp_list):
                    s3_key_value = s3_exp_list[i]
                
                if not s3_key_value:
                    s3_key_value = request.POST.get(f'form-{i}-file_key', None)

                if s3_key_value and 'temp/' in s3_key_value:
                    old_key = s3_key_value
                    new_key = old_key.replace('temp/', '')
                    try:
                        bp_s3_client.copy_object(
                            Bucket=bucket_name,
                            CopySource={'Bucket': bucket_name, 'Key': old_key},
                            Key=new_key
                        )
                        bp_s3_client.delete_object(Bucket=bucket_name, Key=old_key)
                        s3_key_value = new_key
                    except Exception as e:
                        print(f"S3 파일 이동 실패: {e}")
                
                GuideExp.objects.create(
                    guide_report=guide_report,
                    expense_type=exp.get('expense_type', ''),
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
