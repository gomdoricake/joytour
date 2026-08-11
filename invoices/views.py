from django.shortcuts import render, redirect, get_object_or_404
from .forms import MealFormSet, AttractionFormSet
from .models import Meal, Attraction

def index(request):
    if request.method == 'POST': 
        meal_formset = MealFormSet(request.POST, prefix='meal')         
        attraction_formset = AttractionFormSet(request.POST, prefix='attraction')
        
        if meal_formset.is_valid() and attraction_formset.is_valid(): 
            saved_meals = meal_formset.save()
            saved_attractions = attraction_formset.save()

            if saved_meals: 
                target_group_pk = saved_meals[0].pk
            elif saved_attractions: 
                target_group_pk = saved_attractions[0].pk

            return redirect('invoices:index', pk=target_group_pk)
        
    else: 
        meal_formset = MealFormSet(queryset=Meal.objects.none(), prefix='meal')
        attraction_formset = AttractionFormSet(queryset=Attraction.objects.none(), prefix='attraction')

    context = {
        'meal_formset': meal_formset, 
        'attraction_formset': attraction_formset
    }
    return render(request, 'invoices/index.html', context)

