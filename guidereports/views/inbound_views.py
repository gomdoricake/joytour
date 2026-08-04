from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.http import HttpResponse
from ..models import *
from django.forms import inlineformset_factory
from ..forms import *

from datetime import datetime, date
from django.shortcuts import redirect

import json
from django.forms import formset_factory
from django.core.serializers.json import DjangoJSONEncoder



@login_required
@never_cache
def update_attraction(request, pk): 
    guidereport = get_object_or_404(GuideReport, pk=pk)
    
    if request.user.username != 'admin':
        return HttpResponseForbidden("권한이 없습니다.")

    if request.method == 'POST': 
        for attraction in guidereport.attractions.all():
            adt_val = request.POST.get(f'adt_{attraction.pk}')
            chd_val = request.POST.get(f'chd_{attraction.pk}')
            tc_val = request.POST.get(f'tc_{attraction.pk}')
            tg_val = request.POST.get(f'tg_{attraction.pk}')
            tod_val = request.POST.get(f'tod_{attraction.pk}')

            if adt_val is not None:
                attraction.adt = int(adt_val) if adt_val else 0
                attraction.chd = int(chd_val) if chd_val else 0
                attraction.tc = int(tc_val) if tc_val else 0
                attraction.tg = int(tg_val) if tg_val else 0
                attraction.tod = int(tod_val) if tod_val else 0
                
                attraction.expense = 30 * attraction.adt + 20 * attraction.chd + 10 * attraction.tc + 5 * attraction.tg

                attraction.save()

        guidereport.save()
            
    return redirect('guidereports:detail', guidereport.pk)    


@login_required
@never_cache
def update_restaurant(request, pk): 
    guidereport = get_object_or_404(GuideReport, pk=pk)
    
    if request.user.username != 'admin':
        return HttpResponseForbidden("권한이 없습니다.")

    if request.method == 'POST': 
        for restaurant in guidereport.restaurants.all():
            adt_val = request.POST.get(f'adt_{restaurant.pk}')
            chd_val = request.POST.get(f'chd_{restaurant.pk}')
            tc_val = request.POST.get(f'tc_{restaurant.pk}')
            tg_val = request.POST.get(f'tg_{restaurant.pk}')
            dr_val = request.POST.get(f'dr_{restaurant.pk}')

            if adt_val is not None:
                restaurant.adt = int(adt_val) if adt_val else 0
                restaurant.chd = int(chd_val) if chd_val else 0
                restaurant.tc = int(tc_val) if tc_val else 0
                restaurant.tg = int(tg_val) if tg_val else 0
                restaurant.dr = int(dr_val) if dr_val else 0
                
                restaurant.expense = 25 * restaurant.adt + 20 * restaurant.chd + 10 * restaurant.tc + 5 * restaurant.tg
                restaurant.save()
            
        guidereport.save()

    return redirect('guidereports:detail', guidereport.pk)    



@login_required
@never_cache
def guidereport_inbound_agency(request): 
    main_data = request.session.get('main_data')
    if not main_data: 
        return redirect('guidereports:guidereport_main') 

    report_id = main_data.get('guidereport_id')
    if report_id:
        instance = get_object_or_404(GuideReport, id=report_id)
    else:
        instance = GuideReport(role=main_data['role'], day_inbound=main_data['day_inbound'])

    if request.method == 'POST': 
        form = AgencyPaxForm(request.POST, instance=instance)
        if form.is_valid(): 
            guide_report = form.save(commit=False)
            guide_report.guide = guide_report.guide if request.user.username == 'admin' else request.user.guide_profile
            guide_report.save()

            main_data['guidereport_id'] = guide_report.id
            request.session['main_data'] = main_data
            
            request.session['inbound_data'] = {
                'guidereport_id': guide_report.id,
                'role': main_data['role'],
                'day_inbound': main_data['day_inbound'], 
                'agency_code': form.cleaned_data['agency_code'],
                'adt': form.cleaned_data['adt'],
                'tc': form.cleaned_data['tc'], 
                'chd': form.cleaned_data['chd']
            }
            return redirect('guidereports:guidereport_inbound_events')
    else: 
        form = AgencyPaxForm(instance=instance)
    
    return render(request, 'guidereports/inbound/guidereport_inbound_agency.html', {'form': form, 'AGENCY_CHOICES': AGENCY_CHOICES})


@login_required
@never_cache
def guidereport_inbound_events(request): 
    inbound_data = request.session.get('inbound_data')

    if not inbound_data:
        return redirect('guidereports:guidereport_main')
    
    report_id = inbound_data.get('guidereport_id')
    if report_id:
        guide_report = get_object_or_404(GuideReport, id=report_id)
    else:
        guide_report = GuideReport(
            role=inbound_data['role'],
            day_inbound=inbound_data.get('day_inbound'), 
            agency_code=inbound_data['agency_code'],
            guide=request.user.guide_profile,
            adt=inbound_data['adt'],
            tc=inbound_data['tc'],
            chd=inbound_data['chd']
        )
     
    if guide_report.events.count() == 0:
        extra = 3
    else: 
        extra = 0
    
    EventFormSet = inlineformset_factory(
        GuideReport, 
        Event, 
        form=InboundEventForm, 
        extra=extra,             
        can_delete=True  
    )

    if request.method == 'POST':
        formset = EventFormSet(request.POST, instance=guide_report)
        
        if formset.is_valid():            
            guide_report.save()
            request.session['guidereport_id'] = guide_report.id

            events = formset.save()

            first_event = guide_report.events.order_by('id').first()
            if first_event and first_event.report_date:
                try:
                    if isinstance(first_event.report_date, str):
                        representative_date_str = datetime.strptime(first_event.report_date, '%Y-%m-%d').strftime('%d%m%y')
                    else:
                        representative_date_str = first_event.report_date.strftime('%d%m%y')
                    
                    day_inbound_check = str(guide_report.day_inbound).upper().strip()
                    if day_inbound_check == "INBOUND":
                        pax_count = (guide_report.adt or 0) + (guide_report.tc or 0) + (guide_report.chd or 0)
                        suffix = "G" if pax_count > 9 else "F"
                        guide_report.group_code = f"{guide_report.agency_code}{representative_date_str}{suffix}"
                        guide_report.save()
                except Exception as e:
                    print(f"Group Code 생성 실패: {e}")

            inbound_data['guidereport_id'] = guide_report.id
            request.session['inbound_data'] = inbound_data 
            request.session['inbound_events'] = inbound_data

            return redirect('guidereports:guidereport_inbound_restaurant_exp') 
    else:
        formset = EventFormSet(instance=guide_report)
    
    return render(request, 'guidereports/inbound/guidereport_inbound_events.html', {
        'formset': formset, 
        'guide_report': guide_report,
        'INBOUND_EVENTCODE': INBOUND_EVENTCODE
    })


@login_required
@never_cache
def guidereport_inbound_restaurant_exp(request): 
    inbound_events = request.session.get('inbound_events')

    if not inbound_events: 
        return redirect('guidereports:guidereport_inbound_events')
    
    report_id = inbound_events.get('guidereport_id')
    guide_report = get_object_or_404(GuideReport, id=report_id)

    events = guide_report.events.all()
    initial_data = []
    for event in events:
        initial_data.append({'report_date': event.report_date}) 
        initial_data.append({'report_date': event.report_date}) 

    if guide_report.restaurants.count() == 0:
        extra = events.count() * 2
    else:
        extra = 0

    RestaurantFormSet = inlineformset_factory(
        GuideReport, 
        RestaurantExp, 
        form=RestaurantExpForm, 
        extra=extra,             
        can_delete=True  
    )

    if request.method == "POST": 
        formset = RestaurantFormSet(request.POST, instance=guide_report, initial=initial_data)

        if formset.is_valid(): 
            guide_report.save()
            formset.save() 
            
            request.session['inbound_restaurant'] = inbound_events
            return redirect('guidereports:guidereport_inbound_attraction_exp') 
    else:
        formset = RestaurantFormSet(instance=guide_report, initial=initial_data)

    return render(request, 'guidereports/inbound/guidereport_inbound_restaurant_exp.html', {
        'formset': formset, 
        'guide_report': guide_report,
        'RESTAURANT_CHOICES': RESTAURANT_CHOICES
    })


@login_required
@never_cache  
def guidereport_inbound_attraction_exp(request): 
    inbound_restaurant = request.session.get('inbound_restaurant')

    if not inbound_restaurant: 
        return redirect('guidereports:guidereport_inbound_restaurant_exp')
    
    report_id = inbound_restaurant.get('guidereport_id')
    guide_report = get_object_or_404(GuideReport, id=report_id)

    events = guide_report.events.all()
    initial_data = []
    for event in events: 
        initial_data.append({'report_date': event.report_date})
    
    if guide_report.attractions.count() == 0:
        extra = events.count()
    else:
        extra = 0

    AttractionFormSet = inlineformset_factory(
        GuideReport, 
        AttractionExp, 
        form=AttractionExpForm,
        extra=extra,             
        can_delete=True  
    )

    if request.method == "POST": 
        formset = AttractionFormSet(request.POST, instance=guide_report, initial=initial_data)
        
        if formset.is_valid():
            guide_report.save()
            formset.save()

            main_data = request.session.get('main_data', {})
            main_data['guidereport_id'] = guide_report.id
            request.session['main_data'] = main_data
            
            request.session['inbound_attraction'] = inbound_restaurant
            
            return redirect('guidereports:guidereport_inbound_fuel_exp') 
        else:
            print("Attraction 폼셋 유효성 검사 실패:", formset.errors)

    else:
        formset = AttractionFormSet(instance=guide_report, initial=initial_data)

    return render(request, 'guidereports/inbound/guidereport_inbound_attraction_exp.html', {
        'formset': formset, 
        'guide_report': guide_report,
        'ATTRACTION_CHOICES': ATTRACTION_CHOICES
    })


@login_required
@never_cache  
def guidereport_inbound_fuel_exp(request): 
    inbound_attraction = request.session.get('inbound_attraction')

    if not inbound_attraction: 
        return redirect('guidereports:guidereport_inbound_attraction_exp')
        
    report_id = inbound_attraction.get('guidereport_id')
    guide_report = get_object_or_404(GuideReport, id=report_id)

    events = guide_report.events.all()
    initial_data = []
    for event in events:
        if event.report_date:
            initial_data.append({'report_date': event.report_date})

    FuelFormSet = inlineformset_factory(
        GuideReport, 
        FuelExp, 
        form=FuelExpForm,  
        extra=events.count(),             
        can_delete=True  
    )


    if request.method == "POST": 
        formset = FuelFormSet(request.POST, instance=guide_report, initial=initial_data)

        if formset.is_valid():
            guide_report.save()
            
            formset.save()
            
            request.session['inbound_fuel'] = inbound_attraction
            return redirect('guidereports:guidereport_inbound_guide_exp') 
        else:
            print("Fuel 폼셋 유효성 검사 실패:", formset.errors)

    else:
        formset = FuelFormSet(instance=guide_report, initial=initial_data)

    return render(request, 'guidereports/inbound/guidereport_inbound_fuel_exp.html', {
        'formset': formset, 
        'guide_report': guide_report,
    })

import decimal
from decimal import Decimal

def safe_decimal(value, default='0.00'):
    if value is None or str(value).strip() == '':
        return Decimal(default)
    try:
        return Decimal(str(value))
    except (ValueError, TypeError, decimal.InvalidOperation):
        return Decimal(default)



import uuid
import mimetypes
from django.http import JsonResponse
import os
from django.conf import settings

def get_image_path(request, client_file_name, form_index='0'):
    fuel_data = request.session.get("inbound_fuel") or {}
    attraction_data = request.session.get("inbound_attraction") or {}
    
    report_id = request.session.get('guidereport_id', '')
    guide_report = GuideReport.objects.get(id=report_id)

    group_code = guide_report.group_code

    ext = os.path.splitext(client_file_name)[1]
    
    unique_filename = f"{os.path.splitext(client_file_name)[0]}_idx{form_index}_{uuid.uuid4().hex[:8]}{ext}"

    return f"{group_code}/{unique_filename}"


import traceback

def guidereport_inbound_exp_s3_url(request):
    try:
        client_file_name = request.GET.get('file_name', 'receipt.jpg')
        client_prefix = request.GET.get('prefix', '').strip()
        client_index_raw = request.GET.get('index', '0')

        session_data_raw = request.session.get('s3_inbound_temp_list', '{}')
        try:
            serialized_s3_data = json.loads(session_data_raw)
            if not isinstance(serialized_s3_data, dict):
                serialized_s3_data = {}
        except (json.JSONDecodeError, TypeError):
            serialized_s3_data = {}

        content_type, _ = mimetypes.guess_type(client_file_name)
        if not content_type:
            content_type = 'application/octet-stream'

        if client_prefix and 'form-' in client_prefix:
            form_key = client_prefix.split('-file')[0]  
        else:
            form_key = f"form-{client_index_raw}"

        unique_name = get_image_path(request, client_file_name, form_index=client_index_raw)
        s3_key = f"inbound/temp/{unique_name}"

        serialized_s3_data[form_key] = s3_key
        request.session['s3_inbound_temp_list'] = json.dumps(serialized_s3_data, cls=DjangoJSONEncoder)
        request.session.modified = True

        bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None) or getattr(default_storage, 'bucket_name', None)

        try:
            inbound_s3_client = default_storage.connection.meta.client
        except Exception:
            import boto3
            from botocore.config import Config
            inbound_s3_client = boto3.client(
                's3',
                aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', None),
                aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None),
                region_name=getattr(settings, 'AWS_S3_REGION_NAME', 'ap-northeast-2'),
                config=Config(signature_version='s3v4')
            )

        presigned_url = inbound_s3_client.generate_presigned_url(
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

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': f'[{type(e).__name__}] {str(e)}'}, status=500)


@login_required
@never_cache
def guidereport_inbound_guide_exp(request):
    report_id = request.session.get('guidereport_id', None)
    inbound_data = request.session.get('inbound_data')
    if not inbound_data:
        return redirect('guidereports:guidereport_inbound')

    serialized_exp_data = request.session.get('inbound_exp_temp_list', '[]')
    try:
        exp_data_list = json.loads(serialized_exp_data)
        if not isinstance(exp_data_list, list):
            exp_data_list = []
    except json.JSONDecodeError:
        exp_data_list = []

    serialized_s3_data = request.session.get('s3_inbound_temp_list', '{}')
    try:
        s3_data_dict = json.loads(serialized_s3_data)
        if not isinstance(s3_data_dict, dict):
            s3_data_dict = {}
    except json.JSONDecodeError:
        s3_data_dict = {}

    InboundExpFormSet = formset_factory(
        GuideExpForm,
        extra=0,
        can_delete=True
    )

    if request.method == 'POST':
        formset = InboundExpFormSet(request.POST, request.FILES)

        if formset.is_valid():
            exp_temp_list = []
            new_s3_dict = {}
            saved_index = 0

            for form in formset.forms:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    exp_type = form.cleaned_data.get('expense_type')
                    exp_val = form.cleaned_data.get('expense')
                    memo = form.cleaned_data.get('memo', '')

                    if exp_type and exp_val and exp_val > 0:
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

            request.session['inbound_exp_temp_list'] = json.dumps(exp_temp_list, cls=DjangoJSONEncoder)
            request.session['s3_inbound_temp_list'] = json.dumps(new_s3_dict, cls=DjangoJSONEncoder)
            request.session.modified = True

            return redirect('guidereports:guidereport_inbound_summary')
        else:
            print('인바운드 폼셋 유효성 검사 실패: ', formset.errors)

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
                request.session['inbound_exp_temp_list'] = json.dumps(exp_data_list, cls=DjangoJSONEncoder)

            if not s3_data_dict and db_exps.exists():
                for idx, exp_obj in enumerate(db_exps):
                    if exp_obj.file_key:
                        s3_data_dict[f'form-{idx}'] = exp_obj.file_key
                request.session['s3_inbound_temp_list'] = json.dumps(s3_data_dict, cls=DjangoJSONEncoder)

            request.session.modified = True

        if not exp_data_list:
            exp_data_list = [{'expense_type': '', 'expense': 0.0, 'memo': ''}]

        formset = InboundExpFormSet(initial=exp_data_list)

    zipped_forms = []
    for form in formset.forms:
        receipt_url = s3_data_dict.get(form.prefix, None)
        zipped_forms.append((form, receipt_url))

    return render(request, 'guidereports/inbound/guidereport_inbound_guide_exp.html', {
        'formset': formset,
        'zipped_forms': zipped_forms,
    })


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.db import transaction
from datetime import datetime


@login_required
@never_cache
def guidereport_inbound_summary(request):
    inbound_data = request.session.get('inbound_data')
    main_data = request.session.get('main_data')

    if not inbound_data or not main_data:
        return redirect('guidereports:guidereport_inbound_agency')

    report_id = inbound_data.get('guidereport_id') or request.session.get('guidereport_id')
    guide_report = get_object_or_404(GuideReport, pk=report_id)

    events = guide_report.events.all()
    first_event = events.first()
    
    restaurant_qs = guide_report.restaurants.all() if hasattr(guide_report, 'restaurants') else RestaurantExp.objects.filter(guide_report=guide_report)
    attraction_qs = guide_report.attractions.all() if hasattr(guide_report, 'attractions') else AttractionExp.objects.filter(guide_report=guide_report)
    fuel_qs = guide_report.fuels.all() if hasattr(guide_report, 'fuels') else FuelExp.objects.filter(guide_report=guide_report)

    raw_exp_list = request.session.get('inbound_exp_temp_list', '[]')
    exp_list = json.loads(raw_exp_list) if isinstance(raw_exp_list, str) else raw_exp_list

    raw_s3_dict = request.session.get('s3_inbound_temp_list', '{}')
    s3_exp_dict = json.loads(raw_s3_dict) if isinstance(raw_s3_dict, str) else raw_s3_dict

    computed_fee = Decimal('0.00')
    for evt in events:
        if hasattr(evt, 'calculate_guide_fee'):
            computed_fee += safe_decimal(evt.calculate_guide_fee())
        elif hasattr(evt, 'guide_fee'):
            computed_fee += safe_decimal(evt.guide_fee)

    guide_fee_decimal = safe_decimal(computed_fee)

    total_restaurant = sum(safe_decimal(r.expense) for r in restaurant_qs)
    total_attraction = sum(safe_decimal(a.expense) for a in attraction_qs)
    total_fuel = sum(safe_decimal(f.expense) for f in fuel_qs)
    total_inbound_exp = sum(safe_decimal(e.get('expense', 0)) for e in exp_list)

    grand_total = guide_fee_decimal + total_restaurant + total_attraction + total_fuel + total_inbound_exp

    if request.method == 'POST':
        with transaction.atomic():
            GuideExp.objects.filter(guide_report=guide_report).delete()

            inbound_s3_client = default_storage.connection.meta.client
            bucket_name = default_storage.bucket_name

            def move_s3_temp_file(s3_key_val):
                if not s3_key_val or 'temp/' not in str(s3_key_val):
                    return s3_key_val
                
                old_key = str(s3_key_val)
                new_key = old_key.replace('temp/', 'expenses/') 
                
                try:
                    inbound_s3_client.copy_object(
                        Bucket=bucket_name,
                        CopySource={'Bucket': bucket_name, 'Key': old_key},
                        Key=new_key
                    )
                    inbound_s3_client.delete_object(Bucket=bucket_name, Key=old_key)
                    return new_key
                except Exception as e:
                    print(f"[S3 Error] 파일 이동 실패 ({old_key} -> {new_key}): {e}")
                    return old_key 

            for i, exp in enumerate(exp_list):
                s3_key_val = s3_exp_dict.get(f'form-{i}') or s3_exp_dict.get(str(i))
                final_s3_key = move_s3_temp_file(s3_key_val)

                GuideExp.objects.create(
                    guide_report=guide_report,
                    expense_type=exp.get('expense_type', ''),
                    expense=safe_decimal(exp.get('expense', 0)),
                    memo=exp.get('memo', ''),
                    file_key=final_s3_key or ''
                )

            guide_report.final_events_fee = guide_fee_decimal
            guide_report.final_expenses_fee = total_inbound_exp
            guide_report.final_amount_due = grand_total
            count = GuideReport.objects.filter(guide=request.user.guide_profile).count()
            guide_report.invoice_number = count
            guide_report.save()

            session_keys_to_clear = [
                'inbound_data', 'inbound_events', 'inbound_restaurant', 
                'inbound_attraction', 'inbound_fuel', 'inbound_exp_temp_list', 
                's3_inbound_temp_list', 'guidereport_id'
            ]
            for key in session_keys_to_clear:
                request.session.pop(key, None)

            return redirect('guidereports:detail', pk=guide_report.id)

    context = {
        'guide_report': guide_report,
        'report_date': getattr(guide_report, 'report_date', date.today()),
        'events': events,
        'guide_fee': guide_fee_decimal,
        
        'restaurant_expenses': restaurant_qs,
        'attraction_expenses': attraction_qs,
        'fuel_expenses': fuel_qs,
        'inbound_expenses': exp_list,
        
        'total_restaurant': total_restaurant,
        'total_attraction': total_attraction,
        'total_fuel': total_fuel,
        'total_inbound_exp': total_inbound_exp,
        'grand_total': grand_total,

        'invoice_number': guide_report.invoice_number or 1,
        'invoice_date': guide_report.invoice_date or date.today(),
    }
    
    return render(request, 'guidereports/inbound/guidereport_inbound_summary.html', context)