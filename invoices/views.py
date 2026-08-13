from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import MealTypeForm, VehicleTypeForm, GuideInvoiceTypeForm, GuideTipTypeForm, DriverTipTypeForm, MealFormSet, AttractionFormSet, VehicleFormSet,  GuideInvoiceFormSet, TipFormSet
from .models import Group, Meal, Attraction, Vehicle, MealType, AttractionType, VehicleType, Invoice, GuideInvoice, GuideInvoiceType, Tip, GuideTipType, DriverTipType

def index(request, pk): 
    group = get_object_or_404(Group, pk=pk)

    invoice = None
    if Invoice.objects.filter(pk=pk).exists():
        invoice = Invoice.objects.get(pk=pk)
    
    meals = Meal.objects.filter(invoice=invoice)
    attractions = Attraction.objects.filter(invoice=invoice)
    vehicles = Vehicle.objects.filter(invoice=invoice)
    guideinvoices = GuideInvoice.objects.filter(invoice=invoice)
    tips = Tip.objects.filter(invoice=invoice)

    context = {
        'group': group,
        'invoice': invoice,
        'meals': meals, 
        'attractions': attractions,
        'vehicles': vehicles,
        'guideinvoices': guideinvoices, 
        'tips': tips
    }
    return render(request, 'invoices/index.html', context)

from django.db.models import Sum

def create_invoice(request, pk):
    if request.method == 'POST': 
        meal_formset = MealFormSet(request.POST, prefix='meal')         
        attraction_formset = AttractionFormSet(request.POST, prefix='attraction')
        vehicle_formset = VehicleFormSet(request.POST, prefix='vehicle')
        guideinvoice_formset = GuideInvoiceFormSet(request.POST, prefix='guideinvoice')
        tip_formset = TipFormSet(request.POST, prefix='tip')
        
        if meal_formset.is_valid() and attraction_formset.is_valid() and vehicle_formset.is_valid() \
            and guideinvoice_formset.is_valid() and tip_formset.is_valid(): 
            
            target_group_pk = None

            group = get_object_or_404(Group, pk=pk)

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
                meal = Meal() 

                if form.cleaned_data and not form.cleaned_data.get('DELETE', False): 
                    meal.invoice = invoice
                    mealtype = form.cleaned_data.get('mealtype')

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
                attraction = Attraction()
                
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False): 
                    attraction.invoice = invoice
                    attractiontype = form.cleaned_data.get('attractiontype')
                    attraction.attraction_type = attractiontype.name
                    attraction.date = form.cleaned_data.get('date')

                    attraction.price_adt = form.cleaned_data.get('adt') * attractiontype.price_adt if form.cleaned_data.get('adt') else (group.adt * attractiontype.price_adt if group.adt else 0)
                    attraction.price_chd = form.cleaned_data.get('chd') * attractiontype.price_chd if form.cleaned_data.get('chd') else (group.chd * attractiontype.price_chd if group.chd else 0)
                    attraction.price_tc = form.cleaned_data.get('tc') * attractiontype.price_tc if form.cleaned_data.get('tc') else (group.tc * attractiontype.price_tc if group.tc else 0)

                    attraction.price_total = attraction.price_adt + attraction.price_chd + attraction.price_tc
                    attraction.save()

            attraction_result = Attraction.objects.filter(invoice=invoice).aggregate(
                attraction_total = Sum('price_total')
            )

            invoice.attraction_total = attraction_result['attraction_total'] or 0


            for form in vehicle_formset: 
                vehicle = Vehicle()
                
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False): 
                    vehicle.invoice = invoice
                    vehicletype = form.cleaned_data.get('vehicle_type')
                    vehicle.seat = vehicletype.seat
                    vehicle.vehicle_type = vehicle.seat + ": " + vehicletype.location
                    vehicle.date = form.cleaned_data.get('date')

                    vehicle.price_total = form.cleaned_data.get('price') if form.cleaned_data.get('price') else (vehicletype.price if vehicletype.price else 0) 
                    
                    vehicle.save()

            vehicle_result = Vehicle.objects.filter(invoice=invoice).aggregate(
                vehicle_total = Sum('price_total')
            )

            invoice.vehicle_total = vehicle_result['vehicle_total'] or 0

            for form in guideinvoice_formset: 
                guideinvoice = GuideInvoice()

                if form.cleaned_data and not form.cleaned_data.get('DELETE', False): 
                    guideinvoice.invoice = invoice
                    guideinvoicetype = form.cleaned_data.get('guideinvoice_type')

                    guideinvoice.guideinvoice_type = guideinvoicetype.location
                    guideinvoice.date = form.cleaned_data.get('date')

                    guideinvoice.price_total = form.cleaned_data.get('price') if form.cleaned_data.get('price') else (guideinvoicetype.price if guideinvoicetype.price else 0)

                guideinvoice.save()

            guideinvoice_result = GuideInvoice.objects.filter(invoice=invoice).aggregate(
                guideinvoice_total = Sum('price_total')
            )

            invoice.guide_invoice_total = guideinvoice_result['guideinvoice_total'] or 0


            for form in tip_formset: 
                tip = Tip()

                guidetiptype = None
                drivertiptype = None
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False): 
                    tip.invoice = invoice
                    tip.date = form.cleaned_data.get('date')
                    guidetiptype = form.cleaned_data.get('guidetiptype')
                    drivertiptype = form.cleaned_data.get('drivertiptype')

                    tip.price_guidetip = form.cleaned_data.get('price_guide') if form.cleaned_data.get('price_guide') else (guidetiptype.price if guidetiptype else 0)
                    tip.price_drivertip = form.cleaned_data.get('price_driver') if form.cleaned_data.get('price_driver') else (drivertiptype.price if drivertiptype else 0)
                    
                    tip.price_total = tip.price_guidetip + tip.price_drivertip
                
                tip.save()
                tip.guidetiptype.set([guidetiptype])
                tip.drivertiptype.set([drivertiptype])

                
            guidetip_result = Tip.objects.filter(invoice=invoice).aggregate(
                guidetip_total = Sum('price_guidetip')
            )
            drivertip_result = Tip.objects.filter(invoice=invoice).aggregate(
                drivertip_total = Sum('price_drivertip')
            )

            guidetipresult = guidetip_result['guidetip_total'] or 0
            drivertipresult = drivertip_result['drivertip_total'] or 0

            invoice.tip_total = guidetipresult + drivertipresult


            invoice.grand_total = invoice.meal_total + invoice.attraction_total + invoice.vehicle_total + invoice.guide_invoice_total + invoice.tip_total + invoice.agent.operation_fee

            invoice.save()

            return redirect('inbound:group_detail', pk=group.pk)
        
    else: 
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

class MealTypeListView(ListView): 
    model = MealType
    template_name = 'invoices/mealtype_list.html'
    context_object_name = 'mealtype_list'

    def get_queryset(self): 
        queryset = super().get_queryset()
        return queryset
            

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
    

class AttractionTypeListView(ListView): 
    model = AttractionType
    template_name = 'invoices/attractiontype_list.html'
    context_object_name = 'attractiontype_list'

    def get_queryset(self): 
        queryset = super().get_queryset()
        return queryset


@login_required
def create_attractiontype(request): 
    
    if request.method == 'POST': 
        form = AttractionTypeForm(request.POST)
        
        if form.is_valid(): 
            form.save()

            return redirect('invoices:attractiontype_list')
    
    else: 
        form = AttractionTypeForm()
        context = {
            'form': form
        }
        return render(request, 'invoices/create_attractiontype.html', context)


class VehicleTypeListView(ListView): 
    model = VehicleType
    template_name = 'invoices/vehicletype_list.html'
    context_object_name = 'vehicletype_list'

    def get_queryset(self): 
        queryset = super().get_queryset()
        return queryset


@login_required
def create_vehicletype(request): 
    if request.method == 'POST': 
        form = VehicleTypeForm(request.POST)
        
        if form.is_valid(): 
            form.save()

        return redirect('invoices:vehicletype_list')
    
    else: 
        form = VehicleTypeForm()
        context = {
            'form': form
        }
        return render(request, 'invoices/create_vehicletype.html', context)


class GuideInvoiceTypeListView(ListView): 
    model = GuideInvoiceType
    template_name = 'invoices/guideinvoicetype_list.html'
    context_object_name = 'guideinvoicetype_list'

    def get_queryset(self): 
        queryset = super().get_queryset()
        return queryset


@login_required
def create_guideinvoicetype(request): 
    
    if request.method == 'POST': 
        form = GuideInvoiceTypeForm(request.POST)

        if form.is_valid(): 
            form.save()

            return redirect('invoices:guideinvoicetype_list')
        
    else: 
        form = GuideInvoiceTypeForm()
        context = {
            'form': form
        }
        return render(request, 'invoices/create_guideinvoicetype.html', context)


@login_required
def tiptype_list(request): 
    guide_tip = GuideTipType.objects.all()
    driver_tip = DriverTipType.objects.all()

    context = {
        'guide_tip': guide_tip, 
        'driver_tip': driver_tip
    }
    return render(request, 'invoices/tiptype_list.html', context)

@login_required
def create_guidetiptype(request): 
    
    if request.method == 'POST': 
        form = GuideTipTypeForm(request.POST)

        if form.is_valid(): 
            form.save()

            return redirect('invoices:tiptype_list')
    
    else: 
        form = GuideTipTypeForm()
        context = {
            'form': form
        }
        return render(request, 'invoices/create_guidetiptype.html', context)

@login_required
def create_drivertiptype(request): 
    
    if request.method == 'POST': 
        form = DriverTipTypeForm(request.POST)

        if form.is_valid(): 
            form.save()

            return redirect('invoices:tiptype_list')
    
    else: 
        form = DriverTipTypeForm()
        context = {
            'form': form
        }
        return render(request, 'invoices/create_drivertiptype.html', context)


        