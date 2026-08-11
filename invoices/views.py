from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import MealFormSet, MealTypeForm, AttractionFormSet
from .models import Group, Meal, Attraction, MealType, Invoice

def index(request, pk):
    if request.method == 'POST': 
        meal_formset = MealFormSet(request.POST, prefix='meal')         
        attraction_formset = AttractionFormSet(request.POST, prefix='attraction')
        
        if meal_formset.is_valid() and attraction_formset.is_valid(): 
            
            target_group_pk = None

            group = get_object_or_404(Group, pk=pk)


            for form in meal_formset:
                meal = Meal() 
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

                if form.cleaned_data and not form.cleaned_data.get('DELETE', False): 
                    meal.invoice = invoice
                    mealtype = form.cleaned_data.get('mealtype')

                    meal.date = form.cleaned_data.get('date')
                    meal.restaurant = mealtype.name
                    pax_tc = form.cleaned_data.get('tc') if form.cleaned_data.get('tc') else (group.tc if group.tc else 0)
                    
                    price_adt = (form.cleaned_data.get('adt') + pax_tc) * mealtype.price_adt if form.cleaned_data.get('adt') else (group.adt if group.adt else 0)
                    price_chd = form.cleaned_data.get('chd') * mealtype.price_chd if form.cleaned_data.get('chd') else (group.chd if group.chd else 0)
                    meal.price_adt = price_adt
                    meal.price_chd = price_chd

                    meal.price_total = price_adt + price_chd
                    meal.save()

            return redirect('inbound:group_detail', pk=group.pk)
        
    else: 
        meal_formset = MealFormSet(prefix='meal')
        attraction_formset = AttractionFormSet(queryset=Attraction.objects.none(), prefix='attraction')

    context = {
        'meal_formset': meal_formset, 
        'attraction_formset': attraction_formset
    }
    return render(request, 'invoices/index.html', context)


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
    
        