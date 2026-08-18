from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import MealTypeForm, VehicleTypeForm, GuideInvoiceTypeForm, GuideTipTypeForm, DriverTipTypeForm, MealFormSet, AttractionTypeForm, AttractionFormSet, VehicleFormSet,  GuideInvoiceFormSet, TipFormSet
from .models import Group, Meal, Attraction, Vehicle, MealType, AttractionType, VehicleType, Invoice, GuideInvoice, GuideInvoiceType, Tip, GuideTipType, DriverTipType

from django.db.models import Sum


@login_required
def create_or_update_invoice(request, pk):
    group = get_object_or_404(Group, pk=pk)

    if request.method == 'POST': 
        meal_formset = MealFormSet(request.POST, prefix='meal')         
        attraction_formset = AttractionFormSet(request.POST, prefix='attraction')
        vehicle_formset = VehicleFormSet(request.POST, prefix='vehicle')
        guideinvoice_formset = GuideInvoiceFormSet(request.POST, prefix='guideinvoice')
        tip_formset = TipFormSet(request.POST, prefix='tip')


        if Invoice.objects.filter(pk=pk).exists():
            invoice = get_object_or_404(Invoice, pk=pk)
            invoice.delete()
            

        # 생성 로직
        if meal_formset.is_valid() and attraction_formset.is_valid() and vehicle_formset.is_valid() \
            and guideinvoice_formset.is_valid() and tip_formset.is_valid(): 
            
            target_group_pk = None

            invoice = Invoice(
                guide=group.guide, 
                driver=group.driver, 
                agent=group.agent,
                start_date=group.start_date,
                joycode=group.joycode, 
                agent_ref=group.agent_ref, 
                adt=group.adt, 
                chd=group.chd,
                tc=group.tc,
                pk=pk)

            invoice.save()

            for form in meal_formset:
                
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False): 
                    meal = Meal() 
                    meal.invoice = invoice
                    mealtype = form.cleaned_data.get('mealtype')

                    meal.meal_type = mealtype

                    meal.date = form.cleaned_data.get('date')
                    meal.restaurant = mealtype.name
                    pax_tc = form.cleaned_data.get('tc') if form.cleaned_data.get('tc') else (group.tc if group.tc else 0)
                    
                    price_adt = (form.cleaned_data.get('adt') + pax_tc) * mealtype.price_adt if form.cleaned_data.get('adt') else (group.adt * mealtype.price_adt if group.adt else 0)
                    price_chd = form.cleaned_data.get('chd') * mealtype.price_chd if form.cleaned_data.get('chd') else (group.chd * mealtype.price_chd if group.chd else 0)
                    meal.price_adt = price_adt
                    meal.price_chd = price_chd

                    meal.price_total = price_adt + price_chd
                    meal.save()

            
            meal_result = Meal.objects.filter(invoice=invoice).aggregate(
                meal_total = Sum('price_total')
            )

            invoice.meal_total = meal_result['meal_total'] or 0

            for form in attraction_formset: 
                
                
                if form.cleaned_data['attractiontype'] and not form.cleaned_data.get('DELETE', False): 
                    attraction = Attraction()
                    attraction.invoice = invoice
                    
                    attractiontype = form.cleaned_data.get('attractiontype')
                    attraction.attraction_type = attractiontype

                    attraction.attraction_name = attractiontype.name
                    attraction.date = form.cleaned_data.get('date')

                    attraction.price_adt = form.cleaned_data.get('adt') * attractiontype.price_adt if form.cleaned_data.get('adt') else (group.adt * attractiontype.price_adt if group.adt else 0)
                    attraction.price_chd = form.cleaned_data.get('chd') * attractiontype.price_chd if form.cleaned_data.get('chd') else (group.chd * attractiontype.price_chd if group.chd else 0)

                    attraction.price_total = attraction.price_adt + attraction.price_chd
                    attraction.save()

            attraction_result = Attraction.objects.filter(invoice=invoice).aggregate(
                attraction_total = Sum('price_total')
            )

            invoice.attraction_total = attraction_result['attraction_total'] or 0


            for form in vehicle_formset: 
                
                if form.cleaned_data['vehicle_type'] and not form.cleaned_data.get('DELETE', False):

                    vehicle = Vehicle()
                    vehicle.invoice = invoice
                    vehicletype = form.cleaned_data.get('vehicle_type')

                    vehicle.seat = vehicletype.seat
                    vehicle.vehicle_type = vehicletype
                    
                    vehicle.vehicle_name = vehicletype.seat + ": " + vehicletype.location
                    vehicle.date = form.cleaned_data.get('date')

                    vehicle.price_total = form.cleaned_data.get('price') if form.cleaned_data.get('price') else (vehicletype.price if vehicletype.price else 0) 
                    
                    vehicle.save()

            vehicle_result = Vehicle.objects.filter(invoice=invoice).aggregate(
                vehicle_total = Sum('price_total')
            )

            invoice.vehicle_total = vehicle_result['vehicle_total'] or 0

            for form in guideinvoice_formset: 

                if form.cleaned_data and not form.cleaned_data.get('DELETE', False): 
                    guideinvoice = GuideInvoice()

                    guideinvoice.invoice = invoice
                    guideinvoice_type = form.cleaned_data.get('guideinvoice_type')

                    guideinvoice.guideinvoice_type = guideinvoice_type

                    guideinvoice.guideinvoice_name = guideinvoice_type.location
                    guideinvoice.date = form.cleaned_data.get('date')

                    guideinvoice.price_total = form.cleaned_data.get('price') if form.cleaned_data.get('price') else (guideinvoice_type.price if guideinvoice_type.price else 0)

                guideinvoice.save()

            guideinvoice_result = GuideInvoice.objects.filter(invoice=invoice).aggregate(
                guideinvoice_total = Sum('price_total')
            )

            invoice.guide_invoice_total = guideinvoice_result['guideinvoice_total'] or 0


            for form in tip_formset: 
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False): 
                    tip = Tip()

                    tip.invoice = invoice
                    tip.date = form.cleaned_data.get('date')

                    guidetiptype = form.cleaned_data.get('guidetiptype')
                    drivertiptype = form.cleaned_data.get('drivertiptype')

                    tip.guidetip_type = guidetiptype
                    tip.drivertip_type = drivertiptype

                    tip.price_guidetip = form.cleaned_data.get('price_guide') if form.cleaned_data.get('price_guide') else (guidetiptype.price if guidetiptype else 0)
                    tip.price_drivertip = form.cleaned_data.get('price_driver') if form.cleaned_data.get('price_driver') else (drivertiptype.price if drivertiptype else 0)
                    
                    tip.price_total = tip.price_guidetip + tip.price_drivertip
                
                    tip.save()

                
            guidetip_result = Tip.objects.filter(invoice=invoice).aggregate(
                guidetip_total = Sum('price_guidetip')
            )
            drivertip_result = Tip.objects.filter(invoice=invoice).aggregate(
                drivertip_total = Sum('price_drivertip')
            )

            guidetipresult = guidetip_result['guidetip_total'] or 0
            drivertipresult = drivertip_result['drivertip_total'] or 0

            invoice.tip_total = guidetipresult + drivertipresult


            meal_total = invoice.meal_total if invoice.meal_total else 0
            attraction_total = invoice.attraction_total if invoice.attraction_total else 0
            vehicle_total = invoice.vehicle_total if invoice.vehicle_total else 0
            guide_invoice_total = invoice.guide_invoice_total if invoice.guide_invoice_total else 0
            tip_total = invoice.tip_total if invoice.tip_total else 0
            operation_fee = invoice.agent.operation_fee if invoice.agent and invoice.agent.operation_fee else 0

            invoice.grand_total = meal_total + attraction_total + vehicle_total + guide_invoice_total + tip_total 

            invoice.save()

            return redirect('inbound:group_detail', pk=group.pk)

        else: 
            return redirect('invoices:create_or_update_invoice', pk=group.pk)
    # GET
    else: 

        if Invoice.objects.filter(pk=pk).exists():
            invoice = get_object_or_404(Invoice, pk=pk)
            # 1. Meal
            temp_meals = invoice.meals.values()
            meal_initial_data = []


            for meal in temp_meals:
                if meal: 
                    if MealType.objects.filter(name=meal['restaurant']).exists(): 
                        mealtype = MealType.objects.get(name=meal['restaurant'])
                    else: 
                        mealtype = None

                    adt = int(float(meal['price_adt']) / float(mealtype.price_adt)) if meal['price_adt'] and mealtype else 0
                    chd = int(float(meal['price_chd']) / float(mealtype.price_chd)) if meal['price_chd'] and mealtype else 0
                    
                    meal_initial_data.append(
                        {
                            'mealtype': mealtype, 
                            'date': meal['date'],
                            'adt': adt,
                            'chd': chd,
                        }
                    ) 

            initial_meal_formset = MealFormSet(prefix='meal', initial=meal_initial_data) 

            # 2. Attraction
            temp_attractions = invoice.attractions.all()
            attraction_initial_data = []

            for attraction in temp_attractions:
                attractiontype = attraction.attraction_type

                adt = int(float(attraction.price_adt) / float(attractiontype.price_adt)) if attractiontype and attraction.price_adt else 0
                chd = int(float(attraction.price_chd) / float(attractiontype.price_chd)) if attractiontype and attraction.price_chd else 0
                tc = int(float(attraction.price_tc) / float(attractiontype.price_tc)) if attractiontype and attraction.price_tc else 0
                
                attraction_initial_data.append(
                    {
                        'attractiontype': attractiontype, 
                        'date': attraction.date,
                        'adt': adt,
                        'chd': chd,
                        'tc': tc
                    }
                ) 
            
            initial_attraction_formset = AttractionFormSet(prefix='attraction', initial=attraction_initial_data)
            
            # 3. Vehicle
            temp_vehicles = invoice.vehicles.all()
            vehicle_initial_data = []


            for vehicle in temp_vehicles:

                vehicletype = vehicle.vehicle_type
                vehicle_initial_data.append(
                    {
                        'vehicle_type': vehicletype, 
                        'date': vehicle.date,
                        'price': vehicle.price_total
                    }
                ) 

            vehicle_initial_formset = VehicleFormSet(prefix='vehicle', initial=vehicle_initial_data)


            # 4. Guide Invoice
            temp_guideinvoices = invoice.guideinvoices.all()
            guideinvoice_initial_data = []


            for guideinvoice in temp_guideinvoices:

                guideinvoice_type = guideinvoice.guideinvoice_type

                guideinvoice_initial_data.append(
                    {
                        'guideinvoice_type': guideinvoice_type, 
                        'date': guideinvoice.date,
                        'price': guideinvoice_type.price
                    }
                ) 

            guideinvoice_initial_formset = GuideInvoiceFormSet(prefix='guideinvoice', initial=guideinvoice_initial_data)


            # 5. Tip 
            temp_tips = invoice.tips.all()
            tips_initial_data = []


            for tip in temp_tips:

                guidetip_type = tip.guidetip_type if tip.guidetip_type else None
                drivertip_type = tip.drivertip_type if tip.drivertip_type else None

                tips_initial_data.append(
                    {
                        'guidetiptype': guidetip_type, 
                        'drivertiptype': drivertip_type,
                        'date': tip.date,
                        'price_guide': guidetip_type.price if guidetip_type else 0,
                        'price_driver': drivertip_type.price if drivertip_type else 0
                    }
                ) 

            tip_initial_formset = TipFormSet(prefix='tip', initial=tips_initial_data)

            context = {
                'meal_formset': initial_meal_formset,
                'attraction_formset': initial_attraction_formset,
                'vehicle_formset': vehicle_initial_formset,
                'guideinvoice_formset': guideinvoice_initial_formset,
                'tip_formset': tip_initial_formset
            }

            return render(request, 'invoices/create_invoice.html', context)

        meal_formset = MealFormSet(prefix='meal')
        attraction_formset = AttractionFormSet(prefix='attraction')
        vehicle_formset = VehicleFormSet(prefix='vehicle')
        guideinvoice_formset = GuideInvoiceFormSet(prefix='guideinvoice')
        tip_formset = TipFormSet(prefix='tip')
        
        context = {
            'meal_formset': meal_formset, 
            'attraction_formset': attraction_formset,
            'vehicle_formset': vehicle_formset,
            'guideinvoice_formset': guideinvoice_formset,
            'tip_formset': tip_formset,
        }

        return render(request, 'invoices/create_invoice.html', context)


from django.views.generic.list import ListView
     

@login_required
def create_mealtype(request):

    if request.method == 'POST': 
        form = MealTypeForm(request.POST)
        if form.is_valid(): 
            form.save()

            return redirect('invoices:mealtype_list')

    form = MealTypeForm()
    context = {
        'form': form
    }
    return render(request, 'invoices/create_mealtype.html', context)


@login_required
def update_mealtype(request, pk): 
    mealtype = get_object_or_404(MealType, pk=pk)
    if mealtype: 
        if request.method == 'POST': 
            form = MealTypeForm(request.POST, instance=mealtype)
            if form.is_valid(): 
                form.save()
                return redirect('inbound:tariff')
        else: 
            form = MealTypeForm(instance=mealtype)
            return render(request, 'inbound/tariff_list.html', {'form': form})

@login_required
def delete_mealtype(request, pk): 
    mealtype = get_object_or_404(MealType, pk=pk)

    if mealtype: 
        mealtype.delete()
        return redirect('inbound:tariff')



@login_required
def create_attractiontype(request): 
    
    if request.method == 'POST': 
        form = AttractionTypeForm(request.POST)
        
        if form.is_valid(): 
            form.save()

            return redirect('inbound:tariff')
    
    else: 
        form = AttractionTypeForm()
        context = {
            'form': form
        }
        return render(request, 'invoices/create_attractiontype.html', context)


@login_required
def update_attractiontype(request, pk): 

    attractiontype = get_object_or_404(AttractionType, pk=pk)

    if attractiontype: 
        if request.method == 'POST': 
            form = AttractionTypeForm(request.POST, instance=attractiontype)

            if form.is_valid(): 
                form.save()
                return redirect('inbound:tariff')
        
        else: 
            form = AttractionTypeForm(instance=attractiontype)
            
            return redirect('inbound:tariff')


@login_required
def delete_attractiontype(request, pk): 
    attractiontype = get_object_or_404(AttractionType, pk=pk)

    if attractiontype: 
        attractiontype.delete()
        return redirect('inbound:tariff')


@login_required
def create_vehicletype(request): 
    if request.method == 'POST': 
        form = VehicleTypeForm(request.POST)
        
        if form.is_valid(): 
            form.save()

        return redirect('inbound:tariff')
    
    else: 
        form = VehicleTypeForm()
        context = {
            'form': form
        }
        return render(request, 'invoices/create_vehicletype.html', context)


@login_required
def update_vehicletype(request, pk): 
    
    vehicletype = get_object_or_404(VehicleType, pk=pk)

    if vehicletype: 
        if request.method == 'POST': 
            form = VehicleTypeForm(request.POST, instance=vehicletype)

            if form.is_valid(): 
                form.save()
                return redirect('inbound:tariff')
        
        else: 
            form = VehicleTypeForm(instance=vehicletype)
            return redirect('inbound:tariff')


@login_required
def delete_vehicletype(request, pk): 
    vehicletype = get_object_or_404(VehicleType, pk=pk)

    if vehicletype: 
        vehicletype.delete()
        return redirect('inbound:tariff')


@login_required
def create_guideinvoicetype(request): 
    
    if request.method == 'POST': 
        form = GuideInvoiceTypeForm(request.POST)

        if form.is_valid(): 
            form.save()

            return redirect('inbound:tariff')
        
    else: 
        form = GuideInvoiceTypeForm()
        context = {
            'form': form
        }
        return render(request, 'invoices/create_guideinvoicetype.html', context)


@login_required
def update_guideinvoicetype(request, pk): 
    guideinvoicetype = get_object_or_404(GuideInvoiceType, pk=pk)

    if guideinvoicetype:
        if request.method == 'POST': 
            form = GuideInvoiceTypeForm(request.POST, instance=guideinvoicetype)

            if form.is_valid(): 
                form.save()
                return redirect("inbound:tariff")
        
        else: 
            form = GuideInvoiceType(instance=guideinvoicetype)
            return redirect("inbound:tariff")


@login_required
def delete_guideinvoicetype(request, pk): 
    guideinvoicetype = get_object_or_404(GuideInvoiceType, pk=pk)

    if guideinvoicetype: 
        guideinvoicetype.delete()
        return redirect("inbound:tariff") 



@login_required
def create_guidetiptype(request): 
    
    if request.method == 'POST': 
        form = GuideTipTypeForm(request.POST)

        if form.is_valid(): 
            form.save()

            return redirect('inbound:tariff')
    
    else: 
        form = GuideTipTypeForm()
        context = {
            'form': form
        }
        return render(request, 'invoices/create_guidetiptype.html', context)


@login_required
def update_guidetiptype(request, pk): 
    guidetiptype = get_object_or_404(GuideTipType, pk=pk)

    if guidetiptype: 
        if request.method == 'POST': 
            guidetip_form = GuideTipTypeForm(request.POST, instance=guidetiptype)
            if guidetip_form.is_valid(): 
                guidetip_form.save()
                return redirect('inbound:tariff')
        
        else: 
            guidetip_form = GuideTipTypeForm(instance=guidetiptype)
            return render(request, 'invoices/tiptype_list.html', {'guidetip_form': guidetip_form})


@login_required
def delete_guidetiptype(request, pk): 
    guidetiptype = get_object_or_404(GuideTipType, pk=pk)

    if guidetiptype: 
        guidetiptype.delete()
        return redirect('inbound:tariff')


@login_required
def create_drivertiptype(request): 
    
    if request.method == 'POST': 
        form = DriverTipTypeForm(request.POST)

        if form.is_valid(): 
            form.save()

            return redirect('inbound:tariff')
    
    else: 
        form = DriverTipTypeForm()
        context = {
            'form': form
        }
        return render(request, 'invoices/create_drivertiptype.html', context)


@login_required
def update_drivertiptype(request, pk): 
    drivertiptype = get_object_or_404(DriverTipType, pk=pk)

    if drivertiptype: 
        if request.method == 'POST': 
            drivertip_form = DriverTipTypeForm(request.POST, instance=drivertiptype)
            if drivertip_form.is_valid(): 
                drivertip_form.save()
                return redirect('inbound:tariff')
        
        else: 
            drivertip_form = DriverTipTypeForm(instance=drivertiptype)
            return render(request, 'invoices/tiptype_list.html', {'drivertip_form': drivertip_form})

@login_required
def delete_drivertiptype(request, pk): 
    drivertiptype = get_object_or_404(DriverTipType, pk=pk)

    if drivertiptype: 
        drivertiptype.delete()
        return redirect('inbound:tariff')
