from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import MealTypeForm, VehicleTypeForm, GuideInvoiceTypeForm, GuideTipTypeForm, DriverTipTypeForm, MealFormSet, AttractionTypeForm, AttractionFormSet, VehicleFormSet,  GuideInvoiceFormSet, TipFormSet
from .models import Group, Meal, Attraction, Vehicle, MealType, AttractionType, VehicleType, Invoice, GuideInvoice, GuideInvoiceType, Tip, GuideTipType, DriverTipType

from django.db.models import Sum



from django.views.generic.list import ListView
     

@login_required
def create_mealtype(request):

    if request.method == 'POST': 
        form = MealTypeForm(request.POST)
        if form.is_valid(): 
            form.save()

            return redirect('inbound:tariff')

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
