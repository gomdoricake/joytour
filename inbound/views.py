from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .forms import GroupForm, AgentForm, HotelTypeForm
from .models import Agent, Group, GroupFile, HotelType, Hotel
from django.forms import formset_factory
from .forms import HotelForm, ItineraryForm, ItineraryFormSet
from invoices.models import Invoice, Meal, Attraction, Vehicle, GuideInvoice, Tip, \
                                    MealType, AttractionType, VehicleType, GuideInvoiceType, \
                                    GuideTipType, DriverTipType


@login_required
def index(request): 
    return render(request, 'inbound/index.html')

@login_required
def tariff(request): 
    mealtype_list = MealType.objects.all().order_by('-id')
    attractiontype_list = AttractionType.objects.all().order_by('-id')
    vehicletype_list = VehicleType.objects.all().order_by('-id')
    guideinvoicetype_list = GuideInvoiceType.objects.all().order_by('-id')
    guide_tip = GuideTipType.objects.all().order_by('-id')
    driver_tip = DriverTipType.objects.all().order_by('-id')
    hoteltype_list = HotelType.objects.all().order_by('-id')

    context = {
        'mealtype_list': mealtype_list, 
        'attractiontype_list': attractiontype_list,
        'vehicletype_list': vehicletype_list,
        'guideinvoicetype_list': guideinvoicetype_list,
        'guide_tip': guide_tip,
        'driver_tip': driver_tip,
        'hoteltype_list': hoteltype_list,
    } 
    return render(request, 'inbound/tariff.html', context)

@login_required
def agent_list(request): 
    agent_list = Agent.objects.all()

    context = {
        'agent_list': agent_list,
    }
    return render(request, 'inbound/agent_list.html', context)

@login_required
def agent_detail(request, pk): 
    agent = Agent.objects.get(pk=pk)

    context = {
        'agent': agent
    }
    return render(request, 'inbound/agent_detail.html', context)

@login_required
def create_agent(request): 
    form = AgentForm(request.POST)
    if request.method == 'POST': 
        
        if form.is_valid(): 
            code = form.cleaned_data['code']
            form.save()

            return redirect('inbound:agent_list')
    else: 
        context = {
            'form': form
        }
        return render(request, 'inbound/create_agent.html', context)


@login_required
def update_agent(request, pk): 
    agent = get_object_or_404(Agent, pk=pk)

    if agent: 
        if request.method == 'POST': 
            form = AgentForm(request.POST, instance=agent)

            if form.is_valid():
                form.save()

                return redirect('inbound:agent_detail', pk=pk)
            else: 
                return redirect('inbound:update_agent')

        else: 
            
            form = AgentForm(instance=agent) 
            
            context = {
                'agent': agent,
                'form': form
            }
            
            return render(request, 'inbound/create_agent.html', context)
                

@login_required
def delete_agent(request, pk): 
    agent = get_object_or_404(Agent, pk=pk)

    if agent: 
        agent.delete()

    return redirect('inbound:agent_list')

@login_required
def group_list(request): 
    group_list = Group.objects.all()

    context = {
        'group_list': group_list
    }
    return render(request, 'inbound/group_list.html', context)



from invoices.forms import MealTypeForm, VehicleTypeForm, GuideInvoiceTypeForm, GuideTipTypeForm, DriverTipTypeForm, MealFormSet, AttractionTypeForm, AttractionFormSet, VehicleFormSet,  GuideInvoiceFormSet, TipFormSet
from invoices.models import Group, Meal, Attraction, Vehicle, MealType, AttractionType, VehicleType, Invoice, GuideInvoice, GuideInvoiceType, Tip, GuideTipType, DriverTipType
from django.db.models import Sum
from django.db import transaction


@login_required
def group_detail(request, pk):
    group = get_object_or_404(Group, pk=pk)
    invoice = Invoice.objects.filter(pk=pk).first()

    if request.method == 'POST':
        meal_formset = MealFormSet(request.POST, prefix='meal')
        attraction_formset = AttractionFormSet(request.POST, prefix='attraction')
        vehicle_formset = VehicleFormSet(request.POST, prefix='vehicle')
        guideinvoice_formset = GuideInvoiceFormSet(request.POST, prefix='guideinvoice')
        tip_formset = TipFormSet(request.POST, prefix='tip')

        if (meal_formset.is_valid() and 
            attraction_formset.is_valid() and 
            vehicle_formset.is_valid() and 
            guideinvoice_formset.is_valid() and 
            tip_formset.is_valid()):

            with transaction.atomic():
                if invoice:
                    invoice.delete()

                invoice = Invoice.objects.create(
                    pk=pk,
                    guide=group.guide,
                    driver=group.driver,
                    agent=group.agent,
                    start_date=group.start_date,
                    joycode=group.joycode,
                    agent_ref=group.agent_ref,
                    adt=group.adt,
                    chd=group.chd,
                    tc=group.tc
                )

                for form in meal_formset:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        mealtype = form.cleaned_data.get('mealtype')
                        pax_adt = form.cleaned_data.get('pax_adt') or (group.adt + group.tc if group.adt and group.tc else 0)
                        pax_chd = form.cleaned_data.get('pax_chd') or (group.tc if group.chd else 0)
                        price_adt = form.cleaned_data.get('price_adt') or (mealtype.price_adt if mealtype and mealtype.price_adt else 0)
                        price_chd = form.cleaned_data.get('price_chd') or (mealtype.price_chd if mealtype and mealtype.price_chd else 0)

                        price_adt_total = pax_adt * price_adt
                        price_chd_total = pax_chd * price_chd

                        Meal.objects.create(
                            invoice=invoice,
                            meal_type=mealtype,
                            date=form.cleaned_data.get('date'),
                            restaurant=mealtype.name if mealtype else '',
                            pax_adt=pax_adt,
                            pax_chd=pax_chd,
                            price_adt=price_adt,
                            price_chd=price_chd,
                            price_adt_total=price_adt_total,
                            price_chd_total=price_chd_total,
                            price_grand_total=price_adt_total + price_chd_total
                        )

                meal_res = Meal.objects.filter(invoice=invoice).aggregate(total=Sum('price_grand_total'))
                invoice.meal_total = meal_res['total'] or 0

                for form in attraction_formset:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        attractiontype = form.cleaned_data.get('attractiontype')
                        if attractiontype:
                            pax_adt = form.cleaned_data.get('pax_adt') or (group.adt + group.tc if group.adt and group.tc else 0)
                            pax_chd = form.cleaned_data.get('pax_chd') or (group.chd if group.chd else 0)
                            price_adt = form.cleaned_data.get('price_adt') or (attractiontype.price_adt if attractiontype.price_adt else 0)
                            price_chd = form.cleaned_data.get('price_chd') or (attractiontype.price_chd if attractiontype.price_chd else 0)

                            price_adt_total = pax_adt * price_adt
                            price_chd_total = pax_chd * price_chd

                            Attraction.objects.create(
                                invoice=invoice,
                                attraction_type=attractiontype,
                                attraction_name=attractiontype.name,
                                date=form.cleaned_data.get('date'),
                                pax_adt=pax_adt,
                                pax_chd=pax_chd,
                                price_adt=price_adt,
                                price_chd=price_chd,
                                price_adt_total=price_adt_total,
                                price_chd_total=price_chd_total,
                                price_grand_total=price_adt_total + price_chd_total
                            )

                attraction_res = Attraction.objects.filter(invoice=invoice).aggregate(total=Sum('price_grand_total'))
                invoice.attraction_total = attraction_res['total'] or 0

                for form in vehicle_formset:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        vehicletype = form.cleaned_data.get('vehicle_type')
                        if vehicletype:
                            price_total = form.cleaned_data.get('price_total') or (vehicletype.price if vehicletype.price else 0)
                            Vehicle.objects.create(
                                invoice=invoice,
                                vehicle_type=vehicletype,
                                seat=vehicletype.seat,
                                vehicle_name=f"{vehicletype.seat}: {vehicletype.location}",
                                date=form.cleaned_data.get('date'),
                                price_total=price_total
                            )

                vehicle_res = Vehicle.objects.filter(invoice=invoice).aggregate(total=Sum('price_total'))
                invoice.vehicle_total = vehicle_res['total'] or 0

                for form in guideinvoice_formset:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        guideinvoice_type = form.cleaned_data.get('guideinvoice_type')
                        if guideinvoice_type:
                            price_total = form.cleaned_data.get('price') or (guideinvoice_type.price if guideinvoice_type.price else 0)
                            GuideInvoice.objects.create(
                                invoice=invoice,
                                guideinvoice_type=guideinvoice_type,
                                guideinvoice_name=guideinvoice_type.location,
                                date=form.cleaned_data.get('date'),
                                price_total=price_total
                            )

                guideinvoice_res = GuideInvoice.objects.filter(invoice=invoice).aggregate(total=Sum('price_total'))
                invoice.guide_invoice_total = guideinvoice_res['total'] or 0

                for form in tip_formset:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        guidetiptype = form.cleaned_data.get('guidetiptype')
                        drivertiptype = form.cleaned_data.get('drivertiptype')
                        price_guidetip = form.cleaned_data.get('price_guide') or (guidetiptype.price if guidetiptype else 0)
                        price_drivertip = form.cleaned_data.get('price_driver') or (drivertiptype.price if drivertiptype else 0)

                        Tip.objects.create(
                            invoice=invoice,
                            date=form.cleaned_data.get('date'),
                            guidetip_type=guidetiptype,
                            drivertip_type=drivertiptype,
                            price_guidetip=price_guidetip,
                            price_drivertip=price_drivertip,
                            price_total=price_guidetip + price_drivertip
                        )

                tip_res = Tip.objects.filter(invoice=invoice).aggregate(
                    g_total=Sum('price_guidetip'),
                    d_total=Sum('price_drivertip')
                )
                invoice.tip_total = (tip_res['g_total'] or 0) + (tip_res['d_total'] or 0)

                op_fee = invoice.agent.operation_fee if (invoice.agent and invoice.agent.operation_fee) else 0
                invoice.grand_total = (
                    invoice.meal_total + 
                    invoice.attraction_total + 
                    invoice.vehicle_total + 
                    invoice.guide_invoice_total + 
                    invoice.tip_total + 
                    op_fee
                )
                invoice.save()

            return redirect('inbound:group_detail', pk=group.pk)

        context = {
            'group': group,
            'invoice': invoice,
            'meal_formset': meal_formset,
            'attraction_formset': attraction_formset,
            'vehicle_formset': vehicle_formset,
            'guideinvoice_formset': guideinvoice_formset,
            'tip_formset': tip_formset,
        }
        return render(request, 'inbound/group_detail.html', context)

    else:
        meal_initial = []
        attraction_initial = []
        vehicle_initial = []
        guideinvoice_initial = []
        tip_initial = []

        meals = []
        attractions = []
        vehicles = []
        guideinvoices = []
        tips = []

        if invoice:
            meals = invoice.meals.all()
            attractions = invoice.attractions.all()
            vehicles = invoice.vehicles.all()
            guideinvoices = invoice.guideinvoices.all()
            tips = invoice.tips.all()

            for m in meals:
                m_type = MealType.objects.filter(name=m.restaurant).first()
                meal_initial.append({
                    'mealtype': m_type,
                    'date': m.date,
                    'pax_adt': m.pax_adt,
                    'pax_chd': m.pax_chd,
                    'price_adt': m.price_adt,
                    'price_chd': m.price_chd,
                })

            for a in attractions:
                attraction_initial.append({
                    'attractiontype': a.attraction_type,
                    'date': a.date,
                    'pax_adt': a.pax_adt,
                    'pax_chd': a.pax_chd,
                    'price_adt': a.price_adt,
                    'price_chd': a.price_chd,
                })

            for v in vehicles:
                vehicle_initial.append({
                    'vehicle_type': v.vehicle_type,
                    'date': v.date,
                    'price_total': v.price_total,
                })

            for g in guideinvoices:
                guideinvoice_initial.append({
                    'guideinvoice_type': g.guideinvoice_type,
                    'date': g.date,
                    'price': g.price_total,
                })

            for t in tips:
                tip_initial.append({
                    'guidetiptype': t.guidetip_type,
                    'drivertiptype': t.drivertip_type,
                    'date': t.date,
                    'price_guide': t.price_guidetip,
                    'price_driver': t.price_drivertip,
                })

        context = {
            'group': group,
            'invoice': invoice,
            'meals': meals,
            'attractions': attractions,
            'vehicles': vehicles,
            'guideinvoices': guideinvoices,
            'tips': tips,
            'meal_formset': MealFormSet(prefix='meal', initial=meal_initial),
            'attraction_formset': AttractionFormSet(prefix='attraction', initial=attraction_initial),
            'vehicle_formset': VehicleFormSet(prefix='vehicle', initial=vehicle_initial),
            'guideinvoice_formset': GuideInvoiceFormSet(prefix='guideinvoice', initial=guideinvoice_initial),
            'tip_formset': TipFormSet(prefix='tip', initial=tip_initial),
        }

        return render(request, 'inbound/group_detail.html', context)


@login_required
def group_groupfile(request, pk): 
    group = get_object_or_404(Group, pk=pk)
    invoice = Invoice.objects.filter(pk=pk).first()
    guide = group.guide
    hoteltypes = HotelType.objects.all()
    
    form = HotelForm()

    if hasattr(group, 'groupfile'): 
        groupfile = group.groupfile
        hotel = groupfile.hotel
    else: 
        groupfile = GroupFile(group=group)
        groupfile.save()
        hotel = None

    context = {
        'groupfile': groupfile, 
        'group': group, 
        'invoice': invoice, 
        'guide': guide,
        'hotel': hotel,
        'hoteltypes': hoteltypes,
        'form': form
    }
    return render(request, 'inbound/group_groupfile.html', context)


@login_required
def create_hoteltype(request): 
    if request.method == 'POST': 
        form = HotelTypeForm(request.POST)
        if form.is_valid(): 
            form.save()
            return redirect('inbound:tariff')

    else: 
        form = HotelTypeForm()
        context = {
            'form': form
        }
        return render(request, 'inbound/create_hoteltype.html', context)
    

@login_required
def create_hotel(request, pk): 
    group = get_object_or_404(Group, pk=pk)
    groupfile = GroupFile.objects.filter(group=group).first()
    
    if request.method == "POST": 
        form = HotelForm(request.POST)
        if form.is_valid(): 
            Hotel.objects.create(
                groupfile=groupfile,
                hotel_type=form.cleaned_data['hoteltype'],
                confirm_num=form.cleaned_data['confirm_num'], 
                room_type=form.cleaned_data['room_type'],
            )
    return redirect('inbound:group_groupfile', pk)
    
@login_required
def update_hotel(request, pk): 
    hotel = get_object_or_404(Hotel, pk=pk)
    group = hotel.groupfile.group

    if request.method == "POST": 
        form = HotelForm(request.POST)
        if form.is_valid(): 
            hotel.hotel_type = form.cleaned_data['hoteltype'] if form.cleaned_data['hoteltype'] else hotel.hotel_type
            hotel.confirm_num = form.cleaned_data['confirm_num'] if form.cleaned_data['confirm_num'] else hotel.confirm_num
            hotel.room_type = form.cleaned_data['room_type'] if form.cleaned_data['room_type'] else hotel.room_type
            hotel.save()
            return redirect('inbound:group_groupfile', group.pk)
    else: 
        form = HotelForm(initial={
            'hoteltype': hotel.hotel_type,
            'confirm_num': hotel.confirm_num, 
            'room_type': hotel.room_type
        })
        return render(request, 'inbound/group_groupfile.html', {'form': form})


@login_required
def update_hoteltype(request, pk): 
    hoteltype = get_object_or_404(HotelType, pk=pk)

    if hoteltype: 
        if request.method == 'POST': 
            form = HotelTypeForm(request.POST, instance=hoteltype)
            if form.is_valid(): 
                form.save()
                return redirect('inbound:tariff')
        
        else: 
            form = HotelTypeForm(instance=hoteltype)
            context = {
                'form': form
            }
            return render(request, 'inbound/create_hoteltype.html', form)

    
    



@login_required
def create_group(request): 
    form = GroupForm(request.POST)
    if request.method == 'POST': 
        if form.is_valid(): 
            form.save() 

            return redirect('inbound:group_list')
        
    else: 
        context = {
            'form': form,
        }
        return render(request, 'inbound/create_group.html', context)



@login_required
def update_group(request, pk): 
    print('pk: ' + str(pk))
    group = get_object_or_404(Group, pk=pk)
    
     
    if request.method == 'POST': 
        form = GroupForm(request.POST)

        if form.is_valid(): 
            group.guide = form.cleaned_data['guide'] if form.cleaned_data['guide'] else group.guide
            group.driver = form.cleaned_data['driver'] if form.cleaned_data['driver'] else group.driver
            group.agent = form.cleaned_data['agent'] if form.cleaned_data['agent'] else group.agent
            group.start_date = form.cleaned_data['start_date'] if form.cleaned_data['start_date'] else group.start_date
            group.agent_ref = form.cleaned_data['agent_ref'] if form.cleaned_data['agent_ref'] else group.agent_ref
            group.adt = form.cleaned_data['adt'] if form.cleaned_data['adt'] else group.adt
            group.chd = form.cleaned_data['chd'] if form.cleaned_data['chd'] else group.chd
            group.tc = form.cleaned_data['tc'] if form.cleaned_data['tc'] else group.tc
        
        group.save()

        return redirect('inbound:group_detail', pk)
    else: 
        initial_group = {
            'guide': group.guide,
            'driver': group.driver,
            'start_date': group.start_date,
            'agent': group.agent,
            'agent_ref': group.agent_ref,
            'adt': group.adt, 
            'chd': group.chd, 
            'tc': group.tc
        }
        form = GroupForm(
            initial = initial_group
        )
        context = {
            'form': form, 
            'group': group
        }
        return render(request, 'inbound/update_group.html', context)


@login_required
def delete_group(request, pk): 
    group = get_object_or_404(Group, pk=pk)
    if group: 
        group.delete()

    return redirect('inbound:index')



@login_required
def create_groupfile(request, pk): 
    
    group = get_object_or_404(Group, pk=pk)

    if request.method == 'POST': 
        form = GroupFileForm(request.POST)

        if form.is_valid():    

            if form.cleaned_data: 

                GroupFile.objects.update_or_create(
                    group=group,
                    defaults = {
                        'hotel': form.cleaned_data['hotel'], 
                        'meeting_board': form.cleaned_data['meeting_board']
                    }
                )

            return redirect('inbound:group_detail', pk=pk)
    
    else: 
        existing_file = getattr(group, 'groupfile', None)
        
        if existing_file: 
            initial_data = {
                'group': existing_file.group,
                'hotel': existing_file.hotel,
                'meeting_board': existing_file.meeting_board
            }
            form = GroupFileForm(initial=initial_data)
        else: 
            form = GroupFileForm()
        return render(request, 'inbound/create_groupfile.html', {'group': group, 'form': form})
        
            

    