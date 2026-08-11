from django import forms
from django.forms import modelformset_factory
from .models import Meal, Attraction

MealFormSet = modelformset_factory(
    Meal, 
    fields=['date', 'meal_type', 'price_adt', 'price_chd', 'price_total'],
    extra=0
)

AttractionFormSet = modelformset_factory(
    Attraction,
    fields=['date', 'attraction_type', 'price_adt', 'price_chd', 'price_total'],
    extra=0
)