from django.contrib import admin
from .models import Meal, MealType, Attraction, AttractionType, Invoice

admin.site.register(Invoice)
admin.site.register(Meal)
admin.site.register(MealType)
admin.site.register(Attraction)
admin.site.register(AttractionType)